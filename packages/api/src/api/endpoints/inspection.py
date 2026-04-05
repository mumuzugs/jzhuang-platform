"""
验房接口 - 简化版
"""
from fastapi import APIRouter, Depends, UploadFile, File, Form
from pydantic import BaseModel, Field
from typing import Optional, List

from src.api.endpoints.auth import get_current_user
from src.services.inspection import ISSUE_TYPES, CITY_RISKS, inspection_service

router = APIRouter()


class CreateInspectionRequest(BaseModel):
    house_type: str = Field(default="毛坯房")
    city: Optional[str] = None
    district: Optional[str] = None
    area: Optional[int] = None


@router.get("/issue-types")
async def get_issue_types():
    """获取支持的问题类型"""
    return {"types": ISSUE_TYPES}


@router.get("/city-risks/{city}")
async def get_city_risks(city: str):
    """获取城市高频风险"""
    risks = CITY_RISKS.get(city, ["墙面开裂", "地面不平", "水电隐患"])
    return {"city": city, "risks": risks}


@router.post("/create")
async def create_inspection(
    request: CreateInspectionRequest,
    current_user: dict = Depends(get_current_user)
):
    """创建验房任务"""
    result = inspection_service.create_inspection(
        user_id=current_user["id"],
        house_type=request.house_type,
        city=request.city,
        district=request.district,
        area=request.area
    )
    return result


@router.post("/analyze")
async def analyze_inspection_images(
    report_id: str = Form(...),
    files: List[UploadFile] = File(default=[]),
    current_user: dict = Depends(get_current_user)
):
    """分析验房图片"""
    image_urls = [f"https://storage.example.com/images/{file.filename}" for file in files]
    
    result = inspection_service.analyze_images(report_id, image_urls)
    
    return {
        "success": True,
        "report_id": report_id,
        "issues": result["issues"],
        "high_risk_count": result["high_risk_count"],
        "medium_risk_count": result["medium_risk_count"],
        "low_risk_count": result["low_risk_count"],
        "summary": {
            "total": len(result["issues"]),
            "high": result["high_risk_count"],
            "medium": result["medium_risk_count"],
            "low": result["low_risk_count"]
        }
    }


@router.get("/report/{report_id}")
async def get_inspection_report(
    report_id: str,
    current_user: dict = Depends(get_current_user)
):
    """获取验房报告"""
    return {
        "id": report_id,
        "user_id": current_user["id"],
        "house_type": "毛坯房",
        "city": "北京",
        "district": "朝阳",
        "area": 120,
        "status": "completed",
        "high_risk_count": 2,
        "medium_risk_count": 3,
        "low_risk_count": 2,
        "issues": [
            {"type": "wall_crack", "name": "墙面开裂", "description": "客厅墙面有裂缝", "risk_level": "high", "suggestion": "需要修补", "location": "客厅", "confidence": 95, "estimated_cost": 500}
        ],
        "created_at": "2026-04-06T00:30:00"
    }


@router.get("/my-reports")
async def get_my_reports(
    current_user: dict = Depends(get_current_user),
    limit: int = 10,
    offset: int = 0
):
    """获取我的验房报告列表"""
    return {"reports": [], "total": 0, "limit": limit, "offset": offset}


@router.post("/request-review")
async def request_human_review(
    report_id: str,
    current_user: dict = Depends(get_current_user)
):
    """申请人工复核"""
    return {"success": True, "message": "已提交人工复核申请，24小时内完成审核"}
