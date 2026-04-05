"""
施工接口 - 简化版
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
    name: str
    design_project_id: Optional[str] = None
    address: Optional[str] = None
    area: Optional[int] = None
    total_cycle: int = 60


class UpdateNodeRequest(BaseModel):
    node_id: str
    progress: int
    status: Optional[str] = None


@router.get("/standard-nodes")
async def get_standard_nodes():
    """获取标准施工节点"""
    return STANDARD_NODES


@router.post("/create")
async def create_project(
    request: CreateProjectRequest,
    current_user: dict = Depends(get_current_user)
):
    """创建装修项目"""
    project_id = f"construction_{current_user['id']}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    plan = await construction_service.generate_plan(
        project_id=project_id,
        total_cycle=request.total_cycle
    )
    
    return {
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
    """获取项目进度"""
    return {
        "project_id": project_id,
        "total_progress": 45,
        "pending_nodes": 3,
        "in_progress_nodes": 2,
        "completed_nodes": 3,
        "overdue_nodes": 0
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
    return result


@router.post("/supervision/upload")
async def upload_site_photo(
    project_id: str = Form(...),
    node_id: Optional[str] = Form(None),
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user)
):
    """上传工地照片"""
    image_url = f"https://storage.example.com/sites/{project_id}/{file.filename}"
    
    recognition = await cloud_supervision_service.recognize_progress(project_id, image_url)
    anomalies = await cloud_supervision_service.check_anomalies(project_id, image_url, recognition.get("detected_stage", ""))
    archive = await cloud_supervision_service.archive_photos(project_id, node_id or "", image_url)
    
    return {
        "success": True,
        "image_url": image_url,
        "recognition": recognition,
        "anomalies": anomalies,
        "archive": archive
    }


@router.get("/my-projects")
async def get_my_projects(
    current_user: dict = Depends(get_current_user),
    limit: int = 10,
    offset: int = 0
):
    """获取我的装修项目"""
    return {"projects": [], "total": 0}


@router.post("/node/acceptance")
async def submit_acceptance(
    node_id: str,
    comment: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """提交节点验收"""
    return {"success": True, "node_id": node_id, "status": "passed", "message": "验收通过"}
