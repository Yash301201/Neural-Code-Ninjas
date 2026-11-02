"""Explicit MySQL schema setup. Never runs automatically at API startup."""
import argparse
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.engine import make_url
from app.config import settings

def statements(path):
    # Project SQL files contain no procedures or semicolons within string literals.
    source='\n'.join(line for line in path.read_text(encoding='utf-8').splitlines() if not line.lstrip().startswith('--'))
    return [s.strip() for s in source.split(';') if s.strip()]

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--sample-data',action='store_true',help='Load fictional data once into a fresh database')
    p.add_argument('--create-database',action='store_true',help='Requires CREATE DATABASE privilege')
    args=p.parse_args()
    url=make_url(settings.database_url)
    if url.get_backend_name()!='mysql' or url.database!='learnpath_ai':
        raise SystemExit('Use a MySQL URL with database learnpath_ai')
    engine=create_engine(url.set(database=None) if args.create_database else url)
    files=['001_schema.sql','003_calendar.sql','005_oulad_analytics.sql','007_rag_assistant.sql','009_campus_workflows.sql','011_faculty_operations.sql','013_showcase_development.sql','015_year_curriculum.sql']
    if args.sample_data:
        files.append('002_sample_data.sql')
    with engine.connect() as c:
        for filename in files:
            for stmt in statements(Path(__file__).resolve().parents[1]/'db'/filename):
                if stmt.upper().startswith('CREATE DATABASE') and not args.create_database:
                    continue
                c.exec_driver_sql(stmt)
            c.commit()
            print('Applied',filename)
    print('Schema ready. Create a login with python -m scripts.create_admin')

if __name__=='__main__':
    main()
