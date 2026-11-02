"""Apply only the additive development/showcase schema. Never resets a database."""
from pathlib import Path
from app.db import engine
from scripts.init_db import statements
def main():
    with engine.begin() as c:
        for sql in statements(Path(__file__).resolve().parents[1]/'db/013_showcase_development.sql'):c.exec_driver_sql(sql)
    print('Development, feedback and showcase tables ready.')
if __name__=='__main__':main()
