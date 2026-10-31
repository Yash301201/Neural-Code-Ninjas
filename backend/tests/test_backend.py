"""MySQL integration tests. Only target a disposable *_test database."""
import os
from datetime import datetime,timedelta,timezone
from pathlib import Path
import pytest
from sqlalchemy import create_engine,text
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
        for filename in ['001_schema.sql','003_calendar.sql','007_rag_assistant.sql']:
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

def test_validation_and_account_disable(client,state):
    h=state['headers']['ADMIN']
    assert client.post('/users',json={'full_name':'X','email':'x@example.com','password':'weak','role':'ADMIN'},headers=h).status_code==422
    assert client.post('/questions',json={'topic_id':state['topic'],'question_text':'x','question_type':'MCQ','choice_options':['a','b'],'correct_answer':'c'},headers=state['headers']['FACULTY']).status_code==422
    sid=state['users']['STUDENT']['user_id']
    assert client.patch(f'/users/{sid}/status',json={'is_active':False},headers=h).status_code==200
    assert client.get('/auth/me',headers=state['headers']['STUDENT']).status_code==401
