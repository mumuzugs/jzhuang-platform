"""
云监工服务 - AI施工进度识别
"""
import logging
import random
from datetime import datetime
from typing import Optional, List

logger = logging.getLogger(__name__)


# 施工阶段定义
CONSTRUCTION_STAGES = {
    "preparation": {"name": "开工准备", "progress": 5, "features": ["材料", "工具", "保护"]},
    "electrical": {"name": "水电改造", "progress": 20, "features": ["水管", "电线", "开关"]},
    "waterproof": {"name": "防水工程", "progress": 35, "features": ["防水层", "闭水试验"]},
    "tiling": {"name": "泥瓦工程", "progress": 50, "features": ["瓷砖", "水泥", "找平"]},
    "carpentry": {"name": "木工工程", "progress": 70, "features": ["吊顶", "柜体", "背景墙"]},
    "painting": {"name": "油漆工程", "progress": 85, "features": ["腻子", "乳胶漆", "艺术漆"]},
    "installation": {"name": "安装工程", "progress": 95, "features": ["灯具", "洁具", "开关"]},
    "acceptance": {"name": "竣工验收", "progress": 100, "features": ["整体", "细节"]},
}


class CloudSupervisionService:
    """云监工服务"""
    
    async def recognize_progress(
        self,
        project_id: str,
        image_url: str
    ) -> dict:
        """
        AI识别施工进度
        
        实际项目中需要接入图像识别API
        这里使用模拟的识别结果
        """
        # 模拟AI识别（随机返回一个阶段）
        stages = list(CONSTRUCTION_STAGES.keys())
        detected_stage = random.choice(stages)
        stage_info = CONSTRUCTION_STAGES[detected_stage]
        
        # 模拟识别置信度
        confidence = random.randint(85, 99)
        
        return {
            "success": True,
            "image_url": image_url,
            "detected_stage": detected_stage,
            "stage_name": stage_info["name"],
            "progress": stage_info["progress"],
            "confidence": confidence,
            "detected_features": stage_info["features"],
            "recognized_at": datetime.now().isoformat()
        }
    
    async def check_anomalies(
        self,
        project_id: str,
        image_url: str,
        stage: str
    ) -> dict:
        """
        检查施工异常
        
        识别施工不规范、工艺缺陷等问题
        """
        # 模拟异常检测（随机概率发现异常）
        has_anomaly = random.random() < 0.3
        
        result = {
            "has_anomaly": has_anomaly,
            "anomalies": []
        }
        
        if has_anomaly:
            # 模拟常见的施工问题
            common_issues = [
                {"type": "quality", "name": "瓷砖空鼓", "severity": "medium",
                 "suggestion": "建议重新铺贴或灌浆处理"},
                {"type": "safety", "name": "电线外露", "severity": "high",
                 "suggestion": "存在安全隐患，需立即整改"},
                {"type": "quality", "name": "墙面开裂", "severity": "low",
                 "suggestion": "建议挂网处理"},
                {"type": "standard", "name": "防水层破损", "severity": "high",
                 "suggestion": "需重新做防水处理"},
            ]
            
            # 随机选择1-2个问题
            import random
            issues = random.sample(common_issues, min(2, len(common_issues)))
            result["anomalies"] = issues
        
        return result
    
    async def auto_match_node(
        self,
        project_id: str,
        recognized_stage: str,
        planned_nodes: List[dict]
    ) -> dict:
        """
        自动匹配施工节点
        
        根据识别的阶段自动匹配对应的施工节点
        """
        # 查找匹配的节点
        matched_node = None
        for node in planned_nodes:
            if node.get("type") == recognized_stage:
                matched_node = node
                break
        
        if matched_node:
            return {
                "matched": True,
                "node_id": matched_node["id"],
                "node_name": matched_node["name"],
                "message": f"已自动匹配到【{matched_node['name']}】节点"
            }
        else:
            return {
                "matched": False,
                "message": "未找到匹配的施工节点"
            }
    
    async def archive_photos(
        self,
        project_id: str,
        node_id: str,
        photo_url: str
    ) -> dict:
        """
        归档照片到工程档案
        
        自动按节点分类存储
        """
        return {
            "archive_id": f"archive_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "project_id": project_id,
            "node_id": node_id,
            "photo_url": photo_url,
            "category": "construction_records",
            "archived_at": datetime.now().isoformat()
        }
    
    async def generate_progress_report(
        self,
        project_id: str,
        recognized_results: List[dict]
    ) -> dict:
        """
        生成进度报告
        
        根据多次识别结果生成综合进度报告
        """
        if not recognized_results:
            return {"error": "暂无识别数据"}
        
        # 取最新的识别结果
        latest = recognized_results[-1]
        
        # 统计各阶段照片数量
        stage_counts = {}
        for result in recognized_results:
            stage = result.get("detected_stage", "unknown")
            stage_counts[stage] = stage_counts.get(stage, 0) + 1
        
        return {
            "project_id": project_id,
            "current_stage": latest.get("stage_name"),
            "current_progress": latest.get("progress"),
            "confidence": latest.get("confidence"),
            "photo_count": len(recognized_results),
            "stage_distribution": stage_counts,
            "report_time": datetime.now().isoformat()
        }


# 全局单例
cloud_supervision_service = CloudSupervisionService()
