from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select,and_
from .db import table,get_db,one,metadata
from .security import current_user,subject_access,student_access,public_user

router=APIRouter(prefix='/ui',tags=['Frontend data'])

@router.get('/context')
def context(u=Depends(current_user),db=Depends(get_db)):
    names=['departments','courses','sections','subjects','topics','academic_events']
    data={name:[dict(x) for x in db.execute(select(table(name))).mappings()] for name in names}
    levels={r['course_id']:r['program_level'] for r in db.execute(select(table('course_programs'))).mappings()} if 'course_programs' in metadata.tables else {}
    for course in data['courses']:course['program_level']=levels.get(course['course_id'],'UNCLASSIFIED')
    for subject in data['subjects']:
        subject['program_level']=levels.get(subject['course_id'],'UNCLASSIFIED')
    from .academics import year_maps
    years,curriculum=year_maps(db)
    for section in data['sections']:section['study_year']=years.get(section['section_id'])
    for subject in data['subjects']:subject.update(curriculum.get(subject['subject_id'],{'study_year':None}))
    course_dept={c['course_id']:c['department_id'] for c in data['courses']}
    role=u['role'];allowed_sections=set();allowed_pairs=set()
    if role=='STUDENT':
        en=table('student_enrollments');allowed_sections=set(db.scalars(select(en.c.section_id).where(en.c.student_id==u['user_id'],en.c.status=='ACTIVE')))
    if role=='FACULTY':
        fa=table('faculty_subject_assignments');allowed_pairs={(r[0],r[1]) for r in db.execute(select(fa.c.subject_id,fa.c.section_id).where(fa.c.faculty_id==u['user_id']))}
    pairs=[]
    for subject in data['subjects']:
        for section in data['sections']:
            if section['course_id']!=subject['course_id']:continue
            expected=subject.get('study_year')
            if expected is not None and section.get('study_year')!=expected:continue
            permitted=role=='ADMIN' or role=='HOD' and course_dept[subject['course_id']]==u['department_id'] or role=='FACULTY' and (subject['subject_id'],section['section_id']) in allowed_pairs or role=='STUDENT' and section['section_id'] in allowed_sections
            if permitted:pairs.append({'subject_id':subject['subject_id'],'section_id':section['section_id']})
    if u['email'].endswith('@demo.learnpath.dev'):
        demo_subjects={s['subject_id'] for s in data['subjects'] if (s.get('subject_code') or '').startswith(('DEMO-','LP-'))}
        en,us=table('student_enrollments'),table('users')
        demo_sections=set(db.scalars(select(en.c.section_id).join(us,us.c.user_id==en.c.student_id).where(us.c.email.endswith('@demo.learnpath.dev'),en.c.status=='ACTIVE')))
        pairs.sort(key=lambda pair:(pair['subject_id'] not in demo_subjects,pair['section_id'] not in demo_sections,pair['subject_id'],pair['section_id']))
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
