from fastapi import APIRouter,status,Cookie,Header,Form,File,UploadFile
from pydantic import BaseModel,Field
from uuid import  UUID
from datetime import datetime , time , date
from typing import Annotated

class address(BaseModel):
      city : str
      country : str
      zipcode : str

class guardian(BaseModel):
      name : str
      phone : int

class student_info(BaseModel):
    student_id :  UUID 
    name : str = Field (min_length = 3,max_length=10 )
    age : int =  Field (gt = 18,lt = 30 , description = "the age should be greater then 18 less then 30 ")
    course : str 
    address : address
    guardian : guardian 
    skills : list[str]
    enrollment_date : datetime 
    fee : float
    date_of_birth : date

class student_response (BaseModel):
       id : UUID 
       name : str 
       course : str 
       age : int
       address : address
       guardian : guardian 
       skills : list[str]
       enrollment_date : datetime
       date_of_birth : date
       

router = APIRouter()
students_n =[]

@router.post("/info",status_code= status.HTTP_201_CREATED,response_model = student_response)

async def info_students(student_info1 : student_info):
    std = student_info1.model_dump()
    students_n.append(std)
    return student_info1

@router.get("/students")
async def nome ():
        return students_n

@router.get("/profile")
async def sessions(session_id: Annotated[str | None , Cookie()] = None) :
      if session_id == None:
            return {"message":"no session_id"}

      return {"session" : session_id}

@router.get("/device")
async def read_UserAgent(user_agent : Annotated[str | None, Header()]  ):
      return {"User-Agent":user_agent}

@router.post("/login")
async def authentication(username : Annotated[str | None, Form()], password : Annotated [str | None,Form()]):
      return {"message" : "login request received"}
@router.post("/upload-photo")
async def file_upload(files : Annotated[list[bytes],File()],files_name : list[UploadFile]):
      return {"size":len(files),"filename":[i.filename for i in files_name] ,"content_type":[j.content_type for j in files_name]}
      
@router.put("/students/{id}")
async def add_id(id:int):
      return id
@router.delete("/students/{id}")
async def remove_id():
      return {"message":"successfully done"}