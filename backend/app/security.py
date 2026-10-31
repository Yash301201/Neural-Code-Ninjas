from datetime import datetime, timedelta, timezone
import jwt
from argon2 import PasswordHasher
from argon2.exceptions import VerificationError, InvalidHashError
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy import select
from .db import get_db, table, one
from .config import settings

hasher = PasswordHasher()
bearer = HTTPBearer()

def verify(password, hashed):
    try:
        return hasher.verify(hashed, password)
    except (VerificationError, InvalidHashError):
        return False

def token(user):
    return jwt.encode({'sub': str(user['user_id']), 'exp': datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_minutes)}, settings.jwt_secret, algorithm='HS256')

def current_user(auth: HTTPAuthorizationCredentials = Depends(bearer), db=Depends(get_db)):
    try:
        payload = jwt.decode(auth.credentials, settings.jwt_secret, algorithms=['HS256'], options={'require': ['exp','sub']})
        ident = int(payload['sub'])
    except (jwt.InvalidTokenError, ValueError, KeyError):
        raise HTTPException(401, 'Invalid or expired token')
    u = one(db, 'users', ident)
    if not u['is_active']:
        raise HTTPException(401, 'Account disabled')
    return u

def roles(*allowed):
    def check(user=Depends(current_user)):
        if user['role'] not in allowed:
            raise HTTPException(403, 'Role not permitted')
        return user
    return check

def public_user(u):
    return {k:v for k,v in u.items() if k != 'password_hash'}

def subject_access(db, u, subject_id, section_id=None, write=False):
    subject = one(db, 'subjects', subject_id)
    course = one(db, 'courses', subject['course_id'])
    if section_id is not None and one(db, 'sections', section_id)['course_id'] != subject['course_id']:
        raise HTTPException(422, 'Section and subject belong to different courses')
    role = u['role']
    if role == 'ADMIN':
        return
    if role == 'HOD' and u['department_id'] == course['department_id']:
        return
    if role == 'FACULTY':
        t = table('faculty_subject_assignments')
        stmt = select(t).where(t.c.faculty_id == u['user_id'], t.c.subject_id == subject_id)
        if section_id is not None:
            stmt = stmt.where(t.c.section_id == section_id)
        if db.execute(stmt).first():
            return
    if role == 'STUDENT' and not write:
        e, s = table('student_enrollments'), table('sections')
        stmt = select(e).join(s, e.c.section_id == s.c.section_id).where(e.c.student_id == u['user_id'], e.c.status == 'ACTIVE', s.c.course_id == subject['course_id'])
        if section_id is not None:
            stmt = stmt.where(e.c.section_id == section_id)
        if db.execute(stmt).first():
            return
    raise HTTPException(403, 'Academic scope not permitted')

def student_access(db, u, student_id, subject_id):
    student = one(db, 'users', student_id)
    if student['role'] != 'STUDENT':
        raise HTTPException(422, 'Expected a student')
    if u['role'] == 'STUDENT' and u['user_id'] != student_id:
        raise HTTPException(403, 'Cannot access another student')
    subject_access(db, u, subject_id)
    subject_access(db, student, subject_id)
    if u['role'] == 'FACULTY':
        e, f = table('student_enrollments'), table('faculty_subject_assignments')
        stmt = select(e).join(f, e.c.section_id == f.c.section_id).where(e.c.student_id == student_id, e.c.status == 'ACTIVE', f.c.faculty_id == u['user_id'], f.c.subject_id == subject_id)
        if not db.execute(stmt).first():
            raise HTTPException(403, 'Student is outside assigned sections')
