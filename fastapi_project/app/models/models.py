from sqlmodel import create_engine,Field,Session,select,SQLModel

class studentdb(SQLModel, table = True):
    id: int | None = Field(default = None ,primary_key= True)
    name : str | None = Field(index = True)
    age : int 
    course : str | None = Field(index= True)
    university_name: str

