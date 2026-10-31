"""Apply the exact passwords in .local/portal-credentials.json to MySQL.
Never replace that JSON file or invent a different password.
JWT signing is handled by app.security using JWT_SECRET from backend/.env.
"""
from pathlib import Path
import json
from sqlalchemy import select
from app.db import engine,metadata,table
from app.security import hasher,verify

BACKEND=Path(__file__).resolve().parents[1]

def read_credentials(path):
    data=json.loads(path.read_text(encoding='utf-8-sig'))
    expected={'ADMIN':'admin@learnpath.dev','HOD':'hod@learnpath.dev','FACULTY':'faculty@learnpath.dev','STUDENT':'student@learnpath.dev'}
    if not isinstance(data,dict) or set(data)!=set(expected):
        raise ValueError('JSON must contain exactly ADMIN, HOD, FACULTY and STUDENT accounts')
    for role,email in expected.items():
        entry=data[role]
        if not isinstance(entry,dict) or entry.get('email')!=email:
            raise ValueError('Unexpected account email for '+role)
        password=entry.get('password')
        if not isinstance(password,str) or not password:
            raise ValueError('A non-empty password string is required for '+role)
        if password!=password.strip():
            raise ValueError('Remove leading/trailing password whitespace in the JSON for '+role+'; the login form trims surrounding whitespace')
    return data

def main():
    data=read_credentials(BACKEND/'.local/portal-credentials.json')
    metadata.reflect(bind=engine)
    users=table('users')
    changed=0
    with engine.begin() as c:
        targets=[]
        for role,entry in data.items():
            user=c.execute(select(users).where(users.c.email==entry['email']).with_for_update()).mappings().first()
            if not user or user['role']!=role or ('user_id' in entry and entry['user_id']!=user['user_id']):
                raise ValueError('Account identity/role mismatch for '+role+'; no passwords applied')
            if not user['is_active']:
                raise ValueError(role+' account is disabled; enable it intentionally before syncing')
            targets.append((user,entry['password']))
        for user,password in targets:
            if not verify(password,user['password_hash']):
                c.execute(users.update().where(users.c.user_id==user['user_id']).values(password_hash=hasher.hash(password)))
                changed+=1
    text='LearnPath AI - credentials from your edited JSON\nLogin: http://127.0.0.1:8001/app/login\n\n'
    for role,entry in data.items():
        text+=role+'\nEmail: '+entry['email']+'\nPassword: '+entry['password']+'\n\n'
    text+='MySQL stores Argon2id password hashes. Successful login issues an expiring JWT signed with JWT_SECRET from backend/.env. Passwords are never placed inside JWTs.\n'
    (BACKEND/'.local/portal-logins.txt').write_text(text,encoding='utf-8')
    print('Synced four exact JSON passwords; '+str(changed)+' database hashes updated. JSON left unchanged.')

if __name__=='__main__':
    main()
