"""Repeatable student showcase: published tests, study tasks and feedback."""
from datetime import datetime,timedelta,timezone
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.db import engine,metadata,table,add
from app.curriculum_seed import topic_names
from scripts.fill_feature_showcase import NOTE

def main():
    metadata.reflect(bind=engine)
    now=datetime.now(timezone.utc).replace(tzinfo=None,microsecond=0)
    counts={'available_tests':0,'plans':0,'feedback':0,'topics':0}
    with Session(engine) as db:
        us=table('users');users=list(db.execute(select(us)).mappings());admin=next(u for u in users if u['role']=='ADMIN' and u['is_active'])
        # Complete the legacy showcase student's class without changing its enrollment.
        student=next((u for u in users if u['email']=='student@learnpath.dev'),None)
        if student:
            en=table('student_enrollments');sec=table('sections');sub=table('subjects');fa=table('faculty_subject_assignments')
            for cohort in db.execute(select(sec).join(en,en.c.section_id==sec.c.section_id).where(en.c.student_id==student['user_id'],en.c.status=='ACTIVE')).mappings():
                for subject in db.execute(select(sub).where(sub.c.course_id==cohort['course_id'])).mappings():
                    curriculum=table('subject_curriculum')
                    if db.scalar(select(curriculum.c.subject_id).where(curriculum.c.subject_id==subject['subject_id'])):continue
                    tp=table('topics')
                    if not db.scalar(select(tp.c.topic_id).where(tp.c.subject_id==subject['subject_id']).limit(1)):
                        for i,name in enumerate(topic_names(subject['subject_name'])):
                            add(db,'topics',subject_id=subject['subject_id'],topic_name=name);counts['topics']+=1
                    if not db.scalar(select(fa.c.faculty_assignment_id).where(fa.c.subject_id==subject['subject_id'],fa.c.section_id==cohort['section_id'])):
                        teacher=next(u for u in users if u['role']=='FACULTY' and u['department_id']==student['department_id'] and u['is_active'])
                        add(db,'faculty_subject_assignments',faculty_id=teacher['user_id'],subject_id=subject['subject_id'],section_id=cohort['section_id'])
        # Enrolled scopes only. One available daily/weekly/final exam per class.
        en=table('student_enrollments');mappings=list(db.execute(select(table('faculty_subject_assignments'))).mappings());seen=set();planned=set()
        for mapping in mappings:
            sid,section=mapping['subject_id'],mapping['section_id'];pair=(sid,section)
            if pair in seen:continue
            seen.add(pair)
            students=list(db.scalars(select(en.c.student_id).where(en.c.section_id==section,en.c.status=='ACTIVE')))
            if not students:continue
            tp=table('topics');topics=list(db.execute(select(tp).where(tp.c.subject_id==sid).order_by(tp.c.topic_id)).mappings())
            if not topics:continue
            q=table('questions');questions=list(db.execute(select(q).where(q.c.topic_id.in_([t['topic_id'] for t in topics]),q.c.question_type=='MCQ',q.c.review_status=='APPROVED',q.c.is_active==True).limit(3)).mappings())
            if not questions:
                questions=[add(db,'questions',topic_id=topics[0]['topic_id'],created_by=mapping['faculty_id'],question_text='Which step should precede validating a technical solution?',question_type='MCQ',difficulty='EASY',choice_options=['State the assumptions','Hide the inputs','Skip the method','Ignore units'],correct_answer='State the assumptions',explanation=NOTE)]
            for i,kind in enumerate(['DAILY','WEEKLY','FINAL']):
                request=f'student-v1-{sid}-{section}-{i}'
                series=table('exam_series')
                if db.scalar(select(series.c.request_key).where(series.c.request_key==request)):continue
                test=add(db,'tests',subject_id=sid,section_id=section,created_by=mapping['faculty_id'],title=f'{kind.title()} Practice — Subject {sid}',description=NOTE,duration_minutes=30,max_attempts=5,start_at=now-timedelta(days=1),end_at=now+timedelta(days=90),status='PUBLISHED')
                db.execute(series.insert().values(request_key=request,fingerprint='1'*64,created_by=admin['user_id']))
                db.execute(table('exam_schedules').insert().values(test_id=test['test_id'],request_key=request,exam_type=kind,occurrence_number=1))
                for qi,question in enumerate(questions):db.execute(table('test_questions').insert().values(test_id=test['test_id'],question_id=question['question_id'],marks=5,question_order=qi+1))
                counts['available_tests']+=1
            for student_id in students:
                if student_id not in planned:
                    planned.add(student_id);plans=table('study_plans')
                    if not db.scalar(select(plans.c.plan_id).where(plans.c.student_id==student_id,plans.c.status=='ACTIVE').limit(1)):
                        plan=add(db,'study_plans',student_id=student_id,subject_id=sid,created_by=mapping['faculty_id'],generated_by='FACULTY',title='Weekly learning and revision plan',start_date=now.date(),end_date=(now+timedelta(days=7)).date())
                        for ti,topic in enumerate(topics[:3]):add(db,'study_plan_items',plan_id=plan['plan_id'],topic_id=topic['topic_id'],scheduled_date=(now+timedelta(days=ti)).date(),recommendation='Review the key concepts, solve a worked example and attempt a practice quiz. '+NOTE,estimated_minutes=30,status=['COMPLETED','IN_PROGRESS','PENDING'][ti])
                        counts['plans']+=1
                fb=table('staff_feedback');key=f'class:{sid}:{section}'
                if not db.scalar(select(fb.c.feedback_id).where(fb.c.author_id==student_id,fb.c.faculty_id==mapping['faculty_id'],fb.c.context_key==key)):
                    add(db,'staff_feedback',author_id=student_id,faculty_id=mapping['faculty_id'],context_key=key,subject_id=sid,section_id=section,clarity=4,interaction=4,comments='Worked examples and opportunities to ask questions help with revision. '+NOTE);counts['feedback']+=1
        db.commit();print(counts)
if __name__=='__main__':main()

