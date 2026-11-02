"""Export only synthetic demo college rows; password hashes and JWTs are excluded."""
import csv,json,hashlib
from pathlib import Path
from datetime import datetime,timezone
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.db import engine,metadata,table
from app.college_data import college_dataset

def main():
    metadata.reflect(bind=engine)
    with Session(engine) as db:
        us=table('users');u=db.execute(select(us).where(us.c.role=='ADMIN',us.c.is_active==True).order_by(us.c.user_id)).mappings().first()
        data=college_dataset(dict(u),db)
        from app.academics import overview
        academic=overview(dict(u),db)
        evidence_table=table('staff_evidence');people=table('users')
        staff_evidence=[dict(r) for r in db.execute(select(evidence_table).join(people,people.c.user_id==evidence_table.c.owner_id).where(people.c.email.endswith('@demo.learnpath.dev'))).mappings()]
        admins=[dict(r) for r in db.execute(select(people.c.user_id,people.c.full_name,people.c.email,people.c.role,people.c.is_active).where(people.c.role=='ADMIN',people.c.email.endswith('@demo.learnpath.dev'))).mappings()]

    target=Path(__file__).resolve().parents[1]/'data/engineering';target.mkdir(parents=True,exist_ok=True)
    demo=lambda p:p['email'].endswith('@demo.learnpath.dev')
    students=[p for p in data['students'] if demo(p)];faculty=[p for p in data['faculty'] if demo(p)];hods=[p for p in data['hods'] if demo(p)]
    records=[];teaching={};subjects={}
    for r in data['records']:
        if not r['synthetic'] or not (r.get('subject_code') or '').startswith(('DEMO-','LP-')):continue
        fs=[f for f in r['faculty'] if demo(f)];hs=[h for h in r['hods'] if demo(h)]
        records.append({k:v for k,v in r.items() if k not in ['faculty','hods']}|{'faculty_ids':';'.join(str(f['user_id']) for f in fs),'hod_ids':';'.join(str(h['user_id']) for h in hs)})
        subjects[r['subject_id']]={k:r[k] for k in ['subject_id','subject_name','subject_code','study_year','semester','course_id','course_name','program_level','department_id','department_name']}
        for f in fs:teaching[(f['user_id'],r['subject_id'],r['section_id'])]={'faculty_id':f['user_id'],'faculty_name':f['full_name'],'subject_id':r['subject_id'],'section_id':r['section_id'],'study_year':r['study_year'],'semester':r['semester'],'course_id':r['course_id'],'program_level':r['program_level'],'hod_ids':';'.join(str(h['user_id']) for h in hs)}
    enrollment_rows={}
    for r in records:
        key=(r['student_id'],r['section_id'])
        enrollment_rows[key]={k:r[k] for k in ['student_id','section_id','section_name','academic_year','study_year','course_id','course_name','program_level','department_id','department_name']}
    for head in hods:
        head['managed_students']=len({r['student_id'] for r in records if r['department_id']==head['department_id']})
        head['managed_faculty']=sum(f['department_id']==head['department_id'] for f in faculty)
    selected_subjects=set(subjects)
    curriculum=[{**s,'course_name':next(c['course_name'] for c in academic['courses'] if c['course_id']==s['course_id'])} for s in academic['subjects'] if s['subject_id'] in selected_subjects and s.get('study_year')]
    topics=[t for t in academic['topics'] if t['subject_id'] in selected_subjects]
    coverage=[]
    for a in academic['assignments']:
        if a['subject_id'] not in selected_subjects:continue
        for topic in a['topics']:coverage.append({'faculty_assignment_id':a['faculty_assignment_id'],'faculty_id':a['faculty_id'],'faculty_name':a['faculty_name'],'subject_id':a['subject_id'],'section_id':a['section_id'],'topic_id':topic['topic_id'],'topic_name':topic['topic_name'],'status':topic['status']})
    exports={'students':students,'faculty':faculty,'hods':hods,'admins':admins,'staff_evidence':staff_evidence,'enrollments':list(enrollment_rows.values()),'curriculum':curriculum,'topics':topics,'topic_coverage':coverage,'subjects':list(subjects.values()),'teaching_assignments':list(teaching.values()),'student_subject_performance':records}
    manifest={'name':'LearnPath Academic College Dataset','provenance':'Locally generated fictional demo identities and academic records, exported from MySQL. Not a Kaggle/OULAD research dataset.','generated_at':datetime.now(timezone.utc).isoformat(),'passwords_included':False,'counts':{},'files':{}}
    for name,rows in exports.items():
        filename=target/(name+'.csv');heads=list(rows[0]) if rows else ['no_records']
        with filename.open('w',newline='',encoding='utf-8-sig') as f:
            writer=csv.DictWriter(f,fieldnames=heads);writer.writeheader();writer.writerows(rows)
        manifest['counts'][name]=len(rows);manifest['files'][name+'.csv']={'sha256':hashlib.sha256(filename.read_bytes()).hexdigest(),'columns':heads}
    (target/'manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8');print(json.dumps(manifest['counts']))
if __name__=='__main__':main()
