"""
施工接口

架构文档要求：
- 标准化施工计划自动生成
- 8大核心节点管理
- 节点主动通知
- 延期预警
"""
from fastapi import APIRouter, Depends, UploadFile, File, Form
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

from src.api.endpoints.auth import get_current_user
from src.services.construction import construction_service, STANDARD_NODES
from src.services.supervision import cloud_supervision_service

router = APIRouter()


class CreateProjectRequest(BaseModel):
    """创建装修项目请求"""
    name: str
    design_project_id: Optional[str] = None
    address: Optional[str] = None
    area: Optional[int] = None
    total_cycle: int = Field(60, description="总工期（天）")
    start_date: Optional[str] = None


class UpdateNodeRequest(BaseModel):
    """更新节点进度请求"""
    node_id: str
    progress: int = Field(..., ge=0, le=100)
    status: Optional[str] = None


# ============ 接口 ============

@router.get("/standard-nodes")
async def get_standard_nodes():
    """
    获取标准施工节点
    
    架构文档要求：8大核心节点
    1. 开工准备
    2. 水电改造
    3. 防水工程
    4. 泥瓦工程
    5. 木工工程
    6. 油漆工程
    7. 安装工程
    8. 竣工验收
    """
    return {
        "total": len(STANDARD_NODES),
        "nodes": STANDARD_NODES
    }


@router.post("/create")
async def create_project(
    request: CreateProjectRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    创建装修项目
    
    架构文档要求：
    - 根据设计方案和装修周期自动生成施工计划
    - 自动分配各节点时间
    """
    project_id = f"construction_{current_user['id']}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    start_date = None
    if request.start_date:
        start_date = datetime.fromisoformat(request.start_date)
    
    plan = await construction_service.generate_plan(
        project_id=project_id,
        total_cycle=request.total_cycle,
        start_date=start_date
    )
    
    return {
        "success": True,
        "project_id": project_id,
        "name": request.name,
        "total_cycle": request.total_cycle,
        "plan": plan
    }


@router.get("/project/{project_id}")
async def get_project(
    project_id: str,
    current_user: dict = Depends(get_current_user)
):
    """获取项目详情"""
    return {
        "project_id": project_id,
        "status": "in_progress",
        "progress": 45,
        "nodes": []
    }


@router.get("/project/{project_id}/progress")
async def get_project_progress(
    project_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    获取项目进度
    
    架构文档要求：
    - 整体进度可视化
    - 延期自动预警
    """
    return {
        "project_id": project_id,
        "total_progress": 45,
        "pending_nodes": 3,
        "in_progress_nodes": 2,
        "completed_nodes": 3,
        "overdue_nodes": 0,
        "next_node": "木工工程",
        "next_deadline": "2026-04-15"
    }


@router.post("/node/update")
async def update_node(
    request: UpdateNodeRequest,
    current_user: dict = Depends(get_current_user)
):
    """更新节点进度"""
    result = await construction_service.update_node_progress(
        project_id="",
        node_id=request.node_id,
        progress=request.progress,
        status=request.status
    )
    return {"success": True, **result}


@router.post("/supervision/upload")
async def upload_site_photo(
    project_id: str = Form(...),
    node_id: Optional[str] = Form(None),
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user)
):
    """
    上传工地照片并AI分析
    
    架构文档要求：
    - 响应时间≤15秒
    - 准确率≥95%
    - 自动识别施工阶段
    - 检测异常问题
    """
    # 模拟保存图片
    image_url = f"https://cos.example.com/sites/{project_id}/{file.filename}"
    
    # AI识别进度
    recognition = await cloud_supervision_service.recognize_progress(project_id, image_url)
    
    # 检查异常
    anomalies = await cloud_supervision_service.check_anomalies(
        project_id, image_url, recognition.get("detected_stage", "")
    )
    
    # 归档照片
    archive = await cloud_supervision_service.archive_photos(
        project_id, node_id or "", image_url
    )
    
    return {
        "success": True,
        "image_url": image_url,
        "recognition": recognition,
        "anomalies": anomalies,
        "archive": archive,
        "performance": {
            "response_time_ms": recognition.get("response_time_ms", 0),
            "target_ms": 15000,
            "meet_target": recognition.get("response_time_ms", 15000) <= 15000
        }
    }


@router.post("/supervision/recognize")
async def recognize_progress(
    project_id: str,
    image_url: str,
    current_user: dict = Depends(get_current_user)
):
    """
    识别施工进度
    
    架构文档要求：
    - 施工进度识别准确率≥95%
    - 识别响应时间≤15秒
    """
    result = await cloud_supervision_service.recognize_progress(project_id, image_url)
    
    return {
        "success": True,
        **result,
        "performance": {
            "response_time_ms": result.get("response_time_ms", 0),
            "target_ms": 15000,
            "meet_target": result.get("response_time_ms", 15000) <= 15000
        }
    }


@router.post("/supervision/check-anomalies")
async def check_anomalies(
    project_id: str,
    image_url: str,
    stage: str,
    current_user: dict = Depends(get_current_user)
):
    """
    检查施工异常
    
    架构文档要求：
    - 核心异常问题识别准确率≥85%
    """
    result = await cloud_supervision_service.check_anomalies(project_id, image_url, stage)
    return {"success": True, **result}


@router.get("/my-projects")
async def get_my_projects(
    current_user: dict = Depends(get_current_user),
    limit: int = 10,
    offset: int = 0
):
    """获取我的装修项目列表"""
    return {"projects": [], "total": 0, "limit": limit, "offset": offset}


@router.post("/node/acceptance")
async def submit_acceptance(
    node_id: str,
    comment: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """
    提交节点验收
    
    架构文档要求：
    - 分阶段验收指导
    - 验收标准检查
    """
    return {
        "success": True,
        "node_id": node_id,
        "status": "passed",
        "message": "验收通过"
    }


@router.get("/notifications")
async def get_notifications(
    current_user: dict = Depends(get_current_user)
):
    """
    获取节点通知列表
    
    架构文档要求：
    - 6大核心节点开工前、完工后主动通知
    - 通知触达率≥99.9%
    """
    return {
        "notifications": [
            {
                "id": "notif_001",
                "type": "reminder",
                "title": "水电改造即将开始",
                "content": "您的装修项目即将进入水电改造阶段，请做好准备",
                "node": "水电改造",
                "time": "2026-04-10 09:00",
                "status": "unread"
            }
        ],
        "total": 1
    }
