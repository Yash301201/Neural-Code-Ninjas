"""Enable login only for the five known fictional seed accounts; never edit other accounts."""
from pathlib import Path
import secrets
from sqlalchemy import select, text
from app.db import engine,metadata,table
from app.security import hasher

def main():
    metadata.reflect(bind=engine)
    users=table('users')
    mappings=[(1,'Demo Administrator','admin.demo@example.com'),(2,'Demo HOD','hod.demo@example.com'),(3,'Demo Faculty','faculty.demo@example.com'),(4,'Aarav Demo Student','aarav.demo@example.com'),(5,'Mira Demo Student','mira.demo@example.com')]
    password=secrets.token_urlsafe(18)
    with engine.begin() as c:
        for ident,name,email in mappings:
            u=c.execute(select(users).where(users.c.user_id==ident)).mappings().first()
            if not u or (u['full_name']!=name and u['email']!=email):
                raise SystemExit('Expected synthetic seed users are missing. No accounts changed; load the fictional sample data first.')
        for ident,name,email in mappings:
            c.execute(users.update().where(users.c.user_id==ident).values(email=email,password_hash=hasher.hash(password)))
    from datetime import datetime,timedelta,timezone,date
    now=datetime.now(timezone.utc).replace(tzinfo=None)
    with engine.begin() as c:
        tests=table('tests')
        title='Arrays & Trees: Practice Sprint'
        if not c.execute(select(tests).where(tests.c.title==title)).first():
            questions=table('questions');topics=table('topics')
            ids=c.execute(select(questions.c.question_id).join(topics,questions.c.topic_id==topics.c.topic_id).where(topics.c.subject_id==1,questions.c.review_status=='APPROVED',questions.c.is_active==True).limit(3)).scalars().all()
            if ids:
                ident=c.execute(tests.insert().values(subject_id=1,section_id=1,created_by=3,title=title,description='A fresh practice round on indexed access, search trees and graph traversal.',duration_minutes=20,max_attempts=5,status='PUBLISHED')).inserted_primary_key[0]
                for i,qid in enumerate(ids,1):
                    c.execute(table('test_questions').insert().values(test_id=ident,question_id=qid,marks=2,question_order=i))
        assignments=table('assignments')
        if not c.execute(select(assignments).where(assignments.c.title=='Explain a Data Structure')).first():
            c.execute(assignments.insert().values(subject_id=1,section_id=1,created_by=3,title='Explain a Data Structure',description='Choose an array or a binary search tree. Explain its structure, give a real-world use case, and compare the complexity of two operations.',due_at=now+timedelta(days=7),max_marks=20))
        events=table('academic_events')
        if not c.execute(select(events).where(events.c.title=='Learning Progress Review')).first():
            c.execute(events.insert().values(title='Learning Progress Review',starts_on=date.today()+timedelta(days=5),ends_on=date.today()+timedelta(days=5),description='Faculty reviews topic-level progress and follows up on personalized study plans.'))
    local=Path('.local');local.mkdir(exist_ok=True)
    (local/'showcase-logins.txt').write_text('LOCAL FICTIONAL SHOWCASE ACCOUNTS\nPassword: '+password+'\n'+'\n'.join(email for _,_,email in mappings)+'\nThese demo accounts are for this localhost showcase only. Disable them before public deployment.\n')
    print('Five fictional showcase logins enabled. Existing personal administrator unchanged.')

if __name__=='__main__':
    main()
