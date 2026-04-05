"""
支付接口

架构文档要求：
- 微信支付集成
- 订单管理
- VIP状态管理
"""
from fastapi import APIRouter, Depends, Body, Request
from pydantic import BaseModel, Field
from typing import Optional

from src.api.endpoints.auth import get_current_user
from src.services.payment import payment_service

router = APIRouter()


class CreateOrderRequest(BaseModel):
    """创建订单请求"""
    product_type: str = Field(..., description="产品类型: vip_pro")


class PaymentCallbackRequest(BaseModel):
    """支付回调请求"""
    return_code: str
    return_msg: Optional[str] = None
    result_code: Optional[str] = None
    out_trade_no: Optional[str] = None
    transaction_id: Optional[str] = None
    time_end: Optional[str] = None


@router.get("/products")
async def get_products():
    """
    获取产品列表
    
    架构文档要求：299元/装修全周期专业版
    """
    products = []
    for key, info in payment_service.products.items():
        products.append({
            "code": key,
            "name": info["name"],
            "description": info["description"],
            "price": info["price"],
            "price_display": info["price_display"],
            "expire_days": info["expire_days"],
            "features": info["features"]
        })
    
    return {
        "success": True,
        "products": products
    }


@router.post("/create-order")
async def create_order(
    request: CreateOrderRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    创建订单
    
    架构文档要求：微信支付
    """
    order = await payment_service.create_order(
        user_id=current_user["id"],
        product_type=request.product_type
    )
    
    return {
        "success": True,
        **order
    }


@router.post("/get-pay-params")
async def get_pay_params(
    order_no: str,
    openid: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """
    获取微信支付参数
    
    架构文档要求：微信支付集成
    """
    try:
        result = await payment_service.get_wechat_pay_params(
            order_no=order_no,
            openid=openid
        )
        return {
            "success": True,
            **result
        }
    except ValueError as e:
        return {
            "success": False,
            "message": str(e)
        }


@router.post("/callback")
async def payment_callback(request: PaymentCallbackRequest):
    """
    支付回调
    
    架构文档要求：微信支付回调处理
    """
    result = await payment_service.handle_payment_callback(
        callback_data=request.model_dump()
    )
    
    if result["success"]:
        # 激活VIP
        order_no = request.out_trade_no or ""
        if order_no:
            try:
                # 获取订单并激活VIP
                order = await payment_service.get_order(order_no)
                if order:
                    await payment_service.activate_vip(order["user_id"], order_no)
            except Exception as e:
                pass
    
    return result


@router.get("/order/{order_no}")
async def get_order(
    order_no: str,
    current_user: dict = Depends(get_current_user)
):
    """获取订单详情"""
    order = await payment_service.get_order(order_no)
    
    if not order:
        return {
            "success": False,
            "message": "订单不存在"
        }
    
    return {
        "success": True,
        **order
    }


@router.get("/my-orders")
async def get_my_orders(
    current_user: dict = Depends(get_current_user)
):
    """获取我的订单列表"""
    orders = await payment_service.get_user_orders(current_user["id"])
    
    return {
        "success": True,
        "orders": orders,
        "total": len(orders)
    }


@router.get("/vip-status")
async def get_vip_status(
    current_user: dict = Depends(get_current_user)
):
    """
    获取VIP状态
    
    架构文档要求：VIP状态管理
    """
    result = await payment_service.check_vip_status(current_user["id"])
    
    return {
        "success": True,
        **result
    }


@router.post("/check")
async def check_vip(
    current_user: dict = Depends(get_current_user)
):
    """检查VIP状态"""
    result = await payment_service.check_vip_status(current_user["id"])
    
    return {
        "success": True,
        "is_pro": result["is_pro"],
        "role": result["role"],
        "product_name": result.get("product_name")
    }


@router.post("/activate")
async def activate_vip(
    order_no: str,
    current_user: dict = Depends(get_current_user)
):
    """手动激活VIP"""
    try:
        result = await payment_service.activate_vip(current_user["id"], order_no)
        return {
            "success": True,
            **result
        }
    except ValueError as e:
        return {
            "success": False,
            "message": str(e)
        }
