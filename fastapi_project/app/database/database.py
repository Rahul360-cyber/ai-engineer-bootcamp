from sqlmodel import create_engine,Field,Session,select,SQLModel
from typing import Annotated
from fastapi import Depends ,FastAPI
import psycopg
import os
##sql_file_name = "student_db.db"

##sqlite_url = f"sqlite:///{sql_file_name}"
##postgre_sqlite_url = f"postgresql+psycopg://postgres:Rahul%402000@db:5432/student_db"
database_url = os.getenv("DATABASE_URL")
##connect_args = {"check_same_thread":False}
if database_url is None:
    raise RuntimeError("DATABASE_URL is not set")

engine = create_engine(database_url)


def base():
    SQLModel.metadata.create_all(engine)

def get_db():
    with Session(engine)  as session:
        yield session

SessionDep = Annotated[Session, Depends(get_db) ]
