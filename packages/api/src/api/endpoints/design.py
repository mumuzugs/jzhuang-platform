"""
设计接口
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field
from typing import Optional, List

from src.core.database import get_db
from src.models.user import User
from src.api.endpoints.auth import get_current_user
from src.services.design import design_service, STYLES, LAYOUTS
from src.services.budget import budget_service

router = APIRouter()


# ============ 请求/响应模型 ============

class CreateProjectRequest(BaseModel):
    house_type: Optional[str] = None
    area: Optional[int] = None
    city: Optional[str] = None


class GenerateLayoutsRequest(BaseModel):
    project_id: str
    area: int
    rooms: int
    style: Optional[str] = None
    layout_type: Optional[str] = None


class SelectLayoutRequest(BaseModel):
    project_id: str
    layout_id: str


class CalculateBudgetRequest(BaseModel):
    project_id: str
    materials: List[dict]
    city: Optional[str] = "默认"
    budget_limit: Optional[int] = None


# ============ 接口 ============

@router.get("/styles")
async def get_styles():
    """获取装修风格列表"""
    return STYLES


@router.get("/layouts")
async def get_layouts():
    """获取布局类型列表"""
    return LAYOUTS


@router.post("/create")
async def create_project(
    request: CreateProjectRequest,
    current_user: User = Depends(get_current_user)
):
    """创建设计项目"""
    result = await design_service.create_project(
        user_id=current_user.id,
        house_type=request.house_type,
        area=request.area,
        city=request.city
    )
    return result


@router.post("/analyze-layout")
async def analyze_layout(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    """分析户型图"""
    # 模拟保存
    layout_url = f"https://storage.example.com/layouts/{file.filename}"
    
    result = await design_service.analyze_layout(layout_url)
    return result


@router.post("/generate-layouts")
async def generate_layouts(
    request: GenerateLayoutsRequest,
    current_user: User = Depends(get_current_user)
):
    """生成3套平面布局方案"""
    layouts = await design_service.generate_layouts(
        project_id=request.project_id,
        area=request.area,
        rooms=request.rooms,
        style=request.style,
        layout_type=request.layout_type
    )
    return {"layouts": layouts}


@router.post("/generate-renders")
async def generate_renders(
    project_id: str = Form(...),
    style: str = Form(...),
    current_user: User = Depends(get_current_user)
):
    """生成效果图"""
    images = await design_service.generate_render_images(project_id, style)
    return {"images": images}


@router.post("/generate-drawings")
async def generate_drawings(
    project_id: str = Form(...),
    current_user: User = Depends(get_current_user)
):
    """生成施工图"""
    drawings = await design_service.generate_construction_drawings(project_id)
    return {"drawings": drawings}


@router.post("/generate-materials")
async def generate_materials(
    project_id: str = Form(...),
    style: str = Form(...),
    area: int = Form(...),
    current_user: User = Depends(get_current_user)
):
    """生成材料清单"""
    materials = await design_service.generate_material_list(project_id, area, style)
    return {"materials": materials}


@router.post("/calculate-budget")
async def calculate_budget(
    request: CalculateBudgetRequest,
    current_user: User = Depends(get_current_user)
):
    """计算预算"""
    result = await budget_service.calculate_budget(
        project_id=request.project_id,
        materials=request.materials,
        city=request.city
    )
    
    # 检查预算红线
    if request.budget_limit:
        warning = await budget_service.check_budget_warning(
            result["summary"]["total_cost"],
            request.budget_limit
        )
        result["budget_warning"] = warning
    
    return result


@router.post("/change-impact")
async def calculate_change_impact(
    project_id: str,
    change_type: str,
    change_param: dict,
    current_budget: dict,
    current_user: User = Depends(get_current_user)
):
    """计算变更影响"""
    impact = await budget_service.calculate_change_impact(
        project_id, change_type, change_param, current_budget
    )
    return impact


@router.get("/my-projects")
async def get_my_projects(
    current_user: User = Depends(get_current_user),
    limit: int = 10,
    offset: int = 0
):
    """获取我的设计方案"""
    return {"projects": [], "total": 0}