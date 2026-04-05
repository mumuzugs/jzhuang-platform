"""
验房服务
"""
import logging
import json
from datetime import datetime
from typing import Optional

logger = logging.getLogger(__name__)


# 问题类型定义
ISSUE_TYPES = {
    "wall_crack": {
        "name": "墙面开裂",
        "description": "墙面出现裂缝，可能影响美观和结构安全",
        "risk_levels": {
            "low": "细小裂缝，建议观察",
            "medium": "明显裂缝，需要修补",
            "high": "严重裂缝，需专业人员处理"
        },
        "suggestion": "根据裂缝程度选择修补或加固处理"
    },
    "floor_uneven": {
        "name": "地面不平",
        "description": "地面水平度不符合标准",
        "risk_levels": {
            "low": "轻微不平，影响较小",
            "medium": "明显不平，影响地砖铺设",
            "high": "严重不平，需要重新找平"
        },
        "suggestion": "建议使用水泥砂浆找平"
    },
    "water_leak": {
        "name": "防水渗漏",
        "description": "防水层损坏导致渗漏",
        "risk_levels": {
            "low": "轻微渗漏迹象",
            "medium": "有明显渗漏",
            "high": "严重渗漏，影响楼下"
        },
        "suggestion": "建议重新做防水处理，重点处理管道周围"
    },
    "door_window": {
        "name": "门窗密封不良",
        "description": "门窗关闭不严",
        "risk_levels": {
            "low": "轻微透风",
            "medium": "明显透风",
            "high": "严重影响保温"
        },
        "suggestion": "调整五金件或更换密封条"
    },
    "electrical": {
        "name": "水电隐患",
        "description": "水电安装不规范",
        "risk_levels": {
            "low": "轻微不规范",
            "medium": "存在安全隐患",
            "high": "严重安全隐患"
        },
        "suggestion": "建议请专业电工检查整改"
    },
    "hollow_sound": {
        "name": "墙面空鼓",
        "description": "瓷砖或墙面空鼓",
        "risk_levels": {
            "low": "小面积空鼓",
            "medium": "中等面积空鼓",
            "high": "大面积空鼓，易脱落"
        },
        "suggestion": "空鼓面积超过15%建议重新铺贴"
    },
    "corner_not_plumb": {
        "name": "阴阳角不垂直",
        "description": "墙角不垂直",
        "risk_levels": {
            "low": "轻微偏差",
            "medium": "明显偏差",
            "high": "严重影响美观"
        },
        "suggestion": "使用石膏线或重新抹灰"
    },
    "drainage": {
        "name": "下水不畅",
        "description": "排水管道堵塞或坡度不足",
        "risk_levels": {
            "low": "轻微不畅",
            "medium": "明显不畅",
            "high": "严重堵塞"
        },
        "suggestion": "检查管道坡度，必要时重新安装"
    }
}


# 城市高频风险
CITY_RISKS = {
    "北京": ["墙面开裂", "门窗密封不良", "水电隐患"],
    "上海": ["防水渗漏", "地面不平", "水电隐患"],
    "广州": ["防水渗漏", "墙面空鼓", "下水不畅"],
    "深圳": ["水电隐患", "墙面开裂", "门窗密封不良"],
    "成都": ["地面不平", "阴阳角不垂直", "水电隐患"],
    "杭州": ["墙面开裂", "防水渗漏", "门窗密封不良"],
}


class InspectionService:
    """验房服务"""
    
    async def create_inspection(
        self,
        user_id: str,
        house_type: str = "毛坯房",
        city: str = None,
        district: str = None,
        area: int = None,
        layout_image: str = None,
        room_images: list = None
    ) -> dict:
        """创建验房任务"""
        from src.models.inspection import InspectionReport
        
        # 创建验房报告记录
        report = InspectionReport(
            user_id=user_id,
            house_type=house_type,
            city=city,
            district=district,
            area=area,
            layout_image=layout_image,
            room_images=json.dumps(room_images) if room_images else None,
            status="processing"
        )
        
        return {"report_id": report.id, "status": "processing"}
    
    async def analyze_images(
        self,
        report_id: str,
        room_images: list
    ) -> dict:
        """
        分析房屋图片
        
        这里使用模拟的AI分析结果
        实际项目中需要接入阿里云视觉API或腾讯云图像识别
        """
        # 模拟AI分析
        issues = []
        
        # 根据图片数量生成一些问题
        for i, img_url in enumerate(room_images[:5]):
            # 随机生成一些问题
            import random
            issue_type = random.choice(list(ISSUE_TYPES.keys()))
            risk = random.choice(["low", "medium", "high"])
            
            issue_info = ISSUE_TYPES[issue_type]
            
            issue = {
                "type": issue_type,
                "name": issue_info["name"],
                "description": issue_info["description"],
                "risk_level": risk,
                "suggestion": issue_info["risk_levels"][risk],
                "location": random.choice(["客厅", "卧室", "厨房", "卫生间", "阳台"]),
                "confidence": random.randint(70, 99),
                "estimated_cost": random.randint(100, 5000)
            }
            issues.append(issue)
        
        # 统计风险
        high_count = sum(1 for i in issues if i["risk_level"] == "high")
        medium_count = sum(1 for i in issues if i["risk_level"] == "medium")
        low_count = sum(1 for i in issues if i["risk_level"] == "low")
        
        # 生成报告内容
        report_content = self._generate_report(issues, high_count, medium_count, low_count)
        
        return {
            "issues": issues,
            "high_risk_count": high_count,
            "medium_risk_count": medium_count,
            "low_risk_count": low_count,
            "report_content": report_content
        }
    
    def _generate_report(
        self,
        issues: list,
        high_count: int,
        medium_count: int,
        low_count: int
    ) -> str:
        """生成验房报告"""
        report = f"""# 房屋验房报告

## 一、验房概况
- 验房时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}
- 房屋类型：毛坯房

## 二、问题统计
- 🔴 高风险问题：{high_count} 项
- 🟡 中风险问题：{medium_count} 项
- 🟢 低风险问题：{low_count} 项
- **总计：{len(issues)} 项问题**

## 三、问题详情
"""
        for i, issue in enumerate(issues, 1):
            risk_emoji = "🔴" if issue["risk_level"] == "high" else ("🟡" if issue["risk_level"] == "medium" else "🟢")
            report += f"""
### {i}. {issue['name']} {risk_emoji}
- 位置：{issue['location']}
- 问题描述：{issue['description']}
- 风险等级：{issue['risk_level']}
- 整改建议：{issue['suggestion']}
- 预估费用：{issue['estimated_cost']}元
- AI置信度：{issue['confidence']}%
"""
        
        report += """
## 四、总结
本报告由AI智能生成，仅供参考。建议针对高风险问题及时整改，
如有疑问可申请人工复核。
"""
        return report
    
    async def get_city_risks(self, city: str) -> list:
        """获取城市高频风险"""
        return CITY_RISKS.get(city, ["墙面开裂", "地面不平", "水电隐患"])


# 全局单例
inspection_service = InspectionService()