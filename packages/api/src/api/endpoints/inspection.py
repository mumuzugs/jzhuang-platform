"""
验房接口
"""
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field
from typing import Optional, List
import json

from src.core.database import get_db
from src.models.user import User
from src.api.endpoints.auth import get_current_user
from src.services.inspection import inspection_service, ISSUE_TYPES, CITY_RISKS

router = APIRouter()


# ============ 请求模型 ============

class CreateInspectionRequest(BaseModel):
    """创建验房请求"""
    house_type: str = Field(default="毛坯房", description="房屋类型")
    city: Optional[str] = Field(None, description="城市")
    district: Optional[str] = Field(None, description="区/县")
    area: Optional[int] = Field(None, description="面积")


class IssueResponse(BaseModel):
    """问题详情"""
    type: str
    name: str
    description: str
    risk_level: str
    suggestion: str
    location: str
    confidence: int
    estimated_cost: int


class InspectionReportResponse(BaseModel):
    """验房报告响应"""
    id: str
    user_id: str
    house_type: str
    city: Optional[str]
    district: Optional[str]
    area: Optional[int]
    status: str
    high_risk_count: int
    medium_risk_count: int
    low_risk_count: int
    report_content: Optional[str]
    issues: List[IssueResponse]
    created_at: str
    
    class Config:
        from_attributes = True


# ============ 接口 ============

@router.get("/issue-types")
async def get_issue_types():
    """获取支持的问题类型"""
    return ISSUE_TYPES


@router.get("/city-risks/{city}")
async def get_city_risks(city: str):
    """获取城市高频风险"""
    risks = CITY_RISKS.get(city, ["墙面开裂", "地面不平", "水电隐患"])
    return {"city": city, "risks": risks}


@router.post("/create", response_model=dict)
async def create_inspection(
    request: CreateInspectionRequest,
    current_user: User = Depends(get_current_user)
):
    """创建验房任务"""
    result = await inspection_service.create_inspection(
        user_id=current_user.id,
        house_type=request.house_type,
        city=request.city,
        district=request.district,
        area=request.area
    )
    
    return result


@router.post("/analyze")
async def analyze_inspection_images(
    report_id: str = Form(...),
    files: List[UploadFile] = File(...),
    current_user: User = Depends(get_current_user)
):
    """分析验房图片"""
    # 保存上传的图片（这里只是模拟保存）
    image_urls = []
    for file in files:
        # 实际应该保存到云存储
        image_urls.append(f"https://storage.example.com/images/{file.filename}")
    
    # 调用AI分析
    result = await inspection_service.analyze_images(report_id, image_urls)
    
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
    current_user: User = Depends(get_current_user)
):
    """获取验房报告"""
    # 模拟返回报告（实际从数据库查询）
    return {
        "id": report_id,
        "user_id": current_user.id,
        "house_type": "毛坯房",
        "city": "北京",
        "district": "朝阳",
        "area": 120,
        "status": "completed",
        "high_risk_count": 2,
        "medium_risk_count": 3,
        "low_risk_count": 2,
        "issues": [
            {
                "type": "wall_crack",
                "name": "墙面开裂",
                "description": "客厅墙面有裂缝",
                "risk_level": "high",
                "suggestion": "需要修补",
                "location": "客厅",
                "confidence": 95,
                "estimated_cost": 500
            }
        ],
        "created_at": "2026-04-05T12:00:00"
    }


@router.get("/my-reports")
async def get_my_reports(
    current_user: User = Depends(get_current_user),
    limit: int = 10,
    offset: int = 0
):
    """获取我的验房报告列表"""
    # 模拟返回列表
    return {
        "reports": [],
        "total": 0,
        "limit": limit,
        "offset": offset
    }


@router.post("/request-review")
async def request_human_review(
    report_id: str,
    current_user: User = Depends(get_current_user)
):
    """申请人工复核"""
    return {
        "success": True,
        "message": "已提交人工复核申请，24小时内完成审核"
    }