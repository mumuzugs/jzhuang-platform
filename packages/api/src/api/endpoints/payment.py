"""
支付接口
"""
from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field
from typing import Optional

from src.core.database import get_db
from src.models.user import User
from src.api.endpoints.auth import get_current_user
from src.services.payment import payment_service
from src.models.payment import PRODUCTS

router = APIRouter()


# ============ 请求模型 ============

class CreateOrderRequest(BaseModel):
    product_type: str = Field(..., description="产品类型: vip_pro")


class PaymentCallbackRequest(BaseModel):
    order_no: str
    return_code: str
    return_msg: Optional[str] = None
    transaction_id: Optional[str] = None
    time_end: Optional[str] = None


# ============ 接口 ============

@router.get("/products")
async def get_products():
    """获取产品列表"""
    return {"products": PRODUCTS}


@router.post("/create-order")
async def create_order(
    request: CreateOrderRequest,
    current_user: User = Depends(get_current_user)
):
    """创建订单"""
    order = await payment_service.create_order(
        user_id=current_user.id,
        product_type=request.product_type
    )
    return order


@router.post("/get-pay-params")
async def get_pay_params(
    order_no: str,
    amount: int,
    description: str = "集装修专业版",
    current_user: User = Depends(get_current_user)
):
    """获取支付参数"""
    result = await payment_service.get_wechat_pay_params(
        order_no=order_no,
        amount=amount,
        description=description
    )
    return result


@router.post("/callback")
async def payment_callback(
    request: PaymentCallbackRequest,
    db: AsyncSession = Depends(get_db)
):
    """支付回调"""
    payment_result = {
        "return_code": request.return_code,
        "return_msg": request.return_msg
    }
    
    result = await payment_service.handle_payment_callback(
        order_no=request.order_no,
        payment_result=payment_result
    )
    
    # 如果支付成功，激活VIP
    if result["success"]:
        await payment_service.activate_vip(
            user_id="",  # 从订单中获取
            order_no=request.order_no
        )
    
    return result


@router.get("/order/{order_no}")
async def get_order(
    order_no: str,
    current_user: User = Depends(get_current_user)
):
    """获取订单详情"""
    return {
        "order_no": order_no,
        "status": "pending",
        "amount": 29900,
        "created_at": "2026-04-05T12:00:00"
    }


@router.get("/my-orders")
async def get_my_orders(
    current_user: User = Depends(get_current_user),
    limit: int = 10,
    offset: int = 0
):
    """获取我的订单"""
    return {"orders": [], "total": 0}


@router.get("/vip-status")
async def get_vip_status(
    current_user: User = Depends(get_current_user)
):
    """获取VIP状态"""
    result = await payment_service.check_vip_status(current_user.id)
    return result


@router.post("/check")
async def check_vip(
    current_user: User = Depends(get_current_user)
):
    """检查VIP状态"""
    return {
        "is_pro": current_user.is_pro,
        "role": current_user.role.value,
        "pro_expire_time": current_user.pro_expire_time.isoformat() if current_user.pro_expire_time else None
    }