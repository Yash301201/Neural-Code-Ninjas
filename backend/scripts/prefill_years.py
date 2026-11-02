from sqlalchemy import select
from sqlalchemy.orm import Session
from app.db import engine,metadata,table
from app.curriculum_seed import seed

def main():
    metadata.reflect(bind=engine)
    with Session(engine) as db:
        us=table('users');actor=db.execute(select(us).where(us.c.role=='ADMIN',us.c.is_active==True).order_by(us.c.user_id)).mappings().first()
        if not actor:raise SystemExit('Administrator required')
        result=seed(db,dict(actor));db.commit();print(result)
if __name__=='__main__':main()
