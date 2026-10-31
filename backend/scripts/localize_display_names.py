"""Rename only known fictional seed display names. Never touch credentials."""
from sqlalchemy import select
from app.db import engine,metadata,table

RENAMES={
 'aarav.demo@example.com':('Aarav Demo Student','Kondapalli Sai Teja'),
 'mira.demo@example.com':('Mira Demo Student','Penumaka Sravani'),
 'student@learnpath.dev':('Portal Student','Duvvuri Venkata Sai'),
 'faculty.demo@example.com':('Demo Faculty','Dr. K. V. Srinivas'),
 'faculty@learnpath.dev':('Portal Faculty','Dr. N. Lakshmi Prasad'),
}

def main():
    metadata.reflect(bind=engine);users=table('users');changed=0
    with engine.begin() as c:
        before=[tuple(r) for r in c.execute(select(users.c.user_id,users.c.email,users.c.password_hash,users.c.role,users.c.department_id).order_by(users.c.user_id))]
        for email,(old,new) in RENAMES.items():
            row=c.execute(select(users).where(users.c.email==email)).mappings().first()
            if row and row['role'] in ('STUDENT','FACULTY') and row['full_name']==old:
                c.execute(users.update().where(users.c.user_id==row['user_id']).values(full_name=new));changed+=1
        after=[tuple(r) for r in c.execute(select(users.c.user_id,users.c.email,users.c.password_hash,users.c.role,users.c.department_id).order_by(users.c.user_id))]
        if before!=after:raise RuntimeError('Credential/identity invariant failed; rolling back')
    print('Updated',changed,'fictional display names. All IDs, emails, password hashes, roles and departments unchanged.')

if __name__=='__main__':main()
