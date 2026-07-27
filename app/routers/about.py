from fastapi import APIRouter 

router = APIRouter(prefix ="/about", tags=["about"])

@router.get("/")
def intro():
    return("hello user please navigate to other section enjoy!")