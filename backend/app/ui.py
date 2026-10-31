from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select,and_
from .db import table,get_db,one
from .security import current_user,subject_access,student_access,public_user

router=APIRouter(prefix='/ui',tags=['Frontend data'])

@router.get('/context')
def context(u=Depends(current_user),db=Depends(get_db)):
    names=['departments','courses','sections','subjects','topics','academic_events']
    data={name:[dict(x) for x in db.execute(select(table(name))).mappings()] for name in names}
    pairs=[]
    for subject in data['subjects']:
        for section in data['sections']:
            if section['course_id']!=subject['course_id']:
                continue
            try:
                subject_access(db,u,subject['subject_id'],section['section_id'])
                pairs.append({'subject_id':subject['subject_id'],'section_id':section['section_id']})
            except HTTPException as e:
                if e.status_code!=403:
                    raise
    data['scopes']=pairs
    data['user']=public_user(u)
    return data

@router.get('/attempts')
def attempts(subject_id:int,section_id:int,u=Depends(current_user),db=Depends(get_db)):
    subject_access(db,u,subject_id,section_id)
    a,t,us=table('test_attempts'),table('tests'),table('users')
    stmt=select(a,t.c.title,us.c.full_name).join(t,a.c.test_id==t.c.test_id).join(us,us.c.user_id==a.c.student_id).where(t.c.subject_id==subject_id,t.c.section_id==section_id)
    if u['role']=='STUDENT':
        stmt=stmt.where(a.c.student_id==u['user_id'])
    return [dict(x) for x in db.execute(stmt.order_by(a.c.attempt_id.desc()).limit(200)).mappings()]

@router.get('/attendance')
def attendance(subject_id:int,section_id:int,u=Depends(current_user),db=Depends(get_db)):
    subject_access(db,u,subject_id,section_id)
    cs,ar,us=table('class_sessions'),table('attendance_records'),table('users')
    stmt=select(cs.c.session_id,cs.c.session_date,cs.c.starts_at,ar.c.student_id,ar.c.status,us.c.full_name).join(ar,cs.c.session_id==ar.c.session_id).join(us,us.c.user_id==ar.c.student_id).where(cs.c.subject_id==subject_id,cs.c.section_id==section_id)
    if u['role']=='STUDENT':
        stmt=stmt.where(ar.c.student_id==u['user_id'])
    return [dict(x) for x in db.execute(stmt.order_by(cs.c.session_date.desc(),cs.c.session_id.desc()).limit(500)).mappings()]
