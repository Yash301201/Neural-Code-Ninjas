"""Refine only clearly marked synthetic subjects; never relabel research data."""
from sqlalchemy import select
from .db import table,update
from .campus import audit
DB=[('Which key uniquely identifies a table row?',['Primary key','Foreign key','Label','Comment'],'Primary key'),('Which SQL operation reads rows?',['SELECT','INSERT','DELETE','UPDATE'],'SELECT'),('Which form removes partial dependency?',['Second normal form','Unnormalized form','A text file','A view name'],'Second normal form'),('Which property makes a transaction all-or-nothing?',['Atomicity','Sorting','Aliasing','Formatting'],'Atomicity'),('Which structure can speed up row lookup?',['Index','Comment','Caption','Backup name'],'Index')]
NET=[('Which protocol provides reliable ordered delivery?',['TCP','UDP','IP only','ARP'],'TCP'),('Which device forwards packets between networks?',['Router','Keyboard','Monitor','Printer'],'Router'),('What does DNS resolve?',['Names to IP addresses','Marks to grades','Packets to files','Passwords to names'],'Names to IP addresses'),('Which protocol resolves an IPv4 address to a MAC address locally?',['ARP','HTTP','SMTP','FTP'],'ARP'),('Which layer provides end-to-end transport?',['Transport','Physical','Data link','Presentation'],'Transport')]
def refine(db,actor):
    subjects=table('subjects');changed=0
    rows=db.execute(select(subjects).where(subjects.c.subject_code.like('DEMO-%'))).mappings().all()
    for sub in rows:
        if not sub['subject_name'].startswith('[DEMO]'):continue
        database=sub['subject_code'].endswith('-1');name='Database Management Systems' if database else 'Computer Networks';definitions=DB if database else NET
        if sub['subject_name']!='[DEMO] '+name:update(db,'subjects',sub['subject_id'],subject_name='[DEMO] '+name);changed+=1
        topics=table('topics');ts=db.execute(select(topics).where(topics.c.subject_id==sub['subject_id']).order_by(topics.c.topic_id)).mappings().all()
        for i,tp in enumerate(ts):update(db,'topics',tp['topic_id'],topic_name='[DEMO] '+(['Relational Model and SQL','Transactions and Indexing'][i%2] if database else ['Network Protocols','Addressing and Routing'][i%2]),description='Synthetic engineering curriculum example.')
        q=table('questions');qs=db.execute(select(q).where(q.c.topic_id.in_([t['topic_id'] for t in ts])).order_by(q.c.question_id)).mappings().all()
        for i,question in enumerate(qs):
            text,choices,correct=definitions[i%len(definitions)]
            if question['question_text']=='[DEMO] '+text and question['correct_answer']==correct:continue
            update(db,'questions',question['question_id'],question_text='[DEMO] '+text,choice_options=choices,correct_answer=correct,explanation='Synthetic engineering practice question. Reference answer: '+correct)
            answers=table('student_answers')
            for ans in db.execute(select(answers).where(answers.c.question_id==question['question_id'])).mappings():update(db,'student_answers',ans['answer_id'],answer_text=correct if float(ans['awarded_marks'] or 0)>0 else next(c for c in choices if c!=correct),feedback='[DEMO] Engineering MCQ example; synthetic marks preserved.')
            changed+=1
        assignments=table('assignments')
        for i,a in enumerate(db.execute(select(assignments).where(assignments.c.subject_id==sub['subject_id'],assignments.c.title.like('[DEMO]%')).order_by(assignments.c.assignment_id)).mappings()):
            update(db,'assignments',a['assignment_id'],title='[DEMO] '+name+' '+('design exercise' if i%2==0 else 'practical lab'),description=('Design a normalized student-course-enrollment schema, identify keys and write SQL joins.' if database else 'Design a small campus network, explain IP addressing and compare TCP and UDP.'))
            su=table('submissions')
            for response in db.execute(select(su).where(su.c.assignment_id==a['assignment_id'])).mappings():
                update(db,'submissions',response['submission_id'],answer_text=('[DEMO] I normalized the student-course-enrollment model, identified primary/foreign keys and wrote a joined SQL query.' if database else '[DEMO] I designed a campus LAN with subnet addressing, routers and switches, and explained TCP reliability and DNS name resolution.'))
        tests=table('tests')
        for t in db.execute(select(tests).where(tests.c.subject_id==sub['subject_id'],tests.c.title.like('[DEMO]%'))).mappings():
            title=t['title'].replace('[DEMO] Data ','[DEMO] DBMS ').replace('[DEMO] Methods ','[DEMO] Networks ')
            update(db,'tests',t['test_id'],title=title,description='Synthetic engineering-college exam example. Not imported research grades.')
    if changed:audit(db,actor,'ENGINEERING_DEMO_REFINED','user',actor['user_id'],None,{'records_updated':changed},'Clearly marked demo subjects refined to DBMS and Computer Networks; synthetic score totals preserved',None)
    return {'updated':changed}
