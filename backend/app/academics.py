"""Study-year metadata, scoped curriculum and faculty topic coverage."""
from datetime import datetime,timezone
from fastapi import APIRouter,Depends,HTTPException
from sqlalchemy import select
from pydantic import Field
from .db import table,get_db,one,update
from .security import current_user,roles,subject_access
from .schemas import Input
from .campus import audit
router=APIRouter(prefix='/academics',tags=['Academic years and curriculum'])

def year_maps(db):
    from .db import metadata
    if 'section_study_years' not in metadata.tables:return {},{}
    return ({r['section_id']:r['study_year'] for r in db.execute(select(table('section_study_years'))).mappings()},{r['subject_id']:dict(r) for r in db.execute(select(table('subject_curriculum'))).mappings()})

def overview(u,db):
    us=table('users');people={r['user_id']:dict(r) for r in db.execute(select(us.c.user_id,us.c.full_name,us.c.email,us.c.registration_number,us.c.role,us.c.department_id)).mappings()}
    courses=[dict(r) for r in db.execute(select(table('courses'))).mappings() if u['role']=='ADMIN' or r['department_id']==u['department_id']]
    course_ids={c['course_id'] for c in courses};sections=[dict(r) for r in db.execute(select(table('sections'))).mappings() if r['course_id'] in course_ids]
    sy,cur=year_maps(db);levels={r['course_id']:r['program_level'] for r in db.execute(select(table('course_programs'))).mappings()}
    subjects=[{**dict(r),**cur.get(r['subject_id'],{'study_year':None})} for r in db.execute(select(table('subjects'))).mappings() if r['course_id'] in course_ids]
    subject_ids={s['subject_id'] for s in subjects};section_ids={s['section_id'] for s in sections}
    assignments=[dict(r) for r in db.execute(select(table('faculty_subject_assignments'))).mappings() if r['subject_id'] in subject_ids and r['section_id'] in section_ids]
    if u['role']=='FACULTY':
        assignments=[a for a in assignments if a['faculty_id']==u['user_id']];section_ids={a['section_id'] for a in assignments};subject_ids={a['subject_id'] for a in assignments};sections=[s for s in sections if s['section_id'] in section_ids]
    subjects=[s for s in subjects if s['subject_id'] in subject_ids];course_ids={s['course_id'] for s in sections};courses=[c for c in courses if c['course_id'] in course_ids or u['role']!='FACULTY']
    for c in courses:c['program_level']=levels.get(c['course_id'],'UNCLASSIFIED');c['curriculum_subjects']=sum(s['course_id']==c['course_id'] and s['subject_id'] in cur for s in subjects)
    enrollments=[dict(r) for r in db.execute(select(table('student_enrollments'))).mappings() if r['section_id'] in section_ids and r['status']=='ACTIVE']
    students=[{**people[e['student_id']],**e,'study_year':sy.get(e['section_id'])} for e in enrollments]
    for s in sections:s['study_year']=sy.get(s['section_id']);s['student_count']=len({e['student_id'] for e in enrollments if e['section_id']==s['section_id']})
    topics=[dict(r) for r in db.execute(select(table('topics'))).mappings() if r['subject_id'] in subject_ids]
    progress={(r['faculty_assignment_id'],r['topic_id']):r['status'] for r in db.execute(select(table('teaching_topic_progress'))).mappings()}
    for a in assignments:
        a['faculty_name']=people[a['faculty_id']]['full_name'];a['topics']=[{**t,'status':progress.get((a['faculty_assignment_id'],t['topic_id']),'PLANNED')} for t in topics if t['subject_id']==a['subject_id']]
    return {'courses':courses,'sections':sections,'subjects':subjects,'students':students,'assignments':assignments,'topics':topics,'counts':{'students':len({s['student_id'] for s in students}),'enrollments':len(students),'sections':len(sections),'teaching_assignments':len(assignments)},'note':'Year of study and calendar academic year are separate. Unassigned historical cohorts are not guessed.'}

@router.get('/overview')
def get_overview(u=Depends(roles('ADMIN','HOD','FACULTY')),db=Depends(get_db)):return overview(u,db)

class Coverage(Input):
    status:str=Field(pattern='^(PLANNED|IN_PROGRESS|COMPLETED)$')
@router.put('/teaching/{ident}/topics/{topic_id}')
def coverage(ident:int,topic_id:int,body:Coverage,u=Depends(roles('ADMIN','HOD','FACULTY')),db=Depends(get_db)):
    a=one(db,'faculty_subject_assignments',ident,True)
    if u['role']=='FACULTY' and a['faculty_id']!=u['user_id']:raise HTTPException(403,'Not your teaching assignment')
    subject_access(db,u,a['subject_id'],a['section_id'],write=True)
    if one(db,'topics',topic_id)['subject_id']!=a['subject_id']:raise HTTPException(422,'Topic outside this subject')
    t=table('teaching_topic_progress');cond=(t.c.faculty_assignment_id==ident)&(t.c.topic_id==topic_id);old=db.execute(select(t).where(cond)).mappings().first()
    values={'status':body.status,'updated_by':u['user_id'],'updated_at':datetime.now(timezone.utc).replace(tzinfo=None)}
    if old:db.execute(t.update().where(cond).values(**values))
    else:db.execute(t.insert().values(faculty_assignment_id=ident,topic_id=topic_id,**values))
    course=one(db,'courses',one(db,'subjects',a['subject_id'])['course_id']);audit(db,u,'TOPIC_COVERAGE_UPDATED','teaching',ident,{'status':old['status'] if old else 'PLANNED'},body.model_dump(),'Teaching topic coverage saved',course['department_id'])
    return {'saved':True,**body.model_dump()}

class CohortYear(Input):
    study_year:int=Field(ge=1,le=8)
@router.put('/sections/{ident}/year')
def classify_cohort(ident:int,body:CohortYear,u=Depends(roles('ADMIN','HOD')),db=Depends(get_db)):
    section=one(db,'sections',ident,True);course=one(db,'courses',section['course_id'])
    if u['role']=='HOD' and course['department_id']!=u['department_id']:raise HTTPException(403,'Cohort outside department')
    if not course['duration_years'] or body.study_year>course['duration_years']:raise HTTPException(422,'Year exceeds program duration')
    sy,cur=year_maps(db)
    if sy.get(ident) not in [None,body.study_year]:raise HTTPException(409,'Existing cohort year cannot be overwritten; create a new cohort to preserve history')
    f=table('faculty_subject_assignments');mappings=db.execute(select(f).where(f.c.section_id==ident)).mappings().all()
    if any(a['subject_id'] in cur and cur[a['subject_id']]['study_year']!=body.study_year for a in mappings):raise HTTPException(409,'Existing teaching assignment belongs to a different year')
    t=table('section_study_years')
    if ident not in sy:db.execute(t.insert().values(section_id=ident,study_year=body.study_year))
    audit(db,u,'COHORT_YEAR_CLASSIFIED','section',ident,None,body.model_dump(),'Study year assigned to cohort',course['department_id'])
    return {'section_id':ident,**body.model_dump()}
