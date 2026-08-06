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
    id :  UUID 
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
       


