from datetime import date,timedelta
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select,func,and_
from .db import table,one,add,update,get_db
from .security import current_user,student_access,subject_access,roles
from .schemas import PlanRequest,PlanStatus

router=APIRouter(tags=['Analytics and study plans'])

def performance(db,student_id,subject_id):
    # Include every question from every evaluated attempt, including unanswered ones.
    a,t,tq,q,tp,sa=[table(n) for n in ['test_attempts','tests','test_questions','questions','topics','student_answers']]
    stmt=select(tp.c.topic_id,tp.c.topic_name,func.sum(func.coalesce(sa.c.awarded_marks,0)).label('earned'),func.sum(tq.c.marks).label('possible')).select_from(a.join(t,a.c.test_id==t.c.test_id).join(tq,tq.c.test_id==t.c.test_id).join(q,q.c.question_id==tq.c.question_id).join(tp,tp.c.topic_id==q.c.topic_id).outerjoin(sa,and_(sa.c.attempt_id==a.c.attempt_id,sa.c.question_id==q.c.question_id))).where(a.c.student_id==student_id,t.c.subject_id==subject_id,a.c.status=='EVALUATED').group_by(tp.c.topic_id,tp.c.topic_name)
    return [{'topic_id':r.topic_id,'topic_name':r.topic_name,'earned':float(r.earned),'possible':float(r.possible),'percent':round(100*float(r.earned)/float(r.possible),2)} for r in db.execute(stmt)]

def metrics(db,student_id,subject_id):
    topics=performance(db,student_id,subject_id)
    ar,cs=table('attendance_records'),table('class_sessions')
    records=db.execute(select(ar.c.status).join(cs,ar.c.session_id==cs.c.session_id).where(ar.c.student_id==student_id,cs.c.subject_id==subject_id)).scalars().all()
    total=sum(x['possible'] for x in topics)
    score=round(100*sum(x['earned'] for x in topics)/total,2) if total else None
    attendance=round(100*sum(x in ('PRESENT','LATE') for x in records)/len(records),2) if records else None
    return {'topics':topics,'average_score':score,'attendance_percent':attendance,'recorded_sessions':len(records)}

@router.get('/students/{student_id}/performance')
def student_performance(student_id:int,subject_id:int,u=Depends(current_user),db=Depends(get_db)):
    student_access(db,u,student_id,subject_id)
    return metrics(db,student_id,subject_id)

@router.post('/students/{student_id}/risk')
def risk(student_id:int,subject_id:int,u=Depends(current_user),db=Depends(get_db)):
    student_access(db,u,student_id,subject_id)
    m=metrics(db,student_id,subject_id)
    observed=[(0.7,100-m['average_score'])] if m['average_score'] is not None else []
    if m['attendance_percent'] is not None:
        observed.append((0.3,100-m['attendance_percent']))
    if not observed:
        return {'risk_score':None,'risk_level':None,'reason':'Insufficient data','model_version':'heuristic-v1'}
    score=round(sum(w*x for w,x in observed)/sum(w for w,x in observed),2)
    return add(db,'risk_predictions',student_id=student_id,subject_id=subject_id,risk_score=score,risk_level='HIGH' if score>=60 else 'MEDIUM' if score>=35 else 'LOW',model_version='heuristic-v1',input_features={k:v for k,v in m.items() if k!='topics'},explanation='Rule-based early-warning indicator: 70% assessment deficit, 30% attendance deficit; missing indicators excluded. Faculty review required.')

@router.post('/study-plans',status_code=201)
def study_plan(body:PlanRequest,u=Depends(current_user),db=Depends(get_db)):
    student_access(db,u,body.student_id,body.subject_id)
    m=metrics(db,body.student_id,body.subject_id)
    tp=table('topics')
    topics=[dict(x) for x in db.execute(select(tp).where(tp.c.subject_id==body.subject_id)).mappings()]
    if not topics:
        raise HTTPException(422,'Subject has no topics')
    scores={x['topic_id']:x['percent'] for x in m['topics']}
    topics.sort(key=lambda x:scores.get(x['topic_id'],-1))
    start=date.today()
    plan=add(db,'study_plans',student_id=body.student_id,subject_id=body.subject_id,created_by=u['user_id'],generated_by='AI',title='Personalized topic practice',start_date=start,end_date=start+timedelta(days=body.days-1))
    plan['items']=[]
    for i,tp in enumerate(topics):
        score=scores.get(tp['topic_id'])
        recommendation=f"Review {tp['topic_name']}; solve five practice questions and summarize errors. " + ('No assessment history yet.' if score is None else f'Current topic score: {score}%.')
        plan['items'].append(add(db,'study_plan_items',plan_id=plan['plan_id'],topic_id=tp['topic_id'],scheduled_date=start+timedelta(days=i%body.days),recommendation=recommendation,estimated_minutes=45 if score is None or score<50 else 25))
    plan['method']='rule-based topic prioritization v1'
    return plan

@router.get('/study-plans')
def plans(student_id:int,subject_id:int,u=Depends(current_user),db=Depends(get_db)):
    student_access(db,u,student_id,subject_id)
    p,it=table('study_plans'),table('study_plan_items')
    result=[dict(x) for x in db.execute(select(p).where(p.c.student_id==student_id,p.c.subject_id==subject_id).order_by(p.c.plan_id.desc()).limit(50)).mappings()]
    for plan in result:
        plan['items']=[dict(x) for x in db.execute(select(it).where(it.c.plan_id==plan['plan_id'])).mappings()]
    return result

@router.patch('/study-plan-items/{ident}')
def plan_status(ident:int,body:PlanStatus,u=Depends(current_user),db=Depends(get_db)):
    item=one(db,'study_plan_items',ident)
    plan=one(db,'study_plans',item['plan_id'],True)
    student_access(db,u,plan['student_id'],plan['subject_id'])
    result=update(db,'study_plan_items',ident,status=body.status)
    it=table('study_plan_items')
    remaining=db.execute(select(func.count()).select_from(it).where(it.c.plan_id==plan['plan_id'],it.c.status!='COMPLETED')).scalar_one()
    update(db,'study_plans',plan['plan_id'],status='COMPLETED' if remaining==0 else 'ACTIVE')
    return result

@router.get('/dashboard')
def dashboard(subject_id:int,section_id:int,u=Depends(roles('ADMIN','HOD','FACULTY')),db=Depends(get_db)):
    subject_access(db,u,subject_id,section_id,write=True)
    e,us=table('student_enrollments'),table('users')
    students=db.execute(select(us.c.user_id,us.c.full_name).join(e,us.c.user_id==e.c.student_id).where(e.c.section_id==section_id,e.c.status=='ACTIVE')).all()
    result=[]
    for s in students:
        m=metrics(db,s.user_id,subject_id)
        result.append({'student_id':s.user_id,'full_name':s.full_name,**m,'needs_attention':(m['average_score'] is not None and m['average_score']<40) or (m['attendance_percent'] is not None and m['attendance_percent']<60)})
    return {'student_count':len(result),'needs_attention_count':sum(x['needs_attention'] for x in result),'students':result}

@router.get('/departments/{ident}/learning-gaps')
def learning_gaps(ident:int,u=Depends(roles('ADMIN','HOD')),db=Depends(get_db)):
    if u['role']=='HOD' and u['department_id']!=ident:
        raise HTTPException(403,'Department outside scope')
    c,s=table('courses'),table('subjects')
    subjects=db.execute(select(s).join(c,s.c.course_id==c.c.course_id).where(c.c.department_id==ident)).mappings().all()
    result=[]
    for subject in subjects:
        e,sec=table('student_enrollments'),table('sections')
        ids=db.execute(select(e.c.student_id).distinct().join(sec,e.c.section_id==sec.c.section_id).where(sec.c.course_id==subject['course_id'],e.c.status=='ACTIVE')).scalars().all()
        topic_scores={}
        for sid in ids:
            for tp in performance(db,sid,subject['subject_id']):
                item=topic_scores.setdefault(tp['topic_id'],{'topic_id':tp['topic_id'],'topic_name':tp['topic_name'],'scores':[]})
                item['scores'].append(tp['percent'])
        result.append({'subject_id':subject['subject_id'],'subject_name':subject['subject_name'],'enrolled_students':len(ids),'topics':[{'topic_id':x['topic_id'],'topic_name':x['topic_name'],'assessed_students':len(x['scores']),'average_percent':round(sum(x['scores'])/len(x['scores']),2)} for x in topic_scores.values()]})
    return result
