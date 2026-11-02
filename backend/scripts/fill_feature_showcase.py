"""Additive, repeatable illustrative records for enrolled teaching scopes.

Never changes credentials, existing marks, or existing submissions. All new
academic records identify their locally generated sample provenance.
"""
import json
from collections import Counter
from datetime import datetime, timedelta, time, timezone
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.db import engine, metadata, table, add
from app.campus import audit

KEY = 'feature-showcase-fill-v1'
NOTE = 'Locally generated illustrative showcase record; not real academic evidence.'

def main(missing_only=False):
    metadata.reflect(bind=engine)
    counts = Counter()
    with Session(engine) as db:
        users = [dict(r) for r in db.execute(select(table('users'))).mappings()]
        admin = next(u for u in users if u['role'] == 'ADMIN' and u['is_active'])
        runs = table('demo_showcase_runs')
        run_key = KEY if not missing_only else 'feature-showcase-missing-v2'
        old = db.execute(select(runs).where(runs.c.run_key == run_key).with_for_update()).mappings().first()
        if old:
            print(json.dumps({'already_created': True, 'counts': old['summary']})); return
        now = datetime.now(timezone.utc).replace(tzinfo=None,microsecond=0)
        subjects = {r['subject_id']: dict(r) for r in db.execute(select(table('subjects'))).mappings()}
        active = {u['user_id'] for u in users if u['is_active']}
        rosters = {}
        for r in db.execute(select(table('student_enrollments')).where(table('student_enrollments').c.status == 'ACTIVE')).mappings():
            if r['student_id'] in active: rosters.setdefault(r['section_id'], set()).add(r['student_id'])
        scopes = {}
        for r in db.execute(select(table('faculty_subject_assignments'))).mappings():
            scopes.setdefault((r['subject_id'], r['section_id']), r['faculty_id'])
        for (sid, sec), teacher in scopes.items():
            if missing_only and db.scalar(select(table('test_attempts').c.attempt_id).join(table('tests'),table('tests').c.test_id==table('test_attempts').c.test_id).where(table('tests').c.subject_id==sid,table('tests').c.section_id==sec).limit(1)):continue
            students = sorted(rosters.get(sec, []))
            if not students: continue
            tp = table('topics')
            topics = list(db.execute(select(tp).where(tp.c.subject_id == sid).order_by(tp.c.topic_id)).mappings())
            if not topics: continue
            counts['populated_classes'] += 1
            name = subjects[sid]['subject_name']
            questions = []
            for i, topic in enumerate(topics[:3]):
                q = add(db, 'questions', topic_id=topic['topic_id'], created_by=teacher,
                    question_text=f"In {topic['topic_name']}, which approach best supports a reliable engineering solution?",
                    question_type='MCQ', difficulty=['EASY','MEDIUM','HARD'][i],
                    choice_options=['State assumptions, apply the method and validate the result','Ignore boundary conditions','Use an unverified result','Omit units and validation'],
                    correct_answer='State assumptions, apply the method and validate the result', explanation=NOTE)
                questions.append(q); counts['questions'] += 1
            for n, kind in enumerate(['DAILY','WEEKLY','FINAL']):
                started = now - timedelta(days=21-n*7)
                test = add(db, 'tests', subject_id=sid, section_id=sec, created_by=teacher,
                    title=f'{name[:95]} — {kind.title()} Review', description=NOTE,
                    duration_minutes=30, start_at=started, end_at=started+timedelta(hours=1), status='CLOSED')
                request = f'fill-v1-{sid}-{sec}-{n}'
                db.execute(table('exam_series').insert().values(request_key=request, fingerprint='0'*64, created_by=admin['user_id']))
                db.execute(table('exam_schedules').insert().values(test_id=test['test_id'], request_key=request, exam_type=kind, occurrence_number=1))
                for qi,q in enumerate(questions):
                    db.execute(table('test_questions').insert().values(test_id=test['test_id'],question_id=q['question_id'],marks=5,question_order=qi+1))
                for pi, student in enumerate(students):
                    right_count = min(len(questions), 1+(pi+n)%len(questions))
                    attempt = add(db,'test_attempts',test_id=test['test_id'],student_id=student,
                        started_at=started,submitted_at=started+timedelta(minutes=20),score=right_count*5,status='EVALUATED')
                    for qi,q in enumerate(questions):
                        right=qi<right_count
                        add(db,'student_answers',attempt_id=attempt['attempt_id'],question_id=q['question_id'],
                            answer_text=q['correct_answer'] if right else q['choice_options'][1],
                            awarded_marks=5 if right else 0,feedback=NOTE,evaluated_by=teacher)
                    counts['evaluated_attempts'] += 1
                counts['exams'] += 1
            # New assignments retain a mixture of graded, submitted and missing work.
            for n in range(2):
                assignment=add(db,'assignments',subject_id=sid,section_id=sec,created_by=teacher,
                    title=f'{name[:100]} — '+['Applied Problem Set','Case Study'][n],
                    description=f'Explain {topics[n%len(topics)]["topic_name"]}, document assumptions and provide a worked example. '+NOTE,
                    due_at=now+timedelta(days=7+n*7),max_marks=20)
                counts['assignments']+=1
                for pi,student in enumerate(students):
                    if (pi+n)%3==2: continue
                    graded=(pi+n)%3==0
                    add(db,'submissions',assignment_id=assignment['assignment_id'],student_id=student,
                        answer_text='Worked example: identify inputs, state assumptions, apply the relevant method, and verify units and results. '+NOTE,
                        marks_awarded=16 if graded else None,feedback=NOTE if graded else None,
                        status='GRADED' if graded else 'SUBMITTED')
                    counts['submissions']+=1
            for n in range(5):
                day=(now-timedelta(days=2+n)).date()
                cs=table('class_sessions')
                exists=db.scalar(select(cs.c.session_id).where(cs.c.subject_id==sid,cs.c.section_id==sec,cs.c.session_date==day,cs.c.starts_at==time(9,0)))
                if exists: continue
                session=add(db,'class_sessions',subject_id=sid,section_id=sec,topic_id=topics[n%len(topics)]['topic_id'],session_date=day,starts_at=time(9,0),marked_by=teacher)
                db.execute(table('attendance_registers').insert().values(session_id=session['session_id'],version=1,updated_by=teacher))
                for pi,student in enumerate(students):
                    add(db,'attendance_records',session_id=session['session_id'],student_id=student,
                        status='ABSENT' if (pi+n)%7==0 else 'LATE' if (pi+n)%11==0 else 'PRESENT',remarks=NOTE)
                    counts['attendance_marks']+=1
                counts['saved_sessions']+=1
        ev=table('staff_evidence')
        for u in users:
            if u['role'] not in ['FACULTY','HOD'] or not u['is_active']:continue
            for category,title,details in [
                ('SKILL','Engineering teaching and curriculum design','Outcome-based lesson planning, assessment rubrics and practical laboratory instruction.'),
                ('RESUME','Academic profile','Teaching interests include engineering fundamentals, mentoring, curriculum planning and student project supervision.'),
                ('RESEARCH','Illustrative study on active learning','Sample research portfolio entry about classroom problem solving; no actual publication or DOI is claimed.'),
                ('TRAINING','Assessment design workshop','Illustrative professional development workshop on rubrics, MCQ construction and feedback.'),
                ('COLLABORATION','Interdepartmental project mentoring','Illustrative collaboration supporting multidisciplinary student design reviews.')]:
                if db.scalar(select(ev.c.evidence_id).where(ev.c.owner_id==u['user_id'],ev.c.category==category).limit(1)):continue
                add(db,'staff_evidence',owner_id=u['user_id'],category=category,title=title,details=details+' '+NOTE,
                    skill_level=4 if category=='SKILL' else None,status='SUBMITTED')
                counts['staff_evidence']+=1
        audit(db,admin,'SHOWCASE_FEATURES_FILLED','users',admin['user_id'],None,dict(counts),NOTE,admin['department_id'])
        db.execute(runs.insert().values(run_key=run_key,created_by=admin['user_id'],summary=dict(counts)))
        db.commit()
    print(json.dumps({'already_created':False,'counts':dict(counts)}))

if __name__=='__main__':
    import sys
    main('--missing-only' in sys.argv)
