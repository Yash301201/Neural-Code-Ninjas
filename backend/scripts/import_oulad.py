"""Import public OULAD CSVs once; retain source and publish only complete batches.

Usage: python -m scripts.import_oulad [--archive data/oulad/raw/oulad.zip]
Kaggle duplicate directory copies are skipped. Full VLE logs are streamed into
weekly aggregates, not loaded into application attendance or user tables.
"""
import argparse,csv,hashlib,io,json,sys,time,zipfile
from collections import defaultdict
from datetime import datetime,timezone
from pathlib import Path
from sqlalchemy import MetaData,Table,select,func
from app.db import engine

ROOT=Path(__file__).resolve().parents[1]
SOURCE='https://www.kaggle.com/datasets/rocki37/open-university-learning-analytics-dataset'
CREDIT='Kuzilek, J., Hlosta, M., & Zdrahal, Z. (2015). OULAD. DOI: 10.24432/C5KK69. CC BY 4.0.'
REQUIRED=['courses.csv','studentInfo.csv','studentRegistration.csv','assessments.csv','studentAssessment.csv','vle.csv','studentVle.csv']

def integer(value):
    return int(value) if value not in ('',None,'?') else None

def csv_members(archive):
    chosen={}
    for name in REQUIRED:
        matches=[i for i in archive.infolist() if Path(i.filename).name==name and not i.is_dir()]
        if not matches:
            raise ValueError('Missing CSV: '+name)
        if len({(i.CRC,i.file_size) for i in matches})!=1:
            raise ValueError('Ambiguous non-identical CSV copies: '+name)
        chosen[name]=min(matches,key=lambda i:(i.filename.count('/'),i.filename)).filename
    return chosen

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--archive',type=Path,default=ROOT/'data/oulad/raw/oulad.zip')
    parser.add_argument('--force',action='store_true',help='Publish a new batch even if this archive is already imported')
    args=parser.parse_args()
    if engine.dialect.name!='mysql':
        raise SystemExit('OULAD importer targets the configured MySQL database')
    with args.archive.open('rb') as source:
        digest=hashlib.file_digest(source,'sha256').hexdigest()
    with zipfile.ZipFile(args.archive) as archive:
        members=csv_members(archive)
        schema='\n'.join(line for line in (ROOT/'db/005_oulad_analytics.sql').read_text().splitlines() if not line.lstrip().startswith('--'))
        with engine.begin() as conn:
            for statement in schema.split(';'):
                if statement.strip() and not statement.strip().upper().startswith('USE '):
                    conn.exec_driver_sql(statement)
        md=MetaData()
        tables={name:Table('oulad_'+name,md,autoload_with=engine) for name in ['imports','courses','students','registrations','assessments','scores','vle_sites','weekly_engagement','weekly_activity']}
        with engine.begin() as conn:
            existing=conn.execute(select(tables['imports']).where(tables['imports'].c.archive_sha256==digest,tables['imports'].c.status=='READY')).mappings().first()
            if existing and not args.force:
                print('Archive already imported as batch',existing['batch_id'],'- no rows changed.');return
            batch=conn.execute(tables['imports'].insert().values(archive_sha256=digest,status='IMPORTING',source_url=SOURCE,attribution=CREDIT)).inserted_primary_key[0]
        counts={};started=time.monotonic()
        def rows(name):
            return csv.DictReader(io.TextIOWrapper(archive.open(members[name]),encoding='utf-8-sig',newline=''))
        def insert(name,records):
            size=0;buffer=[]
            for record in records:
                buffer.append({'batch_id':batch,**record})
                if len(buffer)>=4000:
                    with engine.begin() as conn:conn.execute(tables[name].insert(),buffer)
                    size+=len(buffer);buffer=[]
            if buffer:
                with engine.begin() as conn:conn.execute(tables[name].insert(),buffer)
                size+=len(buffer)
            counts[name]=size
            print(name+': '+str(size)+' imported',flush=True)
        def scope(r):return {'code_module':r['code_module'],'code_presentation':r['code_presentation']}
        try:
            insert('courses',({**scope(r),'length_days':int(r['module_presentation_length'])} for r in rows('courses.csv')))
            enrollments=set()
            def students():
                for r in rows('studentInfo.csv'):
                    enrollments.add((r['code_module'],r['code_presentation'],int(r['id_student'])))
                    yield {**scope(r),'student_id':int(r['id_student']),'previous_attempts':int(r['num_of_prev_attempts']),'studied_credits':int(r['studied_credits']),'final_result':r['final_result']}
            insert('students',students())
            insert('registrations',({**scope(r),'student_id':int(r['id_student']),'registration_day':integer(r['date_registration']),'unregistration_day':integer(r['date_unregistration'])} for r in rows('studentRegistration.csv')))
            insert('assessments',({**scope(r),'assessment_id':int(r['id_assessment']),'assessment_type':r['assessment_type'],'due_day':integer(r['date']),'weight':float(r['weight'])} for r in rows('assessments.csv')))
            insert('scores',({'assessment_id':int(r['id_assessment']),'student_id':int(r['id_student']),'submitted_day':integer(r['date_submitted']),'is_banked':bool(int(r['is_banked'])),'score':float(r['score']) if r['score'] else None} for r in rows('studentAssessment.csv')))
            site_types={}
            def sites():
                for r in rows('vle.csv'):
                    site_types[(r['code_module'],r['code_presentation'],int(r['id_site']))]=r['activity_type']
                    yield {**scope(r),'site_id':int(r['id_site']),'activity_type':r['activity_type'],'week_from':integer(r['week_from']),'week_to':integer(r['week_to'])}
            insert('vle_sites',sites())
            weekly={};activities={};raw_count=0;click_total=0
            for r in rows('studentVle.csv'):
                m,p=r['code_module'],r['code_presentation'];sid=int(r['id_student']);day=int(r['date']);clicks=int(r['sum_click'])
                if clicks<0 or (m,p,sid) not in enrollments:
                    raise ValueError('Invalid VLE activity or missing enrollment reference')
                week=day//7
                key=(m,p,sid,week)
                item=weekly.get(key)
                if item is None:weekly[key]=[clicks,1,1<<(day%7)]
                else:item[0]+=clicks;item[1]+=1;item[2]|=1<<(day%7)
                activity_type=site_types.get((m,p,int(r['id_site'])))
                if activity_type is None:raise ValueError('Activity site missing from vle.csv')
                akey=(m,p,week,activity_type);value=activities.get(akey)
                if value is None:activities[akey]=[clicks,1]
                else:value[0]+=clicks;value[1]+=1
                raw_count+=1;click_total+=clicks
                if raw_count%2000000==0:print('VLE rows streamed:',raw_count,flush=True)
            counts['raw_vle_records']=raw_count;counts['source_clicks']=click_total
            insert('weekly_engagement',({'code_module':m,'code_presentation':p,'student_id':sid,'week_index':week,'clicks':v[0],'log_records':v[1],'active_days':v[2].bit_count()} for (m,p,sid,week),v in weekly.items()))
            del weekly
            insert('weekly_activity',({'code_module':m,'code_presentation':p,'week_index':week,'activity_type':atype,'clicks':v[0],'log_records':v[1]} for (m,p,week,atype),v in activities.items()))
            with engine.begin() as conn:
                agg=conn.execute(select(func.sum(tables['weekly_engagement'].c.clicks),func.sum(tables['weekly_engagement'].c.log_records)).where(tables['weekly_engagement'].c.batch_id==batch)).one()
                if int(agg[0] or 0)!=click_total or int(agg[1] or 0)!=raw_count:
                    raise RuntimeError('Aggregate totals do not match source records')
                counts['distinct_students']=conn.execute(select(func.count(func.distinct(tables['students'].c.student_id))).where(tables['students'].c.batch_id==batch)).scalar_one()
                conn.execute(tables['imports'].update().where(tables['imports'].c.batch_id==batch).values(status='READY',completed_at=datetime.now(timezone.utc).replace(tzinfo=None),row_counts=counts))
            manifest={'batch_id':batch,'source_url':SOURCE,'license':'CC BY 4.0','attribution':CREDIT,'archive_sha256':digest,'csv_members':members,'counts':counts,'transformations':['Duplicate CSV archive copies skipped','Only academic outcome/credits fields retained from studentInfo','VLE logs aggregated by learner/course/presentation/week','Source identities are not login accounts']}
            (ROOT/'data/oulad/manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
            print('READY batch',batch,'in',round(time.monotonic()-started,1),'seconds.',flush=True)
        except Exception as error:
            with engine.begin() as conn:conn.execute(tables['imports'].update().where(tables['imports'].c.batch_id==batch).values(status='FAILED',error_message=str(error)[:1024]))
            raise

if __name__=='__main__':main()
