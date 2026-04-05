"""
API 路由
"""
from fastapi import APIRouter

from src.api.endpoints import users, auth, design, inspection, construction, payment

router = APIRouter()

# 注册各模块路由
router.include_router(auth.router, prefix="/auth", tags=["认证"])
router.include_router(users.router, prefix="/users", tags=["用户"])
router.include_router(design.router, prefix="/design", tags=["设计"])
router.include_router(inspection.router, prefix="/inspection", tags=["验房"])
router.include_router(construction.router, prefix="/construction", tags=["施工"])
router.include_router(payment.router, prefix="/payment", tags=["支付"])