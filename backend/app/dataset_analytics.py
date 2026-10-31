"""Authenticated analytics over public OULAD research records, never app users."""
import math
from fastapi import APIRouter,Depends,HTTPException,Query
from sqlalchemy import select,func,case,and_,inspect,MetaData,Table
from .db import get_db,engine,metadata
from .security import current_user

router=APIRouter(prefix='/dataset/oulad',tags=['OULAD research analytics'])
private_metadata=MetaData()
FIRST=['Sai Teja','Sravani','Venkata Sai','Lakshmi Priya','Srinivas','Harika','Sandeep','Divya','Ravi Teja','Anusha','Pavan Kumar','Bhavani','Nikhil','Mounika','Surya Prakash','Keerthana','Karthik','Sowmya','Vamsi Krishna','Sahithi','Chaitanya','Deepthi','Manoj','Poojitha']
LAST=['Kondapalli','Penumaka','Duvvuri','Nalluri','Chilukuri','Gollapudi','Vemuri','Kakarla','Maddala','Gorantla','Chaganti','Kandula','Yelamanchili','Velagapudi','Nidamarthi','Tadepalli','Polavarapu','Kommareddy','Chalasani','Muppalla','Rayapudi','Chintalapudi','Gundlapalli','Pasumarthi']

def alias(ident):
    """Fictional Telugu display alias; never an assertion about the source identity."""
    return LAST[(ident//len(FIRST))%len(LAST)]+' '+FIRST[ident%len(FIRST)]

def tables():
    if not inspect(engine).has_table('oulad_imports'):
        raise HTTPException(503,'OULAD is not imported yet. Run python -m scripts.import_oulad from backend.')
    result={}
    for name in ['imports','courses','students','registrations','assessments','scores','weekly_engagement','weekly_activity']:
        key='oulad_'+name
        if key in metadata.tables:result[name]=metadata.tables[key]
        elif key in private_metadata.tables:result[name]=private_metadata.tables[key]
        else:result[name]=Table(key,private_metadata,autoload_with=engine)
    return result

def ready(db,t):
    record=db.execute(select(t['imports']).where(t['imports'].c.status=='READY').order_by(t['imports'].c.batch_id.desc()).limit(1)).mappings().first()
    if not record:raise HTTPException(503,'OULAD import is still running or failed; no complete batch is available.')
    return dict(record)

def cohort_conditions(table,batch,module,presentation):
    return [table.c.batch_id==batch,table.c.code_module==module,table.c.code_presentation==presentation]

def cohort(db,t,batch,module,presentation):
    c=t['courses']
    record=db.execute(select(c).where(*cohort_conditions(c,batch,module,presentation))).mappings().first()
    if not record:raise HTTPException(404,'Dataset course cohort not found')
    return dict(record)

def scope(module:str=Query('BBB',pattern='^[A-Z]{3}$'),presentation:str=Query('2014J',pattern='^[0-9]{4}[BJ]$'),start_week:int=Query(0,ge=-8,le=60),end_week:int=Query(12,ge=-8,le=60)):
    if end_week<start_week:raise HTTPException(422,'End week must be greater than or equal to start week')
    return module,presentation,start_week,end_week

@router.get('/catalog')
def catalog(u=Depends(current_user),db=Depends(get_db)):
    t=tables();info=ready(db,t);s,c=t['students'],t['courses'];batch=info['batch_id']
    courses=[dict(x) for x in db.execute(select(c.c.code_module,c.c.code_presentation,c.c.length_days,func.count(s.c.student_id).label('enrollments')).select_from(c.join(s,and_(s.c.batch_id==c.c.batch_id,s.c.code_module==c.c.code_module,s.c.code_presentation==c.c.code_presentation))).where(c.c.batch_id==batch).group_by(c.c.code_module,c.c.code_presentation,c.c.length_days).order_by(c.c.code_module,c.c.code_presentation)).mappings()]
    w=t['weekly_engagement']
    bounds={(r.code_module,r.code_presentation):(r.min_week,r.max_week) for r in db.execute(select(w.c.code_module,w.c.code_presentation,func.min(w.c.week_index).label('min_week'),func.max(w.c.week_index).label('max_week')).where(w.c.batch_id==batch).group_by(w.c.code_module,w.c.code_presentation))}
    for course in courses:
        course['min_week'],course['max_week']=bounds.get((course['code_module'],course['code_presentation']),(0,math.ceil(course['length_days']/7)))
    return {'source':{**info,'citation':'Kuzilek, Hlosta & Zdrahal (2015), DOI: 10.24432/C5KK69','license_url':'https://creativecommons.org/licenses/by/4.0/','description':'Public anonymized UK Open University research data, separate from this college workspace.','display_names':'Fictional Andhra/Telugu aliases generated from anonymous IDs; not original identities.','engagement_note':'VLE clicks measure online activity, not classroom attendance.'},'courses':courses}

def learner_query(t,batch,module,presentation,start,end):
    s,w,a,g=t['students'],t['weekly_engagement'],t['assessments'],t['scores']
    activity=select(w.c.student_id,func.sum(w.c.clicks).label('clicks'),func.sum(w.c.active_days).label('active_days'),func.count().label('active_weeks')).where(*cohort_conditions(w,batch,module,presentation),w.c.week_index.between(start,end)).group_by(w.c.student_id).subquery()
    scores=select(g.c.student_id,func.avg(g.c.score).label('mean_score'),func.count().label('graded_submissions')).select_from(g.join(a,and_(g.c.batch_id==a.c.batch_id,g.c.assessment_id==a.c.assessment_id))).where(*cohort_conditions(a,batch,module,presentation),g.c.score.is_not(None),g.c.is_banked==False,g.c.submitted_day.between(start*7,end*7+6)).group_by(g.c.student_id).subquery()
    stmt=select(s.c.student_id,s.c.final_result,func.coalesce(activity.c.clicks,0).label('clicks'),func.coalesce(activity.c.active_days,0).label('active_days'),func.coalesce(activity.c.active_weeks,0).label('active_weeks'),scores.c.mean_score,func.coalesce(scores.c.graded_submissions,0).label('graded_submissions')).select_from(s.outerjoin(activity,activity.c.student_id==s.c.student_id).outerjoin(scores,scores.c.student_id==s.c.student_id)).where(*cohort_conditions(s,batch,module,presentation))
    return stmt

def label_learner(row):
    result=dict(row)
    result['display_name']=alias(result['student_id'])
    result['mean_score']=round(float(result['mean_score']),2) if result['mean_score'] is not None else None
    result['attention_signal']='No activity in range' if not result['clicks'] else 'Assessment score below 40%' if result['mean_score'] is not None and result['mean_score']<40 else 'Observed participation'
    return result

@router.get('/analytics')
def analytics(selection=Depends(scope),limit:int=Query(16,ge=4,le=40),order:str=Query('most_active',pattern='^(most_active|least_active)$'),u=Depends(current_user),db=Depends(get_db)):
    module,presentation,start,end=selection;t=tables();info=ready(db,t);batch=info['batch_id'];course=cohort(db,t,batch,module,presentation)
    s,w,a,g=t['students'],t['weekly_engagement'],t['assessments'],t['scores']
    outcomes=[dict(x) for x in db.execute(select(s.c.final_result.label('name'),func.count().label('value')).where(*cohort_conditions(s,batch,module,presentation)).group_by(s.c.final_result)).mappings()]
    enrollment_count=sum(x['value'] for x in outcomes)
    engaged={int(r['week_index']):dict(r) for r in db.execute(select(w.c.week_index,func.sum(w.c.clicks).label('clicks'),func.count(func.distinct(case((w.c.clicks>0,w.c.student_id),else_=None))).label('active_learners'),func.sum(w.c.active_days).label('active_days')).where(*cohort_conditions(w,batch,module,presentation),w.c.week_index.between(start,end)).group_by(w.c.week_index)).mappings()}
    grade_week=func.floor(g.c.submitted_day/7).label('week_index')
    grades={int(r['week_index']):dict(r) for r in db.execute(select(grade_week,func.avg(g.c.score).label('mean_score'),func.count().label('graded_submissions')).select_from(g.join(a,and_(g.c.batch_id==a.c.batch_id,g.c.assessment_id==a.c.assessment_id))).where(*cohort_conditions(a,batch,module,presentation),g.c.score.is_not(None),g.c.is_banked==False,g.c.submitted_day.between(start*7,end*7+6)).group_by(grade_week)).mappings()}
    timeline=[]
    for week in range(start,end+1):
        e=engaged.get(week,{});gr=grades.get(week,{})
        timeline.append({'week':week,'label':'W'+str(week),'clicks':int(e.get('clicks',0)),'active_learners':int(e.get('active_learners',0)),'engagement_rate':round(100*int(e.get('active_learners',0))/enrollment_count,2) if enrollment_count else 0,'mean_score':round(float(gr['mean_score']),2) if gr.get('mean_score') is not None else None,'graded_submissions':int(gr.get('graded_submissions',0))})
    all_learners=[label_learner(x) for x in db.execute(learner_query(t,batch,module,presentation,start,end)).mappings()]
    all_learners.sort(key=lambda p:((-p['clicks'] if order=='most_active' else p['clicks']),p['student_id']))
    sampled=all_learners[:limit];student_ids=[x['student_id'] for x in sampled]
    cells={}
    for row in db.execute(select(w.c.student_id,w.c.week_index,w.c.clicks,w.c.active_days).where(*cohort_conditions(w,batch,module,presentation),w.c.student_id.in_(student_ids),w.c.week_index.between(start,end))).mappings():
        cells[(row['student_id'],row['week_index'])]={'clicks':int(row['clicks']),'active_days':row['active_days']}
    for person in sampled:
        person['weeks']=[{'week':week,**cells.get((person['student_id'],week),{'clicks':0,'active_days':0})} for week in range(start,end+1)]
    at=t['weekly_activity']
    activity_types=[dict(x) for x in db.execute(select(at.c.activity_type.label('name'),func.sum(at.c.clicks).label('clicks')).where(*cohort_conditions(at,batch,module,presentation),at.c.week_index.between(start,end)).group_by(at.c.activity_type).order_by(func.sum(at.c.clicks).desc())).mappings()]
    comparison=[dict(x) for x in db.execute(select(s.c.code_module.label('module'),func.count().label('enrollments'),func.sum(case((s.c.final_result=='Pass',1),else_=0)).label('pass_count'),func.sum(case((s.c.final_result=='Distinction',1),else_=0)).label('distinction_count'),func.sum(case((s.c.final_result=='Fail',1),else_=0)).label('fail_count'),func.sum(case((s.c.final_result=='Withdrawn',1),else_=0)).label('withdrawn_count')).where(s.c.batch_id==batch).group_by(s.c.code_module).order_by(s.c.code_module)).mappings()]
    total_scores=sum(p['graded_submissions'] for p in all_learners)
    mean_score=sum(float(gr['mean_score'])*gr['graded_submissions'] for gr in grades.values())/total_scores if total_scores else None
    pass_count=sum(x['value'] for x in outcomes if x['name'] in ('Pass','Distinction'))
    return {'cohort':course,'range':{'start_week':start,'end_week':end},'summary':{'enrollments':enrollment_count,'active_learners':sum(p['clicks']>0 for p in all_learners),'clicks':sum(p['clicks'] for p in all_learners),'mean_score':round(mean_score,2) if mean_score is not None else None,'graded_submissions':total_scores,'historical_pass_rate':round(100*pass_count/enrollment_count,2) if enrollment_count else None,'no_activity_learners':sum(p['clicks']==0 for p in all_learners),'low_score_learners':sum(p['mean_score'] is not None and p['mean_score']<40 for p in all_learners)},'timeline':timeline,'outcomes':outcomes,'activity_types':activity_types,'comparison':comparison,'learners':sampled,'heatmap_sample':{'shown':len(sampled),'cohort_total':enrollment_count,'order':order},'scatter':[{'student_id':p['student_id'],'display_name':p['display_name'],'clicks':p['clicks'],'log_clicks':round(math.log10(p['clicks']+1),4),'mean_score':p['mean_score']} for p in sorted(all_learners,key=lambda p:p['student_id']) if p['mean_score'] is not None][:300],'notes':['Historical outcomes describe the full course, not the selected week range.','Score averages exclude missing scores and banked credits; weeks without graded submissions remain null.','Attention signals use activity/score observations in the selected range; they are not trained ML predictions.','Display names are fictional Andhra/Telugu aliases for anonymous research IDs.']}

@router.get('/learners/{student_id}')
def learner(student_id:int,selection=Depends(scope),u=Depends(current_user),db=Depends(get_db)):
    module,presentation,start,end=selection;t=tables();batch=ready(db,t)['batch_id'];cohort(db,t,batch,module,presentation)
    student=t['students'];row=db.execute(learner_query(t,batch,module,presentation,start,end).where(student.c.student_id==student_id)).mappings().first()
    if not row:raise HTTPException(404,'Research learner not found in this cohort')
    a,g,w=t['assessments'],t['scores'],t['weekly_engagement']
    history=[dict(x) for x in db.execute(select(a.c.assessment_id,a.c.assessment_type,a.c.due_day,a.c.weight,g.c.submitted_day,g.c.score,g.c.is_banked).select_from(g.join(a,and_(g.c.batch_id==a.c.batch_id,g.c.assessment_id==a.c.assessment_id))).where(*cohort_conditions(a,batch,module,presentation),g.c.student_id==student_id,g.c.submitted_day.between(start*7,end*7+6)).order_by(g.c.submitted_day)).mappings()]
    weeks=[dict(x) for x in db.execute(select(w.c.week_index,w.c.clicks,w.c.active_days).where(*cohort_conditions(w,batch,module,presentation),w.c.student_id==student_id,w.c.week_index.between(start,end)).order_by(w.c.week_index)).mappings()]
    return {'learner':label_learner(row),'weeks':weeks,'assessments':history,'alias_note':'Fictional display alias; this public dataset contains no original names and is not this login account.'}
