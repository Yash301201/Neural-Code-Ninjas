"""Update only synthetic engineering examples. Run explicitly after a backup."""
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.db import engine,metadata,table
from app.engineering_seed import refine

def main():
    metadata.reflect(bind=engine)
    with Session(engine) as db:
        us=table('users');u=db.execute(select(us).where(us.c.role=='ADMIN',us.c.is_active==True).order_by(us.c.user_id)).mappings().first()
        if not u:raise SystemExit('Administrator required')
        result=refine(db,dict(u));db.commit()
    print(result)
if __name__=='__main__':main()
