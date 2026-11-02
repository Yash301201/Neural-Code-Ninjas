"""Explicit one-time academic catalogue prefill. Existing credentials are preserved."""
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.db import engine,metadata,table
from app.academic_prefill import expand

def main():
    metadata.reflect(bind=engine)
    with Session(engine) as db:
        us=table('users');actor=db.execute(select(us).where(us.c.role=='ADMIN',us.c.is_active==True).order_by(us.c.user_id)).mappings().first()
        if not actor:raise SystemExit('An administrator is required')
        result=expand(db,dict(actor));db.commit();print(result)
if __name__=='__main__':main()
