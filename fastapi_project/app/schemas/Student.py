from fastapi import APIRouter,status
from pydantic import BaseModel,Field

class address(BaseModel):
      city : str
      country : str
      zipcode : str

class guardian(BaseModel):
      name : str
      phone : int

class student_info(BaseModel):
    id : int 
    name : str = Field (min_length = 3,max_length=10 )
    age : int =  Field (gt = 18,lt = 30 , description = "the age should be greater then 18 less then 30 ")
    course : str 
    address : address
    guardian : guardian 
    skills : list[str]
    
class studentRefinedInfo (BaseModel):
       id : int 
       name : str 
       course : str 
       age : int
       address : address
       guardian : guardian 

       

router = APIRouter()
students_n =[]

@router.post("/info",status_code= status.HTTP_201_CREATED,response_model = studentRefinedInfo)

async def info_students(student_info1 : student_info):
    std = student_info1.model_dump()
    students_n.append(std)
    return student_info1

@router.get("/students")
async def nome ():
        return students_n