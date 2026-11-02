"""Fill missing illustrative peer feedback without replacing saved feedback."""
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.db import engine,metadata,table,add
from scripts.fill_feature_showcase import NOTE

def main():
    metadata.reflect(bind=engine)
    with Session(engine) as db:
        us=table('users');fb=table('staff_feedback')
        staff=list(db.execute(select(us).where(us.c.role.in_(['FACULTY','HOD','ADMIN']),us.c.is_active==True)).mappings())
        count=0
        for target in staff:
            if target['role']=='ADMIN':continue
            for author in staff:
                if author['user_id']==target['user_id']:continue
                if author['role']!='ADMIN' and author['department_id']!=target['department_id']:continue
                if db.scalar(select(fb.c.feedback_id).where(fb.c.author_id==author['user_id'],fb.c.faculty_id==target['user_id'],fb.c.context_key=='peer')):continue
                add(db,'staff_feedback',author_id=author['user_id'],faculty_id=target['user_id'],context_key='peer',clarity=4,interaction=4,comments='Illustrative peer feedback: communicates lesson objectives and contributes to shared academic planning. '+NOTE)
                count+=1
        db.commit();print({'added_sample_peer_feedback':count})
if __name__=='__main__':main()
