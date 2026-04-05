"""
验收模块接口

架构文档V2.0要求：
- 国家规范验收标准库
- 节点与竣工验收流程管理
- 验收档案数字化管理
- 维保服务与工单管理
- 质保金管控
"""
from fastapi import APIRouter, Depends, UploadFile, File, Form
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

from src.api.endpoints.auth import get_current_user
from src.services.construction import STANDARD_NODES

router = APIRouter()


class AcceptanceCheckRequest(BaseModel):
    """验收检查请求"""
    node_id: str
    project_id: str
    check_items: List[dict] = []
    photos: List[str] = []
    notes: Optional[str] = None


class AcceptanceReportResponse(BaseModel):
    """验收报告响应"""
    report_id: str
    project_id: str
    node_id: str
    node_name: str
    status: str
    check_items: List[dict]
    photos: List[str]
    result: str  # passed, failed
    notes: Optional[str]
    checked_at: str
    checked_by: str


@router.get("/standards")
async def get_acceptance_standards():
    """
    获取国家规范验收标准库
    
    架构文档V2.0要求：
    - 基于GB 50327-2001等国家现行标准
    - 主控项-一般项分类
    - 大白话解读
    """
    standards = {
        "水电改造": {
            "name": "水电改造验收标准",
            "standards": [
                {"type": "主控项", "item": "电线必须穿管保护", "method": "目视检查", "result": "合格/不合格"},
                {"type": "主控项", "item": "水管打压测试0.6MPa，30分钟压降≤0.05MPa", "method": "打压测试", "result": "合格/不合格"},
                {"type": "一般项", "item": "水管横平竖直，间距均匀", "method": "目视检查", "result": "合格/不合格"},
                {"type": "一般项", "item": "强弱电间距≥30cm", "method": "尺量", "result": "合格/不合格"},
            ],
            "description": "大白话解读：电线必须穿管保护，不能裸线；水管要打压测试不漏水；"
        },
        "防水工程": {
            "name": "防水工程验收标准",
            "standards": [
                {"type": "主控项", "item": "闭水试验48小时无渗漏", "method": "闭水测试", "result": "合格/不合格"},
                {"type": "主控项", "item": "防水涂刷高度：淋浴区≥180cm，其他≥30cm", "method": "尺量", "result": "合格/不合格"},
                {"type": "一般项", "item": "防水层无裂纹、无气泡", "method": "目视检查", "result": "合格/不合格"},
            ],
            "description": "大白话解读：卫生间要泡水48小时不漏才算过关；"
        },
        "泥瓦工程": {
            "name": "泥瓦工程验收标准",
            "standards": [
                {"type": "主控项", "item": "瓷砖空鼓率≤5%", "method": "敲击检查", "result": "合格/不合格"},
                {"type": "一般项", "item": "瓷砖接缝均匀，十字缝对齐", "method": "目视检查", "result": "合格/不合格"},
                {"type": "一般项", "item": "地面找平平整度≤3mm/2m", "method": "靠尺测量", "result": "合格/不合格"},
            ],
            "description": "大白话解读：敲瓷砖不能有空空空的声音；"
        },
        "木工工程": {
            "name": "木工工程验收标准",
            "standards": [
                {"type": "主控项", "item": "吊顶结构稳固，无松动", "method": "摇晃测试", "result": "合格/不合格"},
                {"type": "一般项", "item": "板面光滑，无毛刺", "method": "目视/手摸", "result": "合格/不合格"},
            ],
            "description": "大白话解读：吊顶要牢固，不能晃动；"
        },
        "油漆工程": {
            "name": "油漆工程验收标准",
            "standards": [
                {"type": "主控项", "item": "墙面平整度≤2mm/2m", "method": "靠尺测量", "result": "合格/不合格"},
                {"type": "主控项", "item": "无色差、无流坠、无裂纹", "method": "目视检查", "result": "合格/不合格"},
                {"type": "一般项", "item": "阴阳角顺直", "method": "目视检查", "result": "合格/不合格"},
            ],
            "description": "大白话解读：墙面要摸起来平平的，不能有疙瘩；"
        }
    }
    
    return {
        "success": True,
        "total": len(standards),
        "standards": standards
    }


@router.get("/node-checklist/{node_id}")
async def get_node_checklist(
    node_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    获取节点验收清单
    
    架构文档V2.0要求：
    - 自动生成对应节点的验收清单
    - 包含验收项、标准、施工资料
    """
    node_map = {
        "electrical": "水电改造",
        "waterproof": "防水工程",
        "tiling": "泥瓦工程",
        "carpentry": "木工工程",
        "painting": "油漆工程",
        "installation": "安装工程",
        "acceptance": "竣工验收"
    }
    
    node_name = node_map.get(node_id, node_id)
    
    return {
        "success": True,
        "node_id": node_id,
        "node_name": node_name,
        "checklist": [
            {"id": f"{node_id}_1", "item": f"{node_name}验收项1", "standard": "符合规范", "method": "检查方法"},
            {"id": f"{node_id}_2", "item": f"{node_name}验收项2", "standard": "符合规范", "method": "检查方法"},
        ]
    }


@router.post("/submit")
async def submit_acceptance(
    request: AcceptanceCheckRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    提交验收申请
    
    架构文档V2.0要求：
    - 标准化验收流程
    - 支持线上云验收
    """
    report_id = f"acceptance_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    # 统计验收结果
    passed_items = sum(1 for item in request.check_items if item.get("result") == "passed")
    total_items = len(request.check_items)
    
    result = "passed" if passed_items == total_items else "failed"
    
    return {
        "success": True,
        "report_id": report_id,
        "result": result,
        "passed_count": passed_items,
        "total_count": total_items,
        "message": "验收通过" if result == "passed" else "验收不通过，请整改后重新申请"
    }


@router.get("/report/{report_id}")
async def get_acceptance_report(
    report_id: str,
    current_user: dict = Depends(get_current_user)
):
    """获取验收报告"""
    return {
        "success": True,
        "report_id": report_id,
        "project_id": "project_001",
        "node_id": "electrical",
        "node_name": "水电改造",
        "status": "completed",
        "result": "passed",
        "check_items": [],
        "photos": [],
        "notes": None,
        "checked_at": datetime.now().isoformat(),
        "checked_by": current_user.get("phone", "")
    }


@router.get("/my-reports")
async def get_my_acceptance_reports(
    project_id: Optional[str] = None,
    current_user: dict = Depends(get_current_user),
    limit: int = 10,
    offset: int = 0
):
    """获取我的验收报告列表"""
    return {
        "success": True,
        "reports": [],
        "total": 0,
        "limit": limit,
        "offset": offset
    }


@router.get("/warranty/{project_id}")
async def get_warranty_info(
    project_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    获取维保信息
    
    架构文档V2.0要求：
    - 竣工后自动进入维保周期
    - 明确质保期限、范围
    """
    return {
        "success": True,
        "project_id": project_id,
        "warranty_start": "2026-04-01",
        "warranty_end": "2028-03-31",
        "warranty_period": "2年",
        "scope": [
            "水路工程质保",
            "电路工程质保",
            "防水工程质保(5年)"
        ],
        "exclusions": [
            "人为损坏",
            "不可抗力",
            "使用不当"
        ],
        "status": "active"
    }
