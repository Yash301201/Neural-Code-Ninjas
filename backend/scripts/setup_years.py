from pathlib import Path
from app.db import engine
from scripts.init_db import statements

def main():
    with engine.begin() as c:
        for stmt in statements(Path(__file__).resolve().parents[1]/'db/015_year_curriculum.sql'):c.exec_driver_sql(stmt)
    print('Study-year, curriculum and topic coverage tables ready.')
if __name__=='__main__':main()
