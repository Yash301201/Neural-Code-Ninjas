"""Role-scoped, live engineering-college dataset. No password or JWT columns."""
from collections import defaultdict
from fastapi import APIRouter,Depends
from sqlalchemy import select,and_,func
from .db import table,get_db
from .security import current_user
from .ui import context
router=APIRouter(prefix='/college-data',tags=['Engineering college dataset'])

def college_dataset(u,db):
    scope=context(u,db);pairs={(s['subject_id'],s['section_id']) for s in scope['scopes']}
    users,en,sec,sub,course,dept,fa=[table(n) for n in ['users','student_enrollments','sections','subjects','courses','departments','faculty_subject_assignments']]
    registry={r['user_id']:dict(r) for r in db.execute(select(users.c.user_id,users.c.full_name,users.c.email,users.c.role,users.c.department_id,users.c.registration_number,users.c.is_active)).mappings()}
    levels={c['course_id']:c.get('program_level','UNCLASSIFIED') for c in scope['courses']}
    all_mappings=[dict(r) for r in db.execute(select(fa)).mappings() if (r['subject_id'],r['section_id']) in pairs]
    mappings=defaultdict(list)
    for m in all_mappings:mappings[(m['subject_id'],m['section_id'])].append(registry[m['faculty_id']])
    heads=defaultdict(list)
    for p in registry.values():
        if p['role']=='HOD' and p['is_active']:heads[p['department_id']].append(p)
    from .academics import year_maps
    cohort_years=year_maps(db)[0]
    records=[]
    q=select(en.c.student_id,en.c.section_id,sec.c.section_name,sec.c.academic_year,sub.c.subject_id,sub.c.subject_name,sub.c.subject_code,sub.c.semester,course.c.course_id,course.c.course_name,dept.c.department_id,dept.c.department_name).select_from(en.join(sec,sec.c.section_id==en.c.section_id).join(sub,sub.c.course_id==sec.c.course_id).join(course,course.c.course_id==sec.c.course_id).join(dept,dept.c.department_id==course.c.department_id)).where(en.c.status=='ACTIVE')
    for row in db.execute(q).mappings():
        if (row['subject_id'],row['section_id']) not in pairs:continue
        if u['role']=='STUDENT' and row['student_id']!=u['user_id']:continue
        person=registry[row['student_id']]
        records.append({**dict(row),'study_year':cohort_years.get(row['section_id']),'student_name':person['full_name'],'student_email':person['email'],'registration_number':person['registration_number'],'program_level':levels.get(row['course_id'],'UNCLASSIFIED'),'synthetic':person['email'].endswith('@demo.learnpath.dev'),'faculty':mappings[(row['subject_id'],row['section_id'])],'hods':heads[row['department_id']]})
    student_ids={r['student_id'] for r in records}
    attempts,tests,tq=table('test_attempts'),table('tests'),table('test_questions')
    possible=select(tq.c.test_id,func.sum(tq.c.marks).label('maximum')).group_by(tq.c.test_id).subquery()
    scores={}
    for r in db.execute(select(attempts.c.student_id,tests.c.subject_id,tests.c.section_id,func.count().label('exam_attempts'),func.sum(attempts.c.score).label('earned'),func.sum(possible.c.maximum).label('possible')).join(tests,tests.c.test_id==attempts.c.test_id).join(possible,possible.c.test_id==tests.c.test_id).where(attempts.c.student_id.in_(student_ids),attempts.c.status=='EVALUATED').group_by(attempts.c.student_id,tests.c.subject_id,tests.c.section_id)).mappings():scores[(r['student_id'],r['subject_id'],r['section_id'])]=dict(r)
    ar,cs=table('attendance_records'),table('class_sessions');attendance=defaultdict(list)
    for r in db.execute(select(ar.c.student_id,ar.c.status,cs.c.subject_id,cs.c.section_id).join(cs,cs.c.session_id==ar.c.session_id).where(ar.c.student_id.in_(student_ids))).mappings():attendance[(r['student_id'],r['subject_id'],r['section_id'])].append(r['status'])
    ass,su=table('assignments'),table('submissions');counts=defaultdict(int);submitted=defaultdict(int)
    for r in db.execute(select(ass.c.subject_id,ass.c.section_id,func.count().label('n')).group_by(ass.c.subject_id,ass.c.section_id)).mappings():counts[(r['subject_id'],r['section_id'])]=r['n']
    for r in db.execute(select(su.c.student_id,ass.c.subject_id,ass.c.section_id,func.count().label('n')).join(ass,ass.c.assignment_id==su.c.assignment_id).where(su.c.student_id.in_(student_ids)).group_by(su.c.student_id,ass.c.subject_id,ass.c.section_id)).mappings():submitted[(r['student_id'],r['subject_id'],r['section_id'])]=r['n']
    for r in records:
        key=(r['student_id'],r['subject_id'],r['section_id']);score=scores.get(key,{});statuses=attendance[key];total=len(statuses);present=sum(s in ['PRESENT','LATE'] for s in statuses)
        r.update(exam_attempts=score.get('exam_attempts',0),exam_percentage=round(100*float(score['earned'])/float(score['possible']),2) if score.get('possible') else None,classes_recorded=total,classes_attended=present,classes_absent=statuses.count('ABSENT'),attendance_percentage=round(100*present/total,2) if total else None,assignments_total=counts[(r['subject_id'],r['section_id'])],assignments_submitted=submitted[key])
    faculty_ids={p['user_id'] for r in records for p in r['faculty']};head_ids={p['user_id'] for r in records for p in r['hods']}
    if u['role']=='ADMIN':faculty_ids.update(p['user_id'] for p in registry.values() if p['role']=='FACULTY');head_ids.update(p['user_id'] for p in registry.values() if p['role']=='HOD')
    elif u['role']=='HOD':faculty_ids.update(p['user_id'] for p in registry.values() if p['role']=='FACULTY' and p['department_id']==u['department_id']);head_ids.add(u['user_id'])
    elif u['role']=='FACULTY':faculty_ids={u['user_id']}
    faculty=[{**registry[ident],'teaching_mappings':sum(m['faculty_id']==ident for m in all_mappings)} for ident in sorted(faculty_ids)]
    hods=[{**registry[ident],'managed_students':len({r['student_id'] for r in records if r['department_id']==registry[ident]['department_id']}),'managed_faculty':sum(f['department_id']==registry[ident]['department_id'] for f in faculty)} for ident in sorted(head_ids)]
    return {'source':{'name':'LearnPathAI engineering-college records','kind':'Live relational MySQL records with clearly labeled synthetic showcase rows','description':'Named students, engineering/computing subjects, faculty teaching mappings and department HOD accounts. Synthetic records are generated locally, not an external Kaggle study.','scope':u['role'],'research_note':'OULAD remains separate research data; its module codes, grades and identities are not used as college identities.'},'records':records,'students':[registry[i] for i in sorted(student_ids)],'faculty':faculty,'hods':hods,'counts':{'students':len(student_ids),'faculty':len(faculty),'hods':len(hods),'subjects':len({r['subject_id'] for r in records}),'student_subject_records':len(records),'synthetic_students':len({r['student_id'] for r in records if r['synthetic']})}}

@router.get('')
def dataset(u=Depends(current_user),db=Depends(get_db)):return college_dataset(u,db)


@router.get('/catalog')
def academic_catalog(u=Depends(current_user),db=Depends(get_db)):
    from fastapi import HTTPException
    if u['role']!='ADMIN':raise HTTPException(403,'Administrator required')
    us=table('users');sample=us.c.email.endswith('@demo.learnpath.dev')
    counts={role.lower():db.scalar(select(func.count()).select_from(us).where(sample,us.c.role==role)) for role in ['STUDENT','FACULTY','HOD']}
    courses,departments,programs,sections,enrollments,fa=[table(n) for n in ['courses','departments','course_programs','sections','student_enrollments','faculty_subject_assignments']]
    rows=[]
    for r in db.execute(select(courses,departments.c.department_name,programs.c.program_level).join(departments,departments.c.department_id==courses.c.department_id).outerjoin(programs,programs.c.course_id==courses.c.course_id).order_by(courses.c.course_id)).mappings():
        row=dict(r);ids=list(db.scalars(select(sections.c.section_id).where(sections.c.course_id==row['course_id'])))
        row['students']=db.scalar(select(func.count(func.distinct(enrollments.c.student_id))).where(enrollments.c.section_id.in_(ids),enrollments.c.status=='ACTIVE'))
        row['faculty']=db.scalar(select(func.count(func.distinct(fa.c.faculty_id))).where(fa.c.section_id.in_(ids)))
        row['subjects']=db.scalar(select(func.count()).select_from(table('subjects')).where(table('subjects').c.course_id==row['course_id']))
        rows.append(row)
    counts.update(courses=len(rows),exams=db.scalar(select(func.count()).select_from(table('tests'))),evaluated_answers=db.scalar(select(func.count()).select_from(table('student_answers'))))
    return {'name':'LearnPath Academic Data Centre','source_kind':'Synthetic prefilled college records with live MySQL persistence','counts':counts,'courses':rows}
