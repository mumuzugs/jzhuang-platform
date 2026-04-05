"""
施工计划服务
"""
import logging
from datetime import datetime, timedelta
from typing import Optional, List

logger = logging.getLogger(__name__)


class ConstructionService:
    """施工计划服务"""
    
    async def generate_plan(
        self,
        project_id: str,
        total_cycle: int,
        start_date: datetime = None
    ) -> dict:
        """
        生成施工计划
        
        根据总工期自动分配各节点时间
        """
        if not start_date:
            start_date = datetime.now()
        
        nodes = []
        current_date = start_date
        
        # 标准节点定义
        standard_nodes = [
            {"name": "开工准备", "type": "preparation", "days": 3, "sequence": 1},
            {"name": "水电改造", "type": "electrical", "days": 7, "sequence": 2},
            {"name": "防水工程", "type": "waterproof", "days": 5, "sequence": 3},
            {"name": "泥瓦工程", "type": "tiling", "days": 14, "sequence": 4},
            {"name": "木工工程", "type": "carpentry", "days": 10, "sequence": 5},
            {"name": "油漆工程", "type": "painting", "days": 8, "sequence": 6},
            {"name": "安装工程", "type": "installation", "days": 5, "sequence": 7},
            {"name": "竣工验收", "type": "acceptance", "days": 3, "sequence": 8},
        ]
        
        total_standard_days = sum(n["days"] for n in standard_nodes)
        
        # 按比例调整工期
        scale_factor = total_cycle / total_standard_days if total_standard_days > 0 else 1
        
        for node in standard_nodes:
            adjusted_days = max(1, int(node["days"] * scale_factor))
            planned_start = current_date
            planned_end = current_date + timedelta(days=adjusted_days)
            
            nodes.append({
                "id": f"{project_id}_node_{node['sequence']}",
                "name": node["name"],
                "type": node["type"],
                "sequence": node["sequence"],
                "planned_days": adjusted_days,
                "planned_start": planned_start.isoformat(),
                "planned_end": planned_end.isoformat(),
                "status": "pending",
                "progress": 0
            })
            
            current_date = planned_end
        
        return {
            "project_id": project_id,
            "total_cycle": total_cycle,
            "start_date": start_date.isoformat(),
            "end_date": current_date.isoformat(),
            "nodes": nodes,
            "summary": {
                "total_nodes": len(nodes),
                "pending": len(nodes),
                "in_progress": 0,
                "completed": 0
            }
        }
    
    async def update_node_progress(
        self,
        project_id: str,
        node_id: str,
        progress: int,
        status: str = None
    ) -> dict:
        """更新节点进度"""
        return {
            "node_id": node_id,
            "progress": progress,
            "status": status,
            "updated_at": datetime.now().isoformat()
        }
    
    async def check_overdue(
        self,
        nodes: List[dict]
    ) -> List[dict]:
        """检查延期节点"""
        now = datetime.now()
        overdue_nodes = []
        
        for node in nodes:
            if node.get("status") == "in_progress":
                planned_end = datetime.fromisoformat(node["planned_end"])
                if now > planned_end:
                    overdue_days = (now - planned_end).days
                    overdue_nodes.append({
                        "node_id": node["id"],
                        "node_name": node["name"],
                        "overdue_days": overdue_days,
                        "warning_level": "high" if overdue_days > 3 else "medium"
                    })
        
        return overdue_nodes
    
    async def calculate_progress(
        self,
        nodes: List[dict]
    ) -> int:
        """计算整体进度"""
        if not nodes:
            return 0
        
        total_progress = 0
        for node in nodes:
            if node.get("status") == "completed":
                total_progress += 100
            elif node.get("status") == "in_progress":
                total_progress += node.get("progress", 0)
        
        return int(total_progress / len(nodes))


# 全局单例
construction_service = ConstructionService()
