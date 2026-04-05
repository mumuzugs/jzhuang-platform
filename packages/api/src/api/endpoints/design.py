"""
设计接口 - 简化版
"""
from fastapi import APIRouter, Depends, UploadFile, File, Form
from pydantic import BaseModel, Field
from typing import Optional, List

from src.api.endpoints.auth import get_current_user
from src.services.design import design_service, STYLES, LAYOUTS
from src.services.budget import budget_service

router = APIRouter()


class GenerateLayoutsRequest(BaseModel):
    project_id: str
    area: int
    rooms: int
    style: Optional[str] = None
    layout_type: Optional[str] = None


class CalculateBudgetRequest(BaseModel):
    project_id: str
    materials: List[dict]
    city: Optional[str] = "默认"
    budget_limit: Optional[int] = None


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
    house_type: Optional[str] = None,
    area: Optional[int] = None,
    city: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """创建设计项目"""
    result = await design_service.create_project(
        user_id=current_user["id"],
        house_type=house_type,
        area=area,
        city=city
    )
    return result


@router.post("/generate-layouts")
async def generate_layouts(
    request: GenerateLayoutsRequest,
    current_user: dict = Depends(get_current_user)
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
    current_user: dict = Depends(get_current_user)
):
    """生成效果图"""
    images = await design_service.generate_render_images(project_id, style)
    return {"images": images}


@router.post("/generate-drawings")
async def generate_drawings(
    project_id: str = Form(...),
    current_user: dict = Depends(get_current_user)
):
    """生成施工图"""
    drawings = await design_service.generate_construction_drawings(project_id)
    return {"drawings": drawings}


@router.post("/generate-materials")
async def generate_materials(
    project_id: str = Form(...),
    style: str = Form(...),
    area: int = Form(...),
    current_user: dict = Depends(get_current_user)
):
    """生成材料清单"""
    materials = await design_service.generate_material_list(project_id, area, style)
    return {"materials": materials}


@router.post("/calculate-budget")
async def calculate_budget(
    request: CalculateBudgetRequest,
    current_user: dict = Depends(get_current_user)
):
    """计算预算"""
    result = await budget_service.calculate_budget(
        project_id=request.project_id,
        materials=request.materials,
        city=request.city
    )
    
    if request.budget_limit:
        warning = await budget_service.check_budget_warning(
            result["summary"]["total_cost"],
            request.budget_limit
        )
        result["budget_warning"] = warning
    
    return result


@router.get("/my-projects")
async def get_my_projects(
    current_user: dict = Depends(get_current_user),
    limit: int = 10,
    offset: int = 0
):
    """获取我的设计方案"""
    return {"projects": [], "total": 0}
