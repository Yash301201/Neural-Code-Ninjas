"""Idempotent sample year-wise curricula, cohorts and teaching coverage."""
from datetime import datetime,timedelta,timezone
from sqlalchemy import select
from .db import table,add,update,one
from .security import hasher
from .campus import audit
from .showcase_seed import FIRST,LAST,DEMO_DOMAIN
CS=['Engineering Mathematics I','Engineering Physics','Programming in C','Engineering Graphics','Basic Electrical Engineering','Technical Communication','Data Structures','Object Oriented Programming','Discrete Mathematics','Digital Logic','Computer Organization','Numerical Methods','Operating Systems','Software Engineering','Design and Analysis of Algorithms','Theory of Computation','Microprocessors','Web Technologies','Machine Learning','Cloud Computing','Cyber Security','Distributed Systems','Major Project I','Major Project II','Compiler Design','Database Systems Laboratory','Network Programming','Artificial Intelligence','Mobile Application Development','Engineering Economics']
BANKS={
'ECE':['Engineering Mathematics I','Engineering Physics','Programming in C','Engineering Graphics','Basic Electrical Engineering','Technical Communication','Electronic Devices','Circuit Theory','Signals and Systems','Analog Electronics','Electromagnetic Fields','Network Analysis','Digital Signal Processing','Microprocessors','VLSI Design','Control Engineering','Antenna Theory','Embedded Systems','Wireless Communication','Optical Communication','Microwave Engineering','IoT Systems','Major Project I','Major Project II','Communication Laboratory','Digital Design Laboratory','Information Theory','Radar Systems'],
'EEE':['Engineering Mathematics I','Engineering Physics','Programming in C','Engineering Graphics','Basic Electronics','Technical Communication','Electrical Machines I','Circuit Analysis','Electromagnetic Fields','Measurements and Instrumentation','Power Electronics','Network Analysis','Electrical Machines II','Power Systems I','Signals and Systems','Microcontrollers','Control Engineering','Electrical Drives','Power Systems II','Renewable Energy Systems','High Voltage Engineering','Smart Grids','Major Project I','Major Project II','Protection Engineering','Power System Laboratory','Industrial Automation','Energy Auditing'],
'ME':['Engineering Mathematics I','Engineering Physics','Programming in C','Engineering Graphics','Workshop Practice','Technical Communication','Strength of Materials','Fluid Mechanics','Material Science','Manufacturing Processes','Kinematics of Machines','Numerical Methods','Dynamics of Machines','Heat Transfer','Machine Design I','Metrology','Applied Thermodynamics','CAD and CAM','Machine Design II','Refrigeration and Air Conditioning','Automobile Engineering','Industrial Engineering','Major Project I','Major Project II','Finite Element Analysis','Robotics','Production Planning','Thermal Engineering Laboratory'],
'CE':['Engineering Mathematics I','Engineering Physics','Programming in C','Engineering Graphics','Building Materials','Technical Communication','Strength of Materials','Fluid Mechanics','Engineering Geology','Concrete Technology','Construction Methods','Numerical Methods','Geotechnical Engineering','Transportation Engineering','Hydrology','Reinforced Concrete Design','Environmental Engineering','Water Resources Engineering','Steel Structures','Foundation Engineering','Construction Management','Remote Sensing','Major Project I','Major Project II','Urban Planning','Quantity Surveying','Earthquake Engineering','Hydraulics Laboratory']}
PG=['Advanced Algorithms','Advanced Database Systems','Research Methodology','Advanced Computer Networks','Machine Learning Applications','Distributed Computing','Cloud Architecture','Data Engineering','Information Security','Software Architecture','Optimization Methods','Advanced Computing Laboratory','Research Seminar','Dissertation I','Dissertation II','Natural Language Processing','Deep Learning','High Performance Computing']
BCA=['Programming Fundamentals','Mathematics for Computing','Digital Systems','Communication Skills','Web Foundations','Computer Applications','Data Structures','Database Management Systems','Object Oriented Programming','Computer Networks','Software Engineering','Statistics for Computing','Operating Systems','Web Application Development','Cloud Fundamentals','Information Security','Project I','Project II','Programming Laboratory','Database Laboratory']

def topic_names(name):
    words=name.lower()
    for key,topics in [('database',['Relational modelling and SQL','Normalization and transactions','Indexing and query optimization']),('network',['Network layers and protocols','IP addressing and routing','Transport protocols and security']),('data structures',['Arrays, lists and stacks','Trees and graph traversal','Complexity and practical algorithms']),('programming',['Language fundamentals and control flow','Functions and data structures','Testing and problem solving']),('thermo',['Energy and the first law','Entropy and the second law','Thermodynamic cycles']),('circuits',['Circuit laws and network theorems','AC and transient analysis','Measurement and laboratory practice']),('survey',['Levelling and angle measurement','Traversing and contouring','Field survey applications']),('machine learning',['Training, validation and evaluation','Regression and classification','Model limitations and applications']),('mathematics',['Calculus and linear algebra','Differential equations','Engineering numerical applications'])]:
        if key in words:return topics
    return [name+' principles',name+' analytical methods',name+' practical applications']

def seed(db,actor):
    key='year-curriculum-prefill-v1';one(db,'users',actor['user_id'],True);runs=table('demo_showcase_runs');old=db.execute(select(runs).where(runs.c.run_key==key)).mappings().first()
    if old:return {**old['summary'],'already_created':True}
    courses=table('courses');us=table('users');en=table('student_enrollments');sections=table('sections');subjects=table('subjects');fa=table('faculty_subject_assignments');curr=table('subject_curriculum');sy=table('section_study_years')
    cse=db.execute(select(table('departments')).where(table('departments').c.department_code=='CSE')).mappings().first()
    if not cse:cse=db.execute(select(table('departments')).order_by(table('departments').c.department_id)).mappings().first()
    bca=db.execute(select(courses).where(courses.c.course_code=='BCA')).mappings().first()
    if not bca:
        bca=add(db,'courses',department_id=cse['department_id'],course_name='Bachelor of Computer Applications',course_code='BCA',duration_years=3);db.execute(table('course_programs').insert().values(course_id=bca['course_id'],program_level='UG'))
    levels={r['course_id']:r['program_level'] for r in db.execute(select(table('course_programs'))).mappings()};departments={r['department_id']:r['department_code'] for r in db.execute(select(table('departments'))).mappings()}
    hashed=hasher.hash('DemoLearn2026!');now=datetime.now(timezone.utc).replace(tzinfo=None);created_students=0;course_count=0;subject_count=0
    for course in db.execute(select(courses).order_by(courses.c.course_id)).mappings().all():
        level=levels.get(course['course_id']);duration=course['duration_years']
        if (level,duration) not in [('UG',4),('UG',3),('PG',2)]:continue
        cid=course['course_id'];did=course['department_id'];course_count+=1;required=24 if duration==4 else 18 if level=='UG' else 15
        teacher=db.execute(select(us).where(us.c.role=='FACULTY',us.c.department_id==did,us.c.is_active==True,us.c.email.endswith(DEMO_DOMAIN)).order_by(us.c.user_id)).mappings().first()
        if not teacher:continue
        head=db.execute(select(us).where(us.c.role=='HOD',us.c.department_id==did,us.c.is_active==True).order_by(us.c.user_id)).mappings().first();owner=head['user_id'] if head else actor['user_id']
        existing=[dict(r) for r in db.execute(select(subjects).where(subjects.c.course_id==cid,subjects.c.subject_code.like('LP-%')).order_by(subjects.c.subject_id)).mappings()]
        current_year=2 if level=='UG' and duration==4 else 1
        assigned={y:[] for y in range(1,duration+1)}
        for sub in existing[:required]:assigned[current_year].append(sub)
        caps={1:8,2:7} if level=='PG' else {y:6 for y in assigned}
        bank=PG if level=='PG' else BCA if duration==3 else BANKS.get(departments.get(did),CS)
        taken=set(db.scalars(select(subjects.c.subject_name).where(subjects.c.course_id==cid)));index=0
        for year in assigned:
            while len(assigned[year])<caps[year]:
                while index<len(bank) and bank[index] in taken:index+=1
                name=bank[index] if index<len(bank) else course['course_name'].split(' ',1)[-1]+' Applied Laboratory '+str(index+1)
                index+=1;taken.add(name);sem=2*year-1 if len(assigned[year])<(caps[year]+1)//2 else 2*year
                sub=add(db,'subjects',course_id=cid,subject_name=name,subject_code=f'LP-Y{cid}-{year}-{len(assigned[year])+1}',semester=sem);assigned[year].append(sub)
            for i,sub in enumerate(assigned[year]):
                sem=2*year-1 if i<(len(assigned[year])+1)//2 else 2*year;update(db,'subjects',sub['subject_id'],semester=sem)
                db.execute(curr.insert().values(subject_id=sub['subject_id'],study_year=year,semester=sem));subject_count+=1
                topics=table('topics');existing_topics=list(db.execute(select(topics).where(topics.c.subject_id==sub['subject_id'])).mappings())
                for name in topic_names(sub['subject_name']):
                    if len(existing_topics)>=3:break
                    tp=add(db,'topics',subject_id=sub['subject_id'],topic_name=name,description='Planned syllabus coverage for this subject.');existing_topics.append(tp)
        sample_sections=list(db.scalars(select(en.c.section_id).join(us,us.c.user_id==en.c.student_id).join(sections,sections.c.section_id==en.c.section_id).where(us.c.email.endswith(DEMO_DOMAIN),en.c.status=='ACTIVE',sections.c.course_id==cid).distinct()))
        # Existing generated history stays in the same section and user IDs.
        if len(sample_sections)>1:raise ValueError('Multiple existing sample cohorts need explicit year classification before seeding')
        if sample_sections:
            db.execute(sy.insert().values(section_id=sample_sections[0],study_year=current_year))
            update(db,'sections',sample_sections[0],section_name=f'Year {current_year} A')
        for year in assigned:
            for letter in ['A','B']:
                if sample_sections and year==current_year and letter=='A':section=one(db,'sections',sample_sections[0]);new=False
                else:section=add(db,'sections',course_id=cid,academic_year='2026-2027',section_name=f'Year {year} {letter}');db.execute(sy.insert().values(section_id=section['section_id'],study_year=year));new=True
                if new:
                    for j in range(2):
                        n=created_students;email=f'year-{cid}-{year}-{letter.lower()}-{j+1}'+DEMO_DOMAIN
                        person=add(db,'users',full_name=LAST[(n//len(FIRST)+5)%len(LAST)]+' '+FIRST[n%len(FIRST)],email=email,password_hash=hashed,role='STUDENT',department_id=did,registration_number=f'LP-Y{cid}{year}{letter}{j+1:02d}')
                        add(db,'student_enrollments',student_id=person['user_id'],section_id=section['section_id'],enrolled_on=now.date()-timedelta(days=30));created_students+=1
                for sub in assigned[year]:
                    old=db.execute(select(fa).where(fa.c.faculty_id==teacher['user_id'],fa.c.subject_id==sub['subject_id'],fa.c.section_id==section['section_id'])).mappings().first()
                    mapping=dict(old) if old else add(db,'faculty_subject_assignments',faculty_id=teacher['user_id'],subject_id=sub['subject_id'],section_id=section['section_id'])
                    topics=list(db.execute(select(table('topics')).where(table('topics').c.subject_id==sub['subject_id']).order_by(table('topics').c.topic_id)).mappings())
                    for ti,tp in enumerate(topics):db.execute(table('teaching_topic_progress').insert().values(faculty_assignment_id=mapping['faculty_assignment_id'],topic_id=tp['topic_id'],status=['COMPLETED','IN_PROGRESS','PLANNED'][min(ti,2)],updated_by=teacher['user_id']))
                # One completed foundation quiz per newly created cohort, so new-year students have observable records.
                if new:
                    sub=assigned[year][0];topic=db.execute(select(table('topics')).where(table('topics').c.subject_id==sub['subject_id']).order_by(table('topics').c.topic_id)).mappings().first()
                    questions=[]
                    for text,options,correct in [('Which practice makes an engineering calculation reproducible?',['Document assumptions and units','Hide assumptions','Skip units','Change measurements'],'Document assumptions and units'),('Which evidence best supports a technical conclusion?',['A documented worked calculation','An unsupported guess','A title only','A copied label'],'A documented worked calculation')]:questions.append(add(db,'questions',topic_id=topic['topic_id'],created_by=teacher['user_id'],question_text=text,question_type='MCQ',difficulty='EASY',choice_options=options,correct_answer=correct,explanation='Engineering reasoning practice.'))
                    test=add(db,'tests',subject_id=sub['subject_id'],section_id=section['section_id'],created_by=teacher['user_id'],title=sub['subject_name']+' Foundation Quiz',duration_minutes=20,start_at=now-timedelta(days=2),end_at=now-timedelta(days=1),status='CLOSED')
                    for qi,q in enumerate(questions):db.execute(table('test_questions').insert().values(test_id=test['test_id'],question_id=q['question_id'],marks=5,question_order=qi+1))
                    for pi,person in enumerate(db.execute(select(us).join(en,en.c.student_id==us.c.user_id).where(en.c.section_id==section['section_id'],en.c.status=='ACTIVE')).mappings()):
                        attempt=add(db,'test_attempts',test_id=test['test_id'],student_id=person['user_id'],started_at=now-timedelta(days=2),submitted_at=now-timedelta(days=2)+timedelta(minutes=10),score=5+5*(pi%2),status='EVALUATED')
                        for qi,q in enumerate(questions):right=qi==0 or pi%2==1;add(db,'student_answers',attempt_id=attempt['attempt_id'],question_id=q['question_id'],answer_text=q['correct_answer'] if right else q['choice_options'][1],awarded_marks=5 if right else 0,evaluated_by=teacher['user_id'])
        audit(db,actor,'YEAR_CURRICULUM_CREATED','course',cid,None,{'duration_years':duration,'subjects':required},'Illustrative year-wise curriculum and sample cohorts populated',did)
    summary={'courses':course_count,'curriculum_subjects':subject_count,'added_students':created_students,'source':'Locally generated illustrative college curricula, not an accredited university syllabus.'}
    db.execute(runs.insert().values(run_key=key,created_by=actor['user_id'],summary=summary));return {**summary,'already_created':False}
