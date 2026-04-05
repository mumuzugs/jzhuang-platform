"""
用户接口
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field
from typing import Optional

from src.core.database import get_db
from src.models.user import User, get_user_by_id
from src.api.endpoints.auth import get_current_user

router = APIRouter()


class UpdateProfileRequest(BaseModel):
    nickname: Optional[str] = Field(None, max_length=50)
    avatar: Optional[str] = Field(None, max_length=500)


class UserProfileResponse(BaseModel):
    id: str
    phone: str
    nickname: Optional[str]
    avatar: Optional[str]
    role: str
    is_pro: bool
    pro_expire_time: Optional[str]
    created_at: str
    last_login_at: Optional[str]


@router.get("/profile", response_model=UserProfileResponse)
async def get_profile(
    current_user: User = Depends(get_current_user)
):
    """获取用户资料"""
    return UserProfileResponse(
        id=current_user.id,
        phone=current_user.phone,
        nickname=current_user.nickname,
        avatar=current_user.avatar,
        role=current_user.role.value,
        is_pro=current_user.is_pro,
        pro_expire_time=current_user.pro_expire_time.isoformat() if current_user.pro_expire_time else None,
        created_at=current_user.created_at.isoformat(),
        last_login_at=current_user.last_login_at.isoformat() if current_user.last_login_at else None
    )


@router.put("/profile", response_model=UserProfileResponse)
async def update_profile(
    request: UpdateProfileRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """更新用户资料"""
    if request.nickname is not None:
        current_user.nickname = request.nickname
    if request.avatar is not None:
        current_user.avatar = request.avatar
    
    await db.commit()
    
    return UserProfileResponse(
        id=current_user.id,
        phone=current_user.phone,
        nickname=current_user.nickname,
        avatar=current_user.avatar,
        role=current_user.role.value,
        is_pro=current_user.is_pro,
        pro_expire_time=current_user.pro_expire_time.isoformat() if current_user.pro_expire_time else None,
        created_at=current_user.created_at.isoformat(),
        last_login_at=current_user.last_login_at.isoformat() if current_user.last_login_at else None
    )


@router.delete("/account")
async def delete_account(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """注销账号"""
    current_user.status = "deleted"
    current_user.phone = f"deleted_{current_user.id}_{current_user.phone}"
    await db.commit()
    
    return {"message": "账号已注销"}


@router.get("/vip/status")
async def get_vip_status(
    current_user: User = Depends(get_current_user)
):
    """获取VIP状态"""
    return {
        "is_pro": current_user.is_pro,
        "role": current_user.role.value,
        "pro_expire_time": current_user.pro_expire_time.isoformat() if current_user.pro_expire_time else None,
        "pro_order_no": current_user.pro_order_no
    }
