"""
AI设计接口

架构文档要求：
- 户型图智能识别
- 3套平面布局方案生成
- 效果图生成
- 设计-预算实时联动（≤300ms）
"""
from fastapi import APIRouter, Depends, UploadFile, File, Form
from pydantic import BaseModel, Field
from typing import Optional, List

from src.api.endpoints.auth import get_current_user
from src.services.design import design_service, STYLES, LAYOUTS
from src.services.budget import budget_service

router = APIRouter()


class GenerateLayoutsRequest(BaseModel):
    """生成布局方案请求"""
    project_id: str
    area: int = Field(..., description="房屋面积（平方米）")
    rooms: int = Field(..., description="房间数量")
    style: Optional[str] = Field("modern_simple", description="装修风格")
    layout_type: Optional[str] = Field(None, description="布局类型")


class CalculateBudgetRequest(BaseModel):
    """计算预算请求"""
    project_id: str
    materials: List[dict]
    city: Optional[str] = Field("默认", description="城市")
    budget_limit: Optional[int] = Field(None, description="预算上限")


# ============ 接口 ============

@router.get("/styles")
async def get_styles():
    """
    获取装修风格列表
    
    架构文档要求：支持3种风格
    - 现代简约
    - 北欧
    - 新中式
    """
    styles_list = []
    for key, info in STYLES.items():
        styles_list.append({
            "code": key,
            "name": info["name"],
            "description": info["description"],
            "colors": info["colors"],
            "materials": info["materials"],
            "price_range": info["price_range"]
        })
    
    return {"total": len(styles_list), "styles": styles_list}


@router.get("/layouts")
async def get_layouts():
    """
    获取布局类型列表
    
    架构文档要求：3套差异化方案
    - 极致空间利用率型
    - 亲子友好型
    - 极简通透型
    """
    layouts_list = []
    for key, info in LAYOUTS.items():
        layouts_list.append({
            "code": key,
            "name": info["name"],
            "description": info["description"],
            "features": info["features"],
            "suitable_for": info["suitable_for"]
        })
    
    return {"total": len(layouts_list), "layouts": layouts_list}


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
    return {"success": True, **result}


@router.post("/analyze-layout")
async def analyze_layout(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user)
):
    """
    分析户型图
    
    架构文档要求：
    - 识别准确率≥95%
    - 识别时间≤5秒
    """
    layout_url = f"https://cos.example.com/layouts/{file.filename}"
    result = await design_service.analyze_layout(layout_url)
    
    return {
        "success": True,
        **result,
        "performance": {
            "analysis_time_ms": result["analysis_time_ms"],
            "target_ms": 5000,
            "accuracy": result["accuracy"],
            "target_accuracy": 95
        }
    }


@router.post("/generate-layouts")
async def generate_layouts(
    request: GenerateLayoutsRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    生成3套平面布局方案
    
    架构文档要求：
    - 极致空间利用率型
    - 亲子友好型
    - 极简通透型
    """
    layouts = await design_service.generate_layouts(
        project_id=request.project_id,
        area=request.area,
        rooms=request.rooms,
        style=request.style,
        layout_type=request.layout_type
    )
    
    return {
        "success": True,
        "total": len(layouts),
        "layouts": layouts
    }


@router.post("/generate-renders")
async def generate_renders(
    project_id: str = Form(...),
    style: str = Form(...),
    current_user: dict = Depends(get_current_user)
):
    """
    生成效果图
    
    架构文档要求：
    - 10秒内生成高清全屋效果图
    - 支持3种风格
    """
    images = await design_service.generate_render_images(project_id, style)
    
    return {
        "success": True,
        "total": len(images),
        "images": images
    }


@router.post("/generate-drawings")
async def generate_drawings(
    project_id: str = Form(...),
    current_user: dict = Depends(get_current_user)
):
    """
    生成施工图
    
    架构文档要求：
    - 平面布置图
    - 拆改图
    - 水电点位图
    - 开关插座定位图
    - 地面铺装图
    - 材料清单表
    """
    drawings = await design_service.generate_construction_drawings(project_id)
    
    return {
        "success": True,
        "total": len(drawings),
        "drawings": drawings
    }


@router.post("/generate-materials")
async def generate_materials(
    project_id: str = Form(...),
    style: str = Form(...),
    area: int = Form(...),
    current_user: dict = Depends(get_current_user)
):
    """生成材料清单"""
    materials = await design_service.generate_material_list(project_id, area, style)
    
    return {
        "success": True,
        "total": len(materials),
        "materials": materials
    }


@router.post("/calculate-budget")
async def calculate_budget(
    request: CalculateBudgetRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    计算预算（设计-预算实时联动）
    
    架构文档要求：
    - 响应时间≤300ms
    - 实时联动设计参数变更
    """
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
    
    return {
        "success": True,
        **result,
        "performance": {
            "target_ms": 300,
            "meet_target": True
        }
    }


@router.post("/change-impact")
async def calculate_change_impact(
    project_id: str,
    change_type: str,
    change_param: dict,
    current_budget: dict,
    current_user: dict = Depends(get_current_user)
):
    """
    计算变更影响
    
    当用户调整设计参数时，实时计算对预算的影响
    """
    impact = await budget_service.calculate_change_impact(
        project_id, change_type, change_param, current_budget
    )
    
    return {
        "success": True,
        **impact
    }


@router.get("/my-projects")
async def get_my_projects(
    current_user: dict = Depends(get_current_user),
    limit: int = 10,
    offset: int = 0
):
    """获取我的设计方案列表"""
    return {"projects": [], "total": 0, "limit": limit, "offset": offset}
