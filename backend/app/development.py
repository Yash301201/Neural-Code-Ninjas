"""Evidence-based staff development and individual exam insights."""
from datetime import datetime,timezone
from collections import defaultdict
from fastapi import APIRouter,Depends,HTTPException
from pydantic import Field,model_validator
from sqlalchemy import select,func,and_
from .db import table,get_db,one,add,update
from .security import roles,current_user,public_user,subject_access,student_access
from .schemas import Input
from .campus import audit
router=APIRouter(prefix='/development',tags=['Staff development and learner insights'])

def staff_access(db,u,ident,review=False):
    target=one(db,'users',ident)
    if target['role'] not in ['FACULTY','HOD']:raise HTTPException(422,'Faculty or HOD required')
    if not review and ident==u['user_id']:return target
    if u['role']=='ADMIN' and ident!=u['user_id']:return target
    if u['role']=='HOD' and target['role']=='FACULTY' and u['department_id']==target['department_id']:return target
    raise HTTPException(403,'Staff record outside your management scope')

@router.get('/staff')
def staff_list(u=Depends(roles('ADMIN','HOD','FACULTY')),db=Depends(get_db)):
    t=table('users');q=select(t).where(t.c.role.in_(['FACULTY','HOD']))
    if u['role']=='FACULTY':q=q.where(t.c.user_id==u['user_id'])
    elif u['role']=='HOD':q=q.where(t.c.department_id==u['department_id'],(t.c.role=='FACULTY')|(t.c.user_id==u['user_id']))
    return [public_user(dict(r)) for r in db.execute(q.order_by(t.c.full_name)).mappings()]

class Evidence(Input):
    category:str=Field(pattern='^(SKILL|RESUME|RESEARCH|COLLABORATION|TRAINING)$')
    title:str=Field(min_length=3,max_length=160)
    details:str=Field(min_length=5,max_length=5000)
    reference_url:str|None=Field(default=None,max_length=512)
    skill_level:int|None=Field(default=None,ge=1,le=5)
    @model_validator(mode='after')
    def valid_url(self):
        if self.reference_url and not self.reference_url.startswith(('https://','http://')):raise ValueError('Use an http(s) reference URL')
        if self.category!='SKILL':self.skill_level=None
        return self

@router.get('/staff/{ident}')
def staff_profile(ident:int,u=Depends(roles('ADMIN','HOD','FACULTY')),db=Depends(get_db)):
    target=staff_access(db,u,ident);ev,fb,us=table('staff_evidence'),table('staff_feedback'),table('users')
    records=[dict(r) for r in db.execute(select(ev).where(ev.c.owner_id==ident).order_by(ev.c.evidence_id.desc())).mappings()]
    ratings=[]
    for source in ['STUDENT','FACULTY','HOD','ADMIN']:
        q=select(func.count(),func.avg(fb.c.clarity),func.avg(fb.c.interaction)).join(us,us.c.user_id==fb.c.author_id).where(fb.c.faculty_id==ident,us.c.role==source)
        count,clarity,interaction=db.execute(q).one()
        if count:ratings.append({'source':source,'responses':count,'clarity':round(float(clarity),2) if count>=3 else None,'interaction':round(float(interaction),2) if count>=3 else None,'note':'Average hidden until 3 responses' if count<3 else 'Subjective feedback, not a verified teaching-quality score'})
    return {'person':public_user(target),'evidence':records,'feedback':ratings,'can_edit':u['user_id']==ident or u['role']=='ADMIN' or u['role']=='HOD' and target['role']=='FACULTY','can_review':u['user_id']!=ident and (u['role']=='ADMIN' or u['role']=='HOD' and target['role']=='FACULTY'),'verified_papers':sum(r['category']=='RESEARCH' and r['status']=='VERIFIED' for r in records),'submitted_papers':sum(r['category']=='RESEARCH' and r['status']=='SUBMITTED' for r in records)}

@router.post('/staff/{ident}/evidence',status_code=201)
def create_evidence(ident:int,body:Evidence,u=Depends(roles('ADMIN','HOD','FACULTY')),db=Depends(get_db)):
    target=staff_access(db,u,ident);row=add(db,'staff_evidence',owner_id=ident,**body.model_dump())
    audit(db,u,'EVIDENCE_CREATED','staff_evidence',row['evidence_id'],None,{'category':body.category},'Staff development record submitted',target['department_id']);return row

@router.put('/evidence/{ident}')
def edit_evidence(ident:int,body:Evidence,u=Depends(roles('ADMIN','HOD','FACULTY')),db=Depends(get_db)):
    old=one(db,'staff_evidence',ident,True);target=staff_access(db,u,old['owner_id'])
    if old['status']=='ARCHIVED':raise HTTPException(409,'Archived evidence cannot be edited')
    row=update(db,'staff_evidence',ident,**body.model_dump(),status='SUBMITTED',reviewed_by=None,review_note=None,updated_at=datetime.now(timezone.utc).replace(tzinfo=None))
    audit(db,u,'EVIDENCE_UPDATED','staff_evidence',ident,{'status':old['status']},{'status':'SUBMITTED'},'Evidence edited and returned for review',target['department_id']);return row

class EvidenceReview(Input):
    status:str=Field(pattern='^(VERIFIED|RETURNED)$')
    review_note:str=Field(min_length=5,max_length=500)
@router.patch('/evidence/{ident}/review')
def review_evidence(ident:int,body:EvidenceReview,u=Depends(roles('ADMIN','HOD')),db=Depends(get_db)):
    old=one(db,'staff_evidence',ident,True);target=staff_access(db,u,old['owner_id'],True)
    if old['status']=='ARCHIVED':raise HTTPException(409,'Evidence archived')
    row=update(db,'staff_evidence',ident,**body.model_dump(),reviewed_by=u['user_id'])
    audit(db,u,'EVIDENCE_REVIEWED','staff_evidence',ident,{'status':old['status']},{'status':body.status},body.review_note,target['department_id']);return row

@router.delete('/evidence/{ident}')
def archive_evidence(ident:int,u=Depends(roles('ADMIN','HOD','FACULTY')),db=Depends(get_db)):
    old=one(db,'staff_evidence',ident,True);target=staff_access(db,u,old['owner_id']);update(db,'staff_evidence',ident,status='ARCHIVED')
    audit(db,u,'EVIDENCE_ARCHIVED','staff_evidence',ident,{'status':old['status']},{'status':'ARCHIVED'},'Development record archived; history retained',target['department_id']);return {'archived':True}

@router.get('/feedback-options')
def feedback_options(u=Depends(current_user),db=Depends(get_db)):
    f,s,sec,us,en=[table(n) for n in ['faculty_subject_assignments','subjects','sections','users','student_enrollments']]
    if u['role']=='STUDENT':
        q=select(f,us.c.full_name,s.c.subject_name,sec.c.section_name).join(us,us.c.user_id==f.c.faculty_id).join(s,s.c.subject_id==f.c.subject_id).join(sec,sec.c.section_id==f.c.section_id).join(en,and_(en.c.section_id==f.c.section_id,en.c.student_id==u['user_id'],en.c.status=='ACTIVE'))
        return [dict(r) for r in db.execute(q.where(us.c.is_active==True)).mappings()]
    q=select(us.c.user_id.label('faculty_id'),us.c.full_name).where(us.c.is_active==True,us.c.role.in_(['FACULTY','HOD']),us.c.user_id!=u['user_id'])
    if u['role']!='ADMIN':q=q.where(us.c.department_id==u['department_id'])
    return [dict(r) for r in db.execute(q).mappings()]

@router.get('/my-feedback')
def my_feedback(u=Depends(current_user),db=Depends(get_db)):
    t=table('staff_feedback')
    return [dict(r) for r in db.execute(select(t).where(t.c.author_id==u['user_id'])).mappings()]

class Feedback(Input):
    faculty_id:int
    subject_id:int|None=None
    section_id:int|None=None
    clarity:int=Field(ge=1,le=5)
    interaction:int=Field(ge=1,le=5)
    comments:str=Field(min_length=5,max_length=1000)
@router.put('/feedback')
def save_feedback(body:Feedback,u=Depends(current_user),db=Depends(get_db)):
    choices=feedback_options(u,db)
    if u['role']=='STUDENT':
        if not any(r['faculty_id']==body.faculty_id and r['subject_id']==body.subject_id and r['section_id']==body.section_id for r in choices):raise HTTPException(403,'Choose a teacher assigned to your enrolled class')
        key=f'class:{body.subject_id}:{body.section_id}'
    else:
        if body.subject_id is not None or body.section_id is not None:raise HTTPException(422,'Colleague feedback has no class context')
        if not any(r['faculty_id']==body.faculty_id for r in choices):raise HTTPException(403,'Colleague outside department or self feedback')
        key='peer'
    t=table('staff_feedback');old=db.execute(select(t).where(t.c.author_id==u['user_id'],t.c.faculty_id==body.faculty_id,t.c.context_key==key).with_for_update()).mappings().first()
    if old:row=update(db,'staff_feedback',old['feedback_id'],**body.model_dump(),updated_at=datetime.now(timezone.utc).replace(tzinfo=None))
    else:row=add(db,'staff_feedback',author_id=u['user_id'],context_key=key,**body.model_dump())
    return {'feedback_id':row['feedback_id'],'saved':True}

@router.get('/learner-insights')
def learner_insights(subject_id:int,section_id:int,student_id:int|None=None,u=Depends(current_user),db=Depends(get_db)):
    ident=student_id if student_id is not None else u['user_id'];student_access(db,u,ident,subject_id);subject_access(db,u,subject_id,section_id)
    en=table('student_enrollments')
    if not db.scalar(select(en.c.enrollment_id).where(en.c.student_id==ident,en.c.section_id==section_id,en.c.status=='ACTIVE')):raise HTTPException(403,'Student not in this class')
    t,a,q,tq,ans,tp=[table(n) for n in ['tests','test_attempts','questions','test_questions','student_answers','topics']]
    maximums=select(tq.c.test_id,func.sum(tq.c.marks).label('maximum')).group_by(tq.c.test_id).subquery()
    exams=[dict(r) for r in db.execute(select(a.c.attempt_id,a.c.test_id,t.c.title,a.c.submitted_at,a.c.score,maximums.c.maximum).join(t,t.c.test_id==a.c.test_id).join(maximums,maximums.c.test_id==t.c.test_id).where(a.c.student_id==ident,a.c.status=='EVALUATED',t.c.subject_id==subject_id,t.c.section_id==section_id).order_by(a.c.submitted_at,a.c.attempt_id)).mappings()]
    for r in exams:r['percentage']=round(100*float(r['score'] or 0)/float(r['maximum']),2) if r['maximum'] else None
    cells=defaultdict(lambda:[0,0]);topic_names={}
    if exams:
        query=select(ans.c.attempt_id,q.c.topic_id,tp.c.topic_name,ans.c.awarded_marks,tq.c.marks).join(q,q.c.question_id==ans.c.question_id).join(tp,tp.c.topic_id==q.c.topic_id).join(a,a.c.attempt_id==ans.c.attempt_id).join(tq,and_(tq.c.test_id==a.c.test_id,tq.c.question_id==ans.c.question_id)).where(ans.c.attempt_id.in_([e['attempt_id'] for e in exams]))
        for r in db.execute(query).mappings():
            if r['awarded_marks'] is None:continue
            k=(r['attempt_id'],r['topic_id']);cells[k][0]+=float(r['awarded_marks']);cells[k][1]+=float(r['marks']);topic_names[r['topic_id']]=r['topic_name']
    heatmap=[{'topic_id':tid,'topic_name':name,'cells':[{'attempt_id':e['attempt_id'],'percentage':round(100*cells[(e['attempt_id'],tid)][0]/cells[(e['attempt_id'],tid)][1],1) if cells[(e['attempt_id'],tid)][1] else None} for e in exams]} for tid,name in topic_names.items()]
    subject=one(db,'subjects',subject_id);link=table('course_dataset_links');reference=db.execute(select(link).where(link.c.course_id==subject['course_id'])).mappings().first();benchmark=None
    if reference:
        from .dataset_analytics import tables,cohort_conditions
        ds=tables();g,ass=ds['scores'],ds['assessments']
        avg,count=db.execute(select(func.avg(g.c.score),func.count()).join(ass,and_(ass.c.batch_id==g.c.batch_id,ass.c.assessment_id==g.c.assessment_id)).where(*cohort_conditions(ass,reference['batch_id'],reference['code_module'],reference['code_presentation']),g.c.is_banked==False,g.c.score.is_not(None))).one()
        benchmark={**dict(reference),'mean_score':round(float(avg),2) if avg is not None else None,'graded_records':count,'note':'OULAD research cohort reference only. Different assessments and learners; not a ranking, prediction, or equivalent curriculum.'}
    return {'student':public_user(one(db,'users',ident)),'exams':exams,'heatmap':heatmap,'reference':benchmark,'note':'Each cell is earned marks / possible marks for one topic in one evaluated attempt. Grey means not assessed.'}

class DatasetLink(Input):
    module:str=Field(pattern='^[A-Z]{3}$')
    presentation:str=Field(pattern='^[0-9]{4}[BJ]$')
@router.put('/dataset-link/{course_id}')
def dataset_link(course_id:int,body:DatasetLink,u=Depends(roles('ADMIN','HOD')),db=Depends(get_db)):
    course=one(db,'courses',course_id)
    if u['role']=='HOD' and course['department_id']!=u['department_id']:raise HTTPException(403,'Course outside department')
    from .dataset_analytics import tables,ready,cohort
    ds=tables();batch=ready(db,ds)['batch_id'];cohort(db,ds,batch,body.module,body.presentation)
    t=table('course_dataset_links');values={'batch_id':batch,'code_module':body.module,'code_presentation':body.presentation,'linked_by':u['user_id']}
    if db.scalar(select(t.c.course_id).where(t.c.course_id==course_id)):db.execute(t.update().where(t.c.course_id==course_id).values(**values))
    else:db.execute(t.insert().values(course_id=course_id,**values))
    audit(db,u,'DATASET_REFERENCE_LINKED','course',course_id,None,values,'OULAD cohort linked as separate research reference',course['department_id']);return {'linked':True}

class ShowcaseRequest(Input):
    per_major:bool=False
@router.get('/showcase')
def showcase_status(u=Depends(roles('ADMIN')),db=Depends(get_db)):
    return [dict(r) for r in db.execute(select(table('demo_showcase_runs'))).mappings()]
@router.post('/showcase',status_code=201)
def create_showcase(body:ShowcaseRequest,u=Depends(roles('ADMIN')),db=Depends(get_db)):
    from .showcase_seed import seed
    try:return seed(db,u,body.per_major)
    except ValueError as e:raise HTTPException(409,str(e))
