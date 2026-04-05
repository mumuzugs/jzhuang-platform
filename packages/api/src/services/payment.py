"""
支付服务 - 微信支付集成

架构文档要求：
- 微信支付集成
- 订单管理
- 支付回调处理
"""
import logging
import uuid
import hashlib
import time
from datetime import datetime, timedelta
from typing import Optional

logger = logging.getLogger(__name__)


class PaymentService:
    """支付服务"""
    
    def __init__(self):
        # 内存存储（测试用）
        self._orders_db = {}
        
        # 产品定义
        self.products = {
            "vip_pro": {
                "name": "全周期专业版",
                "description": "解锁全部核心功能，服务至装修完成",
                "price": 29900,  # 299元（分）
                "price_display": "299.00",
                "expire_days": 180,  # 6个月
                "features": [
                    "无限次AI验房+高清报告下载",
                    "全套AI设计服务",
                    "设计-预算实时联动+预算红线预警",
                    "自动生成施工计划+节点主动通知",
                    "无限次AI云监工+进度识别+异常预警",
                    "工程档案归档"
                ]
            }
        }
    
    def generate_order_no(self) -> str:
        """生成订单号"""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        random_str = uuid.uuid4().hex[:6].upper()
        return f"JZ{timestamp}{random_str}"
    
    async def create_order(self, user_id: str, product_type: str) -> dict:
        """创建订单"""
        product = self.products.get(product_type)
        if not product:
            raise ValueError(f"产品不存在: {product_type}")
        
        order_no = self.generate_order_no()
        order = {
            "order_id": f"order_{order_no}",
            "order_no": order_no,
            "user_id": user_id,
            "product_type": product_type,
            "product_name": product["name"],
            "description": product["description"],
            "amount": product["price"],
            "amount_display": product["price_display"],
            "status": "pending",
            "payment_method": None,
            "payment_time": None,
            "expire_time": (datetime.now() + timedelta(minutes=30)).isoformat(),
            "created_at": datetime.now().isoformat(),
            "paid_at": None
        }
        
        self._orders_db[order_no] = order
        
        logger.info(f"[支付] 创建订单 order_no={order_no}, amount={product['price']/100}元")
        
        return order
    
    async def get_order(self, order_no: str) -> Optional[dict]:
        """获取订单"""
        return self._orders_db.get(order_no)
    
    async def get_user_orders(self, user_id: str) -> list:
        """获取用户订单列表"""
        return [
            order for order in self._orders_db.values()
            if order["user_id"] == user_id
        ]
    
    async def get_wechat_pay_params(
        self,
        order_no: str,
        openid: str = None
    ) -> dict:
        """
        获取微信支付参数
        
        架构文档要求：微信支付集成
        """
        order = self._orders_db.get(order_no)
        if not order:
            raise ValueError("订单不存在")
        
        if order["status"] != "pending":
            raise ValueError("订单状态不正确")
        
        # 生成微信支付参数（模拟）
        timestamp = str(int(time.time()))
        nonce_str = uuid.uuid4().hex[:32]
        
        pay_params = {
            "appId": "wx_your_appid",  # 实际配置
            "timeStamp": timestamp,
            "nonceStr": nonce_str,
            "package": f"prepay_id=wx_{order_no}",
            "signType": "MD5",
            "paySign": self._generate_sign(order_no, timestamp, nonce_str)
        }
        
        logger.info(f"[支付] 获取支付参数 order_no={order_no}")
        
        return {
            "success": True,
            "order_no": order_no,
            "pay_params": pay_params,
            "code_url": f"weixin://wxpay/bizpayurl?pr=mock_{order_no}"
        }
    
    async def handle_payment_callback(self, callback_data: dict) -> dict:
        """
        处理微信支付回调
        
        架构文档要求：支付回调处理
        """
        return_code = callback_data.get("return_code", "")
        result_code = callback_data.get("result_code", "")
        order_no = callback_data.get("out_trade_no", "")
        transaction_id = callback_data.get("transaction_id", "")
        time_end = callback_data.get("time_end", "")
        
        logger.info(f"[支付] 回调 order_no={order_no}, return_code={return_code}, result_code={result_code}")
        
        if return_code == "SUCCESS" and result_code == "SUCCESS":
            # 支付成功
            if order_no in self._orders_db:
                order = self._orders_db[order_no]
                order["status"] = "paid"
                order["paid_at"] = datetime.now().isoformat()
                order["transaction_id"] = transaction_id
                
                logger.info(f"[支付] 订单支付成功 order_no={order_no}")
                
                return {
                    "success": True,
                    "order_no": order_no,
                    "status": "paid"
                }
        
        return {
            "success": False,
            "order_no": order_no,
            "message": "支付处理失败"
        }
    
    async def activate_vip(self, user_id: str, order_no: str) -> dict:
        """
        激活VIP会员
        
        架构文档要求：VIP状态管理
        """
        order = self._orders_db.get(order_no)
        if not order or order["status"] != "paid":
            raise ValueError("订单未支付")
        
        product = self.products.get(order["product_type"])
        if not product:
            raise ValueError("产品不存在")
        
        effective_time = datetime.now()
        expire_time = effective_time + timedelta(days=product["expire_days"])
        
        logger.info(f"[支付] 激活VIP user_id={user_id}, order_no={order_no}, expire_time={expire_time}")
        
        return {
            "success": True,
            "user_id": user_id,
            "role": "pro",
            "product_name": product["name"],
            "effective_time": effective_time.isoformat(),
            "expire_time": expire_time.isoformat(),
            "message": f"专业版已激活，有效期至{expire_time.strftime('%Y-%m-%d')}"
        }
    
    async def check_vip_status(self, user_id: str) -> dict:
        """检查VIP状态"""
        # 查找用户最近的有效订单
        user_orders = await self.get_user_orders(user_id)
        paid_order = None
        
        for order in user_orders:
            if order["status"] == "paid":
                product = self.products.get(order["product_type"])
                if product:
                    paid_order = order
                    break
        
        if paid_order:
            product = self.products.get(paid_order["product_type"])
            return {
                "is_pro": True,
                "role": "pro",
                "product_name": product["name"],
                "paid_at": paid_order["paid_at"],
                "expire_time": None,
                "can_use": product["features"]
            }
        
        return {
            "is_pro": False,
            "role": "free",
            "product_name": None,
            "expire_time": None,
            "can_use": ["3次免费AI验房基础报告", "3套免费设计方案预览", "基础装修预算计算器"]
        }
    
    def _generate_sign(self, order_no: str, timestamp: str, nonce_str: str) -> str:
        """生成签名（简化版）"""
        data = f"{order_no}{timestamp}{nonce_str}"
        return hashlib.md5(data.encode()).hexdigest()


# 全局单例
payment_service = PaymentService()
