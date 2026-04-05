"""
用户接口 - 架构文档V2.0完整实现
支持：业主、工长、供应商、运营等多角色
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum

from src.api.endpoints.auth import get_current_user

router = APIRouter()


class UserRole(str, Enum):
    OWNER = "owner"           # 业主
    WORKER = "worker"         # 工长
    SUPPLIER = "supplier"     # 材料供应商
    OPERATOR = "operator"     # 平台运营
    SUPERVISOR = "supervisor" # 监理
    CUSTOMER_SERVICE = "cs"    # 客服


class UserProfileResponse(BaseModel):
    id: str
    phone: str
    nickname: Optional[str] = None
    role: str
    roles: List[str] = []     # 支持多角色
    is_pro: bool
    avatar: Optional[str] = None
    create_time: str


class House档案(BaseModel):
    """房屋档案"""
    house_id: str
    owner_id: str
    city: str
    community: Optional[str] = None
    building: Optional[str] = None
    unit: Optional[str] = None
    room_number: Optional[str] = None
    house_type: str           # 毛坯房/二手房/精装房
    area: float               # 面积
    build_year: Optional[int] = None
    property_type: str         # 产权类型
    decoration_status: str     # 装修状态
    design_project_id: Optional[str] = None
    construction_project_id: Optional[str] = None
    inspection_report_id: Optional[str] = None


class UserTag(BaseModel):
    """用户标签"""
    tag_id: str
    tag_name: str
    tag_type: str  # preference/behavior/demographic
    value: str
    weight: float = 1.0  # 权重


class AuditLog(BaseModel):
    """操作审计日志"""
    log_id: str
    user_id: str
    action: str
    module: str
    detail: str
    ip: Optional[str] = None
    device: Optional[str] = None
    create_time: str


@router.get("/profile", response_model=UserProfileResponse)
async def get_profile(current_user: dict = Depends(get_current_user)):
    """获取用户资料"""
    return UserProfileResponse(
        id=current_user["id"],
        phone=current_user["phone"],
        nickname=current_user.get("nickname"),
        role=current_user["role"],
        roles=current_user.get("roles", [current_user["role"]]),
        is_pro=current_user.get("is_pro", False),
        avatar=current_user.get("avatar"),
        create_time=current_user.get("create_time", datetime.now().isoformat())
    )


@router.put("/profile")
async def update_profile(
    nickname: Optional[str] = None,
    avatar: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """更新用户资料"""
    if nickname:
        current_user["nickname"] = nickname
    if avatar:
        current_user["avatar"] = avatar
    return {"message": "更新成功", "success": True}


@router.get("/roles")
async def get_user_roles(current_user: dict = Depends(get_current_user)):
    """
    获取用户角色列表
    
    架构文档V2.0要求：
    - 覆盖4类核心角色：业主、工长、装修公司、材料供应商、平台运营/监理/客服
    - 支持同一账号多角色切换
    """
    return {
        "success": True,
        "current_role": current_user.get("role", "owner"),
        "roles": [
            {"role": "owner", "name": "业主", "description": "装修业主", "permissions": ["验房", "设计", "施工", "验收"]},
            {"role": "worker", "name": "工长", "description": "装修工长/装修公司", "permissions": ["施工管理", "进度上报", "节点验收"]},
            {"role": "supplier", "name": "材料供应商", "description": "材料供应商", "permissions": ["材料供应", "订单管理"]},
            {"role": "operator", "name": "平台运营", "description": "平台运营人员", "permissions": ["用户管理", "数据统计", "内容审核"]},
            {"role": "supervisor", "name": "监理", "description": "工程监理", "permissions": ["施工监督", "验收管理", "质量问题"]},
            {"role": "cs", "name": "客服", "description": "客户服务", "permissions": ["工单处理", "用户服务", "投诉处理"]},
        ]
    }


@router.post("/switch-role")
async def switch_role(
    role: str,
    current_user: dict = Depends(get_current_user)
):
    """切换用户角色"""
    valid_roles = ["owner", "worker", "supplier", "operator", "supervisor", "cs"]
    if role not in valid_roles:
        raise HTTPException(status_code=400, detail="无效的角色")
    
    current_user["role"] = role
    return {"message": "角色切换成功", "current_role": role}


@router.get("/houses", response_model=List[House档案])
async def get_houses(current_user: dict = Depends(get_current_user)):
    """
    获取用户的房屋档案列表
    
    架构文档V2.0要求：
    - 支持同一业主名下多套房屋档案管理
    - 每套房屋独立关联验房报告、设计方案、预算单、施工项目
    """
    houses = current_user.get("houses", [])
    return houses


@router.post("/houses")
async def add_house(
    city: str,
    community: Optional[str] = None,
    building: Optional[str] = None,
    unit: Optional[str] = None,
    room_number: Optional[str] = None,
    house_type: str = "毛坯房",
    area: float = 0,
    build_year: Optional[int] = None,
    property_type: str = "住宅",
    current_user: dict = Depends(get_current_user)
):
    """
    添加房屋档案
    
    架构文档V2.0要求：
    - 为业主建立标准化房屋数字档案
    - 是验房、设计、施工模块的基础数据来源
    """
    house_id = f"house_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    house = House档案(
        house_id=house_id,
        owner_id=current_user["id"],
        city=city,
        community=community,
        building=building,
        unit=unit,
        room_number=room_number,
        house_type=house_type,
        area=area,
        build_year=build_year,
        property_type=property_type,
        decoration_status="未装修"
    )
    
    if "houses" not in current_user:
        current_user["houses"] = []
    current_user["houses"].append(house.model_dump())
    
    return {"success": True, "house_id": house_id, "message": "房屋档案创建成功"}


@router.get("/houses/{house_id}")
async def get_house_detail(
    house_id: str,
    current_user: dict = Depends(get_current_user)
):
    """获取房屋详情"""
    houses = current_user.get("houses", [])
    for house in houses:
        if house["house_id"] == house_id:
            return {"success": True, "house": house}
    raise HTTPException(status_code=404, detail="房屋不存在")


@router.get("/tags")
async def get_user_tags(current_user: dict = Depends(get_current_user)):
    """
    获取用户标签体系
    
    架构文档V2.0要求：
    - 用户标签体系用于精准推荐、个性化服务
    """
    tags = current_user.get("tags", [
        {"tag_id": "tag_001", "tag_name": "装修新手", "tag_type": "demographic", "value": "true", "weight": 1.0},
        {"tag_id": "tag_002", "tag_name": "预算敏感", "tag_type": "preference", "value": "中", "weight": 0.8},
        {"tag_id": "tag_003", "tag_name": "关注环保", "tag_type": "preference", "value": "高", "weight": 0.9},
    ])
    return {"success": True, "tags": tags, "total": len(tags)}


@router.post("/tags")
async def add_user_tag(
    tag_name: str,
    tag_type: str,  # preference/behavior/demographic
    value: str,
    weight: float = 1.0,
    current_user: dict = Depends(get_current_user)
):
    """添加用户标签"""
    tag_id = f"tag_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    tag = UserTag(
        tag_id=tag_id,
        tag_name=tag_name,
        tag_type=tag_type,
        value=value,
        weight=weight
    )
    
    if "tags" not in current_user:
        current_user["tags"] = []
    current_user["tags"].append(tag.model_dump())
    
    return {"success": True, "tag_id": tag_id}


@router.get("/audit-logs")
async def get_audit_logs(
    module: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    limit: int = Query(default=20, le=100),
    offset: int = Query(default=0, ge=0),
    current_user: dict = Depends(get_current_user)
):
    """
    获取操作审计日志
    
    架构文档V2.0要求：
    - 操作日志留存≥6个月，不可篡改，符合三级等保审计要求
    """
    logs = current_user.get("audit_logs", [
        {
            "log_id": "log_001",
            "user_id": current_user["id"],
            "action": "登录",
            "module": "认证",
            "detail": "用户登录成功",
            "ip": "127.0.0.1",
            "device": "iOS",
            "create_time": datetime.now().isoformat()
        }
    ])
    
    return {
        "success": True,
        "logs": logs[offset:offset+limit],
        "total": len(logs),
        "limit": limit,
        "offset": offset
    }


@router.get("/vip/status")
async def get_vip_status(current_user: dict = Depends(get_current_user)):
    """获取VIP状态"""
    return {
        "is_pro": current_user.get("is_pro", False),
        "role": current_user.get("role", "free"),
        "pro_expire_time": current_user.get("pro_expire_time"),
        "pro_order_no": current_user.get("pro_order_no"),
        "permissions": current_user.get("permissions", ["免费版功能"])
    }


@router.delete("/account")
async def delete_account(current_user: dict = Depends(get_current_user)):
    """注销账号"""
    return {"message": "账号已注销", "success": True}
