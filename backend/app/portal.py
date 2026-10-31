from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, func
from .db import table, get_db, one, update
from .security import current_user, public_user, subject_access, roles, hasher
from .analytics import metrics
from .ui import context
from .schemas import Input
from pydantic import Field
from .config import settings

router=APIRouter(prefix='/portal',tags=['Integrated React portal'])

@router.get('/workspace')
def workspace(u=Depends(current_user),db=Depends(get_db)):
    data=context(u,db)
    pairs={(x['subject_id'],x['section_id']) for x in data['scopes']}
    subjects={x[0] for x in pairs}
    sections={x[1] for x in pairs}
    users=table('users');en=table('student_enrollments');fa=table('faculty_subject_assignments')
    if u['role']=='ADMIN':
        people=db.execute(select(users)).mappings().all()
    elif u['role']=='HOD':
        people=db.execute(select(users).where(users.c.department_id==u['department_id'])).mappings().all()
    elif u['role']=='FACULTY':
        ids=select(en.c.student_id).where(en.c.section_id.in_(sections),en.c.status=='ACTIVE')
        people=db.execute(select(users).where((users.c.user_id.in_(ids))|(users.c.user_id==u['user_id']))).mappings().all()
    else:
        people=[u]
    data['people']=[public_user(dict(x)) for x in people]
    def records(name,condition=None):
        stmt=select(table(name))
        if condition is not None:
            stmt=stmt.where(condition)
        return [dict(x) for x in db.execute(stmt).mappings()]
    data['enrollments']=records('student_enrollments',en.c.section_id.in_(sections)) if u['role']!='STUDENT' else records('student_enrollments',en.c.student_id==u['user_id'])
    data['faculty_assignments']=records('faculty_subject_assignments',fa.c.section_id.in_(sections)) if u['role']!='STUDENT' else []
    data['metrics']=[]
    for person in data['people']:
        if person['role']!='STUDENT':
            continue
        for sid in subjects:
            subject=next(x for x in data['subjects'] if x['subject_id']==sid)
            eligible=[e for e in data['enrollments'] if e['student_id']==person['user_id'] and e['status']=='ACTIVE' and any(sec['section_id']==e['section_id'] and sec['course_id']==subject['course_id'] for sec in data['sections'])]
            if not eligible:
                continue
            if not any((sid,e['section_id']) in pairs for e in eligible):
                continue
            data['metrics'].append({'student_id':person['user_id'],'subject_id':sid,**metrics(db,person['user_id'],sid)})
    te=table('tests')
    data['tests']=[t for t in records('tests') if (t['subject_id'],t['section_id']) in pairs and (u['role']!='STUDENT' or t['status']=='PUBLISHED')]
    tq=table('test_questions')
    for t in data['tests']:
        totals=db.execute(select(func.count(),func.coalesce(func.sum(tq.c.marks),0)).where(tq.c.test_id==t['test_id'])).one()
        t['question_count']=totals[0];t['max_marks']=totals[1]
    test_ids=[t['test_id'] for t in data['tests']]
    a=table('test_attempts')
    data['attempts']=records('test_attempts',(a.c.test_id.in_(test_ids)) & ((a.c.student_id==u['user_id']) if u['role']=='STUDENT' else True))
    data['assignments']=[a for a in records('assignments') if (a['subject_id'],a['section_id']) in pairs]
    sub=table('submissions');ids=[a['assignment_id'] for a in data['assignments']]
    data['submissions']=records('submissions',(sub.c.assignment_id.in_(ids)) & ((sub.c.student_id==u['user_id']) if u['role']=='STUDENT' else True))
    data['questions']=records('questions',table('questions').c.topic_id.in_([t['topic_id'] for t in data['topics'] if t['subject_id'] in subjects])) if u['role']!='STUDENT' else []
    cs=table('class_sessions');ar=table('attendance_records')
    sessions=[s for s in records('class_sessions') if (s['subject_id'],s['section_id']) in pairs]
    data['sessions']=sessions
    data['attendance']=records('attendance_records',(ar.c.session_id.in_([s['session_id'] for s in sessions])) & ((ar.c.student_id==u['user_id']) if u['role']=='STUDENT' else True))
    plans=table('study_plans')
    allowed_ids=[p['user_id'] for p in data['people'] if p['role']=='STUDENT']
    data['plans']=records('study_plans',(plans.c.student_id.in_(allowed_ids))&(plans.c.subject_id.in_(subjects)))
    data['plan_items']=records('study_plan_items',table('study_plan_items').c.plan_id.in_([p['plan_id'] for p in data['plans']]))
    data['provider_configured']=bool(settings.llm_api_key)
    return data

class ResetPassword(Input):
    password:str=Field(min_length=12,max_length=128)

@router.patch('/users/{ident}/password')
def reset_password(ident:int,body:ResetPassword,u=Depends(roles('ADMIN')),db=Depends(get_db)):
    one(db,'users',ident)
    update(db,'users',ident,password_hash=hasher.hash(body.password))
    return {'detail':'Password updated'}
