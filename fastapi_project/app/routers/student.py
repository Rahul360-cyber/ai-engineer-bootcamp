from fastapi import APIRouter,status,Cookie,Header,Form,File,UploadFile,Depends,HTTPException, status
from typing import Annotated,Any
from app.schemas.Student import address,guardian,student_info,student_response
from fastapi.security import OAuth2PasswordBearer,OAuth2PasswordRequestForm
from pwdlib import PasswordHash
import jwt 
from jwt.exceptions import InvalidTokenError
from datetime import datetime, timedelta, timezone
from app.database.database import SessionDep
from app.models.models import studentdb
from sqlmodel import Field,Session, SQLModel,create_engine,select
secret_key = "98f18646b61f3e78d3886bca1feeef22b0d6cc0fdbd6ba6a1a3ffe1b7b914473"
ALGORITHM = "HS256"
expire_time = 10
async def get_api_key(x_token : Annotated[str | None ,Header()]):
      if x_token == "my_secret_key":
            return True
      raise HTTPException(status_code = status.HTTP_401_UNAUTHORIZED,detail="wrong api_key")
      


async def verify_user(keyverify :Annotated [Any , Depends(get_api_key)]):
      if keyverify:
            return "verified"
      else:
            return keyverify      
router = APIRouter(prefix = "/student",tags =["student"])

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

@router.post("/info",status_code= status.HTTP_201_CREATED)

async def info_students(student_info1 : studentdb,session : SessionDep):
    session.add(student_info1)
    session.commit()
    session.refresh(student_info1)
    return student_info1

@router.get("/students")
async def nome (session :SessionDep):
        pupils = session.exec(select(studentdb)).all()
        return pupils

@router.get("/profile",dependencies=[Depends(logging_confirmation)])
async def sessions(session_id: Annotated[str | None , Cookie()] = None) :
      if session_id == None:
            return {"message":"no session_id"}

      return {"session" : session_id}

@router.get("/device",dependencies=[Depends(logging_confirmation)])
async def read_UserAgent(user_agent : Annotated[str | None, Header()] = None  ):
      return {"User-Agent":user_agent}

@router.post("/logins",dependencies=[Depends(logging_confirmation)])
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

### security part
password_HASH = PasswordHash.recommended()
fake_users = {"rahul45":{
                 "password":password_HASH.hash("123")
                     },
               "rohit56":{
                     "password":password_HASH.hash("789")},
                "luca79":{
                      "password":password_HASH.hash("895")}
              }
ouath2_scheme =  OAuth2PasswordBearer(tokenUrl="/student/login") 



def verify_password(plain_password,password):
      return password_HASH.verify(plain_password,password)

def get_passsword_hash():
      for i,j in fake_users.items():
        hash =  j["password"]
        j["password"] = password_HASH.hash(hash)




      

@router.post("/login")
async def login_info(form_data : Annotated[OAuth2PasswordRequestForm,Depends()],expire_delta : timedelta | None = None):
      passwor_d = fake_users.get(form_data.username)
      username = form_data.username
      if form_data.username  in fake_users:   
         if not verify_password(form_data.password,passwor_d["password"]):
               raise HTTPException(status_code =status.HTTP_422_UNPROCESSABLE_CONTENT,detail="password is wrong or new signup")
      else:
         raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,detail = "username is wrong or new signup")
      data = {"sub":username}
      To_encode : dict[str,Any] = data.copy()
      if expire_delta:
            expire = datetime.now(timezone.utc) + expire_delta
      else:
            expire = datetime.now(timezone.utc) + timedelta(minutes=5)
      To_encode.update({"exp": expire})
      encoded_jwt = jwt.encode(To_encode,secret_key,algorithm=ALGORITHM)      
      return {"access_token" :encoded_jwt,"token_type": "bearer"} 
     

          

def get_user(user:str):
      try:
            payload = jwt.decode(user,secret_key,algorithms=[ALGORITHM])
            user_n = payload.get("sub")
            if user_n in fake_users:
                        return user_n
      except InvalidTokenError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
      

@router.get("/me")
async def allow_autneticated(token : Annotated [str,Depends(ouath2_scheme)]):
      user1 = get_user(token)
      if not user1:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="notfound username")
      return user1

@router.get("/protected")
def get_values(details : Annotated[str,Depends(allow_autneticated)]):
      return fake_users[details]