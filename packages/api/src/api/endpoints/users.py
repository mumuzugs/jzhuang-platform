"""
用户接口 - 简化版
"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from typing import Optional

from src.api.endpoints.auth import get_current_user

router = APIRouter()


class UserProfileResponse(BaseModel):
    id: str
    phone: str
    nickname: Optional[str]
    role: str
    is_pro: bool


@router.get("/profile", response_model=UserProfileResponse)
async def get_profile(current_user: dict = Depends(get_current_user)):
    """获取用户资料"""
    return UserProfileResponse(
        id=current_user["id"],
        phone=current_user["phone"],
        nickname=current_user.get("nickname"),
        role=current_user["role"],
        is_pro=current_user["is_pro"]
    )


@router.put("/profile")
async def update_profile(
    nickname: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """更新用户资料"""
    if nickname:
        current_user["nickname"] = nickname
    return {"message": "更新成功"}


@router.delete("/account")
async def delete_account(current_user: dict = Depends(get_current_user)):
    """注销账号"""
    return {"message": "账号已注销"}


@router.get("/vip/status")
async def get_vip_status(current_user: dict = Depends(get_current_user)):
    """获取VIP状态"""
    return {
        "is_pro": current_user.get("is_pro", False),
        "role": current_user.get("role", "free"),
        "pro_expire_time": None,
        "pro_order_no": None
    }
