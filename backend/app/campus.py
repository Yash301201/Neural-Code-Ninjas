"""Role-scoped classroom operations. All mutations persist in MySQL transactions."""
from datetime import date,time,datetime,timedelta,timezone
from collections import Counter
import hashlib,json
from fastapi import APIRouter,Depends,HTTPException,Query
from pydantic import Field,model_validator
from sqlalchemy import select,func,and_
from .db import table,one,add,update,get_db
from .security import current_user,roles,subject_access,public_user
from .schemas import Input,AttendanceItem,TestCreate,TestQuestion
router=APIRouter(prefix='/campus',tags=['Campus workflows'])

def audit(db,u,action,kind,ident,before,after,reason,department=None):
    add(db,'campus_audit',actor_id=u['user_id'],department_id=department,action=action,entity_type=kind,entity_id=ident,before_data=before,after_data=after,reason=reason)
def dept_for_subject(db,ident):return one(db,'courses',one(db,'subjects',ident)['course_id'])['department_id']
def roster(db,section):
    us,en=table('users'),table('student_enrollments')
    return [dict(r) for r in db.execute(select(us.c.user_id,us.c.full_name,us.c.registration_number).join(en,en.c.student_id==us.c.user_id).where(en.c.section_id==section,en.c.status=='ACTIVE',us.c.is_active==True,us.c.role=='STUDENT').order_by(us.c.full_name)).mappings()]
def session_at(db,subject,section,day,start):
    t=table('class_sessions')
    r=db.execute(select(t).where(t.c.subject_id==subject,t.c.section_id==section,t.c.session_date==day,t.c.starts_at==start)).mappings().first()
    return dict(r) if r else None
def register_rows(db,session_id,section):
    people={r['user_id']:r for r in roster(db,section)};ar,us=table('attendance_records'),table('users')
    old={}
    if session_id:
        for r in db.execute(select(ar.c.student_id,ar.c.status,us.c.full_name,us.c.registration_number).join(us,us.c.user_id==ar.c.student_id).where(ar.c.session_id==session_id)).mappings():
            old[r['student_id']]=r['status']
            people.setdefault(r['student_id'],dict(user_id=r['student_id'],full_name=r['full_name'],registration_number=r['registration_number']))
    return [{**r,'status':old.get(r['user_id'])} for r in people.values()]

@router.get('/attendance/register')
def register(subject_id:int,section_id:int,session_date:date,starts_at:time,u=Depends(current_user),db=Depends(get_db)):
    if u['role']=='STUDENT':raise HTTPException(403,'Staff register only')
    subject_access(db,u,subject_id,section_id,write=True)
    session=session_at(db,subject_id,section_id,session_date,starts_at);ident=session['session_id'] if session else None
    version=db.scalar(select(table('attendance_registers').c.version).where(table('attendance_registers').c.session_id==ident)) if ident else 0
    return {'session_id':ident,'version':version or 0,'students':register_rows(db,ident,section_id)}

class RegisterSave(Input):
    subject_id:int
    section_id:int
    session_date:date
    starts_at:time
    session_id:int|None=None
    version:int=Field(default=0,ge=0)
    reason:str=Field(default='',max_length=500)
    records:list[AttendanceItem]=Field(min_length=1,max_length=500)

@router.post('/attendance/register')
def save_register(body:RegisterSave,u=Depends(roles('ADMIN','HOD','FACULTY')),db=Depends(get_db)):
    subject_access(db,u,body.subject_id,body.section_id,write=True)
    if body.session_date>date.today():raise HTTPException(422,'Attendance cannot be recorded for a future date')
    one(db,'sections',body.section_id,True)
    session=session_at(db,body.subject_id,body.section_id,body.session_date,body.starts_at)
    ident=session['session_id'] if session else None
    if body.session_id!=ident:raise HTTPException(409,'Register changed. Reload before saving.')
    if len({r.student_id for r in body.records})!=len(body.records):raise HTTPException(422,'Duplicate student')
    expected={r['user_id'] for r in register_rows(db,ident,body.section_id)}
    if {r.student_id for r in body.records}!=expected:raise HTTPException(409,'Roster changed or is incomplete. Reload and mark every student.')
    ar,reg=table('attendance_records'),table('attendance_registers');before=[]
    current=db.scalar(select(reg.c.version).where(reg.c.session_id==ident)) if ident else 0
    if body.version!=(current or 0):raise HTTPException(409,'Another staff member saved this register. Reload before correcting.')
    if ident:
        if len(body.reason.strip())<5:raise HTTPException(422,'Give a correction reason (at least 5 characters)')
        before=[dict(r) for r in db.execute(select(ar.c.student_id,ar.c.status).where(ar.c.session_id==ident)).mappings()]
    else:ident=add(db,'class_sessions',subject_id=body.subject_id,section_id=body.section_id,session_date=body.session_date,starts_at=body.starts_at,marked_by=u['user_id'])['session_id']
    existing={r['student_id']:r['attendance_id'] for r in db.execute(select(ar.c.student_id,ar.c.attendance_id).where(ar.c.session_id==ident)).mappings()}
    for r in body.records:
        if r.student_id in existing:update(db,'attendance_records',existing[r.student_id],status=r.status)
        else:add(db,'attendance_records',session_id=ident,**r.model_dump())
    version=(current or 0)+1
    values=dict(version=version,updated_by=u['user_id'],updated_at=datetime.now(timezone.utc).replace(tzinfo=None))
    if current is not None and session:db.execute(reg.update().where(reg.c.session_id==ident).values(**values))
    else:db.execute(reg.insert().values(session_id=ident,**values))
    audit(db,u,'ATTENDANCE_CORRECTED' if session else 'ATTENDANCE_RECORDED','class_session',ident,before,[r.model_dump() for r in body.records],body.reason or 'Initial complete class register',dept_for_subject(db,body.subject_id))
    return {'session_id':ident,'version':version,'counts':dict(Counter(r.status for r in body.records))}

@router.get('/attendance/report')
def attendance_report(subject_id:int,section_id:int,u=Depends(current_user),db=Depends(get_db)):
    subject_access(db,u,subject_id,section_id)
    ar,cs,us=[table(n) for n in ('attendance_records','class_sessions','users')]
    stmt=select(ar.c.student_id,us.c.full_name,us.c.registration_number,ar.c.status,cs.c.session_id,cs.c.session_date,cs.c.starts_at).join(cs,cs.c.session_id==ar.c.session_id).join(us,us.c.user_id==ar.c.student_id).where(cs.c.subject_id==subject_id,cs.c.section_id==section_id)
    if u['role']=='STUDENT':stmt=stmt.where(ar.c.student_id==u['user_id'])
    records=[dict(r) for r in db.execute(stmt.order_by(cs.c.session_date.desc(),cs.c.starts_at.desc())).mappings()]
    people={r['user_id']:r for r in roster(db,section_id) if u['role']!='STUDENT' or r['user_id']==u['user_id']}
    for r in records:people.setdefault(r['student_id'],dict(user_id=r['student_id'],full_name=r['full_name'],registration_number=r['registration_number']))
    totals=[]
    for ident,p in people.items():
        counts=Counter(r['status'] for r in records if r['student_id']==ident);total=sum(counts.values());attended=counts['PRESENT']+counts['LATE']
        totals.append({**p,'present':counts['PRESENT'],'absent':counts['ABSENT'],'late':counts['LATE'],'leave':counts['LEAVE'],'attended':attended,'recorded_classes':total,'percentage':round(100*attended/total,2) if total else None})
    return {'students':totals,'history':records,'session_count':len({r['session_id'] for r in records}),'denominator':'Classes with a saved mark for that student. Late counts as attended. Leave remains in the denominator.'}

class ExamSeries(Input):
    request_key:str=Field(pattern=r'^[a-fA-F0-9-]{36}$')
    subject_id:int
    section_id:int
    title:str=Field(min_length=3,max_length=100)
    exam_type:str=Field(pattern='^(DAILY|WEEKLY|FINAL)$')
    first_start_at:datetime
    occurrences:int=Field(default=1,ge=1,le=30)
    duration_minutes:int=Field(default=20,ge=1,le=180)
    window_minutes:int=Field(default=120,ge=1,le=1440)
    questions:list[TestQuestion]=Field(min_length=1,max_length=100)
    @model_validator(mode='after')
    def valid(self):
        if self.first_start_at.tzinfo:raise ValueError('Use UTC without an offset')
        if self.window_minutes<self.duration_minutes:raise ValueError('Exam window must cover its duration')
        if self.exam_type=='FINAL' and self.occurrences!=1:raise ValueError('Final exam has one occurrence')
        return self

@router.post('/exam-series',status_code=201)
def create_series(body:ExamSeries,u=Depends(roles('ADMIN','HOD','FACULTY')),db=Depends(get_db)):
    subject_access(db,u,body.subject_id,body.section_id,write=True);one(db,'sections',body.section_id,True)
    series,meta=table('exam_series'),table('exam_schedules');fingerprint=hashlib.sha256(body.model_dump_json(exclude={'request_key'}).encode()).hexdigest()
    old=db.execute(select(series).where(series.c.request_key==body.request_key)).mappings().first()
    if old:
        if old['created_by']!=u['user_id'] or old['fingerprint']!=fingerprint:raise HTTPException(409,'Request key already used for another schedule')
        return {'test_ids':list(db.scalars(select(meta.c.test_id).where(meta.c.request_key==body.request_key))),'already_created':True}
    if body.first_start_at+timedelta(minutes=body.window_minutes)<=datetime.now(timezone.utc).replace(tzinfo=None):raise HTTPException(422,'First exam window has already ended')
    for item in body.questions:
        q=one(db,'questions',item.question_id,True)
        if q['question_type']!='MCQ':raise HTTPException(422,'Scheduled exams support approved MCQ questions only')
    from .main import create_test
    db.execute(series.insert().values(request_key=body.request_key,fingerprint=fingerprint,created_by=u['user_id']))
    ids=[];step=7 if body.exam_type=='WEEKLY' else 1
    for i in range(body.occurrences):
        start=body.first_start_at+timedelta(days=i*step)
        test=create_test(TestCreate(subject_id=body.subject_id,section_id=body.section_id,title=f'{body.title} #{i+1}',duration_minutes=body.duration_minutes,max_attempts=1,start_at=start,end_at=start+timedelta(minutes=body.window_minutes),questions=body.questions),u,db)
        ident=test['test_id'];ids.append(ident)
        db.execute(meta.insert().values(test_id=ident,request_key=body.request_key,exam_type=body.exam_type,occurrence_number=i+1))
    audit(db,u,'EXAM_SERIES_CREATED','test',ids[0],None,{'test_ids':ids,'exam_type':body.exam_type},'Finite MCQ schedule created as drafts',dept_for_subject(db,body.subject_id))
    return {'test_ids':ids,'already_created':False,'status':'DRAFT','review_required':True}

@router.get('/exam-schedules')
def exam_schedules(u=Depends(current_user),db=Depends(get_db)):
    from .ui import context
    pairs={(x['subject_id'],x['section_id']) for x in context(u,db)['scopes']}
    t,m=table('tests'),table('exam_schedules');stmt=select(t,m.c.exam_type,m.c.occurrence_number).join(m,t.c.test_id==m.c.test_id)
    if u['role']=='STUDENT':stmt=stmt.where(t.c.status=='PUBLISHED')
    return [dict(r) for r in db.execute(stmt.order_by(t.c.start_at)).mappings() if (r['subject_id'],r['section_id']) in pairs]

class PersonEdit(Input):
    full_name:str=Field(min_length=1,max_length=120)
    registration_number:str|None=Field(default=None,max_length=60)
    is_active:bool
    reason:str=Field(min_length=5,max_length=500)

@router.get('/management')
def management(u=Depends(roles('ADMIN','HOD')),db=Depends(get_db)):
    us=table('users');stmt=select(us)
    if u['role']=='HOD':stmt=stmt.where(us.c.department_id==u['department_id'],us.c.role.in_(['STUDENT','FACULTY']))
    people=[public_user(dict(r)) for r in db.execute(stmt.order_by(us.c.full_name)).mappings()]
    fa,en=table('faculty_subject_assignments'),table('student_enrollments')
    ids=[p['user_id'] for p in people]
    assignments=[dict(r) for r in db.execute(select(fa).where(fa.c.faculty_id.in_(ids))).mappings()]
    enrollments=[dict(r) for r in db.execute(select(en).where(en.c.student_id.in_(ids))).mappings()]
    from .faculty_ops import program,timetable_records
    sections={r['section_id']:dict(r) for r in db.execute(select(table('sections'))).mappings()}
    courses={r['course_id']:dict(r) for r in db.execute(select(table('courses'))).mappings()}
    from .academics import year_maps
    cohort_years=year_maps(db)[0]
    for person in people:
        links=[]
        for enrollment in enrollments:
            if enrollment['student_id']!=person['user_id'] or enrollment['status']!='ACTIVE':continue
            section=sections[enrollment['section_id']];course=courses[section['course_id']]
            links.append({**section,'study_year':cohort_years.get(section['section_id']),'course_name':course['course_name'],'program_level':program(db,course['course_id']),'department_id':course['department_id']})
        person['academic_programs']=links
        person['is_demo']=person['email'].endswith('@demo.learnpath.dev')
    counts=Counter(p['role'] for p in people)
    return {'people':people,'assignments':assignments,'enrollments':enrollments,'counts':dict(counts),'active':sum(p['is_active'] for p in people),'timetable':timetable_records(db,u)}

@router.patch('/people/{ident}')
def edit_person(ident:int,body:PersonEdit,u=Depends(roles('ADMIN','HOD')),db=Depends(get_db)):
    target=one(db,'users',ident,True)
    if ident==u['user_id']:raise HTTPException(409,'Use another administrator for changes to your own account')
    if u['role']=='HOD' and (target['department_id']!=u['department_id'] or target['role'] not in ['STUDENT','FACULTY']):raise HTTPException(403,'Department student/faculty management only')
    if target['role']=='ADMIN' and not body.is_active:
        us=table('users');db.execute(select(us.c.user_id).where(us.c.role=='ADMIN').with_for_update()).all()
        if db.scalar(select(func.count()).select_from(us).where(us.c.role=='ADMIN',us.c.is_active==True))<=1:raise HTTPException(409,'At least one active administrator must remain')
    values=body.model_dump(exclude={'reason'});result=update(db,'users',ident,**values)
    audit(db,u,'PERSON_UPDATED','user',ident,{k:target[k] for k in values},values,body.reason,target['department_id'])
    return public_user(result)

class TeachingMap(Input):
    faculty_id:int
    subject_id:int
    section_id:int
@router.post('/teaching',status_code=201)
def teaching(body:TeachingMap,u=Depends(roles('ADMIN','HOD')),db=Depends(get_db)):
    subject_access(db,u,body.subject_id,body.section_id,write=True)
    f=one(db,'users',body.faculty_id);dept=dept_for_subject(db,body.subject_id)
    if f['role']!='FACULTY' or f['department_id']!=dept or not f['is_active']:raise HTTPException(422,'Choose active faculty in the subject department')
    one(db,'sections',body.section_id,True);t=table('faculty_subject_assignments')
    old=db.execute(select(t).where(t.c.faculty_id==body.faculty_id,t.c.subject_id==body.subject_id,t.c.section_id==body.section_id)).mappings().first()
    if old:return dict(old)
    result=add(db,'faculty_subject_assignments',**body.model_dump())
    audit(db,u,'TEACHING_ASSIGNED','subject',body.subject_id,None,body.model_dump(),'Teaching assignment added',dept)
    return result

@router.get('/audit')
def audits(u=Depends(roles('ADMIN','HOD')),db=Depends(get_db)):
    t=table('campus_audit');stmt=select(t)
    if u['role']=='HOD':stmt=stmt.where(t.c.department_id==u['department_id'])
    return [dict(r) for r in db.execute(stmt.order_by(t.c.audit_id.desc()).limit(100)).mappings()]

class DraftAnswer(Input):
    question_id:int
    answer_text:str=Field(max_length=20000)

def own_scheduled_attempt(db,u,ident,lock=False):
    a=one(db,'test_attempts',ident,lock)
    if a['student_id']!=u['user_id']:raise HTTPException(403,'Not your attempt')
    t=one(db,'tests',a['test_id'])
    subject_access(db,u,t['subject_id'],t['section_id'])
    if not db.scalar(select(table('exam_schedules').c.test_id).where(table('exam_schedules').c.test_id==t['test_id'])):raise HTTPException(422,'Scheduled exam required')
    return a,t

@router.get('/attempts/{ident}/draft')
def draft_answers(ident:int,u=Depends(roles('STUDENT')),db=Depends(get_db)):
    own_scheduled_attempt(db,u,ident)
    d=table('exam_answer_drafts')
    return [dict(r) for r in db.execute(select(d.c.question_id,d.c.answer_text).where(d.c.attempt_id==ident)).mappings()]

@router.put('/attempts/{ident}/draft')
def save_draft(ident:int,body:DraftAnswer,u=Depends(roles('STUDENT')),db=Depends(get_db)):
    a,t=own_scheduled_attempt(db,u,ident,True)
    now=datetime.now(timezone.utc).replace(tzinfo=None)
    deadline=min(a['started_at']+timedelta(minutes=t['duration_minutes']),t['end_at'] or datetime.max)
    if a['status']!='IN_PROGRESS' or t['status']!='PUBLISHED' or now>=deadline:raise HTTPException(409,'Answer saving window has ended')
    tq=table('test_questions')
    if not db.execute(select(tq.c.question_id).where(tq.c.test_id==t['test_id'],tq.c.question_id==body.question_id)).first():raise HTTPException(422,'Question outside this exam')
    q=one(db,'questions',body.question_id)
    if q['question_type']!='MCQ' or body.answer_text not in q['choice_options']:raise HTTPException(422,'Choose a valid MCQ option')
    d=table('exam_answer_drafts');cond=and_(d.c.attempt_id==ident,d.c.question_id==body.question_id)
    if db.execute(select(d.c.question_id).where(cond)).first():db.execute(d.update().where(cond).values(answer_text=body.answer_text,updated_at=now))
    else:db.execute(d.insert().values(attempt_id=ident,question_id=body.question_id,answer_text=body.answer_text,updated_at=now))
    return {'saved':True,'question_id':body.question_id}

@router.post('/attempts/{ident}/finish')
def finish_exam(ident:int,u=Depends(roles('STUDENT')),db=Depends(get_db)):
    a,t=own_scheduled_attempt(db,u,ident,True)
    if a['status']=='EVALUATED':return a
    if a['status']!='IN_PROGRESS':raise HTTPException(409,'Attempt is not in progress')
    # Only pre-deadline server-saved drafts are accepted, even when finishing later.
    d,tq=table('exam_answer_drafts'),table('test_questions')
    answers={r['question_id']:r['answer_text'] for r in db.execute(select(d).where(d.c.attempt_id==ident)).mappings()}
    links=db.execute(select(tq).where(tq.c.test_id==t['test_id']).order_by(tq.c.question_order)).mappings().all();score=0
    for link in links:
        q=one(db,'questions',link['question_id']);answer=answers.get(q['question_id'],'')
        if q['question_type']!='MCQ':raise HTTPException(409,'Scheduled paper contains an unsupported question')
        marks=float(link['marks']) if answer==q['correct_answer'] else 0;score+=marks
        add(db,'student_answers',attempt_id=ident,question_id=q['question_id'],answer_text=answer,awarded_marks=marks,feedback='Correct' if marks else 'Incorrect')
    return update(db,'test_attempts',ident,status='EVALUATED',score=score,submitted_at=datetime.now(timezone.utc).replace(tzinfo=None))

@router.post('/demo-faculty',status_code=201)
def demo_faculty(u=Depends(roles('ADMIN')),db=Depends(get_db)):
    """Idempotent, disabled fictional faculty. No usable password is distributed."""
    import secrets
    from .security import hasher
    us=table('users');departments=db.execute(select(table('departments')).order_by(table('departments').c.department_id).limit(3)).mappings().all()
    names=['Dr. K. Sravani','Prof. V. Ramana','Dr. P. Ravi Teja'];created=[]
    for i,dept in enumerate(departments):
        email=f"faculty-{dept['department_id']}@demo.learnpath.dev"
        if db.scalar(select(us.c.user_id).where(us.c.email==email)):continue
        person=add(db,'users',full_name=names[i]+' [DEMO]',email=email,role='FACULTY',department_id=dept['department_id'],password_hash=hasher.hash(secrets.token_urlsafe(32)),is_active=False)
        created.append(person['user_id'])
        audit(db,u,'DEMO_FACULTY_CREATED','user',person['user_id'],None,{'demo':True,'is_active':False},'Clearly labeled fictional showcase faculty',dept['department_id'])
    return {'created':len(created),'user_ids':created,'message':'Demo faculty are fictional and disabled. Existing credentials unchanged.'}
