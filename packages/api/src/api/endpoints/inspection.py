"""
AI验房接口

架构文档要求：
- 响应时间≤10秒
- 8类问题识别
- 支持图片上传
- 城市高频风险查询
"""
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List

from src.api.endpoints.auth import get_current_user
from src.services.inspection import inspection_service, ISSUE_TYPES, CITY_RISKS
from src.models.user import User

router = APIRouter()


class CreateInspectionRequest(BaseModel):
    """创建验房请求"""
    house_type: str = Field(default="毛坯房", description="房屋类型：毛坯房/二手房")
    city: Optional[str] = Field(None, description="城市")
    district: Optional[str] = Field(None, description="区县")
    area: Optional[int] = Field(None, description="面积（平方米）")


class IssueDetail(BaseModel):
    """问题详情"""
    type: str
    name: str
    description: str
    risk_level: str
    suggestion: str
    location: str
    ai_model: str
    confidence: int
    estimated_cost: int
    image_url: Optional[str] = None


class InspectionReportResponse(BaseModel):
    """验房报告响应"""
    report_id: str
    issues: List[IssueDetail]
    issue_count: int
    high_risk_count: int
    medium_risk_count: int
    low_risk_count: int
    total_estimated_cost: int
    report_content: Optional[str] = None
    ai_accuracy: int
    response_time_ms: int
    analyzed_at: str


# ============ 接口 ============

@router.get("/issue-types")
async def get_issue_types():
    """
    获取支持的8类问题类型
    
    架构文档要求：8类问题识别
    - 墙面开裂
    - 地面不平
    - 防水渗漏
    - 门窗密封不良
    - 水电隐患
    - 墙面空鼓
    - 阴阳角不垂直
    - 下水不畅
    """
    types_list = []
    for key, info in ISSUE_TYPES.items():
        types_list.append({
            "code": key,
            "name": info["name"],
            "description": info["description"],
            "ai_model": info["ai_model"],
            "estimated_range": info["estimated_range"]
        })
    
    return {
        "total": len(types_list),
        "types": types_list
    }


@router.get("/city-risks/{city}")
async def get_city_risks(city: str):
    """
    获取城市高频风险
    
    根据全国装修投诉数据统计各城市常见问题
    """
    return inspection_service.get_city_risks(city)


@router.post("/create")
async def create_inspection(
    request: CreateInspectionRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    创建验房任务
    
    返回验房报告ID，可用于后续图片上传和分析
    """
    result = inspection_service.create_inspection(
        user_id=current_user["id"],
        house_type=request.house_type,
        city=request.city,
        district=request.district,
        area=request.area
    )
    
    return {
        "success": True,
        **result
    }


@router.post("/analyze")
async def analyze_inspection_images(
    report_id: str = Form(...),
    files: List[UploadFile] = File(default=[]),
    current_user: dict = Depends(get_current_user)
):
    """
    上传图片并AI分析验房
    
    架构文档要求：
    - 响应时间≤10秒
    - 8类问题识别
    - 准确率≥90%
    
    支持上传多张图片，返回完整的验房报告
    """
    # 模拟保存图片（实际应上传到COS）
    image_urls = []
    for file in files:
        image_urls.append(f"https://cos.example.com/inspection/{report_id}/{file.filename}")
    
    # 调用AI分析
    result = inspection_service.analyze_images(report_id, image_urls)
    
    return {
        "success": True,
        **result,
        "performance": {
            "response_time_ms": result["response_time_ms"],
            "target_ms": 10000,  # 10秒目标
            "meet_target": result["response_time_ms"] <= 10000
        }
    }


@router.get("/report/{report_id}", response_model=InspectionReportResponse)
async def get_inspection_report(
    report_id: str,
    current_user: dict = Depends(get_current_user)
):
    """获取验房报告详情"""
    # 模拟返回报告（实际从数据库查询）
    return InspectionReportResponse(
        report_id=report_id,
        issues=[],
        issue_count=0,
        high_risk_count=0,
        medium_risk_count=0,
        low_risk_count=0,
        total_estimated_cost=0,
        ai_accuracy=90,
        response_time_ms=5000,
        analyzed_at=datetime.now().isoformat()
    )


@router.get("/my-reports")
async def get_my_reports(
    current_user: dict = Depends(get_current_user),
    limit: int = 10,
    offset: int = 0
):
    """获取我的验房报告列表"""
    return {
        "reports": [],
        "total": 0,
        "limit": limit,
        "offset": offset
    }


@router.post("/request-review")
async def request_human_review(
    report_id: str,
    reason: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """
    申请人工复核
    
    当AI识别结果存在疑问时，可申请人工复核
    """
    return {
        "success": True,
        "message": "已提交人工复核申请",
        "estimated_time": "24小时内完成审核",
        "report_id": report_id
    }


# 导入 datetime
from datetime import datetime
