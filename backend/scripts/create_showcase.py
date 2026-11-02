"""Create labeled fictional showcase records using an existing administrator."""
import argparse,json
from pathlib import Path
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.db import engine,metadata,table
from app.showcase_seed import seed

def main():
    p=argparse.ArgumentParser();p.add_argument('--per-major',action='store_true');args=p.parse_args()
    metadata.reflect(bind=engine)
    with Session(engine) as db:
        users=table('users');admin=db.execute(select(users).where(users.c.role=='ADMIN',users.c.is_active==True).order_by(users.c.user_id)).mappings().first()
        if not admin:raise SystemExit('Create an administrator first')
        result=seed(db,dict(admin),args.per_major);db.commit()
    target=Path(__file__).resolve().parents[1]/'.local/showcase-summary.json';target.parent.mkdir(exist_ok=True);target.write_text(json.dumps(result,indent=2))
    print(json.dumps(result,indent=2))
if __name__=='__main__':main()
