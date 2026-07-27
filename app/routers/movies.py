from fastapi import APIRouter
router = APIRouter (prefix = "/movies",tags = ["movies"])

@router.get("/{mov_id}")

def movie_id(mov_id:int):
    return {"movie_id": mov_id}