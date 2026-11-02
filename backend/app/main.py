import json
from contextlib import asynccontextmanager
from datetime import datetime, timedelta, timezone
from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import select, func, text
from sqlalchemy.exc import IntegrityError, OperationalError
from .config import settings
from .db import engine, metadata, table, get_db, one, add, update
from .security import current_user, roles, subject_access, student_access, public_user, hasher, verify, token
from .schemas import *

@asynccontextmanager
async def lifespan(app):
    metadata.reflect(bind=engine)
    required = {'users','questions','tests','test_attempts','study_plans','academic_events'}
    if not required.issubset(metadata.tables):
        raise RuntimeError('Database not initialized: run python -m scripts.init_db')
    yield
    engine.dispose()

app = FastAPI(title='LearnPath AI Backend', version='1.0.0', lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=settings.cors_origins, allow_credentials=True, allow_methods=['*'], allow_headers=['*'])

@app.exception_handler(IntegrityError)
async def integrity_error(request, exc):
    return JSONResponse(status_code=409, content={'detail':'Duplicate record or invalid database reference/constraint'})

@app.exception_handler(OperationalError)
async def database_error(request, exc):
    import logging
    logging.getLogger(__name__).exception('Database operation failed')
    return JSONResponse(status_code=503, content={'detail':'Database unavailable'})

staff = roles('ADMIN','HOD','FACULTY')
admin = roles('ADMIN')
student = roles('STUDENT')

def rows(db, name, *conditions, limit=200):
    return [dict(r) for r in db.execute(select(table(name)).where(*conditions).limit(limit)).mappings()]

def question_scope(db, u, q):
    subject_access(db, u, one(db, 'topics', q['topic_id'])['subject_id'], write=True)

@app.get('/health', tags=['System'])
def health(db=Depends(get_db)):
    db.execute(text('SELECT 1'))
    return {'status':'ok','database':'connected'}

@app.post('/auth/login', tags=['Authentication'])
def login(body: Login, db=Depends(get_db)):
    t = table('users')
    u = db.execute(select(t).where(func.lower(t.c.email) == str(body.email).lower())).mappings().first()
    if not u or not verify(body.password, u['password_hash']) or not u['is_active']:
        raise HTTPException(401, 'Invalid credentials')
    return {'access_token':token(u),'token_type':'bearer'}

@app.get('/auth/me', tags=['Authentication'])
def me(u=Depends(current_user)):
    return public_user(u)

@app.post('/users', status_code=201, tags=['Administration'])
def create_user(body: UserCreate, u=Depends(admin), db=Depends(get_db)):
    data = body.model_dump(exclude={'password'})
    data['email'] = str(body.email).lower()
    return public_user(add(db, 'users', **data, password_hash=hasher.hash(body.password)))

@app.get('/users', tags=['Administration'])
def users(offset: int=Query(0,ge=0), limit: int=Query(50,ge=1,le=200), u=Depends(admin), db=Depends(get_db)):
    return [public_user(dict(r)) for r in db.execute(select(table('users')).order_by(table('users').c.user_id).offset(offset).limit(limit)).mappings()]

class AccountStatus(Input):
    is_active: bool
@app.patch('/users/{ident}/status', tags=['Administration'])
def account_status(ident:int, body:AccountStatus, u=Depends(admin), db=Depends(get_db)):
    if ident == u['user_id']:
        raise HTTPException(422,'Cannot disable your own account')
    one(db,'users',ident)
    return public_user(update(db,'users',ident,**body.model_dump()))

# Typed administration endpoints; no arbitrary table names or SQL accepted.
class Department(Input):
    department_name: str = Field(min_length=1,max_length=120)
    department_code: str = Field(min_length=1,max_length=20)
class Course(Input):
    program_level: Literal['UG','PG','UNCLASSIFIED'] | None = None
    department_id: int
    course_name: str = Field(min_length=1,max_length=120)
    course_code: str = Field(min_length=1,max_length=30)
    duration_years: int = Field(ge=1,le=10)
class Section(Input):
    course_id: int
    academic_year: str = Field(pattern=r'^\d{4}-\d{4}$')
    section_name: str = Field(min_length=1,max_length=30)
class Subject(Input):
    course_id: int
    subject_name: str = Field(min_length=1,max_length=120)
    subject_code: str = Field(min_length=1,max_length=30)
    semester: int = Field(ge=1,le=16)
class Topic(Input):
    subject_id: int
    topic_name: str = Field(min_length=1,max_length=160)
    description: str = ''
class Enrollment(Input):
    student_id: int
    section_id: int
class FacultyAssignment(Input):
    faculty_id: int
    subject_id: int
    section_id: int
class Event(Input):
    title: str = Field(min_length=1,max_length=160)
    starts_on: date
    ends_on: date
    description: str = ''
    @model_validator(mode='after')
    def dates(self):
        if self.ends_on < self.starts_on:
            raise ValueError('ends_on must follow starts_on')
        return self

def register_catalog(name, schema, scope):
    def linked(db,entity,ident):
        refs={'subjects':[('faculty_subject_assignments','subject_id'),('tests','subject_id'),('assignments','subject_id'),('class_sessions','subject_id')],
              'sections':[('student_enrollments','section_id'),('faculty_subject_assignments','section_id'),('tests','section_id'),('assignments','section_id'),('class_sessions','section_id')],
              'topics':[('questions','topic_id'),('study_plan_items','topic_id'),('class_sessions','topic_id'),('teaching_topic_progress','topic_id')]}
        return any(db.execute(select(list(table(t).primary_key)[0]).where(table(t).c[col]==ident).limit(1)).first() for t,col in refs.get(entity,[]) if t in metadata.tables)
    def department_for(db,row):
        if name=='departments':return row['department_id']
        if name=='courses':return row['department_id']
        if name in ['subjects','sections']:return one(db,'courses',row['course_id'])['department_id']
        if name=='topics':return one(db,'courses',one(db,'subjects',row['subject_id'])['course_id'])['department_id']
        return None
    def record_audit(db,u,action,ident,before,after):
        from .campus import audit
        safe=lambda value:json.loads(json.dumps(value,default=str)) if value is not None else None
        audit(db,u,action,name,ident,safe(before),safe(after),'Academic catalog change saved',ident if name=='departments' else department_for(db,after))
    def validate(db,u,data):
        if scope == 'subject':
            subject_access(db,u,data['subject_id'],write=True)
        elif scope == 'course' and u['role'] != 'ADMIN':
            c=one(db,'courses',data['course_id'])
            if c['department_id'] != u['department_id'] or u['role'] not in ('HOD','FACULTY'):
                raise HTTPException(403,'Course outside department')
            if 'subject_id' in data:
                subject_access(db,u,data['subject_id'],write=True)
    def create(body, u=Depends(staff if scope else admin), db=Depends(get_db)):
        data=body.model_dump()
        validate(db,u,data)
        level=data.pop('program_level',None) if name=='courses' else None
        result=add(db,name,**data)
        if name=='courses':
            db.execute(table('course_programs').insert().values(course_id=result['course_id'],program_level=level or 'UNCLASSIFIED'))
        record_audit(db,u,'CATALOG_CREATED',result[list(table(name).primary_key)[0].name],None,data)
        return result
    create.__annotations__['body']=schema
    create.__name__='create_'+name
    def edit(ident:int,body,u=Depends(staff if scope else admin),db=Depends(get_db)):
        old=one(db,name,ident,True)
        validate(db,u,old)
        data=body.model_dump()
        validate(db,u,data)
        level=data.pop('program_level',None) if name=='courses' else None
        curriculum=None
        if name=='subjects':
            if data['course_id']!=old['course_id'] and linked(db,name,ident):raise HTTPException(409,'Subject has teaching or academic history; create a new subject instead of moving it')
            if 'subject_curriculum' in metadata.tables:
                ct=table('subject_curriculum');curriculum=db.execute(select(ct).where(ct.c.subject_id==ident)).mappings().first()
                year=(data['semester']+1)//2
                if year>(one(db,'courses',data['course_id'])['duration_years'] or 8):raise HTTPException(422,'Semester exceeds program duration')
                if curriculum and year!=curriculum['study_year'] and linked(db,name,ident):raise HTTPException(409,'Subject year has teaching or academic history; create a new subject for the other year')
        if name=='sections' and data['course_id']!=old['course_id'] and linked(db,name,ident):raise HTTPException(409,'Section has enrollment or academic history; create a new section instead')
        if name=='topics' and data['subject_id']!=old['subject_id'] and linked(db,name,ident):raise HTTPException(409,'Topic has questions, progress or academic history; create a new topic instead')
        if name=='courses':
            max_year=0
            if 'subject_curriculum' in metadata.tables:
                ct,st=table('subject_curriculum'),table('subjects');max_year=db.scalar(select(func.max(ct.c.study_year)).join(st,st.c.subject_id==ct.c.subject_id).where(st.c.course_id==ident)) or 0
            if 'section_study_years' in metadata.tables:
                sy,sec=table('section_study_years'),table('sections');max_year=max(max_year,db.scalar(select(func.max(sy.c.study_year)).join(sec,sec.c.section_id==sy.c.section_id).where(sec.c.course_id==ident)) or 0)
            if data['duration_years']<max_year:raise HTTPException(409,'Duration cannot exclude existing curriculum or cohort years')
            if data['department_id']!=old['department_id']:
                st,sec=table('subjects'),table('sections')
                if db.execute(select(st.c.subject_id).where(st.c.course_id==ident).limit(1)).first() or db.execute(select(sec.c.section_id).where(sec.c.course_id==ident).limit(1)).first():raise HTTPException(409,'Course has subjects or sections; create a new course for another department')
        result=update(db,name,ident,**data)
        if curriculum:
            ct=table('subject_curriculum');db.execute(ct.update().where(ct.c.subject_id==ident).values(study_year=(data['semester']+1)//2,semester=data['semester']))
        if name=='courses'  and level is not None:
            cp=table('course_programs')
            if db.execute(select(cp.c.course_id).where(cp.c.course_id==ident)).first():db.execute(cp.update().where(cp.c.course_id==ident).values(program_level=level))
            else:db.execute(cp.insert().values(course_id=ident,program_level=level))
        record_audit(db,u,'CATALOG_UPDATED',ident,{k:old.get(k) for k in data},data)
        return result
    edit.__annotations__['body']=schema
    edit.__name__='edit_'+name
    def listing(offset:int=Query(0,ge=0),limit:int=Query(50,ge=1,le=200),u=Depends(current_user),db=Depends(get_db)):
        # Organization catalog contains no private student data.
        return [dict(r) for r in db.execute(select(table(name)).order_by(list(table(name).primary_key)[0]).offset(offset).limit(limit)).mappings()]
    listing.__name__='list_'+name
    app.add_api_route('/'+name,create,methods=['POST'],status_code=201,tags=['Academic catalog'])
    app.add_api_route('/'+name+'/{ident}',edit,methods=['PUT'],tags=['Academic catalog'])
    app.add_api_route('/'+name,listing,methods=['GET'],tags=['Academic catalog'])

for name,schema,scope in [('departments',Department,None),('courses',Course,None),('sections',Section,None),('subjects',Subject,'course'),('topics',Topic,'subject'),('academic_events',Event,None)]:
    register_catalog(name,schema,scope)

@app.post('/enrollments',status_code=201,tags=['Administration'])
def enroll(body:Enrollment,u=Depends(admin),db=Depends(get_db)):
    s=one(db,'users',body.student_id)
    section=one(db,'sections',body.section_id)
    c=one(db,'courses',section['course_id'])
    if s['role']!='STUDENT' or s['department_id']!=c['department_id']:
        raise HTTPException(422,'Student must belong to course department')
    return add(db,'student_enrollments',**body.model_dump())

@app.post('/faculty-assignments',status_code=201,tags=['Administration'])
def faculty_assignment(body:FacultyAssignment,u=Depends(admin),db=Depends(get_db)):
    f=one(db,'users',body.faculty_id)
    subject_access(db,u,body.subject_id,body.section_id,write=True)
    c=one(db,'courses',one(db,'subjects',body.subject_id)['course_id'])
    if f['role']!='FACULTY' or f['department_id']!=c['department_id']:
        raise HTTPException(422,'Faculty must belong to subject department')
    return add(db,'faculty_subject_assignments',**body.model_dump())

@app.post('/questions',status_code=201,tags=['Question bank'])
def create_question(body:Question,u=Depends(staff),db=Depends(get_db)):
    question_scope(db,u,body.model_dump())
    return add(db,'questions',**body.model_dump(),created_by=u['user_id'],question_source='FACULTY',review_status='APPROVED')

@app.get('/questions',tags=['Question bank'])
def questions(subject_id:int,offset:int=Query(0,ge=0),limit:int=Query(50,ge=1,le=200),u=Depends(staff),db=Depends(get_db)):
    subject_access(db,u,subject_id,write=True)
    q,t=table('questions'),table('topics')
    return [dict(r) for r in db.execute(select(q).join(t,q.c.topic_id==t.c.topic_id).where(t.c.subject_id==subject_id).order_by(q.c.question_id).offset(offset).limit(limit)).mappings()]

@app.put('/questions/{ident}',tags=['Question bank'])
def edit_question(ident:int,body:Question,u=Depends(staff),db=Depends(get_db)):
    old=one(db,'questions',ident,True)
    question_scope(db,u,old)
    question_scope(db,u,body.model_dump())
    tq,te=table('test_questions'),table('tests')
    if db.execute(select(tq).join(te,tq.c.test_id==te.c.test_id).where(tq.c.question_id==ident,te.c.status!='DRAFT')).first():
        raise HTTPException(409,'Question used by a published/closed test; create a new question instead')
    return update(db,'questions',ident,**body.model_dump(),review_status='PENDING_REVIEW' if old['question_source']=='GENAI' else 'APPROVED')

@app.patch('/questions/{ident}/review',tags=['Question bank'])
def review(ident:int,body:Review,u=Depends(staff),db=Depends(get_db)):
    q=one(db,'questions',ident,True)
    question_scope(db,u,q)
    tq,te=table('test_questions'),table('tests')
    if db.execute(select(tq).join(te,tq.c.test_id==te.c.test_id).where(tq.c.question_id==ident,te.c.status!='DRAFT')).first():
        raise HTTPException(409,'Question is frozen by a published test')
    return update(db,'questions',ident,**body.model_dump())

@app.post('/tests',status_code=201,tags=['Tests'])
def create_test(body:TestCreate,u=Depends(staff),db=Depends(get_db)):
    subject_access(db,u,body.subject_id,body.section_id,write=True)
    for item in body.questions:
        q=one(db,'questions',item.question_id,True)
        if one(db,'topics',q['topic_id'])['subject_id']!=body.subject_id or q['review_status']!='APPROVED' or not q['is_active']:
            raise HTTPException(422,'Questions must be active, approved and in the same subject')
    test=add(db,'tests',**body.model_dump(exclude={'questions'}),created_by=u['user_id'])
    for i,item in enumerate(body.questions,1):
        db.execute(table('test_questions').insert().values(test_id=test['test_id'],question_id=item.question_id,marks=item.marks,question_order=i))
    return test

class TestStatus(Input):
    status: Literal['PUBLISHED','CLOSED']
@app.patch('/tests/{ident}/status',tags=['Tests'])
def test_status(ident:int,body:TestStatus,u=Depends(staff),db=Depends(get_db)):
    t=one(db,'tests',ident,True)
    subject_access(db,u,t['subject_id'],t['section_id'],write=True)
    if t['status']=='CLOSED' or (t['status']=='DRAFT' and body.status=='CLOSED'):
        raise HTTPException(409,'Invalid test state transition')
    if body.status=='PUBLISHED':
        tq=table('test_questions')
        links=rows(db,'test_questions',tq.c.test_id==ident)
        if not links:
            raise HTTPException(422,'Test needs questions')
        for link in links:
            question=one(db,'questions',link['question_id'],True)
            if question['review_status']!='APPROVED' or not question['is_active']:
                raise HTTPException(409,'Every question must still be active and approved')
    return update(db,'tests',ident,status=body.status)

@app.get('/tests',tags=['Tests'])
def list_tests(subject_id:int,section_id:int,u=Depends(current_user),db=Depends(get_db)):
    subject_access(db,u,subject_id,section_id)
    t=table('tests')
    conditions=[t.c.subject_id==subject_id,t.c.section_id==section_id]
    if u['role']=='STUDENT':
        conditions.append(t.c.status=='PUBLISHED')
    return rows(db,'tests',*conditions)

@app.get('/tests/{ident}/questions',tags=['Tests'])
def test_questions(ident:int,u=Depends(current_user),db=Depends(get_db)):
    t=one(db,'tests',ident)
    subject_access(db,u,t['subject_id'],t['section_id'])
    if u['role']=='STUDENT':
        a=table('test_attempts')
        if not db.execute(select(a).where(a.c.test_id==ident,a.c.student_id==u['user_id'],a.c.status=='IN_PROGRESS')).first():
            raise HTTPException(403,'Start an attempt first')
    q,tq=table('questions'),table('test_questions')
    result=[dict(r) for r in db.execute(select(q,tq.c.marks,tq.c.question_order).join(tq,q.c.question_id==tq.c.question_id).where(tq.c.test_id==ident).order_by(tq.c.question_order)).mappings()]
    if u['role']=='STUDENT':
        for r in result:
            for key in ('correct_answer','explanation'):
                r.pop(key,None)
    return result

def available(t,now):
    if t['status']!='PUBLISHED' or (t['start_at'] and now<t['start_at']) or (t['end_at'] and now>t['end_at']):
        raise HTTPException(409,'Test is not open')

@app.post('/tests/{ident}/attempts',status_code=201,tags=['Attempts'])
def start_attempt(ident:int,u=Depends(student),db=Depends(get_db)):
    # Lock parent row to serialize allocation of attempt_number under MySQL.
    t=one(db,'tests',ident,True)
    subject_access(db,u,t['subject_id'],t['section_id'])
    available(t,datetime.now(timezone.utc).replace(tzinfo=None))
    a=table('test_attempts')
    previous=rows(db,'test_attempts',a.c.test_id==ident,a.c.student_id==u['user_id'])
    active=next((x for x in previous if x['status']=='IN_PROGRESS'),None)
    if active:
        if t['duration_minutes'] and datetime.now(timezone.utc).replace(tzinfo=None) > active['started_at'] + timedelta(minutes=t['duration_minutes']):
            if 'exam_schedules' in metadata.tables:
                scheduled = table('exam_schedules')
                if db.scalar(select(scheduled.c.test_id).where(scheduled.c.test_id==ident)):
                    return active
            update(db,'test_attempts',active['attempt_id'],status='CANCELLED')
        else:
            return active
    if len(previous)>=t['max_attempts']:
        raise HTTPException(409,'Maximum attempts reached')
    return add(db,'test_attempts',test_id=ident,student_id=u['user_id'],attempt_number=len(previous)+1)

@app.post('/attempts/{ident}/submit',tags=['Attempts'])
def submit(ident:int,body:Submit,u=Depends(student),db=Depends(get_db)):
    a=one(db,'test_attempts',ident,True)
    if a['student_id']!=u['user_id']:
        raise HTTPException(403,'Not your attempt')
    if a['status']!='IN_PROGRESS':
        raise HTTPException(409,'Attempt already submitted')
    t=one(db,'tests',a['test_id'])
    now=datetime.now(timezone.utc).replace(tzinfo=None)
    available(t,now)
    if t['duration_minutes'] and now>a['started_at']+timedelta(minutes=t['duration_minutes']):
        raise HTTPException(409,'Attempt time expired')
    tq=table('test_questions')
    qs=rows(db,'test_questions',tq.c.test_id==t['test_id'])
    answers={x.question_id:x.answer_text for x in body.answers}
    if len(answers)!=len(body.answers) or not set(answers).issubset({x['question_id'] for x in qs}):
        raise HTTPException(422,'Duplicate or unrelated answer question')
    score=0.0
    manual=False
    for link in qs:
        q=one(db,'questions',link['question_id'])
        answer=answers.get(q['question_id'],'')
        objective=q['question_type'] in ('MCQ','TRUE_FALSE')
        marks=float(link['marks']) if objective and answer.strip().casefold()==(q['correct_answer'] or '').strip().casefold() else 0.0
        manual |= not objective
        score+=marks
        add(db,'student_answers',attempt_id=ident,question_id=q['question_id'],answer_text=answer,awarded_marks=marks if objective else None,feedback=('Correct' if marks else 'Incorrect') if objective else None)
    return update(db,'test_attempts',ident,submitted_at=now,score=score,status='SUBMITTED' if manual else 'EVALUATED')

@app.get('/attempts/{ident}',tags=['Attempts'])
def result(ident:int,u=Depends(current_user),db=Depends(get_db)):
    a=one(db,'test_attempts',ident)
    t=one(db,'tests',a['test_id'])
    student_access(db,u,a['student_id'],t['subject_id'])
    subject_access(db,u,t['subject_id'],t['section_id'])
    sa=table('student_answers')
    a['answers']=rows(db,'student_answers',sa.c.attempt_id==ident)
    return a

@app.patch('/answers/{ident}/grade',tags=['Evaluation'])
def grade_answer(ident:int,body:Grade,u=Depends(staff),db=Depends(get_db)):
    answer=one(db,'student_answers',ident)
    attempt=one(db,'test_attempts',answer['attempt_id'],True)
    t=one(db,'tests',attempt['test_id'])
    subject_access(db,u,t['subject_id'],t['section_id'],write=True)
    if attempt['status'] not in ('SUBMITTED','EVALUATED'):
        raise HTTPException(409,'Attempt not submitted')
    tq=table('test_questions')
    link=db.execute(select(tq).where(tq.c.test_id==t['test_id'],tq.c.question_id==answer['question_id'])).mappings().one()
    if body.marks>float(link['marks']):
        raise HTTPException(422,'Marks exceed question maximum')
    update(db,'student_answers',ident,awarded_marks=body.marks,feedback=body.feedback,evaluated_by=u['user_id'])
    sa=table('student_answers')
    all_answers=rows(db,'student_answers',sa.c.attempt_id==attempt['attempt_id'])
    return update(db,'test_attempts',attempt['attempt_id'],score=sum(float(x['awarded_marks'] or 0) for x in all_answers),status='EVALUATED' if all(x['awarded_marks'] is not None for x in all_answers) else 'SUBMITTED')

@app.post('/assignments',status_code=201,tags=['Assignments'])
def assignment(body:Assignment,u=Depends(staff),db=Depends(get_db)):
    subject_access(db,u,body.subject_id,body.section_id,write=True)
    return add(db,'assignments',**body.model_dump(),created_by=u['user_id'])

@app.get('/assignments',tags=['Assignments'])
def list_assignments(subject_id:int,section_id:int,u=Depends(current_user),db=Depends(get_db)):
    subject_access(db,u,subject_id,section_id)
    t=table('assignments')
    return rows(db,'assignments',t.c.subject_id==subject_id,t.c.section_id==section_id)

@app.post('/assignments/{ident}/submit',status_code=201,tags=['Assignments'])
def submit_assignment(ident:int,body:Submission,u=Depends(student),db=Depends(get_db)):
    a=one(db,'assignments',ident)
    subject_access(db,u,a['subject_id'],a['section_id'])
    if datetime.now(timezone.utc).replace(tzinfo=None)>a['due_at']:
        raise HTTPException(409,'Assignment deadline passed')
    return add(db,'submissions',assignment_id=ident,student_id=u['user_id'],**body.model_dump())

@app.get('/assignments/{ident}/submissions',tags=['Assignments'])
def submissions(ident:int,u=Depends(current_user),db=Depends(get_db)):
    a=one(db,'assignments',ident)
    subject_access(db,u,a['subject_id'],a['section_id'])
    s=table('submissions')
    conditions=[s.c.assignment_id==ident]
    if u['role']=='STUDENT':
        conditions.append(s.c.student_id==u['user_id'])
    return rows(db,'submissions',*conditions)

@app.patch('/submissions/{ident}/grade',tags=['Evaluation'])
def grade_submission(ident:int,body:Grade,u=Depends(staff),db=Depends(get_db)):
    s=one(db,'submissions',ident)
    a=one(db,'assignments',s['assignment_id'])
    subject_access(db,u,a['subject_id'],a['section_id'],write=True)
    if body.marks>float(a['max_marks']):
        raise HTTPException(422,'Marks exceed assignment maximum')
    return update(db,'submissions',ident,marks_awarded=body.marks,feedback=body.feedback,status='GRADED')

@app.post('/attendance',status_code=201,tags=['Attendance'])
def attendance(body:Attendance,u=Depends(staff),db=Depends(get_db)):
    subject_access(db,u,body.subject_id,body.section_id,write=True)
    if body.topic_id and one(db,'topics',body.topic_id)['subject_id']!=body.subject_id:
        raise HTTPException(422,'Topic outside subject')
    if len({r.student_id for r in body.records})!=len(body.records):
        raise HTTPException(422,'Duplicate attendance student')
    for r in body.records:
        s=one(db,'users',r.student_id)
        if s['role']!='STUDENT':
            raise HTTPException(422,'Expected student')
        subject_access(db,s,body.subject_id,body.section_id)
    session=add(db,'class_sessions',**body.model_dump(exclude={'records'}),marked_by=u['user_id'])
    for r in body.records:
        add(db,'attendance_records',session_id=session['session_id'],**r.model_dump())
    return session

from .analytics import router as analytics_router
from .ai import router as ai_router
app.include_router(analytics_router)
app.include_router(ai_router)



from .ui import router as ui_router
app.include_router(ui_router)

# Original APIs remain available; /api aliases support the React Vite proxy.
from .portal import router as portal_router
app.include_router(portal_router)
from .dataset_analytics import router as dataset_router
app.include_router(dataset_router)
from .rag import router as rag_router
app.include_router(rag_router)
from .campus import router as campus_router
app.include_router(campus_router)
from .faculty_ops import router as faculty_ops_router
app.include_router(faculty_ops_router)
from .development import router as development_router
app.include_router(development_router)
from .college_data import router as college_router
app.include_router(college_router)
from .academics import router as academics_router
app.include_router(academics_router)
from fastapi import APIRouter
from fastapi.routing import APIRoute
api_aliases=APIRouter()
api_aliases.routes.extend(route for route in app.routes if isinstance(route,APIRoute))
app.include_router(api_aliases,prefix='/api')
for linked_router in (portal_router, ui_router, analytics_router, ai_router, dataset_router, rag_router, campus_router, faculty_ops_router, development_router, college_router, academics_router):
    app.include_router(linked_router,prefix='/api')

from pathlib import Path
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, RedirectResponse
project_path=Path(__file__).resolve().parents[2]
legacy_path=project_path/'frontend'
react_path=project_path/'frontend-react'/'dist'
if legacy_path.is_dir():
    app.mount('/assets',StaticFiles(directory=legacy_path/'assets'),name='legacy-assets')
    @app.get('/legacy',include_in_schema=False)
    def legacy_frontend():
        return FileResponse(legacy_path/'index.html')

@app.get('/',include_in_schema=False)
def frontend_root():
    return RedirectResponse('/app/')

if (react_path/'assets').is_dir():
    app.mount('/app/assets',StaticFiles(directory=react_path/'assets'),name='react-assets')

@app.get('/app',include_in_schema=False)
@app.get('/app/{client_path:path}',include_in_schema=False)
def frontend_app(client_path:str=''):
    if (react_path/'index.html').is_file():
        return FileResponse(react_path/'index.html',headers={'Cache-Control':'no-cache'})
    return FileResponse(legacy_path/'index.html',headers={'Cache-Control':'no-cache'})
