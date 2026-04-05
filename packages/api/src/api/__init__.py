"""
API 路由
"""
from fastapi import APIRouter

api_router = APIRouter()

def include_routers():
    from src.api.endpoints import auth, users, design, inspection, construction, payment, acceptance
    
    api_router.include_router(auth.router, prefix="/auth", tags=["认证"])
    api_router.include_router(users.router, prefix="/users", tags=["用户"])
    api_router.include_router(design.router, prefix="/design", tags=["设计"])
    api_router.include_router(inspection.router, prefix="/inspection", tags=["验房"])
    api_router.include_router(construction.router, prefix="/construction", tags=["施工"])
    api_router.include_router(payment.router, prefix="/payment", tags=["支付"])
    api_router.include_router(acceptance.router, prefix="/acceptance", tags=["验收"])

include_routers()
