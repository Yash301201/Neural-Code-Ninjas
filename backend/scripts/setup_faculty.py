"""Apply faculty operations schema. Does not create students or change credentials."""
from pathlib import Path
from app.db import engine
from scripts.init_db import statements
def main():
    with engine.begin() as c:
        for s in statements(Path(__file__).resolve().parents[1]/'db/011_faculty_operations.sql'):c.exec_driver_sql(s)
    print('Faculty program, timetable and leave tables ready. No demo students added.')
if __name__=='__main__':main()
