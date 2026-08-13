from sqlmodel import create_engine,Field,Session,select,SQLModel
from typing import Annotated
from fastapi import Depends ,FastAPI
import psycopg

sql_file_name = "student_db.db"

sqlite_url = f"sqlite:///{sql_file_name}"
postgre_sqlite_url = f"postgresql+psycopg://postgres:Rahul%402000@localhost:5432/student_db"

##connect_args = {"check_same_thread":False}
engine = create_engine (postgre_sqlite_url,isolation_level="REPEATABLE READ")


def base():
    SQLModel.metadata.create_all(engine)

def get_db():
    with Session(engine)  as session:
        yield session

SessionDep = Annotated[Session, Depends(get_db) ]
print(postgre_sqlite_url)