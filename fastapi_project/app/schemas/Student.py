from fastapi import APIRouter
from pydantic import BaseModel

class student_info(BaseModel):
    id : int = 1
    name : str = "rahul"
    age : int = 26
    course : str | None = None

router = APIRouter()

@router.post("/info")

async def info_students(student_info : student_info):
    student_info_schema = student_info.model_dump()
    student_info_schema.update({"message":"student created successfully"})

    return student_info_schema


