"""
认证接口
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field, field_validator
from typing import Optional

from src.core.database import get_db
from src.core.security import create_access_token, decode_access_token, get_password_hash
from src.models.user import User, LoginLog
from src.services.sms import send_sms_code, verify_sms_code

router = APIRouter()
security = HTTPBearer(auto_error=False)


# ============ 请求模型 ============

class SendCodeRequest(BaseModel):
    """发送验证码请求"""
    phone: str = Field(..., description="手机号")
    
    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: str) -> str:
        import re
        if not re.match(r"^1[3-9]\d{9}$", v):
            raise ValueError("手机号格式不正确")
        return v


class LoginRequest(BaseModel):
    """手机号验证码登录请求"""
    phone: str = Field(..., description="手机号")
    code: str = Field(..., min_length=6, max_length=6, description="验证码")
    
    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: str) -> str:
        import re
        if not re.match(r"^1[3-9]\d{9}$", v):
            raise ValueError("手机号格式不正确")
        return v


class LoginPasswordRequest(BaseModel):
    """手机号密码登录请求"""
    phone: str = Field(..., description="手机号")
    password: str = Field(..., min_length=6, description="密码")


class RegisterRequest(BaseModel):
    """注册请求"""
    phone: str = Field(..., description="手机号")
    code: str = Field(..., min_length=6, max_length=6, description="验证码")
    password: Optional[str] = Field(None, min_length=6, description="密码（可选）")
    nickname: Optional[str] = Field(None, max_length=50, description="昵称")


# ============ 响应模型 ============

class UserInfo(BaseModel):
    """用户信息"""
    id: str
    phone: str
    nickname: Optional[str] = None
    avatar: Optional[str] = None
    role: str
    is_pro: bool = False
    pro_expire_time: Optional[str] = None
    created_at: str
    
    class Config:
        from_attributes = True


class LoginResponse(BaseModel):
    """登录响应"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int = 10080  # 分钟
    user: UserInfo


class SendCodeResponse(BaseModel):
    """发送验证码响应"""
    success: bool
    message: str
    expire_minutes: int = 5


# ============ 依赖项 ============

async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False)),
    db: AsyncSession = Depends(get_db)
) -> User:
    """获取当前用户"""
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="未登录",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    token = credentials.credentials
    payload = decode_access_token(token)
    
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
    
    user = await User.get_by_id(db, user_id)
    if not user or user.status.value == "deleted":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户不存在",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    return user


# ============ 接口 ============

@router.post("/send-code", response_model=SendCodeResponse)
async def send_code(
    request: SendCodeRequest,
    db: AsyncSession = Depends(get_db)
):
    """发送短信验证码"""
    try:
        code = await send_sms_code(request.phone)
        return SendCodeResponse(
            success=True,
            message="验证码已发送",
            expire_minutes=5
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="发送失败，请稍后重试"
        )


@router.post("/login", response_model=LoginResponse)
async def login(
    request: LoginRequest,
    req: Request,
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
        # 新用户自动注册
        user = await User.create(db, phone=request.phone)
    
    # 更新登录信息
    client_ip = req.client.host if req.client else None
    await user.update_login(db, ip=client_ip)
    await db.commit()
    
    # 记录登录日志
    login_log = LoginLog(
        user_id=user.id,
        phone=user.phone,
        ip=client_ip,
        status="success"
    )
    db.add(login_log)
    await db.commit()
    
    # 生成Token
    access_token = create_access_token(data={"sub": user.id})
    
    return LoginResponse(
        access_token=access_token,
        user=UserInfo(
            id=user.id,
            phone=user.phone,
            nickname=user.nickname,
            avatar=user.avatar,
            role=user.role.value,
            is_pro=user.is_pro,
            pro_expire_time=user.pro_expire_time.isoformat() if user.pro_expire_time else None,
            created_at=user.created_at.isoformat()
        )
    )


@router.post("/login/password", response_model=LoginResponse)
async def login_password(
    request: LoginPasswordRequest,
    req: Request,
    db: AsyncSession = Depends(get_db)
):
    """手机号密码登录"""
    from src.core.security import verify_password
    
    user = await User.get_by_phone(db, request.phone)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="手机号或密码错误"
        )
    
    if not user.password_hash or not verify_password(request.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="手机号或密码错误"
        )
    
    # 更新登录信息
    client_ip = req.client.host if req.client else None
    await user.update_login(db, ip=client_ip)
    await db.commit()
    
    # 生成Token
    access_token = create_access_token(data={"sub": user.id})
    
    return LoginResponse(
        access_token=access_token,
        user=UserInfo(
            id=user.id,
            phone=user.phone,
            nickname=user.nickname,
            avatar=user.avatar,
            role=user.role.value,
            is_pro=user.is_pro,
            pro_expire_time=user.pro_expire_time.isoformat() if user.pro_expire_time else None,
            created_at=user.created_at.isoformat()
        )
    )


@router.post("/register", response_model=LoginResponse)
async def register(
    request: RegisterRequest,
    req: Request,
    db: AsyncSession = Depends(get_db)
):
    """用户注册"""
    # 验证验证码
    if not await verify_sms_code(request.phone, request.code):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="验证码错误或已过期"
        )
    
    # 检查手机号是否已注册
    existing_user = await User.get_by_phone(db, request.phone)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="该手机号已注册"
        )
    
    # 创建用户
    user_data = {
        "phone": request.phone,
        "nickname": request.nickname
    }
    if request.password:
        user_data["password_hash"] = get_password_hash(request.password)
    
    user = await User.create(db, **user_data)
    await db.commit()
    
    # 记录登录日志
    client_ip = req.client.host if req.client else None
    login_log = LoginLog(
        user_id=user.id,
        phone=user.phone,
        ip=client_ip,
        status="success"
    )
    db.add(login_log)
    await db.commit()
    
    # 生成Token
    access_token = create_access_token(data={"sub": user.id})
    
    return LoginResponse(
        access_token=access_token,
        user=UserInfo(
            id=user.id,
            phone=user.phone,
            nickname=user.nickname,
            avatar=user.avatar,
            role=user.role.value,
            is_pro=user.is_pro,
            pro_expire_time=None,
            created_at=user.created_at.isoformat()
        )
    )


@router.get("/me", response_model=UserInfo)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """获取当前用户信息"""
    return UserInfo(
        id=current_user.id,
        phone=current_user.phone,
        nickname=current_user.nickname,
        avatar=current_user.avatar,
        role=current_user.role.value,
        is_pro=current_user.is_pro,
        pro_expire_time=current_user.pro_expire_time.isoformat() if current_user.pro_expire_time else None,
        created_at=current_user.created_at.isoformat()
    )


@router.post("/logout")
async def logout(
    current_user: User = Depends(get_current_user)
):
    """退出登录（前端删除Token即可）"""
    return {"message": "已退出登录"}


@router.post("/change-password")
async def change_password(
    old_password: str,
    new_password: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """修改密码"""
    from src.core.security import verify_password, get_password_hash
    
    if not current_user.password_hash:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="您还未设置密码"
        )
    
    if not verify_password(old_password, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="原密码错误"
        )
    
    current_user.password_hash = get_password_hash(new_password)
    await db.commit()
    
    return {"message": "密码修改成功"}


@router.post("/bind-phone")
async def bind_phone(
    phone: str,
    code: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """绑定手机号"""
    # 验证验证码
    if not await verify_sms_code(phone, code):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="验证码错误或已过期"
        )
    
    # 检查手机号是否已被绑定
    existing = await User.get_by_phone(db, phone)
    if existing and existing.id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="该手机号已被其他账号绑定"
        )
    
    current_user.phone = phone
    await db.commit()
    
    return {"message": "手机号绑定成功"}