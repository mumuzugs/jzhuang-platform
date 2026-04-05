"""
支付接口 - 简化版
"""
from fastapi import APIRouter, Depends, Body
from pydantic import BaseModel, Field
from typing import Optional

from src.api.endpoints.auth import get_current_user
from src.services.payment import payment_service
from src.models.payment import PRODUCTS

router = APIRouter()


class CreateOrderRequest(BaseModel):
    product_type: str = Field(..., description="产品类型: vip_pro")


@router.get("/products")
async def get_products():
    """获取产品列表"""
    return {"products": PRODUCTS}


@router.post("/create-order")
async def create_order(
    request: CreateOrderRequest,
    current_user: dict = Depends(get_current_user)
):
    """创建订单"""
    order = await payment_service.create_order(
        user_id=current_user["id"],
        product_type=request.product_type
    )
    return order


@router.get("/order/{order_no}")
async def get_order(
    order_no: str,
    current_user: dict = Depends(get_current_user)
):
    """获取订单详情"""
    return {
        "order_no": order_no,
        "status": "pending",
        "amount": 29900,
        "created_at": "2026-04-06T00:30:00"
    }


@router.get("/my-orders")
async def get_my_orders(
    current_user: dict = Depends(get_current_user),
    limit: int = 10,
    offset: int = 0
):
    """获取我的订单"""
    return {"orders": [], "total": 0}


@router.get("/vip-status")
async def get_vip_status(current_user: dict = Depends(get_current_user)):
    """获取VIP状态"""
    result = await payment_service.check_vip_status(current_user["id"])
    return result


@router.post("/check")
async def check_vip(current_user: dict = Depends(get_current_user)):
    """检查VIP状态"""
    return {
        "is_pro": current_user.get("is_pro", False),
        "role": current_user.get("role", "free"),
        "pro_expire_time": None
    }
