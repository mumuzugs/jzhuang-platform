"""
预算服务 - 设计-预算实时联动引擎
"""
import logging
from datetime import datetime
from typing import Optional, List, Dict

logger = logging.getLogger(__name__)


# 基础价格表（单位：元）
BASE_PRICES = {
    # 地面材料
    "瓷砖": {"普通": 80, "品牌": 150, "高端": 300},
    "木地板": {"普通": 120, "品牌": 200, "高端": 400},
    "实木地板": {"普通": 300, "品牌": 500, "高端": 800},
    
    # 墙面材料
    "乳胶漆": {"普通": 50, "品牌": 120, "高端": 300},
    "墙纸": {"普通": 30, "品牌": 80, "高端": 200},
    
    # 橱柜
    "橱柜": {"普通": 800, "品牌": 1500, "高端": 3000},
    
    # 人工费系数（按材料费的百分比）
    "人工费系数": 0.4,
    
    # 管理费系数
    "管理费系数": 0.1,
    
    # 杂费系数
    "杂费系数": 0.05
}

# 地区调价系数
CITY_COEFFICIENTS = {
    "北京": 1.3,
    "上海": 1.25,
    "广州": 1.1,
    "深圳": 1.2,
    "成都": 0.95,
    "杭州": 1.15,
    "武汉": 0.9,
    "西安": 0.85,
    "默认": 1.0
}


class BudgetService:
    """预算服务 - 核心壁垒功能"""
    
    def __init__(self):
        self.price_db = BASE_PRICES.copy()
    
    async def calculate_budget(
        self,
        project_id: str,
        materials: List[Dict],
        city: str = "默认"
    ) -> dict:
        """
        计算预算
        
        设计参数变更时调用此方法实时重算预算
        """
        city_coef = CITY_COEFFICIENTS.get(city, CITY_COEFFICIENTS["默认"])
        
        # 按类别汇总
        material_cost = 0
        labor_cost = 0
        management_fee = 0
        misc_cost = 0
        
        items = []
        
        for item in materials:
            # 计算该项总价
            unit_price = item.get("estimated_price", 0)
            quantity = item.get("quantity", 1)
            total_price = int(unit_price * quantity * city_coef)
            
            # 计算人工费
            item_labor = int(total_price * BASE_PRICES["人工费系数"])
            
            item_total = total_price + item_labor
            
            material_cost += total_price
            labor_cost += item_labor
            
            items.append({
                "category": item.get("category", "其他"),
                "space": item.get("space", ""),
                "item": item.get("item", ""),
                "spec": item.get("spec", ""),
                "unit": item.get("unit", ""),
                "quantity": quantity,
                "unit_price": unit_price,
                "total_price": total_price,
                "labor_cost": item_labor,
                "grand_total": item_total
            })
        
        # 计算管理费和杂费
        base_cost = material_cost + labor_cost
        management_fee = int(base_cost * BASE_PRICES["管理费系数"])
        misc_cost = int(base_cost * BASE_PRICES["杂费系数"])
        
        # 总价
        total_cost = base_cost + management_fee + misc_cost
        
        return {
            "project_id": project_id,
            "city": city,
            "city_coefficient": city_coef,
            "items": items,
            "summary": {
                "material_cost": material_cost,
                "labor_cost": labor_cost,
                "management_fee": management_fee,
                "misc_cost": misc_cost,
                "total_cost": total_cost
            },
            "version": 1,
            "updated_at": datetime.now().isoformat()
        }
    
    async def calculate_change_impact(
        self,
        project_id: str,
        change_type: str,
        change_param: Dict,
        current_budget: dict
    ) -> dict:
        """
        计算变更影响
        
        当用户调整设计参数时，计算对预算的影响
        """
        impact = {
            "change_type": change_type,
            "changed_items": [],
            "total_impact": 0,
            "impact_percentage": 0
        }
        
        if change_type == "material_change":
            # 材料变更
            old_price = change_param.get("old_price", 0)
            new_price = change_param.get("new_price", 0)
            quantity = change_param.get("quantity", 1)
            
            price_diff = new_price - old_price
            total_impact = int(price_diff * quantity)
            
            impact["changed_items"].append({
                "item": change_param.get("item", ""),
                "old_price": old_price,
                "new_price": new_price,
                "quantity": quantity,
                "impact": total_impact
            })
            
        elif change_type == "area_change":
            # 面积变更
            old_area = change_param.get("old_area", 0)
            new_area = change_param.get("new_area", 0)
            area_diff = new_area - old_area
            price_per_sqm = change_param.get("price_per_sqm", 1000)
            
            total_impact = int(area_diff * price_per_sqm)
            
            impact["changed_items"].append({
                "type": "面积调整",
                "old_area": old_area,
                "new_area": new_area,
                "impact": total_impact
            })
        
        elif change_type == "layout_change":
            # 布局变更
            total_impact = int(current_budget.get("summary", {}).get("total_cost", 0) * 0.15)
            
            impact["changed_items"].append({
                "type": "布局调整",
                "description": "涉及水电、墙体等多项变更",
                "estimated_impact": total_impact
            })
        
        impact["total_impact"] = total_impact
        
        if current_budget.get("summary", {}).get("total_cost", 0) > 0:
            impact["impact_percentage"] = round(
                total_impact / current_budget["summary"]["total_cost"] * 100, 2
            )
        
        return impact
    
    async def check_budget_warning(
        self,
        current_budget: int,
        budget_limit: int
    ) -> dict:
        """
        预算红线检查
        
        检查当前预算是否超过用户设定的红线
        """
        remaining = budget_limit - current_budget
        
        if current_budget > budget_limit:
            return {
                "is_over_budget": True,
                "over_amount": current_budget - budget_limit,
                "remaining": remaining,
                "warning_level": "high" if (current_budget - budget_limit) > budget_limit * 0.1 else "medium",
                "suggestions": [
                    "考虑更换为性价比更高的材料",
                    "适当减少装修项目",
                    "调整装修档次"
                ]
            }
        elif remaining < budget_limit * 0.1:
            return {
                "is_over_budget": False,
                "remaining": remaining,
                "warning_level": "low",
                "suggestions": ["预算接近红线，注意控制"]
            }
        else:
            return {
                "is_over_budget": False,
                "remaining": remaining,
                "warning_level": "normal",
                "suggestions": []
            }
    
    async def get_alternative_materials(
        self,
        original_item: Dict,
        budget_limit: Optional[int] = None
    ) -> List[Dict]:
        """
        推荐替代材料
        
        当预算超限时，推荐性价比更高的替代方案
        """
        item_name = original_item.get("item", "")
        alternatives = []
        
        if item_name in ["瓷砖", "木地板", "实木地板"]:
            alternatives = [
                {"item": item_name, "grade": "普通", "price_saving": 30},
                {"item": item_name, "grade": "品牌", "price_saving": 50}
            ]
        elif item_name == "乳胶漆":
            alternatives = [
                {"item": "乳胶漆", "grade": "品牌", "price_saving": 40}
            ]
        elif item_name == "橱柜":
            alternatives = [
                {"item": "橱柜", "grade": "品牌", "price_saving": 500}
            ]
        
        return alternatives


# 全局单例
budget_service = BudgetService()
