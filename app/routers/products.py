from fastapi import APIRouter

router = APIRouter(prefix = "/products",tags = ["products"])

@router.get("/{prod_id}")
def product_id(prod_id:int):
    return {"product_id":prod_id}