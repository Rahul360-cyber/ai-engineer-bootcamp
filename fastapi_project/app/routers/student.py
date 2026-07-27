from fastapi import APIRouter

router = APIRouter(prefix = "/student",tags =["student"])

@router.get("/")
def get_all_student():
    return{"students":["rahul","raul","messi"]}

@router.get("/search")
def get_status(status:str):
    return {"status":status}

@router.get("/{student_id}")
def pupil_id(student_id:int):
    return {"id":student_id}

