from fastapi import APIRouter,status,Cookie,Header,Form,File,UploadFile,Depends,HTTPException, status
from typing import Annotated,Any
from app.schemas.Student import address,guardian,student_info,student_response

async def get_api_key(x_token : Annotated[str | None ,Header()]):
      if x_token == "my_secret_key":
            return True
      raise HTTPException(status_code = status.HTTP_401_UNAUTHORIZED,detail="wrong api_key")
      


async def verify_user(keyverify :Annotated [Any , Depends(get_api_key)]):
      if keyverify:
            return "verified"
      else:
            return keyverify      
router = APIRouter(prefix = "/student",tags =["student"],dependencies =[Depends(verify_user)])

async def  logging_confirmation():
      return "request received"


@router.get("/",dependencies=[Depends(logging_confirmation)])
def get_all_student():
    return{"students":["rahul","raul","messi"]}

@router.get("/search",dependencies=[Depends(logging_confirmation)])
def get_status(status:str):
    return {"status":status}
"""
@router.get("/{student_id}")
def pupil_id(student_id:int):
    return {"id":student_id}
"""
students_n =[]

@router.post("/info",status_code= status.HTTP_201_CREATED,response_model = student_response)

async def info_students(student_info1 : student_info):
    std = student_info1.model_dump()
    students_n.append(std)
    return student_info1

@router.get("/students",dependencies=[Depends(logging_confirmation)])
async def nome ():
        return students_n

@router.get("/profile",dependencies=[Depends(logging_confirmation)])
async def sessions(session_id: Annotated[str | None , Cookie()] = None) :
      if session_id == None:
            return {"message":"no session_id"}

      return {"session" : session_id}

@router.get("/device",dependencies=[Depends(logging_confirmation)])
async def read_UserAgent(user_agent : Annotated[str | None, Header()] = None  ):
      return {"User-Agent":user_agent}

@router.post("/login",dependencies=[Depends(logging_confirmation)])
async def authentication(username : Annotated[str | None, Form()], password : Annotated [str | None,Form()]):
      return {"message" : "login request received"}
@router.post("/upload-photo",dependencies=[Depends(logging_confirmation)])
async def file_upload(files : Annotated[list[bytes],File()],files_name : list[UploadFile]):
      return {"size":len(files),"filename":[i.filename for i in files_name] ,"content_type":[j.content_type for j in files_name]}
      
@router.put("/students/{id}",dependencies=[Depends(logging_confirmation)])
async def add_id(id:int):
      return id
@router.delete("/students/{id}")
async def remove_id():
      return {"message":"successfully done"}
def welcome():
      return "hello all users"
@router.get("/welcome")
async def hello(cps : Annotated [str,Depends(welcome)]):
      return cps
class std_verificaton:
      def __init__(self,age: int):
            self.age = age
      def verification(self):
             if self.age >= 18:
                   return self.age
             raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student age must be greater than 18",)
@router.get("/verification")
async def verify(Verify : Annotated[std_verificaton,Depends()]):
      results = Verify.verification()
      return {"results": results}


    