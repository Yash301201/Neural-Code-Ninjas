"""Add a stable, prefilled engineering catalogue. Safe to run repeatedly."""
from datetime import datetime,timedelta,time,timezone
from sqlalchemy import select,func
from .db import table,add,update,one
from .security import hasher
from .campus import audit
from .showcase_seed import FIRST,LAST,DEMO_DOMAIN
CATALOG=[('CSE','Computer Science and Engineering','B.Tech Artificial Intelligence and Machine Learning','BTAIML','Python Programming','Machine Learning'),('CSE','Computer Science and Engineering','B.Tech Data Science','BTDS','Data Structures','Data Analytics'),('ECE','Electronics and Communication Engineering','B.Tech Electronics and Communication Engineering','BTECE','Digital Electronics','Communication Systems'),('EEE','Electrical and Electronics Engineering','B.Tech Electrical and Electronics Engineering','BTEEE','Electrical Circuits','Control Systems'),('ME','Mechanical Engineering','B.Tech Mechanical Engineering','BTME','Engineering Mechanics','Thermodynamics'),('CE','Civil Engineering','B.Tech Civil Engineering','BTCE','Structural Analysis','Surveying')]
QA={
'Python Programming':[('Which Python type stores key-value pairs?',['dict','list','tuple','set'],'dict'),('Which keyword defines a function?',['def','class','import','return'],'def')],
'Machine Learning':[('Which method uses labeled examples?',['Supervised learning','Unsupervised learning','File sorting','Compression'],'Supervised learning'),('What is a held-out test set used for?',['Evaluating generalization','Changing labels','Training every step','Storing passwords'],'Evaluating generalization')],
'Data Structures':[('Which structure uses FIFO order?',['Queue','Stack','Tree','Heap'],'Queue'),('Which structure supports LIFO?',['Stack','Queue','Graph','Table'],'Stack')],
'Data Analytics':[('Which measure is the middle sorted value?',['Median','Mean','Range','Variance'],'Median'),('What describes association between variables?',['Correlation','Encryption','Indexing','Compilation'],'Correlation')],
'Digital Electronics':[('Which gate outputs 1 only when both inputs are 1?',['AND','OR','NOT','XOR'],'AND'),('How many states does one bit have?',['Two','Three','Four','Eight'],'Two')],
'Communication Systems':[('What shifts information onto a carrier?',['Modulation','Rectification','Sorting','Normalization'],'Modulation'),('What is bandwidth measured in?',['Hertz','Volts','Ohms','Watts'],'Hertz')],
'Electrical Circuits':[('Which law relates voltage, current and resistance?',["Ohm law",'Hooke law','Boyle law','Snell law'],'Ohm law'),('What unit measures resistance?',['Ohm','Volt','Ampere','Farad'],'Ohm')],
'Control Systems':[('What compares output with a reference?',['Feedback','Compression','Hashing','Rectification'],'Feedback'),('Which controller term uses accumulated error?',['Integral','Proportional','Derivative','Constant'],'Integral')],
'Engineering Mechanics':[('What is the SI unit of force?',['Newton','Joule','Pascal','Watt'],'Newton'),('What describes resistance to a change in motion?',['Inertia','Pressure','Density','Heat'],'Inertia')],
'Thermodynamics':[('Which law expresses energy conservation?',['First law','Second law','Third law','Zeroth law'],'First law'),('What unit measures thermodynamic temperature?',['Kelvin','Pascal','Newton','Watt'],'Kelvin')],
'Structural Analysis':[('What resists bending in a beam?',['Bending moment','Voltage','Temperature','Frequency'],'Bending moment'),('What is the SI unit of stress?',['Pascal','Newton','Joule','Metre'],'Pascal')],
'Surveying':[('What instrument measures horizontal and vertical angles?',['Theodolite','Ammeter','Microscope','Thermometer'],'Theodolite'),('What is a contour line?',['Equal elevation','Equal pressure','Equal rainfall','Equal temperature'],'Equal elevation')]
}

def clean_names(db):
    us=table('users');sample_ids=set(db.scalars(select(us.c.user_id).where(us.c.email.endswith(DEMO_DOMAIN))))
    for ident in sample_ids:
        r=one(db,'users',ident);values={'full_name':r['full_name'].replace(' [DEMO]','').replace('[DEMO] ','').replace('Showcase Administrator','Academic Administrator')}
        if r['registration_number']:values['registration_number']=r['registration_number'].replace('DEMO-','LP-')
        update(db,'users',ident,**values)
    sub=table('subjects');subject_ids=set()
    for r in db.execute(select(sub).where(sub.c.subject_code.like('DEMO-%'))).mappings():
        subject_ids.add(r['subject_id']);name=r['subject_name'].replace('[DEMO] ','')
        if db.scalar(select(sub.c.subject_id).where(sub.c.course_id==r['course_id'],sub.c.subject_name==name,sub.c.subject_id!=r['subject_id'])):name='Applied '+name
        if db.scalar(select(sub.c.subject_id).where(sub.c.course_id==r['course_id'],sub.c.subject_name==name,sub.c.subject_id!=r['subject_id'])):name=name+' '+str(r['subject_id'])
        update(db,'subjects',r['subject_id'],subject_name=name,subject_code=r['subject_code'].replace('DEMO-','LP-'))
    subject_ids.update(db.scalars(select(sub.c.subject_id).where(sub.c.subject_code.like('LP-%'))))
    for name,idkey,textcols,cond in [('topics','topic_id',['topic_name','description'],table('topics').c.subject_id.in_(subject_ids)),('questions','question_id',['question_text','explanation'],table('questions').c.created_by.in_(sample_ids)),('tests','test_id',['title','description'],table('tests').c.subject_id.in_(subject_ids)),('assignments','assignment_id',['title','description'],table('assignments').c.subject_id.in_(subject_ids)),('staff_evidence','evidence_id',['title','details','review_note'],table('staff_evidence').c.owner_id.in_(sample_ids)),('submissions','submission_id',['answer_text','feedback'],table('submissions').c.student_id.in_(sample_ids)),('student_answers','answer_id',['feedback'],table('student_answers').c.evaluated_by.in_(sample_ids))]:
        t=table(name)
        for r in db.execute(select(t).where(cond)).mappings():update(db,name,r[idkey],**{c:r[c].replace('[DEMO] ','').replace('Fictional','Sample').replace('fictional','sample') if r[c] else r[c] for c in textcols})
    en=table('student_enrollments');sec=table('sections')
    for r in db.execute(select(sec).where(sec.c.section_id.in_(select(en.c.section_id).where(en.c.student_id.in_(sample_ids))),sec.c.section_name.like('DEMO-%'))).mappings():update(db,'sections',r['section_id'],section_name='2026 Cohort')

def expand(db,actor):
    key='academic-catalog-prefill-v1';one(db,'users',actor['user_id'],True);runs=table('demo_showcase_runs')
    old=db.execute(select(runs).where(runs.c.run_key==key)).mappings().first()
    if old:return {**old['summary'],'already_created':True}
    now=datetime.now(timezone.utc).replace(tzinfo=None);today=now.date();hashed=hasher.hash('DemoLearn2026!');new_students=0
    us=table('users')
    def account(email,name,role,dept,reference):
        old=db.execute(select(us).where(us.c.email==email)).mappings().first()
        if old:return dict(old)
        return add(db,'users',full_name=name,email=email,password_hash=hashed,role=role,department_id=dept,registration_number=reference)
    for ci,(code,department,coursename,ccode,first,second) in enumerate(CATALOG):
        dt=table('departments');dept=db.execute(select(dt).where(dt.c.department_code==code)).mappings().first()
        if not dept:dept=add(db,'departments',department_name=department,department_code=code)
        did=dept['department_id'];ct=table('courses');course=db.execute(select(ct).where(ct.c.course_code==ccode)).mappings().first()
        if course:raise ValueError('Reserved course code already exists: '+ccode)
        course=add(db,'courses',department_id=did,course_name=coursename,course_code=ccode,duration_years=4);cid=course['course_id'];db.execute(table('course_programs').insert().values(course_id=cid,program_level='UG'))
        sec=add(db,'sections',course_id=cid,academic_year='2026-2027',section_name='Section A')
        head=db.execute(select(us).where(us.c.role=='HOD',us.c.department_id==did,us.c.email.endswith(DEMO_DOMAIN))).mappings().first()
        if not head:head=account(f'hod-{did}'+DEMO_DOMAIN,['Dr. N. Madhavi','Dr. K. Venkata Rao','Dr. P. Padma','Dr. M. Srinivas','Dr. V. Anuradha','Dr. G. Prasad'][ci],'HOD',did,f'LP-HOD-{did}')
        teacher=db.execute(select(us).where(us.c.role=='FACULTY',us.c.department_id==did,us.c.email.endswith(DEMO_DOMAIN)).order_by(us.c.user_id)).mappings().first()
        if not teacher:teacher=account(f'faculty-{code.lower()}'+DEMO_DOMAIN,['Dr. R. Kiran','Dr. S. Haritha','Dr. B. Ravi Kumar','Dr. C. Suresh','Dr. K. Madhavi','Dr. P. Satish'][ci],'FACULTY',did,f'LP-FAC-{code}')
        students=[]
        for j in range(10):
            ix=ci*10+j;person=account(f'{ccode.lower()}-student-{j+1:02d}'+DEMO_DOMAIN,LAST[(ix//20+2)%len(LAST)]+' '+FIRST[ix%len(FIRST)],'STUDENT',did,f'LP-{ccode}-{j+1:03d}');students.append(person);new_students+=1
            add(db,'student_enrollments',student_id=person['user_id'],section_id=sec['section_id'],enrolled_on=today-timedelta(days=30))
        for si,name in enumerate([first,second]):
            subject=add(db,'subjects',course_id=cid,subject_name=name,subject_code=f'LP-{ccode}-{si+1}',semester=3)
            add(db,'faculty_subject_assignments',faculty_id=teacher['user_id'],subject_id=subject['subject_id'],section_id=sec['section_id'])
            topic=add(db,'topics',subject_id=subject['subject_id'],topic_name=name+' Fundamentals',description='Academic practice and application')
            questions=[]
            for text,options,correct in QA[name]:questions.append(add(db,'questions',topic_id=topic['topic_id'],created_by=teacher['user_id'],question_text=text,question_type='MCQ',difficulty='EASY',choice_options=options,correct_answer=correct,explanation='Reference answer: '+correct))
            from .development import save_feedback,Feedback
            for j,person in enumerate(students[:5]):save_feedback(Feedback(faculty_id=teacher['user_id'],subject_id=subject['subject_id'],section_id=sec['section_id'],clarity=3+j%3,interaction=3+(j+1)%3,comments='The class included worked examples, questions and a clear practical explanation.'),person,db)
            if si==0:
                for person in students:
                    plan=add(db,'study_plans',student_id=person['user_id'],subject_id=subject['subject_id'],created_by=teacher['user_id'],generated_by='FACULTY',title=name+' Weekly Study Plan',start_date=today,end_date=today+timedelta(days=6))
                    add(db,'study_plan_items',plan_id=plan['plan_id'],topic_id=topic['topic_id'],scheduled_date=today,recommendation='Review the fundamental concepts and solve two engineering practice questions.',estimated_minutes=30)
            for ei,kind in enumerate(['Daily','Weekly','Final','Practice']):
                start=now-timedelta(days=15-ei*4) if ei<3 else now-timedelta(hours=1)
                t=add(db,'tests',subject_id=subject['subject_id'],section_id=sec['section_id'],created_by=teacher['user_id'],title=name+' '+kind+' Assessment',description='Prefilled academic sample assessment.',duration_minutes=20,start_at=start,end_at=start+timedelta(hours=2 if ei<3 else 48),status='CLOSED' if ei<3 else 'PUBLISHED')
                for qi,q in enumerate(questions):db.execute(table('test_questions').insert().values(test_id=t['test_id'],question_id=q['question_id'],marks=5,question_order=qi+1))
                if ei==3:continue
                for j,person in enumerate(students):
                    score=5*((j+ei)%3);a=add(db,'test_attempts',test_id=t['test_id'],student_id=person['user_id'],started_at=start,submitted_at=start+timedelta(minutes=10),score=score,status='EVALUATED')
                    for qi,q in enumerate(questions):right=qi<score//5;add(db,'student_answers',attempt_id=a['attempt_id'],question_id=q['question_id'],answer_text=q['correct_answer'] if right else next(x for x in q['choice_options'] if x!=q['correct_answer']),awarded_marks=5 if right else 0,evaluated_by=teacher['user_id'],feedback='Concept mastered.' if right else 'Review the reference concept.')
            assignment=add(db,'assignments',subject_id=subject['subject_id'],section_id=sec['section_id'],created_by=teacher['user_id'],title=name+' Practical Assignment',description='Explain the core concepts and solve one worked engineering example.',due_at=now+timedelta(days=7),max_marks=20)
            for j,person in enumerate(students[:8]):add(db,'submissions',assignment_id=assignment['assignment_id'],student_id=person['user_id'],answer_text='I explained the core concepts of '+name+' and documented a worked application.',status='GRADED' if j%2 else 'SUBMITTED',marks_awarded=12+j if j%2 else None,feedback='Add assumptions and calculation steps.' if j%2 else None)
            for day in range(4):
                session=add(db,'class_sessions',subject_id=subject['subject_id'],section_id=sec['section_id'],topic_id=topic['topic_id'],session_date=today-timedelta(days=5-day),starts_at=time(9+si,0),marked_by=teacher['user_id']);db.execute(table('attendance_registers').insert().values(session_id=session['session_id'],version=1,updated_by=teacher['user_id']))
                for j,person in enumerate(students):add(db,'attendance_records',session_id=session['session_id'],student_id=person['user_id'],status='ABSENT' if (day+j)%5==0 else 'PRESENT')
            add(db,'faculty_timetable',faculty_id=teacher['user_id'],subject_id=subject['subject_id'],section_id=sec['section_id'],weekday=ci%5,starts_at=time(13+si,0),ends_at=time(14+si,0),room=f'{code} Block {101+ci}',created_by=head['user_id'])
        if not db.scalar(select(table('staff_evidence').c.evidence_id).where(table('staff_evidence').c.owner_id==teacher['user_id'])):add(db,'staff_evidence',owner_id=teacher['user_id'],category='RESUME',title='Teaching profile',details='Engineering faculty portfolio with classroom teaching, laboratory supervision and project mentoring.',status='SUBMITTED')
        ev=table('staff_evidence')
        for category,title,detail in [('SKILL','Engineering laboratory instruction','Self-reported skill in explaining practical engineering concepts.'),('RESEARCH','Engineering education study','Sample research proposal on laboratory learning and feedback; no real publication claim.'),('COLLABORATION','Department planning meeting','Shared laboratory resources and discussed student support with colleagues.'),('TRAINING','Assessment design workshop','Professional development record for objective questions and formative feedback.')]:
            if not db.scalar(select(ev.c.evidence_id).where(ev.c.owner_id==teacher['user_id'],ev.c.title==title)):add(db,'staff_evidence',owner_id=teacher['user_id'],category=category,title=title,details=detail,skill_level=4 if category=='SKILL' else None)
        if not db.scalar(select(ev.c.evidence_id).where(ev.c.owner_id==head['user_id'])):add(db,'staff_evidence',owner_id=head['user_id'],category='TRAINING',title='Department leadership and academic planning',details='Sample leadership evidence covering faculty allocations, assessment review and student mentoring.')
        leaves=table('faculty_leave_requests')
        if not db.scalar(select(leaves.c.leave_id).where(leaves.c.requester_id==teacher['user_id'])):add(db,'faculty_leave_requests',requester_id=teacher['user_id'],start_date=today+timedelta(days=4),end_date=today+timedelta(days=4),leave_type='ACADEMIC',reason='Attend an engineering teaching and laboratory workshop.')
    clean_names(db)
    result={'added_courses':len(CATALOG),'added_students':new_students,'collection':'LearnPath Academic College Dataset','provenance':'Synthetic prefilled college records; identities and credentials retained separately from display names.'}
    db.execute(runs.insert().values(run_key=key,created_by=actor['user_id'],summary=result));audit(db,actor,'ACADEMIC_CATALOG_FILLED','user',actor['user_id'],None,result,'Engineering sample catalogue populated once; visible names normalized',None)
    return {**result,'already_created':False}
