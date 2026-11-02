"""Apply additive campus workflow tables without changing existing accounts/data."""
from pathlib import Path
from app.db import engine
from scripts.init_db import statements
def main():
    with engine.begin() as c:
        for sql in statements(Path(__file__).resolve().parents[1]/'db/009_campus_workflows.sql'):c.exec_driver_sql(sql)
    print('Campus workflow tables ready. Existing credentials and academic records unchanged.')
if __name__=='__main__':main()
