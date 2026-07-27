from fastapi import APIRouter
router = APIRouter(prefix="/users",tags=["users"])

@router.get('/')
def welcome():
    return ("HELLO API TESTER")

@router.get("/{user_id}")
def get_users(user_id:int):
    return {"id": user_id}

@router.get("/{user_id}/{user_name}")
def user(user_id:int,user_name:str):
    return{"id":user_id,"name":user_name}

@router.get("/{user_id}/{user_name}/orders")
def get_orders(user_id:int,user_name:str,status:str):
    return {"id":user_id,"name":user_name,"status":status}

    

