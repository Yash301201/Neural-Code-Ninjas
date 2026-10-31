import getpass
from sqlalchemy import MetaData,Table,select
from sqlalchemy.orm import Session
from pydantic import TypeAdapter,EmailStr
from app.db import engine
from app.security import hasher

def main():
    email=str(TypeAdapter(EmailStr).validate_python(input('Admin email: ').strip())).lower()
    password=getpass.getpass('Password (12+ characters): ')
    if len(password)<12 or len(password)>128:
        raise SystemExit('Password must contain 12-128 characters')
    users=Table('users',MetaData(),autoload_with=engine)
    with Session(engine) as db:
        if db.execute(select(users).where(users.c.email==email)).first():
            raise SystemExit('Account already exists; no changes made')
        db.execute(users.insert().values(full_name='Administrator',email=email,password_hash=hasher.hash(password),role='ADMIN'))
        db.commit()
    print('Administrator created')
if __name__=='__main__':
    main()
