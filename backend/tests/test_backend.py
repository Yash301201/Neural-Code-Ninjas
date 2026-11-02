"""MySQL integration tests. Only target a disposable *_test database."""
import os
from datetime import datetime,timedelta,timezone
from pathlib import Path
import pytest
from sqlalchemy import create_engine,text,select
from sqlalchemy.engine import make_url

url=os.getenv('TEST_DATABASE_URL','')
if not url:
    pytest.skip('Set TEST_DATABASE_URL to a disposable MySQL database ending _test',allow_module_level=True)
parsed=make_url(url)
if parsed.get_backend_name()!='mysql' or not (parsed.database or '').endswith('_test'):
    raise RuntimeError('Tests refuse to modify a database not ending _test')
os.environ['DATABASE_URL']=url
os.environ.setdefault('JWT_SECRET','integration-tests-only-secret-with-48-characters')

from fastapi.testclient import TestClient
from app.db import engine,metadata,table
if engine.url.database != parsed.database or not (engine.url.database or "").endswith("_test"):
    raise RuntimeError("Actual SQLAlchemy engine is not the requested disposable test database; refusing all test operations")
from app.main import app
from app.security import hasher,token

@pytest.fixture(scope='module')
def client():
    source=Path(__file__).resolve().parents[1]/'db'
    from scripts.init_db import statements
    with engine.connect() as c:
        c.exec_driver_sql('SET FOREIGN_KEY_CHECKS=0')
        for view in ['student_subject_dashboard','student_attendance_summary','student_topic_performance']:
            c.exec_driver_sql('DROP VIEW IF EXISTS '+view)
        from sqlalchemy import inspect
        for name in inspect(c).get_table_names():
            c.exec_driver_sql('DROP TABLE `'+name+'`')
        c.exec_driver_sql('SET FOREIGN_KEY_CHECKS=1')
        for filename in ['001_schema.sql','003_calendar.sql','005_oulad_analytics.sql','007_rag_assistant.sql','009_campus_workflows.sql','011_faculty_operations.sql','013_showcase_development.sql','015_year_curriculum.sql']:
            for stmt in statements(source/filename):
                if stmt.upper().startswith(('CREATE DATABASE','USE ')):
                    continue
                c.exec_driver_sql(stmt)
        c.commit()
    with TestClient(app) as c:
        yield c
    with engine.begin() as c:
        c.exec_driver_sql('SET FOREIGN_KEY_CHECKS=0')
        for t in reversed(metadata.sorted_tables):
            c.execute(t.delete())
        c.exec_driver_sql('SET FOREIGN_KEY_CHECKS=1')

@pytest.fixture(scope='module')
def state(client):
    with engine.begin() as db:
        ident=db.execute(table('users').insert().values(full_name='Admin',email='admin@example.com',password_hash=hasher.hash('AdminPassword123!'),role='ADMIN')).inserted_primary_key[0]
    auth={'Authorization':'Bearer '+token({'user_id':ident})}
    def post(path,data,headers=auth):
        r=client.post(path,json=data,headers=headers)
        assert r.status_code in (200,201),r.text
        return r.json()
    department=post('/departments',{'department_name':'Computer Science','department_code':'CS'})
    did=department['department_id']
    course=post('/courses',{'department_id':did,'course_name':'BTech','course_code':'BT','duration_years':4})
    cid=course['course_id']
    section=post('/sections',{'course_id':cid,'academic_year':'2026-2027','section_name':'A'})
    sid=section['section_id']
    othersection=post('/sections',{'course_id':cid,'academic_year':'2026-2027','section_name':'B'})
    subject=post('/subjects',{'course_id':cid,'subject_name':'Data Structures','subject_code':'DS','semester':3})
    sub=subject['subject_id']
    topic=post('/topics',{'subject_id':sub,'topic_name':'Arrays'})
    users={}
    for role in ['FACULTY','HOD','STUDENT']:
        u=post('/users',{'full_name':role,'email':role.lower()+'@example.com','password':'DemoPassword123!','role':role,'department_id':did})
        users[role]=u
    other=post('/users',{'full_name':'Other Student','email':'other@example.com','password':'DemoPassword123!','role':'STUDENT','department_id':did})
    for u,section_id in [(users['STUDENT'],sid),(other,othersection['section_id'])]:
        post('/enrollments',{'student_id':u['user_id'],'section_id':section_id})
    post('/faculty-assignments',{'faculty_id':users['FACULTY']['user_id'],'subject_id':sub,'section_id':sid})
    users['ADMIN']={'user_id':ident}
    headers={k:{'Authorization':'Bearer '+token(v)} for k,v in users.items()}
    headers['OTHER']={'Authorization':'Bearer '+token(other)}
    return dict(post=post,headers=headers,users=users,subject=sub,section=sid,topic=topic['topic_id'],other=other,department=did)

def test_login_and_roles(client,state):
    r=client.post('/auth/login',json={'email':'student@example.com','password':'DemoPassword123!'})
    assert r.status_code==200
    assert client.post('/auth/login',json={'email':'student@example.com','password':'wrong'}).status_code==401
    assert client.get('/users',headers=state['headers']['STUDENT']).status_code==403
    assert client.get('/auth/me',headers=state['headers']['STUDENT']).json().get('password_hash') is None
    assert client.get('/health').json()['database']=='connected'
    assert client.get('/openapi.json').status_code==200

def make_test(state,descriptive=False):
    p=state['post']; h=state['headers']['FACULTY']
    q=p('/questions',{'topic_id':state['topic'],'question_text':'What reads an array index?','question_type':'MCQ','choice_options':['Indexing','Sorting'],'correct_answer':'Indexing'},h)
    qs=[{'question_id':q['question_id'],'marks':2}]
    if descriptive:
        d=p('/questions',{'topic_id':state['topic'],'question_text':'Explain indexing','question_type':'DESCRIPTIVE'},h)
        qs.append({'question_id':d['question_id'],'marks':3})
    t=p('/tests',{'subject_id':state['subject'],'section_id':state['section'],'title':'Weekly test','questions':qs,'max_attempts':1},h)
    assert client_patch(state,t['test_id']).status_code==200
    return t,qs

def client_patch(state,ident):
    # Attached test client is set below for helper reuse.
    return state['client'].patch(f'/tests/{ident}/status',json={'status':'PUBLISHED'},headers=state['headers']['FACULTY'])

def test_objective_workflow_and_isolation(client,state):
    state['client']=client
    t,qs=make_test(state)
    h=state['headers']['STUDENT']; tid=t['test_id']
    assert client.get(f'/tests/{tid}/questions',headers=h).status_code==403
    assert client.post(f'/tests/{tid}/attempts',headers=state['headers']['OTHER']).status_code==403
    a=state['post'](f'/tests/{tid}/attempts',{},h)
    q=client.get(f'/tests/{tid}/questions',headers=h).json()[0]
    assert 'correct_answer' not in q and 'explanation' not in q
    r=state['post'](f"/attempts/{a['attempt_id']}/submit",{'answers':[{'question_id':qs[0]['question_id'],'answer_text':'Indexing'}]},h)
    assert r['status']=='EVALUATED' and float(r['score'])==2
    assert client.post(f"/attempts/{a['attempt_id']}/submit",json={'answers':[]},headers=h).status_code==409
    assert client.post(f'/tests/{tid}/attempts',headers=h).status_code==409
    assert client.get(f"/attempts/{a['attempt_id']}",headers=state['headers']['OTHER']).status_code==403
    assert client.put(f"/questions/{qs[0]['question_id']}",json={'topic_id':state['topic'],'question_text':'Changed','question_type':'MCQ','choice_options':['A','B'],'correct_answer':'A'},headers=state['headers']['FACULTY']).status_code==409

def test_manual_grading(client,state):
    state['client']=client
    t,qs=make_test(state,True)
    h=state['headers']['STUDENT']
    a=state['post'](f"/tests/{t['test_id']}/attempts",{},h)
    r=state['post'](f"/attempts/{a['attempt_id']}/submit",{'answers':[{'question_id':qs[1]['question_id'],'answer_text':'Direct memory lookup'}]},h)
    assert r['status']=='SUBMITTED'
    result=client.get(f"/attempts/{a['attempt_id']}",headers=state['headers']['FACULTY']).json()
    answer=next(x for x in result['answers'] if x['question_id']==qs[1]['question_id'])
    assert client.patch(f"/answers/{answer['answer_id']}/grade",json={'marks':4},headers=state['headers']['FACULTY']).status_code==422
    r=client.patch(f"/answers/{answer['answer_id']}/grade",json={'marks':2.5,'feedback':'Good'},headers=state['headers']['FACULTY'])
    assert r.status_code==200,r.text
    assert r.json()['status']=='EVALUATED' and float(r.json()['score'])==2.5

def test_invalid_answers_and_time_limit(client,state):
    state['client']=client
    t,qs=make_test(state)
    h=state['headers']['STUDENT']
    a=state['post'](f"/tests/{t['test_id']}/attempts",{},h)
    endpoint=f"/attempts/{a['attempt_id']}/submit"
    assert client.post(endpoint,json={'answers':[{'question_id':999999,'answer_text':'x'}]},headers=h).status_code==422
    with engine.begin() as db:
        db.execute(table('test_attempts').update().where(table('test_attempts').c.attempt_id==a['attempt_id']).values(started_at=datetime.now(timezone.utc).replace(tzinfo=None)-timedelta(hours=2)))
    assert client.post(endpoint,json={'answers':[]},headers=h).status_code==409

def test_assignments_attendance_analytics(client,state):
    p=state['post']; faculty=state['headers']['FACULTY']; student=state['headers']['STUDENT']
    common={'subject_id':state['subject'],'section_id':state['section']}
    a=p('/assignments',{**common,'title':'Exercise','due_at':(datetime.now(timezone.utc).replace(tzinfo=None)+timedelta(days=1)).isoformat(),'max_marks':10},faculty)
    s=p(f"/assignments/{a['assignment_id']}/submit",{'answer_text':'My answer'},student)
    assert client.patch(f"/submissions/{s['submission_id']}/grade",json={'marks':11},headers=faculty).status_code==422
    assert client.patch(f"/submissions/{s['submission_id']}/grade",json={'marks':8},headers=faculty).status_code==200
    expired=p('/assignments',{**common,'title':'Expired','due_at':(datetime.now(timezone.utc).replace(tzinfo=None)-timedelta(days=1)).isoformat()},faculty)
    assert client.post(f"/assignments/{expired['assignment_id']}/submit",json={'answer_text':'Late'},headers=student).status_code==409
    p('/attendance',{**common,'topic_id':state['topic'],'session_date':'2026-10-31','starts_at':'10:00:00','records':[{'student_id':state['users']['STUDENT']['user_id'],'status':'PRESENT'}]},faculty)
    sid=state['users']['STUDENT']['user_id']
    m=client.get(f'/students/{sid}/performance',params={'subject_id':state['subject']},headers=student)
    assert m.status_code==200 and m.json()['attendance_percent']==100
    assert client.get(f"/students/{state['other']['user_id']}/performance",params={'subject_id':state['subject']},headers=faculty).status_code==403
    risk=p(f'/students/{sid}/risk?subject_id={state["subject"]}',{},student)
    assert risk['model_version']=='heuristic-v1'
    plan=p('/study-plans',{'student_id':sid,'subject_id':state['subject']},student)
    assert plan['items']
    assert client.patch(f"/study-plan-items/{plan['items'][0]['plan_item_id']}",json={'status':'COMPLETED'},headers=student).status_code==200
    assert client.get('/dashboard',params=common,headers=faculty).json()['student_count']==1
    assert client.get(f"/departments/{state['department']}/learning-gaps",headers=state['headers']['HOD']).status_code==200

def test_genai_missing_key_and_mocked_provider(client,state,monkeypatch):
    import app.ai as ai
    monkeypatch.setattr(ai.settings,'llm_api_key','')
    h=state['headers']['FACULTY']
    assert client.post('/ai/questions',json={'topic_id':state['topic']},headers=h).status_code==503
    monkeypatch.setattr(ai,'generate',lambda *args:{'questions':[{'question_text':'Array lookup?','question_type':'MCQ','choice_options':['O(1)','O(n)'],'correct_answer':'O(1)','explanation':'Indexed access'}]})
    r=client.post('/ai/questions',json={'topic_id':state['topic'],'count':1},headers=h)
    assert r.status_code==200,r.text
    q=r.json()['questions'][0]
    assert q['review_status']=='PENDING_REVIEW'
    t=client.post('/tests',json={'subject_id':state['subject'],'section_id':state['section'],'title':'Pending question','questions':[{'question_id':q['question_id'],'marks':1}]},headers=h)
    assert t.status_code==422
    assert client.patch(f"/questions/{q['question_id']}/review",json={'review_status':'APPROVED'},headers=h).status_code==200
    monkeypatch.setattr(ai,'generate',lambda *args:{'questions':[{'broken':True}]})
    assert client.post('/ai/questions',json={'topic_id':state['topic'],'count':1},headers=h).status_code==502


def test_frontend_context_and_routes(client,state):
    h=state['headers']['FACULTY']
    context=client.get('/ui/context',headers=h)
    assert context.status_code==200
    assert {'subject_id':state['subject'],'section_id':state['section']} in context.json()['scopes']
    assert 'password_hash' not in context.json()['user']
    assert 'students' not in context.json()
    params={'subject_id':state['subject'],'section_id':state['section']}
    for route in ['/ui/attempts','/ui/attendance']:
        response=client.get(route,params=params,headers=state['headers']['STUDENT'])
        assert response.status_code==200
        assert all(r['student_id']==state['users']['STUDENT']['user_id'] for r in response.json())
        assert client.get(route,params=params,headers=state['headers']['OTHER']).status_code==403
    assert client.get('/ui/context').status_code in (401,403)
    assert client.get('/app').status_code==200
    assert 'LearnPath AI' in client.get('/app').text
    assert client.get('/assets/app.js').status_code==200
    assert client.get('/assets/styles.css').status_code==200

def test_expired_attempt_can_use_next_allowed_attempt(client,state):
    state['client']=client
    t,qs=make_test(state)
    with engine.begin() as db:
        db.execute(table('tests').update().where(table('tests').c.test_id==t['test_id']).values(max_attempts=2))
    h=state['headers']['STUDENT']
    first=state['post'](f"/tests/{t['test_id']}/attempts",{},h)
    with engine.begin() as db:
        db.execute(table('test_attempts').update().where(table('test_attempts').c.attempt_id==first['attempt_id']).values(started_at=datetime.now(timezone.utc).replace(tzinfo=None)-timedelta(hours=2)))
    second=state['post'](f"/tests/{t['test_id']}/attempts",{},h)
    assert second['attempt_number']==2
    assert second['attempt_id']!=first['attempt_id']
    old=client.get(f"/attempts/{first['attempt_id']}",headers=h).json()
    assert old['status']=='CANCELLED'


def test_react_portal_scope_and_password_protection(client,state):
    student=state['headers']['STUDENT']
    faculty=state['headers']['FACULTY']
    response=client.get('/api/portal/workspace',headers=student)
    assert response.status_code==200,response.text
    data=response.json()
    sid=state['users']['STUDENT']['user_id']
    assert data['user']['user_id']==sid
    assert [p['user_id'] for p in data['people']]==[sid]
    assert data['questions']==[]
    assert all(x['student_id']==sid for x in data['metrics'])
    assert all(x['student_id']==sid for x in data['attempts'])
    assert all(x['student_id']==sid for x in data['attendance'])
    assert all('password_hash' not in p for p in data['people'])
    staff=client.get('/api/portal/workspace',headers=faculty)
    assert staff.status_code==200
    assert state['other']['user_id'] not in [p['user_id'] for p in staff.json()['people']]
    denied=client.patch(f'/api/portal/users/{sid}/password',headers=student,json={'password':'NewStudentPassword123!'})
    assert denied.status_code==403
    assert client.get('/api/portal/workspace').status_code in (401,403)
    bad=client.post('/api/auth/login',json={'email':'student@example.com','password':'IncorrectPassword123!'})
    assert bad.status_code==401
    assert client.get('/app/login').status_code==200
    assert client.get('/app/student/performance').status_code==200


def test_oulad_public_research_analytics(client,state):
    from scripts.init_db import statements
    from app.dataset_analytics import private_metadata
    with engine.begin() as c:
        for stmt in statements(Path(__file__).resolve().parents[1]/'db/005_oulad_analytics.sql'):
            if not stmt.upper().startswith('USE '):
                c.exec_driver_sql(stmt)
    metadata.reflect(bind=engine)
    private_metadata.clear()
    with engine.begin() as c:
        batch=c.execute(table('oulad_imports').insert().values(archive_sha256='a'*64,status='READY',source_url='https://example.test/oulad',attribution='Synthetic integration fixture',row_counts={'students':2,'raw_vle_records':3})).inserted_primary_key[0]
        course={'batch_id':batch,'code_module':'AAA','code_presentation':'2013J'}
        c.execute(table('oulad_courses').insert().values(**course,length_days=70))
        c.execute(table('oulad_students').insert(),[{**course,'student_id':901,'previous_attempts':0,'studied_credits':60,'final_result':'Pass'},{**course,'student_id':902,'previous_attempts':0,'studied_credits':60,'final_result':'Fail'}])
        c.execute(table('oulad_assessments').insert(),[{**course,'assessment_id':501,'assessment_type':'TMA','due_day':6,'weight':50},{**course,'assessment_id':502,'assessment_type':'TMA','due_day':13,'weight':50}])
        c.execute(table('oulad_scores').insert(),[{'batch_id':batch,'assessment_id':501,'student_id':901,'submitted_day':3,'is_banked':False,'score':100},{'batch_id':batch,'assessment_id':502,'student_id':901,'submitted_day':8,'is_banked':True,'score':20},{'batch_id':batch,'assessment_id':501,'student_id':902,'submitted_day':8,'is_banked':False,'score':None}])
        c.execute(table('oulad_weekly_engagement').insert(),[{**course,'student_id':901,'week_index':0,'clicks':12,'log_records':1,'active_days':2},{**course,'student_id':901,'week_index':1,'clicks':8,'log_records':1,'active_days':1},{**course,'student_id':902,'week_index':1,'clicks':0,'log_records':1,'active_days':1}])
        c.execute(table('oulad_weekly_activity').insert(),[{**course,'week_index':0,'activity_type':'forumng','clicks':12,'log_records':1},{**course,'week_index':1,'activity_type':'forumng','clicks':8,'log_records':2}])
    h=state['headers']['STUDENT']
    response=client.get('/api/dataset/oulad/catalog',headers=h)
    assert response.status_code==200,response.text
    assert response.json()['courses'][0]['min_week']==0
    params={'module':'AAA','presentation':'2013J','start_week':0,'end_week':2}
    response=client.get('/api/dataset/oulad/analytics',params=params,headers=h)
    assert response.status_code==200,response.text
    data=response.json()
    assert data['summary']['enrollments']==2
    assert data['summary']['clicks']==20
    assert data['summary']['active_learners']==1
    assert data['summary']['no_activity_learners']==1
    assert data['summary']['mean_score']==100
    assert data['summary']['graded_submissions']==1
    assert data['summary']['historical_pass_rate']==50
    assert data['timeline'][1]['active_learners']==1
    assert data['timeline'][1]['mean_score'] is None
    assert data['timeline'][2]['clicks']==0
    assert data['timeline'][2]['mean_score'] is None
    assert sum(x['value'] for x in data['outcomes'])==2
    assert all(sum(c['clicks'] for c in p['weeks'])==p['clicks'] for p in data['learners'])
    detail=client.get('/api/dataset/oulad/learners/901',params=params,headers=h)
    assert detail.status_code==200
    assert len(detail.json()['assessments'])==2
    assert client.get('/api/dataset/oulad/catalog').status_code in (401,403)
    assert client.get('/api/dataset/oulad/analytics',params={**params,'end_week':-1},headers=h).status_code==422
    assert client.get('/api/dataset/oulad/analytics',params={**params,'module':'ZZZ'},headers=h).status_code==404
    assert client.get('/api/dataset/oulad/learners/9999',params=params,headers=h).status_code==404

def test_oulad_archive_duplicate_copies_not_double_counted():
    import io,zipfile
    from scripts.import_oulad import REQUIRED,csv_members
    data=io.BytesIO()
    with zipfile.ZipFile(data,'w') as z:
        for name in REQUIRED:
            z.writestr(name,'column\nvalue\n')
            z.writestr('nested/'+name,'column\nvalue\n')
    with zipfile.ZipFile(data) as z:
        result=csv_members(z)
        assert len(result)==len(REQUIRED)
        assert all(name==path for name,path in result.items())

def test_oulad_archive_rejects_conflicting_copies():
    import io,zipfile
    from scripts.import_oulad import REQUIRED,csv_members
    data=io.BytesIO()
    with zipfile.ZipFile(data,'w') as z:
        for name in REQUIRED:z.writestr(name,'column\nvalue\n')
        z.writestr('nested/courses.csv','different data')
    with zipfile.ZipFile(data) as z:
        with pytest.raises(ValueError,match='Ambiguous'):
            csv_members(z)

def test_oulad_archive_rejects_missing_required_csv():
    import io,zipfile
    from scripts.import_oulad import csv_members
    data=io.BytesIO()
    with zipfile.ZipFile(data,'w') as z:z.writestr('courses.csv','column\nvalue\n')
    with zipfile.ZipFile(data) as z:
        with pytest.raises(ValueError,match='Missing CSV'):
            csv_members(z)


def test_rag_rank_and_citations():
    from app.rag import rank,synthesize,settings
    from unittest.mock import patch,Mock
    rows=[{'source_key':'a','title':'Engagement','content':'VLE clicks measure online activity'}, {'source_key':'b','title':'Passwords','content':'Argon2id hashes authenticate users'}]
    assert rank('VLE clicks',rows)[0]['source_key']=='a'
    assert rank('zxyunrelated',rows)==[]
    with patch.object(settings,'llm_api_key','test-only'):
        response=Mock();response.json.return_value={'choices':[{'message':{'content':'Claim [S99]'}}]}
        with patch('app.rag.httpx.Client') as factory:
            factory.return_value.__enter__.return_value.post.return_value=response
            answer,reason=synthesize('question',[{'id':'S1','excerpt':'Evidence'}])
            assert answer is None and reason=='invalid_citations'
            response.json.return_value={'choices':[{'message':{'content':'Evidence [S1]'}}]}
            assert synthesize('question',[{'id':'S1','excerpt':'Evidence'}])[0]=='Evidence [S1]'

def test_rag_mysql_history_scope_and_fallback(client,state):
    from app.rag import tables,settings
    from unittest.mock import patch
    chunks=tables()['rag_chunks']
    with engine.begin() as db:
        db.execute(chunks.insert().values(source_key='test-evidence',title='OULAD VLE engagement',content='VLE clicks describe online engagement, not classroom attendance.',source_kind='GUIDE',content_sha256='a'*64))
    student=state['headers']['STUDENT'];admin=state['headers']['ADMIN']
    assert client.get('/api/rag/status').status_code in (401,403)
    assert client.post('/api/rag/reindex',headers=student).status_code==403
    with patch.object(settings,'llm_api_key',''):
        response=client.post('/api/rag/ask',headers=student,json={'question':'What are VLE clicks?'})
    assert response.status_code==200,response.text
    data=response.json();ident=data['conversation_id']
    assert data['answer_mode']=='retrieval_only'
    assert data['provider_note']=='missing_key'
    assert data['citations'][0]['id']=='S1'
    assert client.get('/api/rag/conversations/'+str(ident),headers=student).json()[0]['answer']==data['answer']
    assert client.get('/api/rag/conversations/'+str(ident),headers=admin).status_code==404
    assert client.post('/api/rag/ask',headers=admin,json={'question':'VLE clicks','conversation_id':ident}).status_code==404
    result=client.post('/api/rag/ask',headers=student,json={'question':'zzxnonmatching','mode':'retrieve'})
    assert result.json()['answer_mode']=='no_evidence'
    assert client.post('/api/rag/ask',headers=student,json={'question':'VLE clicks','cohort':'bad'}).status_code==422
    assert client.get('/api/rag/status',headers=student).json()['chunks']==1


def test_live_attendance_register_corrections_and_ownership(client,state):
    faculty=state['headers']['FACULTY'];student=state['headers']['STUDENT']
    params=dict(subject_id=state['subject'],section_id=state['section'],session_date='2026-01-03',starts_at='09:20:00')
    assert client.get('/api/campus/attendance/register',params=params,headers=student).status_code==403
    loaded=client.get('/api/campus/attendance/register',params=params,headers=faculty)
    assert loaded.status_code==200,loaded.text
    r=loaded.json();assert r['session_id'] is None and r['version']==0
    sid=state['users']['STUDENT']['user_id'];assert [p['user_id'] for p in r['students']]==[sid]
    body={**params,'session_id':None,'version':0,'records':[{'student_id':sid,'status':'PRESENT'}]}
    saved=client.post('/api/campus/attendance/register',json=body,headers=faculty)
    assert saved.status_code==200,saved.text
    result=saved.json();assert result['version']==1 and result['counts']['PRESENT']==1
    assert client.post('/api/campus/attendance/register',json=body,headers=faculty).status_code==409
    correction={**body,'session_id':result['session_id'],'version':1,'reason':'Corrected roll call after review','records':[{'student_id':sid,'status':'ABSENT'}]}
    fixed=client.post('/api/campus/attendance/register',json=correction,headers=faculty)
    assert fixed.status_code==200,fixed.text
    assert fixed.json()['version']==2
    assert client.post('/api/campus/attendance/register',json=correction,headers=faculty).status_code==409
    invalid={**correction,'version':2,'records':[{'student_id':state['other']['user_id'],'status':'PRESENT'}]}
    assert client.post('/api/campus/attendance/register',json=invalid,headers=faculty).status_code==409
    report=client.get('/api/campus/attendance/report',params={k:v for k,v in params.items() if k in ['subject_id','section_id']},headers=student)
    assert report.status_code==200,report.text
    assert [p['user_id'] for p in report.json()['students']]==[sid]
    assert any(r['session_id']==result['session_id'] and r['status']=='ABSENT' for r in report.json()['history'])
    assert client.get('/api/campus/attendance/report',params={'subject_id':state['subject'],'section_id':state['section']},headers=state['headers']['OTHER']).status_code==403
    assert any(r['action']=='ATTENDANCE_CORRECTED' for r in client.get('/api/campus/audit',headers=state['headers']['HOD']).json())

def test_mcq_exam_schedule_persistence_and_idempotency(client,state):
    import uuid
    q=state['post']('/questions',{'topic_id':state['topic'],'question_text':'Network MCQ for schedule','question_type':'MCQ','choice_options':['Packet','Stone','Tree','Cloud'],'correct_answer':'Packet'})
    first=(datetime.now(timezone.utc)+timedelta(days=2)).replace(tzinfo=None,microsecond=0)
    body={'request_key':str(uuid.uuid4()),'subject_id':state['subject'],'section_id':state['section'],'title':'Daily topic quiz','exam_type':'DAILY','first_start_at':first.isoformat(),'occurrences':3,'duration_minutes':15,'window_minutes':60,'questions':[{'question_id':q['question_id'],'marks':2}]}
    faculty=state['headers']['FACULTY'];student=state['headers']['STUDENT']
    assert client.post('/api/campus/exam-series',json=body,headers=student).status_code==403
    created=client.post('/api/campus/exam-series',json=body,headers=faculty)
    assert created.status_code==201,created.text
    ids=created.json()['test_ids'];assert len(ids)==3
    assert client.post('/api/campus/exam-series',json=body,headers=faculty).json()['test_ids']==ids
    changed={**body,'title':'Another title'}
    assert client.post('/api/campus/exam-series',json=changed,headers=faculty).status_code==409
    rows=client.get('/api/campus/exam-schedules',headers=faculty).json()
    rows=[r for r in rows if r['test_id'] in ids]
    assert len(rows)==3 and all(r['status']=='DRAFT' for r in rows)
    assert datetime.fromisoformat(rows[1]['start_at'])-datetime.fromisoformat(rows[0]['start_at'])==timedelta(days=1)
    assert not any(r['test_id'] in ids for r in client.get('/api/campus/exam-schedules',headers=student).json())
    assert client.patch('/tests/'+str(ids[0])+'/status',json={'status':'PUBLISHED'},headers=faculty).status_code==200
    assert client.post('/tests/'+str(ids[0])+'/attempts',headers=student).status_code==409
    short=state['post']('/questions',{'topic_id':state['topic'],'question_text':'Not an MCQ','question_type':'DESCRIPTIVE'})
    invalid={**body,'request_key':str(uuid.uuid4()),'questions':[{'question_id':short['question_id'],'marks':1}]}
    assert client.post('/api/campus/exam-series',json=invalid,headers=faculty).status_code==422
    invalid={**body,'request_key':str(uuid.uuid4()),'exam_type':'FINAL'}
    assert client.post('/api/campus/exam-series',json=invalid,headers=faculty).status_code==422

def test_department_management_permissions_and_audit(client,state):
    hod=state['headers']['HOD'];student=state['headers']['STUDENT'];faculty=state['headers']['FACULTY']
    assert client.get('/api/campus/management',headers=student).status_code==403
    assert client.get('/api/campus/management',headers=faculty).status_code==403
    directory=client.get('/api/campus/management',headers=hod)
    assert directory.status_code==200,directory.text
    assert all(p['role'] in ['STUDENT','FACULTY'] and p['department_id']==state['department'] and 'password_hash' not in p for p in directory.json()['people'])
    sid=state['users']['STUDENT']['user_id']
    body={'full_name':'Nalluri Sai Teja','registration_number':'CSE-009','is_active':True,'reason':'Department profile corrected'}
    r=client.patch('/api/campus/people/'+str(sid),json=body,headers=hod)
    assert r.status_code==200,r.text
    assert r.json()['full_name']==body['full_name'] and 'password_hash' not in r.json()
    assert client.patch('/api/campus/people/'+str(state['users']['ADMIN']['user_id']),json=body,headers=hod).status_code==403
    mapping={'faculty_id':state['users']['FACULTY']['user_id'],'subject_id':state['subject'],'section_id':state['section']}
    assert client.post('/api/campus/teaching',json=mapping,headers=hod).status_code==201
    assert client.post('/api/campus/teaching',json=mapping,headers=faculty).status_code==403
    audit=client.get('/api/campus/audit',headers=hod).json()
    assert any(r['action']=='PERSON_UPDATED' and r['entity_id']==sid for r in audit)


def test_scheduled_exam_drafts_and_expiry_grade_saved_answers_only(client,state):
    import uuid
    faculty=state['headers']['FACULTY'];student=state['headers']['STUDENT'];other=state['headers']['OTHER']
    q=state['post']('/questions',{'topic_id':state['topic'],'question_text':'Autosave MCQ','question_type':'MCQ','choice_options':['A','B','C','D'],'correct_answer':'A'})
    start=(datetime.now(timezone.utc)-timedelta(minutes=1)).replace(tzinfo=None,microsecond=0)
    body={'request_key':str(uuid.uuid4()),'subject_id':state['subject'],'section_id':state['section'],'title':'Autosave test','exam_type':'FINAL','first_start_at':start.isoformat(),'occurrences':1,'duration_minutes':1,'window_minutes':30,'questions':[{'question_id':q['question_id'],'marks':3}]}
    r=client.post('/api/campus/exam-series',json=body,headers=faculty);assert r.status_code==201,r.text
    ident=r.json()['test_ids'][0]
    assert client.patch('/tests/'+str(ident)+'/status',headers=faculty,json={'status':'PUBLISHED'}).status_code==200
    attempt=client.post('/tests/'+str(ident)+'/attempts',headers=student).json()['attempt_id']
    path='/api/campus/attempts/'+str(attempt)
    assert client.put(path+'/draft',headers=other,json={'question_id':q['question_id'],'answer_text':'A'}).status_code==403
    assert client.put(path+'/draft',headers=student,json={'question_id':q['question_id'],'answer_text':'not an option'}).status_code==422
    saved=client.put(path+'/draft',headers=student,json={'question_id':q['question_id'],'answer_text':'A'})
    assert saved.status_code==200,saved.text
    assert client.get(path+'/draft',headers=student).json()[0]['answer_text']=='A'
    with engine.begin() as db:db.execute(table('test_attempts').update().where(table('test_attempts').c.attempt_id==attempt).values(started_at=datetime.now(timezone.utc).replace(tzinfo=None)-timedelta(minutes=2)))
    assert client.put(path+'/draft',headers=student,json={'question_id':q['question_id'],'answer_text':'B'}).status_code==409
    final=client.post(path+'/finish',headers=student)
    assert final.status_code==200,final.text
    assert final.json()['status']=='EVALUATED' and final.json()['score']==3
    assert client.post(path+'/finish',headers=student).json()['score']==3
    answers=client.get('/attempts/'+str(attempt),headers=student).json()['answers']
    assert len(answers)==1 and answers[0]['answer_text']=='A'


def test_assignment_coverage_real_roster_and_marks(client,state):
    faculty=state['headers']['FACULTY'];student=state['headers']['STUDENT']
    assignment=state['post']('/assignments',{'subject_id':state['subject'],'section_id':state['section'],'title':'Coverage verification','description':'Answer the prompt','due_at':(datetime.now(timezone.utc)+timedelta(days=2)).replace(tzinfo=None).isoformat(),'max_marks':10},faculty)
    path='/api/faculty-ops/assignments/'+str(assignment['assignment_id'])+'/coverage'
    assert client.get(path,headers=student).status_code==403
    r=client.get(path,headers=faculty);assert r.status_code==200,r.text
    assert (r.json()['eligible'],r.json()['submitted'],r.json()['not_submitted'])==(1,0,1)
    sent=client.post('/assignments/'+str(assignment['assignment_id'])+'/submit',headers=student,json={'answer_text':'A real saved response'})
    assert sent.status_code==201,sent.text
    r=client.get(path,headers=faculty).json();assert (r['submitted'],r['not_submitted'],r['awaiting_grading'])==(1,0,1)
    assert [p['user_id'] for p in r['students']]==[state['users']['STUDENT']['user_id']]
    assert client.patch('/submissions/'+str(sent.json()['submission_id'])+'/grade',headers=faculty,json={'marks':8,'feedback':'Reviewed'}).status_code==200
    r=client.get(path,headers=faculty).json();assert r['graded']==1 and r['awaiting_grading']==0
    assert r['students'][0]['submission']['marks_awarded']==8

def test_programs_separate_ug_and_pg_records(client,state):
    faculty=state['headers']['FACULTY'];hod=state['headers']['HOD']
    with engine.connect() as db:cid=db.scalar(select(table('subjects').c.course_id).where(table('subjects').c.subject_id==state['subject']))
    assert client.put('/api/faculty-ops/programs/'+str(cid),headers=faculty,json={'program_level':'UG'}).status_code==403
    assert client.put('/api/faculty-ops/programs/'+str(cid),headers=hod,json={'program_level':'UG'}).status_code==200
    pg=state['post']('/courses',{'department_id':state['department'],'course_name':'M.Tech Research','course_code':'MTR','duration_years':2,'program_level':'PG'})
    section=state['post']('/sections',{'course_id':pg['course_id'],'academic_year':'2026-2027','section_name':'PG-A'})
    subject=state['post']('/subjects',{'course_id':pg['course_id'],'subject_name':'Advanced Networks','subject_code':'PGN','semester':1})
    learner=state['post']('/users',{'full_name':'PG Student','email':'pg-student@example.com','password':'PostgraduatePassword123!','role':'STUDENT','department_id':state['department']})
    state['post']('/enrollments',{'student_id':learner['user_id'],'section_id':section['section_id']})
    state['post']('/faculty-assignments',{'faculty_id':state['users']['FACULTY']['user_id'],'subject_id':subject['subject_id'],'section_id':section['section_id']})
    state['faculty_pg']={'subject':subject['subject_id'],'section':section['section_id'],'student':learner['user_id']}
    ug=client.get('/api/faculty-ops/class-register',params={'subject_id':state['subject'],'section_id':state['section']},headers=faculty)
    postgraduate=client.get('/api/faculty-ops/class-register',params={'subject_id':subject['subject_id'],'section_id':section['section_id']},headers=faculty)
    assert ug.status_code==200,ug.text
    assert postgraduate.status_code==200,postgraduate.text
    assert ug.json()['class']['program_level']=='UG' and postgraduate.json()['class']['program_level']=='PG'
    assert learner['user_id'] not in [p['user_id'] for p in ug.json()['students']]
    assert [p['user_id'] for p in postgraduate.json()['students']]==[learner['user_id']]
    assert client.get('/api/faculty-ops/class-register',params={'subject_id':subject['subject_id'],'section_id':state['section']},headers=faculty).status_code==422
    context=client.get('/api/portal/workspace',headers=faculty).json()
    assert next(c for c in context['courses'] if c['course_id']==pg['course_id'])['program_level']=='PG'

def test_timetable_permissions_overlap_and_adjacent_slots(client,state):
    hod=state['headers']['HOD'];faculty=state['headers']['FACULTY'];student=state['headers']['STUDENT']
    body={'faculty_id':state['users']['FACULTY']['user_id'],'subject_id':state['subject'],'section_id':state['section'],'weekday':0,'starts_at':'09:00','ends_at':'10:00','room':'A101','session_type':'LECTURE'}
    assert client.post('/api/faculty-ops/timetable',headers=faculty,json=body).status_code==403
    created=client.post('/api/faculty-ops/timetable',headers=hod,json=body)
    assert created.status_code==201,created.text
    state['timetable_slot']=created.json()['slot_id']
    assert client.post('/api/faculty-ops/timetable',headers=hod,json={**body,'starts_at':'09:30','ends_at':'10:30'}).status_code==409
    pg=state['faculty_pg']
    assert client.post('/api/faculty-ops/timetable',headers=hod,json={**body,'subject_id':pg['subject'],'section_id':pg['section'],'starts_at':'09:30','ends_at':'10:30'}).status_code==409
    assert client.post('/api/faculty-ops/timetable',headers=hod,json={**body,'subject_id':pg['subject'],'section_id':pg['section'],'starts_at':'10:00','ends_at':'11:00'}).status_code==201
    own=client.get('/api/faculty-ops/timetable',headers=faculty).json()
    assert len(own)==2 and {r['program_level'] for r in own}=={'UG','PG'}
    assert len(client.get('/api/faculty-ops/timetable',headers=student).json())==1

def test_faculty_leave_overlap_approval_privacy_and_history(client,state):
    faculty=state['headers']['FACULTY'];hod=state['headers']['HOD'];student=state['headers']['STUDENT'];admin=state['headers']['ADMIN']
    from datetime import date
    start=date.today()+timedelta(days=(7-date.today().weekday())%7+7)
    body={'start_date':start.isoformat(),'end_date':start.isoformat(),'leave_type':'ACADEMIC','reason':'Attend a faculty development program'}
    assert client.post('/api/faculty-ops/leave',json=body,headers=student).status_code==403
    created=client.post('/api/faculty-ops/leave',json=body,headers=faculty)
    assert created.status_code==201,created.text
    ident=created.json()['leave_id'];path='/api/faculty-ops/leave/'+str(ident)
    assert client.post('/api/faculty-ops/leave',json=body,headers=faculty).status_code==409
    rows=client.get('/api/faculty-ops/leave',headers=faculty).json()
    assert all(r['requester_id']==state['users']['FACULTY']['user_id'] for r in rows)
    assert rows[0]['affected_classes']==2
    assert client.patch(path+'/review',json={'status':'APPROVED','review_note':'Class coverage arranged'},headers=faculty).status_code==403
    decision=client.patch(path+'/review',json={'status':'APPROVED','review_note':'Class coverage arranged'},headers=hod)
    assert decision.status_code==200,decision.text
    assert client.patch(path+'/cancel',headers=faculty).status_code==409
    assert client.patch(path+'/review',json={'status':'REJECTED','review_note':'Changed mind'},headers=admin).status_code==409
    # HOD requests need another authorized reviewer (an admin), never self approval.
    nextday=(start+timedelta(days=1)).isoformat()
    own=client.post('/api/faculty-ops/leave',headers=hod,json={**body,'start_date':nextday,'end_date':nextday})
    assert own.status_code==201,own.text
    assert client.patch('/api/faculty-ops/leave/'+str(own.json()['leave_id'])+'/review',headers=hod,json={'status':'APPROVED','review_note':'Self approval'}).status_code==403
    assert client.patch('/api/faculty-ops/leave/'+str(own.json()['leave_id'])+'/cancel',headers=hod).status_code==200
    assert client.get('/api/faculty-ops/leave',headers=student).status_code==403
    assert client.delete('/api/faculty-ops/timetable/'+str(state['timetable_slot']),headers=hod).status_code==200


def test_admin_directory_and_demo_faculty(client,state):
    admin=state['auth'] if 'auth' in state else None
    # Authenticate from the database fixture without exposing credentials.
    with engine.connect() as db:
        uid=db.scalar(select(table('users').c.user_id).where(table('users').c.role=='ADMIN'))
    admin={'Authorization':'Bearer '+token({'user_id':uid})}
    response=client.post('/api/campus/demo-faculty',headers=admin)
    assert response.status_code==201,response.text
    again=client.post('/api/campus/demo-faculty',headers=admin)
    assert again.json()['created']==0
    data=client.get('/api/campus/management',headers=admin).json()
    demos=[p for p in data['people'] if p['is_demo']]
    assert demos and all(not p['is_active'] and '[DEMO]' in p['full_name'] for p in demos)
    assert all('password_hash' not in p and 'academic_programs' in p for p in data['people'])
    for role in ['FACULTY','STUDENT','HOD']:
        h={'Authorization':'Bearer '+token({'user_id':state['users'][role]['user_id']})}
        assert client.post('/api/campus/demo-faculty',headers=h).status_code==403



def test_professional_evidence_hierarchy_feedback_and_privacy(client,state):
    faculty,hod,student,admin=[state['headers'][r] for r in ['FACULTY','HOD','STUDENT','ADMIN']]
    ident=state['users']['FACULTY']['user_id']
    body={'category':'SKILL','title':'API design practice','details':'Built a classroom API and documented validation.','skill_level':4}
    created=client.post(f'/api/development/staff/{ident}/evidence',json=body,headers=faculty)
    assert created.status_code==201,created.text
    eid=created.json()['evidence_id']
    assert client.get(f'/api/development/staff/{ident}',headers=student).status_code==403
    reviewed=client.patch(f'/api/development/evidence/{eid}/review',json={'status':'VERIFIED','review_note':'Reviewed classroom evidence'},headers=hod)
    assert reviewed.status_code==200,reviewed.text
    assert client.put(f'/api/development/evidence/{eid}',json={**body,'title':'Revised API design practice'},headers=faculty).json()['status']=='SUBMITTED'
    assert client.post(f'/api/development/staff/{ident}/evidence',json={**body,'reference_url':'javascript:alert(1)'},headers=faculty).status_code==422
    own=client.post('/api/development/staff/'+str(state['users']['HOD']['user_id'])+'/evidence',json=body,headers=hod).json()
    assert client.patch('/api/development/evidence/'+str(own['evidence_id'])+'/review',json={'status':'VERIFIED','review_note':'Self review not allowed'},headers=hod).status_code==403
    options=client.get('/api/development/feedback-options',headers=student).json()
    assert options
    choice=options[0]
    feedback={k:choice[k] for k in ['faculty_id','subject_id','section_id']};feedback.update(clarity=4,interaction=5,comments='Constructive classroom feedback')
    assert client.put('/api/development/feedback',json=feedback,headers=student).status_code==200
    profile=client.get('/api/development/staff/'+str(choice['faculty_id']),headers=admin).json()
    assert profile['feedback'][0]['clarity'] is None
    assert all('comments' not in r and 'author_id' not in r for r in profile['feedback'])
    assert client.delete(f'/api/development/evidence/{eid}',headers=faculty).status_code==200
    assert client.put(f'/api/development/evidence/{eid}',json=body,headers=faculty).status_code==409


def test_showcase_seed_is_additive_scoped_and_dataset_reference(client,state):
    # Small public dataset fixture, separate from the generated college records.
    with engine.begin() as db:
        imp=table('oulad_imports')
        batch=db.execute(imp.insert().values(archive_sha256='b'*64,status='READY',source_url='https://example.org/test-only',attribution='OULAD test fixture')).inserted_primary_key[0]
        db.execute(table('oulad_courses').insert().values(batch_id=batch,code_module='BBB',code_presentation='2014J',length_days=240))
        db.execute(table('oulad_assessments').insert().values(batch_id=batch,assessment_id=999,code_module='BBB',code_presentation='2014J',assessment_type='TMA',due_day=20,weight=10))
        db.execute(table('oulad_scores').insert().values(batch_id=batch,assessment_id=999,student_id=777,submitted_day=19,is_banked=False,score=72))
        original={r['user_id']:r['password_hash'] for r in db.execute(select(table('users'))).mappings()}
    admin=state['headers']['ADMIN']
    for role in ['STUDENT','FACULTY','HOD']:
        assert client.post('/api/development/showcase',headers=state['headers'][role],json={'per_major':False}).status_code==403
    r=client.post('/api/development/showcase',headers=admin,json={'per_major':False})
    assert r.status_code==201,r.text
    result=r.json();assert result['students']==50 and result['faculty']==7
    assert client.post('/api/development/showcase',headers=admin,json={'per_major':False}).json()['already_created'] is True
    with engine.connect() as db:
        for uid,password_hash in original.items():
            user=db.execute(select(table('users')).where(table('users').c.user_id==uid)).mappings().one()
            if not user['email'].endswith('@demo.learnpath.dev'):assert user['password_hash']==password_hash
        user=db.execute(select(table('users')).where(table('users').c.email==result['demo_student_email'])).mappings().one();uid=user['user_id']
        en=db.execute(select(table('student_enrollments')).where(table('student_enrollments').c.student_id==uid)).mappings().one();section=en['section_id']
        sec=db.execute(select(table('sections')).where(table('sections').c.section_id==section)).mappings().one()
        sub=db.execute(select(table('subjects')).where(table('subjects').c.course_id==sec['course_id'],table('subjects').c.subject_name.like('[DEMO]%'))).mappings().first()
    login=client.post('/api/auth/login',json={'email':result['demo_student_email'],'password':'DemoLearn2026!'})
    assert login.status_code==200,login.text
    headers={'Authorization':'Bearer '+login.json()['access_token']}
    workspace=client.get('/api/portal/workspace',headers=headers).json()
    first=workspace['scopes'][0]
    assert next(s for s in workspace['subjects'] if s['subject_id']==first['subject_id'])['subject_name'].startswith('[DEMO]')
    assert any(t['status']=='CLOSED' for t in workspace['tests']) and workspace['attempts']
    insights=client.get(f"/api/development/learner-insights?subject_id={sub['subject_id']}&section_id={section}",headers=headers)
    assert insights.status_code==200,insights.text
    assert insights.json()['heatmap'] and insights.json()['reference']['mean_score']==72
    assert client.get(f"/api/development/learner-insights?subject_id={sub['subject_id']}&section_id={section}&student_id={state['users']['STUDENT']['user_id']}",headers=headers).status_code==403



def test_engineering_college_dataset_relationships_and_scope(client,state):
    admin=state['headers']['ADMIN'];response=client.get('/api/college-data',headers=admin)
    assert response.status_code==200,response.text
    dataset=response.json();assert dataset['counts']['synthetic_students']==50
    assert 'password_hash' not in response.text and 'access_token' not in response.text
    demo=[r for r in dataset['records'] if r['synthetic'] and r['subject_name'].startswith('[DEMO]')]
    assert demo and all(r['subject_name'] in ['[DEMO] Database Management Systems','[DEMO] Computer Networks'] for r in demo)
    assert all(r['faculty'] and r['hods'] for r in demo)
    assert any(r['exam_percentage'] is not None for r in demo)
    for role in ['STUDENT','FACULTY','HOD']:
        r=client.get('/api/college-data',headers=state['headers'][role]);assert r.status_code==200,r.text
        records=r.json()['records'];uid=state['users'][role]['user_id']
        if role=='STUDENT':assert all(x['student_id']==uid for x in records)
        if role=='FACULTY':assert all(any(f['user_id']==uid for f in x['faculty']) for x in records)
        if role=='HOD':assert all(x['department_id']==state['users'][role]['department_id'] for x in records)



def test_academic_prefill_course_data_and_plain_display_names(client,state):
    from app.academic_prefill import expand
    from sqlalchemy.orm import Session
    with Session(engine) as db:
        us=table('users');actor=dict(db.execute(select(us).where(us.c.role=='ADMIN')).mappings().first())
        subs=table('subjects')
        sample=db.execute(select(subs).where(subs.c.subject_code.like('DEMO-%'))).mappings().first()
        plain=sample['subject_name'].replace('[DEMO] ','')
        if not db.scalar(select(subs.c.subject_id).where(subs.c.course_id==sample['course_id'],subs.c.subject_name==plain)):
            db.execute(subs.insert().values(course_id=sample['course_id'],subject_name=plain,subject_code='COLLISION-CHECK',semester=1))
        before={r['user_id']:r['password_hash'] for r in db.execute(select(us)).mappings()}
        result=expand(db,actor);db.commit();assert result['added_courses']==6 and result['added_students']==60
        assert expand(db,actor)['already_created'] is True
        for r in db.execute(select(us)).mappings():
            if r['user_id'] in before:assert r['password_hash']==before[r['user_id']]
            if r['email'].endswith('@demo.learnpath.dev'):assert '[DEMO]' not in r['full_name']
    response=client.get('/api/college-data/catalog',headers=state['headers']['ADMIN'])
    assert response.status_code==200,response.text
    courses=response.json()['courses']
    expanded=[c for c in courses if c['course_code'] in ['BTAIML','BTDS','BTECE','BTEEE','BTME','BTCE']]
    assert len(expanded)==6 and all(c['students']==10 and c['subjects']==2 and c['faculty']>=1 for c in expanded)
    for role in ['STUDENT','FACULTY','HOD']:assert client.get('/api/college-data/catalog',headers=state['headers'][role]).status_code==403



def test_year_curricula_student_cohorts_scope_and_topic_coverage(client,state):
    from app.curriculum_seed import seed
    from sqlalchemy.orm import Session
    with Session(engine) as db:
        users=table('users');actor=dict(db.execute(select(users).where(users.c.role=='ADMIN')).mappings().first())
        before={r['user_id']:r['password_hash'] for r in db.execute(select(users)).mappings()}
        marks={r['attempt_id']:r['score'] for r in db.execute(select(table('test_attempts'))).mappings()}
        result=seed(db,actor);db.commit();assert result['curriculum_subjects']>0
        assert seed(db,actor)['already_created'] is True
        for r in db.execute(select(users)).mappings():
            if r['user_id'] in before:assert r['password_hash']==before[r['user_id']]
        for r in db.execute(select(table('test_attempts'))).mappings():
            if r['attempt_id'] in marks:assert r['score']==marks[r['attempt_id']]
    admin=state['headers']['ADMIN'];r=client.get('/api/academics/overview',headers=admin);assert r.status_code==200,r.text
    data=r.json();mapped=[s for s in data['subjects'] if s['study_year']]
    for course in data['courses']:
        subs=[s for s in mapped if s['course_id']==course['course_id']]
        if not subs:continue
        target=24 if course['duration_years']==4 else 18 if course['duration_years']==3 else 15
        assert len(subs)>=target
        assert set(s['study_year'] for s in subs)==set(range(1,course['duration_years']+1))
        assert all(2*s['study_year']-1<=s['semester']<=2*s['study_year'] for s in subs)
    unknown=next((section for section in data['sections'] if section['study_year'] is None),None)
    if unknown:
        r=client.put('/api/academics/sections/'+str(unknown['section_id'])+'/year',headers=admin,json={'study_year':1});assert r.status_code==200,r.text
        assert client.put('/api/academics/sections/'+str(unknown['section_id'])+'/year',headers=admin,json={'study_year':2}).status_code==409
    assert client.put('/api/academics/sections/'+str(data['sections'][0]['section_id'])+'/year',headers=admin,json={'study_year':8}).status_code==422
    bca=next(c for c in data['courses'] if c['course_code']=='BCA');assert bca['duration_years']==3 and bca['program_level']=='UG'
    first=next(s for s in mapped if s['study_year']==1)
    section=next(s for s in data['sections'] if s['course_id']==first['course_id'] and s['study_year']==1)
    other=next(s for s in data['sections'] if s['course_id']==first['course_id'] and s['study_year']==2)
    a=next(a for a in data['assignments'] if a['subject_id']==first['subject_id'] and a['section_id']==section['section_id'])
    assert client.post('/api/campus/teaching',headers=admin,json={'faculty_id':a['faculty_id'],'subject_id':first['subject_id'],'section_id':other['section_id']}).status_code==422
    h={'Authorization':'Bearer '+token({'user_id':a['faculty_id']})};topic=a['topics'][0]
    path=f"/api/academics/teaching/{a['faculty_assignment_id']}/topics/{topic['topic_id']}"
    assert client.put(path,headers=h,json={'status':'COMPLETED'}).status_code==200
    profile=client.get('/api/academics/overview',headers=h).json()
    assert all(x['faculty_id']==a['faculty_id'] for x in profile['assignments'])
    assert next(x for x in profile['assignments'] if x['faculty_assignment_id']==a['faculty_assignment_id'])['topics'][0]['status']=='COMPLETED'
    student=next(s for s in data['students'] if s['section_id']==section['section_id'])
    sh={'Authorization':'Bearer '+token({'user_id':student['student_id']})}
    assert client.get('/api/academics/overview',headers=sh).status_code==403
    workspace=client.get('/api/portal/workspace',headers=sh).json()
    assert workspace['scopes']
    years={s['subject_id']:s['study_year'] for s in workspace['subjects']}
    assert all(years[p['subject_id']] in [None,1] for p in workspace['scopes'])
    assert client.put(path,headers=sh,json={'status':'PLANNED'}).status_code==403



def test_admin_catalog_saved_edits_sync_curriculum_and_are_audited(client,state):
    admin=state['headers']['ADMIN'];overview=client.get('/api/academics/overview',headers=admin).json()
    subject=next(s for s in overview['subjects'] if s['study_year']==1)
    body={k:subject[k] for k in ['course_id','subject_name','subject_code','semester']};body['semester']=2 if subject['semester']==1 else 1
    changed=client.put('/api/subjects/'+str(subject['subject_id']),json=body,headers=admin)
    assert changed.status_code==200,changed.text
    with engine.connect() as db:
        cur=db.execute(select(table('subject_curriculum')).where(table('subject_curriculum').c.subject_id==subject['subject_id'])).mappings().one()
        assert cur['semester']==body['semester'] and cur['study_year']==1
        audits=table('campus_audit');assert db.scalar(select(audits.c.audit_id).where(audits.c.action=='CATALOG_UPDATED',audits.c.entity_type=='subjects',audits.c.entity_id==subject['subject_id']).limit(1))
    context=client.get('/api/ui/context',headers=admin).json()
    assert next(s for s in context['subjects'] if s['subject_id']==subject['subject_id'])['semester']==body['semester']
    assert client.put('/api/subjects/'+str(subject['subject_id']),json={**body,'semester':3},headers=admin).status_code==409
    course=next(c for c in overview['courses'] if c['course_id']==subject['course_id'])
    course_body={k:course[k] for k in ['department_id','course_name','course_code','duration_years','program_level']};course_body['duration_years']-=1
    assert client.put('/api/courses/'+str(course['course_id']),json=course_body,headers=admin).status_code==409
    fresh=state['post']('/academic_events',{'title':'Persistence verification event','starts_on':'2027-01-10','ends_on':'2027-01-11','description':'Saved through the API'})
    assert client.put('/api/academic_events/'+str(fresh['event_id']),json={'title':'Updated verification event','starts_on':'2027-01-10','ends_on':'2027-01-12','description':'Updated through the API'},headers=admin).status_code==200
    assert any(e['event_id']==fresh['event_id'] and e['title']=='Updated verification event' for e in client.get('/api/ui/context',headers=admin).json()['academic_events'])


def test_validation_and_account_disable(client,state):
    h=state['headers']['ADMIN']
    assert client.post('/users',json={'full_name':'X','email':'x@example.com','password':'weak','role':'ADMIN'},headers=h).status_code==422
    assert client.post('/questions',json={'topic_id':state['topic'],'question_text':'x','question_type':'MCQ','choice_options':['a','b'],'correct_answer':'c'},headers=state['headers']['FACULTY']).status_code==422
    sid=state['users']['STUDENT']['user_id']
    assert client.patch(f'/users/{sid}/status',json={'is_active':False},headers=h).status_code==200
    assert client.get('/auth/me',headers=state['headers']['STUDENT']).status_code==401

