from sqlmodel import create_engine,Field,Session,select,SQLModel
from typing import Annotated
from fastapi import Depends ,FastAPI
sql_file_name = "studentdb.db"
sqlite_url = f"sqlite:///{sql_file_name}"

connect_args = {"check_same_thread":False}
engine = create_engine (sqlite_url,connect_args=connect_args)


def base():
    SQLModel.metadata.create_all(engine)

def get_db():
    with Session(engine)  as session:
        yield session

SessionDep = Annotated[Session, Depends(get_db) ]