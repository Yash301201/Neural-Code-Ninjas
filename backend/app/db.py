from sqlalchemy import create_engine, MetaData, select, event
from sqlalchemy.orm import Session
from fastapi import HTTPException
from .config import settings

engine = create_engine(settings.database_url, pool_pre_ping=True, hide_parameters=True)
@event.listens_for(engine, 'connect')
def set_utc(connection, record):
    if engine.dialect.name == 'mysql':
        with connection.cursor() as cursor:
            cursor.execute("SET time_zone = '+00:00'")

metadata = MetaData()

def table(name):
    return metadata.tables[name]

def get_db():
    with Session(engine) as session:
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise

def one(db, name, ident, lock=False):
    t = table(name)
    stmt = select(t).where(list(t.primary_key)[0] == ident)
    if lock:
        stmt = stmt.with_for_update()
    row = db.execute(stmt).mappings().first()
    if not row:
        raise HTTPException(404, f'{name} record not found')
    return dict(row)

def add(db, name, **data):
    result = db.execute(table(name).insert().values(**data))
    return one(db, name, result.inserted_primary_key[0])

def update(db, name, ident, **data):
    t = table(name)
    db.execute(t.update().where(list(t.primary_key)[0] == ident).values(**data))
    return one(db, name, ident)
