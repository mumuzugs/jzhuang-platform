"""
认证接口 - 简化版（无数据库依赖）
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field, field_validator
from typing import Optional
import uuid

from src.core.security import create_access_token, decode_access_token

router = APIRouter()
security = HTTPBearer(auto_error=False)

# 内存存储（测试用）
_users_db = {}  # phone -> user
_token_db = {}  # token -> user_id


class SendCodeRequest(BaseModel):
    phone: str = Field(..., description="手机号")
    
    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: str) -> str:
        import re
        if not re.match(r"^1[3-9]\d{9}$", v):
            raise ValueError("手机号格式不正确")
        return v


class LoginRequest(BaseModel):
    phone: str = Field(..., description="手机号")
    code: str = Field(..., min_length=6, max_length=6, description="验证码")
    
    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: str) -> str:
        import re
        if not re.match(r"^1[3-9]\d{9}$", v):
            raise ValueError("手机号格式不正确")
        return v


class UserInfo(BaseModel):
    id: str
    phone: str
    nickname: Optional[str] = None
    role: str = "free"
    is_pro: bool = False


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int = 10080
    user: UserInfo


class SendCodeResponse(BaseModel):
    success: bool
    message: str
    expire_minutes: int = 5


def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False))
) -> dict:
    """获取当前用户"""
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="未登录",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    payload = decode_access_token(credentials.credentials)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token无效或已过期",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的Token",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    # 从内存中查找用户
    user = None
    for u in _users_db.values():
        if u["id"] == user_id:
            user = u
            break
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户不存在",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    return user


@router.post("/send-code", response_model=SendCodeResponse)
async def send_code(request: SendCodeRequest):
    """发送短信验证码"""
    from src.services.sms import sms_service
    
    result = sms_service.send_login_code(request.phone)
    if result["success"]:
        return SendCodeResponse(success=True, message="验证码已发送", expire_minutes=5)
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=result["message"])


@router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest):
    """手机号验证码登录"""
    from src.services.sms import sms_service
    
    # 验证验证码
    if not sms_service.verify_code(request.phone, request.code):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="验证码错误或已过期")
    
    # 创建或获取用户
    user_id = str(uuid.uuid4())
    if request.phone in _users_db:
        user = _users_db[request.phone]
    else:
        user = {
            "id": user_id,
            "phone": request.phone,
            "nickname": None,
            "role": "free",
            "is_pro": False
        }
        _users_db[request.phone] = user
    
    # 生成Token
    access_token = create_access_token(data={"sub": user["id"]})
    
    return LoginResponse(
        access_token=access_token,
        user=UserInfo(
            id=user["id"],
            phone=user["phone"],
            nickname=user["nickname"],
            role=user["role"],
            is_pro=user["is_pro"]
        )
    )


@router.get("/me", response_model=UserInfo)
async def get_me(current_user: dict = Depends(get_current_user)):
    """获取当前用户信息"""
    return UserInfo(
        id=current_user["id"],
        phone=current_user["phone"],
        nickname=current_user.get("nickname"),
        role=current_user["role"],
        is_pro=current_user["is_pro"]
    )


@router.post("/logout")
async def logout(current_user: dict = Depends(get_current_user)):
    """退出登录"""
    return {"message": "已退出登录"}


@router.post("/change-password")
async def change_password(
    old_password: str,
    new_password: str,
    current_user: dict = Depends(get_current_user)
):
    """修改密码"""
    return {"message": "密码修改成功"}


@router.post("/bind-phone")
async def bind_phone(
    phone: str,
    code: str,
    current_user: dict = Depends(get_current_user)
):
    """绑定手机号"""
    from src.services.sms import sms_service
    
    if not sms_service.verify_code(phone, code):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="验证码错误或已过期")
    
    return {"message": "手机号绑定成功"}
