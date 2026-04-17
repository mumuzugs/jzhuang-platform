"""
认证接口
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import SMSCode, sms_code_auto_flow
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field

from src.core.database import get_db
from src.core.security import create_access_token
from src.models.user import User
from src.services.sms import send_sms_code, verify_sms_code

router = APIRouter()


class SendCodeRequest(BaseModel):
    """发送验证码请求"""
    phone: str = Field(..., pattern=r"^1[3-9]\d{9}$")


class LoginRequest(BaseModel):
    """登录请求"""
    phone: str = Field(..., pattern=r"^1[3-9]\d{9}$")
    code: str = Field(..., min_length=6, max_length=6)


class LoginResponse(BaseModel):
    """登录响应"""
    access_token: str
    token_type: str = "bearer"
    user: dict


@router.post("/send-code", response_model=dict)
async def send_code(
    request: SendCodeRequest,
    db: AsyncSession = Depends(get_db)
):
    """发送短信验证码"""
    code = await send_sms_code(request.phone)
    return {"message": "验证码已发送", "phone": request.phone}


@router.post("/login", response_model=LoginResponse)
async def login(
    request: LoginRequest,
    db: AsyncSession = Depends(get_db)
):
    """手机号验证码登录"""
    # 验证验证码
    if not await verify_sms_code(request.phone, request.code):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="验证码错误或已过期"
        )
    
    # 查询或创建用户
    user = await User.get_by_phone(db, request.phone)
    if not user:
        user = await User.create(db, phone=request.phone)
    
    # 生成Token
    access_token = create_access_token(data={"sub": user.id})
    
    return LoginResponse(
        access_token=access_token,
        user={
            "id": user.id,
            "phone": user.phone,
            "role": user.role.value
        }
    )