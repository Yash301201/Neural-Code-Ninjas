"""Idempotent synthetic college showcase. Never rewrites non-demo accounts."""
from datetime import datetime,date,time,timedelta,timezone
import os,uuid,hashlib
from sqlalchemy import select
from .db import table,one,add,update
from .security import hasher
from .campus import audit
from .development import create_evidence,edit_evidence,review_evidence,archive_evidence,Evidence,EvidenceReview,save_feedback,Feedback,dataset_link,DatasetLink
DEMO_DOMAIN='@demo.learnpath.dev'
FIRST=['Sai Teja','Sravani','Venkata Sai','Lakshmi Priya','Srinivas','Harika','Sandeep','Divya','Ravi Teja','Anusha','Pavan Kumar','Bhavani','Nikhil','Mounika','Surya Prakash','Keerthana','Karthik','Sowmya','Vamsi Krishna','Sahithi']
LAST=['Kondapalli','Penumaka','Duvvuri','Nalluri','Chilukuri','Gollapudi','Vemuri','Kakarla','Maddala','Gorantla']

def seed(db,actor,per_major=False):
    run_key='college-showcase-v1-'+('50-per-major' if per_major else '50-total')
    one(db,'users',actor['user_id'],True)
    runs=table('demo_showcase_runs');existing=db.execute(select(runs).where(runs.c.run_key==run_key)).mappings().first()
    if existing:return {**existing['summary'],'already_created':True}
    if db.scalar(select(runs.c.run_key).limit(1)):raise ValueError('A showcase already exists. Use its existing records; do not layer another size over it.')
    courses=[dict(r) for r in db.execute(select(table('courses')).order_by(table('courses').c.course_id)).mappings()]
    if not courses:raise ValueError('Create at least one course first')
    if len(courses)>7:raise ValueError('This showcase supports up to seven existing majors with seven demo faculty')
    password=os.getenv('DEMO_SHOWCASE_PASSWORD','DemoLearn2026!');hashed=hasher.hash(password)
    def account(email,name,role,dept=None,registration=None):
        users=table('users');old=db.execute(select(users).where(users.c.email==email)).mappings().first()
        if old:
            if not email.endswith(DEMO_DOMAIN):raise ValueError('Only synthetic accounts may be reused')
            return update(db,'users',old['user_id'],full_name=name+' [DEMO]',role=role,department_id=dept,is_active=True,password_hash=hashed)
        return add(db,'users',full_name=name+' [DEMO]',email=email,password_hash=hashed,role=role,department_id=dept,is_active=True,registration_number=registration)
    demo_admin=account('admin-showcase'+DEMO_DOMAIN,'Showcase Administrator','ADMIN')
    hods={}
    for course in courses:
        dept=course['department_id']
        if dept not in hods:hods[dept]=account(f'hod-{dept}'+DEMO_DOMAIN,'Dr. N. Madhavi','HOD',dept)
    old_demo=[dict(r) for r in db.execute(select(table('users')).where(table('users').c.role=='FACULTY',table('users').c.email.endswith(DEMO_DOMAIN)).order_by(table('users').c.user_id)).mappings()]
    faculty=[];names=['Dr. K. Sravani','Prof. V. Ramana','Dr. P. Ravi Teja','Dr. N. Harika','Prof. M. Srinivas','Dr. G. Lakshmi Priya','Prof. D. Pavan Kumar']
    for i in range(7):
        dept=courses[i%len(courses)]['department_id'];email=old_demo[i]['email'] if i<len(old_demo) else f'faculty-{i+1:02d}-showcase'+DEMO_DOMAIN
        faculty.append(account(email,names[i],'FACULTY',dept,f'DEMO-FAC-{i+1:03d}'))
    now=datetime.now(timezone.utc).replace(tzinfo=None);today=now.date();students=[];mappings=[];exam_count=0;answer_count=0
    # Each major has its own demo section, distinct from actual existing classes.
    for ci,course in enumerate(courses):
        cid=course['course_id'];dept=course['department_id'];manager=hods[dept]
        sec=add(db,'sections',course_id=cid,academic_year='2026-2027',section_name='DEMO-Showcase')
        count=50 if per_major else 50//len(courses)+(ci<50%len(courses))
        cohort=[]
        for j in range(count):
            n=len(students)+1;student=account(f'student-{n:03d}'+DEMO_DOMAIN,LAST[(n-1)//len(FIRST)%len(LAST)]+' '+FIRST[(n-1)%len(FIRST)],'STUDENT',dept,f'DEMO-STU-{n:03d}')
            add(db,'student_enrollments',student_id=student['user_id'],section_id=sec['section_id'],enrolled_on=today-timedelta(days=40),status='ACTIVE');cohort.append(student);students.append(student)
        # Two subject examples within the existing degree, with realistic database / methods content.
        for si,(name,prefix) in enumerate([('Data and Information Systems','Data'),('Research and Problem Solving','Methods')]):
            sub=add(db,'subjects',course_id=cid,subject_name='[DEMO] '+name,subject_code=f'DEMO-{cid}-{si+1}',semester=1)
            assigned=[f for f in faculty if f['department_id']==dept];teacher=assigned[(ci*2+si)%len(assigned)]
            add(db,'faculty_subject_assignments',faculty_id=teacher['user_id'],subject_id=sub['subject_id'],section_id=sec['section_id']);mappings.append((teacher,sub,sec,manager,cohort))
            topic1=add(db,'topics',subject_id=sub['subject_id'],topic_name='[DEMO] Foundations',description='Synthetic showcase: core concepts and application')
            topic2=add(db,'topics',subject_id=sub['subject_id'],topic_name='[DEMO] Applied reasoning',description='Synthetic showcase: evaluation and problem solving')
            definitions=[('Which SQL operation reads rows?',['SELECT','INSERT','DELETE','UPDATE'],'SELECT'),('Which key uniquely identifies a row?',['Primary key','Label','Comment','Alias'],'Primary key'),('Which action keeps an operation atomic?',['Transaction','Screenshot','Rename','Sorting'],'Transaction'),('What is a good first step in research?',['Define the question','Invent results','Skip evidence','Copy conclusions'],'Define the question'),('Which practice supports reproducibility?',['Document methods','Hide data sources','Omit assumptions','Change outcomes'],'Document methods')]
            qs=[]
            for qi,(text,choices,correct) in enumerate(definitions):qs.append(add(db,'questions',topic_id=(topic1 if qi<3 else topic2)['topic_id'],created_by=teacher['user_id'],question_text='[DEMO] '+text,question_type='MCQ',difficulty='EASY' if qi<3 else 'MEDIUM',choice_options=choices,correct_answer=correct,explanation='Synthetic question for the LearnPath showcase.',review_status='APPROVED'))
            for ei,kind in enumerate(['DAILY','WEEKLY','FINAL']):
                for future in [False,True]:
                    start=now+timedelta(days=[0,3,7][ei],hours=-1) if future else now-timedelta(days=18-ei*6)
                    end=start+timedelta(hours=24 if future else 2)
                    test=add(db,'tests',subject_id=sub['subject_id'],section_id=sec['section_id'],created_by=teacher['user_id'],title=f'[DEMO] {prefix} {kind.title()} '+('Open practice' if future else 'Completed example'),description='Fictional college showcase. Results are synthetic, not OULAD scores.',duration_minutes=25,start_at=start,end_at=end,max_attempts=1,status='PUBLISHED' if future else 'CLOSED')
                    key=str(uuid.uuid4());db.execute(table('exam_series').insert().values(request_key=key,fingerprint=hashlib.sha256(key.encode()).hexdigest(),created_by=teacher['user_id']));db.execute(table('exam_schedules').insert().values(test_id=test['test_id'],request_key=key,exam_type=kind,occurrence_number=1))
                    for qi,q in enumerate(qs):db.execute(table('test_questions').insert().values(test_id=test['test_id'],question_id=q['question_id'],marks=4,question_order=qi+1))
                    exam_count+=1
                    if future:continue
                    for j,student in enumerate(cohort):
                        if (j+ei)%11==0:continue
                        right=min(5,1+(j*3+ci+si)%5+ei//2)
                        attempt=add(db,'test_attempts',test_id=test['test_id'],student_id=student['user_id'],attempt_number=1,started_at=start,submitted_at=start+timedelta(minutes=15),score=4*right,status='EVALUATED')
                        for qi,q in enumerate(qs):
                            correct=qi<right;answer=q['correct_answer'] if correct else next(v for v in q['choice_options'] if v!=q['correct_answer'])
                            add(db,'student_answers',attempt_id=attempt['attempt_id'],question_id=q['question_id'],answer_text=answer,awarded_marks=4 if correct else 0,evaluated_by=teacher['user_id'],feedback='[DEMO] Automatically evaluated MCQ');answer_count+=1
            for ai in range(2):
                assignment=add(db,'assignments',subject_id=sub['subject_id'],section_id=sec['section_id'],created_by=teacher['user_id'],title=f'[DEMO] {prefix} '+('case study' if ai==0 else 'mini project'),description='Explain a relational data model, identify keys, and describe a reproducible evaluation. Synthetic showcase assignment.',due_at=now+timedelta(days=4+ai*3),max_marks=20)
                for j,student in enumerate(cohort):
                    if (j+ai)%4==0:continue
                    graded=j%3!=0
                    add(db,'submissions',assignment_id=assignment['assignment_id'],student_id=student['user_id'],answer_text='[DEMO] I designed a student/course/enrollment model, selected primary and foreign keys, and documented the evaluation method.',submitted_at=now-timedelta(days=2),status='GRADED' if graded else 'SUBMITTED',marks_awarded=10+j%11 if graded else None,feedback='[DEMO] Clear structure; add a concrete validation example.' if graded else None)
            for day in range(8):
                session=add(db,'class_sessions',subject_id=sub['subject_id'],section_id=sec['section_id'],topic_id=topic1['topic_id'],session_date=today-timedelta(days=12-day),starts_at=time(9+si,0),marked_by=teacher['user_id'])
                db.execute(table('attendance_registers').insert().values(session_id=session['session_id'],version=1,updated_by=teacher['user_id']))
                for j,student in enumerate(cohort):add(db,'attendance_records',session_id=session['session_id'],student_id=student['user_id'],status='ABSENT' if (j+day)%6==0 else 'PRESENT',remarks='[DEMO] Fictional attendance')
            for student in cohort[:3]:
                plan=add(db,'study_plans',student_id=student['user_id'],subject_id=sub['subject_id'],created_by=teacher['user_id'],generated_by='FACULTY',title='[DEMO] Topic practice plan',start_date=today,end_date=today+timedelta(days=6),status='ACTIVE')
                for ti,tp in enumerate([topic1,topic2]):add(db,'study_plan_items',plan_id=plan['plan_id'],topic_id=tp['topic_id'],scheduled_date=today+timedelta(days=ti),recommendation='[DEMO] Review topic and solve practice questions',estimated_minutes=30,status='PENDING')
            for j,student in enumerate(cohort[:8]):save_feedback(Feedback(faculty_id=teacher['user_id'],subject_id=sub['subject_id'],section_id=sec['section_id'],clarity=3+j%3,interaction=3+(j+1)%3,comments='[DEMO] The teacher invited questions and explained examples clearly.'),student,db)
        # Reference data stays in the OULAD tables; no learner IDs are relabeled as college users.
        dataset_link(cid,DatasetLink(module='BBB',presentation='2014J'),actor,db)
    # Ensure every one of the seven faculty has a real synthetic teaching mapping.
    assigned_ids={m[0]['user_id'] for m in mappings}
    for teacher in faculty:
        if teacher['user_id'] in assigned_ids:continue
        base=next(m for m in mappings if m[1]['course_id'] in [c['course_id'] for c in courses if c['department_id']==teacher['department_id']]);_,sub,sec,manager,cohort=base
        add(db,'faculty_subject_assignments',faculty_id=teacher['user_id'],subject_id=sub['subject_id'],section_id=sec['section_id']);mappings.append((teacher,sub,sec,manager,cohort))
    for i,(teacher,sub,sec,manager,cohort) in enumerate(mappings):
        # Unique slot across sections and faculty, from morning to afternoon.
        add(db,'faculty_timetable',faculty_id=teacher['user_id'],subject_id=sub['subject_id'],section_id=sec['section_id'],weekday=i%5,starts_at=time(9+i//5,0),ends_at=time(10+i//5,0),room=f'DEMO Room {101+i}',session_type='LECTURE',created_by=manager['user_id'])
        audit(db,manager,'TEACHING_ASSIGNED','subject',sub['subject_id'],None,{'faculty_id':teacher['user_id'],'section_id':sec['section_id'],'demo':True},'Fictional teaching coverage assigned by demo HOD',teacher['department_id'])
    for i,teacher in enumerate(faculty):
        manager=hods[teacher['department_id']]
        for category,title,detail,level in [('SKILL','Python and FastAPI','Self-reported demo skill; API design and validation practice.',3+i%3),('SKILL','Classroom facilitation','Self-reported demo skill; guided questions and active discussion.',3+i%2),('RESUME','Teaching resume summary','Fictional qualifications: M.Tech; classroom teaching, student mentoring and database systems. No real resume.',None),('RESEARCH','Research methods in learning systems','Fictional publication example for demonstration. No real DOI or journal claim.',None),('RESEARCH','Adaptive feedback study proposal','Fictional work in progress; pending department review.',None),('COLLABORATION','Peer lesson-planning workshop','Fictional co-planning session with colleagues and a student support meeting.',None),('TRAINING','Assessment design workshop','Fictional professional development record: MCQ quality and constructive feedback.',None)]:
            row=create_evidence(teacher['user_id'],Evidence(category=category,title='[DEMO] '+title,details=detail,skill_level=level),teacher,db)
            if category=='RESEARCH' and 'proposal' not in title:review_evidence(row['evidence_id'],EvidenceReview(status='VERIFIED',review_note='[DEMO] Fictional evidence reviewed for showcase only.'),manager,db)
        disposable=create_evidence(teacher['user_id'],Evidence(category='TRAINING',title='[DEMO] Draft evidence exercise',details='Fictional draft created to showcase add, modify and archive.'),teacher,db)
        edit_evidence(disposable['evidence_id'],Evidence(category='TRAINING',title='[DEMO] Updated evidence exercise',details='Fictional record modified before archival; visible in audit history.'),teacher,db);archive_evidence(disposable['evidence_id'],teacher,db)
        leave=add(db,'faculty_leave_requests',requester_id=teacher['user_id'],start_date=today+timedelta(days=3+i),end_date=today+timedelta(days=3+i),leave_type='ACADEMIC',reason='[DEMO] Fictional professional development leave request.',status=['PENDING','APPROVED','REJECTED'][i%3],reviewed_by=manager['user_id'] if i%3 else None,review_note='[DEMO] Reviewed by department head' if i%3 else None)
        for colleague in [f for f in faculty if f['department_id']==teacher['department_id'] and f['user_id']!=teacher['user_id']][:3]:save_feedback(Feedback(faculty_id=teacher['user_id'],clarity=4,interaction=3+i%3,comments='[DEMO] Shared lesson resources and participated in peer planning.'),colleague,db)
    for manager in hods.values():
        row=create_evidence(manager['user_id'],Evidence(category='TRAINING',title='[DEMO] Department leadership workshop',details='Fictional department leadership and mentoring evidence.'),manager,db);review_evidence(row['evidence_id'],EvidenceReview(status='VERIFIED',review_note='[DEMO] Admin reviewed fictional leadership training.'),demo_admin,db)
    from .engineering_seed import refine
    refine(db,actor)
    summary={'students':len(students),'faculty':len(faculty),'hods':len(hods),'admin':1,'courses':len(courses),'exams':exam_count,'evaluated_answers':answer_count,'demo_student_email':students[0]['email'],'demo_faculty_email':faculty[0]['email'],'demo_hod_email':next(iter(hods.values()))['email'],'demo_admin_email':demo_admin['email'],'dataset':'OULAD BBB / 2014J research reference','run_key':run_key}
    db.execute(runs.insert().values(run_key=run_key,created_by=actor['user_id'],summary=summary))
    audit(db,actor,'SHOWCASE_CREATED','user',demo_admin['user_id'],None,summary,'Clearly labeled synthetic data generated across four roles',None)
    return {**summary,'already_created':False}
