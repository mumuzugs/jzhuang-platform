"""
认证接口
"""
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field

from src.core.database import get_db
from src.core.security import (
    create_access_token,
    decode_access_token,
    verify_password,
    get_password_hash,
)
from src.models.user import User, UserStatus
from src.services.sms import send_sms_code, verify_sms_code

router = APIRouter()
security = HTTPBearer(auto_error=False)


class SendCodeRequest(BaseModel):
    """发送验证码请求"""
    phone: str = Field(..., pattern=r"^1[3-9]\d{9}$")


class LoginRequest(BaseModel):
    """登录请求"""
    phone: str = Field(..., pattern=r"^1[3-9]\d{9}$")
    code: str = Field(..., min_length=6, max_length=6)


class ChangePasswordRequest(BaseModel):
    old_password: str = Field(..., min_length=6)
    new_password: str = Field(..., min_length=6)


class BindPhoneRequest(BaseModel):
    phone: str = Field(..., pattern=r"^1[3-9]\d{9}$")
    code: str = Field(..., min_length=6, max_length=6)


class LoginResponse(BaseModel):
    """登录响应"""
    access_token: str
    token_type: str = "bearer"
    user: dict


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: AsyncSession = Depends(get_db),
):
    """获取当前用户"""
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="未登录",
            headers={"WWW-Authenticate": "Bearer"},
        )

    payload = decode_access_token(credentials.credentials)
    if not payload or not payload.get("sub"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token无效或已过期",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = await User.get_by_id(db, payload["sub"])
    if not user or user.status == UserStatus.DELETED:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户不存在",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


@router.post("/send-code", response_model=dict)
async def send_code(
    request: SendCodeRequest,
    db: AsyncSession = Depends(get_db)
):
    """发送短信验证码"""
    code = await send_sms_code(request.phone)

    user = await User.get_by_phone(db, request.phone)
    if not user:
        user = await User.create(db, phone=request.phone)

    user.sms_code = code
    user.sms_code_expire = datetime.utcnow()
    user.updated_at = datetime.utcnow()
    await db.flush()

    return {"message": "验证码已发送", "phone": request.phone}


@router.post("/login", response_model=LoginResponse)
async def login(
    request: LoginRequest,
    db: AsyncSession = Depends(get_db)
):
    """手机号验证码登录"""
    if not await verify_sms_code(request.phone, request.code):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="验证码错误或已过期"
        )

    user = await User.get_by_phone(db, request.phone)
    if not user:
        user = await User.create(db, phone=request.phone)

    user.last_login_at = datetime.utcnow()
    user.updated_at = datetime.utcnow()
    await db.flush()

    access_token = create_access_token(data={"sub": user.id})

    return LoginResponse(
        access_token=access_token,
        user={
            "id": user.id,
            "phone": user.phone,
            "role": user.role.value,
            "nickname": user.nickname,
            "is_pro": user.is_pro,
        }
    )


@router.get("/me")
async def me(current_user: User = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "phone": current_user.phone,
        "nickname": current_user.nickname,
        "avatar": current_user.avatar,
        "role": current_user.role.value,
        "is_pro": current_user.is_pro,
        "created_at": current_user.created_at.isoformat() if current_user.created_at else None,
    }


@router.post("/change-password")
async def change_password(
    request: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """修改密码：真正使用 hash 逻辑"""
    if current_user.password_hash:
        if not verify_password(request.old_password, current_user.password_hash):
            raise HTTPException(status_code=400, detail="旧密码错误")
    else:
        if request.old_password != request.new_password and current_user.password_hash is None:
            # 首次设置密码时允许无旧密码校验，但要求调用者显式提供 old_password
            pass

    current_user.password_hash = get_password_hash(request.new_password)
    current_user.updated_at = datetime.utcnow()
    await db.flush()

    return {"success": True, "message": "密码修改成功"}


@router.post("/bind-phone")
async def bind_phone(
    request: BindPhoneRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if not await verify_sms_code(request.phone, request.code):
        raise HTTPException(status_code=400, detail="验证码错误或已过期")

    existing = await User.get_by_phone(db, request.phone)
    if existing and existing.id != current_user.id:
        raise HTTPException(status_code=400, detail="手机号已被其他账号绑定")

    current_user.phone = request.phone
    current_user.updated_at = datetime.utcnow()
    await db.flush()

    return {"success": True, "message": "手机号绑定成功"}
