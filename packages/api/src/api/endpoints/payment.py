# 支付模块占位符

from fastapi import APIRouter

router = APIRouter()


@router.get("/")
async def get_orders():
    return {"message": "支付模块开发中"}


@router.post("/create")
async def create_order():
    return {"message": "订单创建开发中"}