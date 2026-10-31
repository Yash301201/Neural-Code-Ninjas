"""Create four named showcase accounts with random, role-specific passwords.
Existing accounts are never reset. Re-run safely to add missing accounts.
"""
from pathlib import Path
import json,secrets
from sqlalchemy import select
from app.db import engine,metadata,table
from app.security import hasher

def main():
    metadata.reflect(bind=engine)
    output=Path('.local/portal-credentials.json')
    saved=json.loads(output.read_text()) if output.exists() else {}
    spec=[('ADMIN','Portal Administrator','admin@learnpath.dev'),('HOD','Portal HOD','hod@learnpath.dev'),('FACULTY','Portal Faculty','faculty@learnpath.dev'),('STUDENT','Portal Student','student@learnpath.dev')]
    with engine.begin() as c:
        department=c.execute(select(table('departments')).order_by(table('departments').c.department_id)).mappings().first()
        if not department:
            raise SystemExit('Create a department and course/section before preparing portal accounts')
        for role,name,email in spec:
            users=table('users')
            user=c.execute(select(users).where(users.c.email==email)).mappings().first()
            if user and (user['role']!=role):
                raise SystemExit('Email already belongs to a different account; no existing account will be overwritten')
            if not user:
                password=secrets.token_urlsafe(15)
                ident=c.execute(users.insert().values(full_name=name,email=email,password_hash=hasher.hash(password),role=role,department_id=department['department_id'])).inserted_primary_key[0]
                saved[role]={'email':email,'password':password,'user_id':ident}
            else:
                ident=user['user_id']
            if role=='STUDENT':
                en=table('student_enrollments');sections=table('sections');courses=table('courses')
                sec=c.execute(select(sections).join(courses,sections.c.course_id==courses.c.course_id).where(courses.c.department_id==department['department_id'])).mappings().first()
                if sec and not c.execute(select(en).where(en.c.student_id==ident,en.c.section_id==sec['section_id'])).first():
                    c.execute(en.insert().values(student_id=ident,section_id=sec['section_id']))
            if role=='FACULTY':
                subs=table('subjects');sec=table('sections');courses=table('courses');assign=table('faculty_subject_assignments')
                pairs=c.execute(select(subs.c.subject_id,sec.c.section_id).join(courses,subs.c.course_id==courses.c.course_id).join(sec,sec.c.course_id==courses.c.course_id).where(courses.c.department_id==department['department_id'])).all()
                for sid,section_id in pairs:
                    if not c.execute(select(assign).where(assign.c.faculty_id==ident,assign.c.subject_id==sid,assign.c.section_id==section_id)).first():
                        c.execute(assign.insert().values(faculty_id=ident,subject_id=sid,section_id=section_id))
    output.parent.mkdir(exist_ok=True)
    output.write_text(json.dumps(saved,indent=2))
    text='LearnPath AI - integrated portal credentials\nLocal URL: http://127.0.0.1:8001/app/\n\n'
    for role,_,email in spec:
        entry=saved.get(role)
        text+=role+'\nEmail: '+email+'\nPassword: '+(entry['password'] if entry else 'Existing password unchanged; use your saved password')+'\n\n'
    text+='Passwords are stored as Argon2id hashes in MySQL users.password_hash. This local credentials file is private; do not commit it. Existing demo and personal administrator accounts are unchanged.\n'
    Path('.local/portal-logins.txt').write_text(text)
    print('Four role accounts prepared; credentials saved to backend/.local/portal-logins.txt. No passwords printed.')
if __name__=='__main__':
    main()
