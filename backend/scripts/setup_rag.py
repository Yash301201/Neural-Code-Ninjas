"""Apply additive RAG migration then refresh public retrieval chunks. No user changes."""
from pathlib import Path
from sqlalchemy.orm import Session
from app.db import engine
from scripts.init_db import statements
def main():
    with engine.begin() as db:
        for stmt in statements(Path(__file__).resolve().parents[1]/'db'/'007_rag_assistant.sql'):db.exec_driver_sql(stmt)
    from app.rag import index_public
    with Session(engine) as db:
        result=index_public(db);db.commit();print('MySQL RAG migration and index ready:',result)
if __name__=='__main__':main()
