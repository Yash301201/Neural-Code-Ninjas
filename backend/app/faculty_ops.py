from datetime import date,datetime,time,timedelta,timezone
from collections import Counter
from fastapi import APIRouter,Depends,HTTPException
from pydantic import Field,model_validator
from sqlalchemy import select,and_,or_,func
from .db import table,get_db,one,add,update
from .security import current_user,roles,subject_access
from .schemas import Input
from .campus import roster,audit,dept_for_subject,attendance_report
router=APIRouter(prefix='/faculty-ops',tags=['Faculty program operations'])
staff=roles('ADMIN','HOD','FACULTY')
def program(db,course_id):
    t=table('course_programs')
    return db.scalar(select(t.c.program_level).where(t.c.course_id==course_id)) or 'UNCLASSIFIED'
def class_info(db,subject_id,section_id):
    s=one(db,'subjects',subject_id);c=one(db,'courses',s['course_id']);section=one(db,'sections',section_id)
    from .academics import year_maps
    years,curriculum=year_maps(db)
    return {'study_year':years.get(section_id),'semester':curriculum.get(subject_id,{}).get('semester',s['semester']),'subject_id':subject_id,'subject_name':s['subject_name'],'course_id':c['course_id'],'course_name':c['course_name'],'program_level':program(db,c['course_id']),'department_id':c['department_id'],'department_name':one(db,'departments',c['department_id'])['department_name'],'section_id':section_id,'section_name':section['section_name'],'academic_year':section['academic_year']}

class ProgramEdit(Input):
    program_level:str=Field(pattern='^(UG|PG|UNCLASSIFIED)$')
@router.put('/programs/{course_id}')
def classify(course_id:int,body:ProgramEdit,u=Depends(roles('ADMIN','HOD')),db=Depends(get_db)):
    c=one(db,'courses',course_id,True)
    if u['role']=='HOD' and c['department_id']!=u['department_id']:raise HTTPException(403,'Course outside department')
    t=table('course_programs');before=program(db,course_id)
    if db.execute(select(t.c.course_id).where(t.c.course_id==course_id)).first():db.execute(t.update().where(t.c.course_id==course_id).values(program_level=body.program_level,updated_at=datetime.now(timezone.utc).replace(tzinfo=None)))
    else:db.execute(t.insert().values(course_id=course_id,program_level=body.program_level))
    audit(db,u,'PROGRAM_CLASSIFIED','course',course_id,{'program_level':before},body.model_dump(),'Course program classification updated',c['department_id'])
    return {'course_id':course_id,**body.model_dump()}

def coverage(db,a):
    people=roster(db,a['section_id']);ids={p['user_id'] for p in people};t=table('submissions')
    submissions={r['student_id']:dict(r) for r in db.execute(select(t).where(t.c.assignment_id==a['assignment_id'])).mappings()}
    rows=[]
    for p in people:
        sub=submissions.get(p['user_id'])
        rows.append({**p,'submission':sub,'submission_state':sub['status'] if sub else 'NOT_SUBMITTED'})
    count=sum(r['submission'] is not None for r in rows);graded=sum(r['submission_state']=='GRADED' for r in rows);returned=sum(r['submission_state']=='RETURNED' for r in rows)
    return {'assignment':a,'class':class_info(db,a['subject_id'],a['section_id']),'eligible':len(rows),'submitted':count,'not_submitted':len(rows)-count,'graded':graded,'awaiting_grading':count-graded-returned,'returned':returned,'historical_submissions':sum(ident not in ids for ident in submissions),'students':rows,'roster_basis':'Currently active enrolled students. Historical submissions outside that roster are counted separately.'}

@router.get('/assignments/{ident}/coverage')
def assignment_coverage(ident:int,u=Depends(staff),db=Depends(get_db)):
    a=one(db,'assignments',ident);subject_access(db,u,a['subject_id'],a['section_id'],write=True)
    return coverage(db,a)

@router.get('/class-register')
def class_register(subject_id:int,section_id:int,u=Depends(staff),db=Depends(get_db)):
    subject_access(db,u,subject_id,section_id,write=True)
    ar=attendance_report(subject_id,section_id,u,db);people=ar['students'];ids={p['user_id'] for p in people}
    at=table('assignments');assignments=[dict(r) for r in db.execute(select(at).where(at.c.subject_id==subject_id,at.c.section_id==section_id).order_by(at.c.due_at.desc())).mappings()]
    covers=[coverage(db,a) for a in assignments]
    t,a,tq=table('tests'),table('test_attempts'),table('test_questions')
    maximums={r[0]:float(r[1]) for r in db.execute(select(tq.c.test_id,func.sum(tq.c.marks)).join(t,t.c.test_id==tq.c.test_id).where(t.c.subject_id==subject_id,t.c.section_id==section_id).group_by(tq.c.test_id))}
    attempts=[dict(r) for r in db.execute(select(a,t.c.title).join(t,t.c.test_id==a.c.test_id).where(t.c.subject_id==subject_id,t.c.section_id==section_id,a.c.student_id.in_(ids)).order_by(a.c.attempt_id.desc())).mappings()]
    for p in people:
        subs=[{'assignment_id':c['assignment']['assignment_id'],'title':c['assignment']['title'],'due_at':c['assignment']['due_at'],'max_marks':c['assignment']['max_marks'],**next(({'submission_state':r['submission_state'],'submission':r['submission']} for r in c['students'] if r['user_id']==p['user_id']),{'submission_state':'NOT_ON_CURRENT_ROSTER','submission':None})} for c in covers]
        exams=[{**a,'max_marks':maximums.get(a['test_id'],0)} for a in attempts if a['student_id']==p['user_id']]
        evaluated=[a for a in exams if a['status']=='EVALUATED'];possible=sum(a['max_marks'] for a in evaluated);earned=sum(float(a['score'] or 0) for a in evaluated)
        p.update(assignments=subs,exams=exams,submitted_assignments=sum(a['submission'] is not None for a in subs),pending_assignments=sum(a['submission_state']=='NOT_SUBMITTED' for a in subs),exam_percentage=round(100*earned/possible,2) if possible else None)
    return {'class':class_info(db,subject_id,section_id),'students':people,'assignments':[{k:v for k,v in c.items() if k not in ['students','class']} for c in covers],'counts':{'active_enrolled':len(roster(db,section_id)),'learners_including_attendance_history':len(people),'assignments':len(assignments),'awaiting_grading':sum(c['awaiting_grading'] for c in covers)}}

class TimetableSlot(Input):
    faculty_id:int
    subject_id:int
    section_id:int
    weekday:int=Field(ge=0,le=6)
    starts_at:time
    ends_at:time
    room:str=Field(min_length=1,max_length=80)
    session_type:str=Field(default='LECTURE',pattern='^(LECTURE|LAB|TUTORIAL)$')
    @model_validator(mode='after')
    def valid(self):
        if self.ends_at<=self.starts_at:raise ValueError('End time must follow start time')
        return self

def timetable_records(db,u):
    t,s,c,sec,us=[table(n) for n in ['faculty_timetable','subjects','courses','sections','users']]
    stmt=select(t,s.c.subject_name,c.c.course_name,c.c.course_id,c.c.department_id,sec.c.section_name,sec.c.academic_year,us.c.full_name.label('faculty_name')).join(s,s.c.subject_id==t.c.subject_id).join(c,c.c.course_id==s.c.course_id).join(sec,sec.c.section_id==t.c.section_id).join(us,us.c.user_id==t.c.faculty_id).where(t.c.is_active==True)
    if u['role']=='FACULTY':stmt=stmt.where(t.c.faculty_id==u['user_id'])
    elif u['role']=='HOD':stmt=stmt.where(c.c.department_id==u['department_id'])
    elif u['role']=='STUDENT':
        en=table('student_enrollments');stmt=stmt.where(t.c.section_id.in_(select(en.c.section_id).where(en.c.student_id==u['user_id'],en.c.status=='ACTIVE')))
    rows=[]
    for r in db.execute(stmt.order_by(t.c.weekday,t.c.starts_at)).mappings():
        row=dict(r);row['program_level']=program(db,row['course_id'])
        from .academics import year_maps
        row['study_year']=year_maps(db)[0].get(row['section_id'])
        for k in ['starts_at','ends_at']:
            v=row[k];seconds=int(v.total_seconds()) if isinstance(v,timedelta) else v.hour*3600+v.minute*60;row[k]=f'{seconds//3600:02d}:{seconds%3600//60:02d}'
        rows.append(row)
    return rows

@router.get('/timetable')
def timetable(u=Depends(current_user),db=Depends(get_db)):return timetable_records(db,u)

@router.post('/timetable',status_code=201)
def add_slot(body:TimetableSlot,u=Depends(roles('ADMIN','HOD')),db=Depends(get_db)):
    subject_access(db,u,body.subject_id,body.section_id,write=True)
    one(db,'sections',body.section_id,True);faculty=one(db,'users',body.faculty_id,True)
    if faculty['role']!='FACULTY' or not faculty['is_active']:raise HTTPException(422,'Choose active faculty')
    subject_access(db,faculty,body.subject_id,body.section_id,write=True)
    t=table('faculty_timetable')
    collision=db.execute(select(t.c.slot_id).where(t.c.is_active==True,t.c.weekday==body.weekday,t.c.starts_at<body.ends_at,t.c.ends_at>body.starts_at,or_(t.c.faculty_id==body.faculty_id,t.c.section_id==body.section_id)).with_for_update()).first()
    if collision:raise HTTPException(409,'Faculty or class section already has an overlapping timetable slot')
    row=add(db,'faculty_timetable',**body.model_dump(),created_by=u['user_id'])
    audit(db,u,'TIMETABLE_ADDED','timetable',row['slot_id'],None,{'faculty_id':body.faculty_id,'weekday':body.weekday,'subject_id':body.subject_id,'section_id':body.section_id},'Weekly teaching slot scheduled',dept_for_subject(db,body.subject_id))
    return {'slot_id':row['slot_id']}

@router.delete('/timetable/{ident}')
def archive_slot(ident:int,u=Depends(roles('ADMIN','HOD')),db=Depends(get_db)):
    t=one(db,'faculty_timetable',ident,True);subject_access(db,u,t['subject_id'],t['section_id'],write=True)
    update(db,'faculty_timetable',ident,is_active=False)
    audit(db,u,'TIMETABLE_ARCHIVED','timetable',ident,{'is_active':True},{'is_active':False},'Weekly slot archived',dept_for_subject(db,t['subject_id']))
    return {'archived':True}

class LeaveRequest(Input):
    start_date:date
    end_date:date
    leave_type:str=Field(pattern='^(CASUAL|SICK|PERSONAL|ACADEMIC)$')
    reason:str=Field(min_length=5,max_length=1000)
    @model_validator(mode='after')
    def valid(self):
        if self.end_date<self.start_date or (self.end_date-self.start_date).days>30:raise ValueError('Choose a date range of at most 31 calendar days')
        if self.start_date<date.today():raise ValueError('Leave must start today or later')
        return self

def leave_access(u,requester):return u['role']=='ADMIN' or u['user_id']==requester['user_id'] or (u['role']=='HOD' and requester['role']=='FACULTY' and requester['department_id']==u['department_id'])
def impacted(db,owner,start,end):
    t=table('faculty_timetable');slots=db.execute(select(t.c.weekday,t.c.subject_id,t.c.section_id,t.c.starts_at,t.c.ends_at).where(t.c.faculty_id==owner,t.c.is_active==True)).mappings().all()
    return sum(sum(slot['weekday']==(start+timedelta(days=i)).weekday() for slot in slots) for i in range((end-start).days+1))

@router.get('/leave')
def leaves(u=Depends(roles('ADMIN','HOD','FACULTY')),db=Depends(get_db)):
    t,us=table('faculty_leave_requests'),table('users');stmt=select(t,us.c.full_name,us.c.role,us.c.department_id).join(us,us.c.user_id==t.c.requester_id)
    if u['role']=='FACULTY':stmt=stmt.where(t.c.requester_id==u['user_id'])
    elif u['role']=='HOD':stmt=stmt.where(or_(t.c.requester_id==u['user_id'],and_(us.c.department_id==u['department_id'],us.c.role=='FACULTY')))
    result=[]
    for r in db.execute(stmt.order_by(t.c.leave_id.desc())).mappings():
        row=dict(r);row['calendar_days']=(row['end_date']-row['start_date']).days+1;row['affected_classes']=impacted(db,row['requester_id'],row['start_date'],row['end_date']);row['can_review']=row['requester_id']!=u['user_id'] and (u['role']=='ADMIN' or u['role']=='HOD' and row['role']=='FACULTY');result.append(row)
    return result

@router.post('/leave',status_code=201)
def request_leave(body:LeaveRequest,u=Depends(roles('FACULTY','HOD')),db=Depends(get_db)):
    one(db,'users',u['user_id'],True);t=table('faculty_leave_requests')
    if db.execute(select(t.c.leave_id).where(t.c.requester_id==u['user_id'],t.c.status.in_(['PENDING','APPROVED']),t.c.start_date<=body.end_date,t.c.end_date>=body.start_date).with_for_update()).first():raise HTTPException(409,'An overlapping pending or approved leave request already exists')
    r=add(db,'faculty_leave_requests',requester_id=u['user_id'],**body.model_dump())
    audit(db,u,'LEAVE_REQUESTED','leave',r['leave_id'],None,{'status':'PENDING'},'Faculty leave request submitted',u['department_id'])
    return r

class LeaveDecision(Input):
    status:str=Field(pattern='^(APPROVED|REJECTED)$')
    review_note:str=Field(min_length=3,max_length=500)
@router.patch('/leave/{ident}/review')
def review_leave(ident:int,body:LeaveDecision,u=Depends(roles('ADMIN','HOD')),db=Depends(get_db)):
    r=one(db,'faculty_leave_requests',ident,True);owner=one(db,'users',r['requester_id'])
    if r['requester_id']==u['user_id'] or not leave_access(u,owner):raise HTTPException(403,'Cannot review your own request or another department')
    if r['status']!='PENDING':raise HTTPException(409,'Only pending requests can be reviewed')
    result=update(db,'faculty_leave_requests',ident,**body.model_dump(),reviewed_by=u['user_id'],reviewed_at=datetime.now(timezone.utc).replace(tzinfo=None))
    audit(db,u,'LEAVE_REVIEWED','leave',ident,{'status':r['status']},{'status':body.status},'Leave decision recorded',owner['department_id'])
    return result

@router.patch('/leave/{ident}/cancel')
def cancel_leave(ident:int,u=Depends(roles('FACULTY','HOD')),db=Depends(get_db)):
    r=one(db,'faculty_leave_requests',ident,True)
    if r['requester_id']!=u['user_id']:raise HTTPException(403,'Not your leave request')
    if r['status']!='PENDING':raise HTTPException(409,'Only pending requests can be withdrawn')
    update(db,'faculty_leave_requests',ident,status='CANCELLED')
    audit(db,u,'LEAVE_CANCELLED','leave',ident,{'status':'PENDING'},{'status':'CANCELLED'},'Requester withdrew pending leave',u['department_id'])
    return {'status':'CANCELLED'}
