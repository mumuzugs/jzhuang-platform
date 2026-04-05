"""
5个目标客户全流程测试脚本
模拟真实用户场景，测试完整业务流程
"""
import requests
import json
import time
import random
from datetime import datetime, timedelta

BASE_URL = "http://localhost:8000"


# 5个虚拟客户画像
CUSTOMERS = [
    {
        "name": "张先生",
        "profile": {
            "phone": "13800001001",
            "role": "owner",
            "city": "北京",
            "house_type": "毛坯房",
            "area": 89,
            "rooms": 2,
            "family": "三口之家",
            "budget": "15-20万",
            "style_preference": "现代简约",
            "needs": ["验房", "设计", "预算联动", "施工"]
        },
        "scenario": "张先生购买了一套89平的毛坯房，准备装修给三口之家居住。他关注预算控制和施工质量，希望通过平台一站式完成装修。"
    },
    {
        "name": "李女士",
        "profile": {
            "phone": "13800001002",
            "role": "owner",
            "city": "上海",
            "house_type": "二手房",
            "area": 120,
            "rooms": 3,
            "family": "三代同堂",
            "budget": "30-40万",
            "style_preference": "新中式",
            "needs": ["验房", "设计", "施工", "监工"]
        },
        "scenario": "李女士购买了一套120平的二手房，需要先验房再装修。她和公婆孩子一起住，注重环保和安全，对施工透明度要求高。"
    },
    {
        "name": "王工长",
        "profile": {
            "phone": "13800001003",
            "role": "worker",
            "city": "广州",
            "house_type": "工长",
            "specialty": "水电隐蔽工程",
            "experience": "10年",
            "needs": ["施工管理", "云监工", "验收"]
        },
        "scenario": "王工长是一位有10年经验的工长，擅长水电工程。他希望在平台上接单，并通过平台管理工地进度和与业主沟通。"
    },
    {
        "name": "赵监理",
        "profile": {
            "phone": "13800001004",
            "role": "supervisor",
            "city": "深圳",
            "house_type": "监理",
            "certification": "国家注册监理工程师",
            "needs": ["验收", "云监工", "问题追踪"]
        },
        "scenario": "赵监理是专业的装修监理，为多个工地提供监理服务。他需要审核施工质量，追踪问题整改进度，确保装修符合国家标准。"
    },
    {
        "name": "陈老板",
        "profile": {
            "phone": "13800001005",
            "role": "supplier",
            "city": "成都",
            "house_type": "材料供应商",
            "products": ["瓷砖", "地板", "卫浴"],
            "needs": ["订单管理", "供应追踪"]
        },
        "scenario": "陈老板经营一家建材店，为装修公司提供瓷砖、地板、卫浴等材料。他希望在平台上展示产品、接收订单、管理供应。"
    }
]


class CustomerTestRunner:
    def __init__(self, customer):
        self.customer = customer
        self.profile = customer["profile"]
        self.name = customer["name"]
        self.token = None
        self.test_results = {}
        
    def log(self, msg):
        print(f"  [{self.name}] {msg}")
        
    def send_code(self):
        """发送验证码"""
        try:
            # 发送前先等待，避免频繁发送
            time.sleep(random.uniform(0.5, 2.0))
            resp = requests.post(
                f"{BASE_URL}/api/v1/auth/send-code",
                json={"phone": self.profile["phone"]},
                timeout=10
            )
            if resp.status_code == 200:
                self.log("✅ 发送验证码成功")
                return True
            else:
                self.log(f"⚠️ 发送验证码: {resp.status_code}")
                return False
        except Exception as e:
            self.log(f"❌ 发送验证码失败: {e}")
            return False
            
    def login(self):
        """登录"""
        try:
            time.sleep(0.5)
            resp = requests.post(
                f"{BASE_URL}/api/v1/auth/login",
                json={"phone": self.profile["phone"], "code": "123456"},
                timeout=15
            )
            if resp.status_code == 200:
                data = resp.json()
                self.token = data.get("access_token")
                self.log(f"✅ 登录成功")
                return True
            else:
                self.log(f"❌ 登录失败: {resp.status_code}")
                return False
        except Exception as e:
            self.log(f"❌ 登录异常: {e}")
            return False
    
    def get_headers(self):
        return {"Authorization": f"Bearer {self.token}"} if self.token else {}
    
    def test_auth(self):
        """测试认证模块"""
        self.log("=== 测试认证模块 ===")
        results = []
        
        # 发送验证码
        r = self.send_code()
        results.append(("发送验证码", r))
        
        # 登录
        r = self.login()
        results.append(("登录", r))
        
        if self.token:
            # 获取用户信息
            try:
                resp = requests.get(
                    f"{BASE_URL}/api/v1/auth/me",
                    headers=self.get_headers(),
                    timeout=10
                )
                results.append(("获取用户", resp.status_code == 200))
            except:
                results.append(("获取用户", False))
                
        self.test_results["认证"] = results
        return all(r[1] for r in results)
    
    def test_user_module(self):
        """测试用户模块"""
        self.log("=== 测试用户模块 ===")
        results = []
        
        if not self.token:
            return False
            
        try:
            # 获取资料
            resp = requests.get(f"{BASE_URL}/api/v1/users/profile", 
                              headers=self.get_headers(), timeout=10)
            results.append(("获取资料", resp.status_code == 200))
            
            # 获取角色
            resp = requests.get(f"{BASE_URL}/api/v1/users/roles",
                              headers=self.get_headers(), timeout=10)
            results.append(("获取角色", resp.status_code == 200))
            
            # 添加房屋
            resp = requests.post(f"{BASE_URL}/api/v1/users/houses",
                json={
                    "city": self.profile.get("city", "北京"),
                    "house_type": self.profile.get("house_type", "毛坯房"),
                    "area": self.profile.get("area", 100)
                },
                headers=self.get_headers(), timeout=10
            )
            results.append(("添加房屋", resp.status_code == 200))
            
        except Exception as e:
            self.log(f"用户模块异常: {e}")
            results.append(("用户模块", False))
            
        self.test_results["用户"] = results
        return all(r[1] for r in results)
    
    def test_inspection(self):
        """测试验房模块"""
        self.log("=== 测试验房模块 ===")
        results = []
        
        if not self.token:
            return False
            
        try:
            # 获取问题类型
            resp = requests.get(f"{BASE_URL}/api/v1/inspection/issue-types", timeout=10)
            results.append(("问题类型", resp.status_code == 200))
            
            # 城市风险
            city = self.profile.get("city", "北京")
            resp = requests.get(f"{BASE_URL}/api/v1/inspection/city-risks/{city}", timeout=10)
            results.append(("城市风险", resp.status_code == 200))
            
            # 创建验房任务
            resp = requests.post(f"{BASE_URL}/api/v1/inspection/create",
                json={
                    "house_type": self.profile.get("house_type", "毛坯房"),
                    "city": city,
                    "area": self.profile.get("area", 100)
                },
                headers=self.get_headers(), timeout=10
            )
            results.append(("创建任务", resp.status_code == 200))
            
        except Exception as e:
            self.log(f"验房模块异常: {e}")
            results.append(("验房模块", False))
            
        self.test_results["验房"] = results
        return all(r[1] for r in results)
    
    def test_design(self):
        """测试设计模块"""
        self.log("=== 测试设计模块 ===")
        results = []
        
        if not self.token:
            return False
            
        try:
            # 获取风格
            resp = requests.get(f"{BASE_URL}/api/v1/design/styles", timeout=10)
            results.append(("装修风格", resp.status_code == 200))
            
            # 获取布局
            resp = requests.get(f"{BASE_URL}/api/v1/design/layouts", timeout=10)
            results.append(("布局类型", resp.status_code == 200))
            
            # 创建设计项目
            resp = requests.post(f"{BASE_URL}/api/v1/design/create",
                json={
                    "house_type": self.profile.get("house_type", "毛坯房"),
                    "area": self.profile.get("area", 100),
                    "city": self.profile.get("city", "北京")
                },
                headers=self.get_headers(), timeout=10
            )
            results.append(("创建项目", resp.status_code == 200))
            
        except Exception as e:
            self.log(f"设计模块异常: {e}")
            results.append(("设计模块", False))
            
        self.test_results["设计"] = results
        return all(r[1] for r in results)
    
    def test_construction(self):
        """测试施工模块"""
        self.log("=== 测试施工模块 ===")
        results = []
        
        if not self.token:
            return False
            
        try:
            # 标准节点
            resp = requests.get(f"{BASE_URL}/api/v1/construction/standard-nodes", timeout=10)
            results.append(("标准节点", resp.status_code == 200))
            
            # 创建项目
            resp = requests.post(f"{BASE_URL}/api/v1/construction/create",
                json={
                    "name": f"{self.name}的装修项目",
                    "total_cycle": 60
                },
                headers=self.get_headers(), timeout=10
            )
            results.append(("创建项目", resp.status_code == 200))
            
            # 获取通知
            resp = requests.get(f"{BASE_URL}/api/v1/construction/notifications",
                headers=self.get_headers(), timeout=10
            )
            results.append(("通知列表", resp.status_code == 200))
            
        except Exception as e:
            self.log(f"施工模块异常: {e}")
            results.append(("施工模块", False))
            
        self.test_results["施工"] = results
        return all(r[1] for r in results)
    
    def test_supervision(self):
        """测试云监工模块"""
        self.log("=== 测试云监工模块 ===")
        results = []
        
        if not self.token:
            return False
            
        try:
            # 上传监工图片
            resp = requests.post(f"{BASE_URL}/api/v1/construction/supervision/upload",
                json={
                    "project_id": "test_project",
                    "node_id": "electrical"
                },
                headers=self.get_headers(), timeout=10
            )
            results.append(("上传图片", resp.status_code == 200))
            
            # AI识别
            resp = requests.post(f"{BASE_URL}/api/v1/construction/supervision/recognize",
                json={"image_id": "test"},
                headers=self.get_headers(), timeout=10
            )
            results.append(("AI识别", resp.status_code == 200))
            
        except Exception as e:
            self.log(f"云监工模块异常: {e}")
            results.append(("云监工", False))
            
        self.test_results["云监工"] = results
        return all(r[1] for r in results)
    
    def test_acceptance(self):
        """测试验收模块"""
        self.log("=== 测试验收模块 ===")
        results = []
        
        if not self.token:
            return False
            
        try:
            # 获取验收标准
            resp = requests.get(f"{BASE_URL}/api/v1/acceptance/standards",
                headers=self.get_headers(), timeout=10
            )
            results.append(("验收标准", resp.status_code == 200))
            
            # 获取节点清单
            resp = requests.get(f"{BASE_URL}/api/v1/acceptance/node-checklist/electrical",
                headers=self.get_headers(), timeout=10
            )
            results.append(("节点清单", resp.status_code == 200))
            
            # 提交验收
            resp = requests.post(f"{BASE_URL}/api/v1/acceptance/submit",
                json={
                    "node_id": "test",
                    "project_id": "test",
                    "check_items": [],
                    "photos": []
                },
                headers=self.get_headers(), timeout=10
            )
            results.append(("提交验收", resp.status_code == 200))
            
        except Exception as e:
            self.log(f"验收模块异常: {e}")
            results.append(("验收模块", False))
            
        self.test_results["验收"] = results
        return all(r[1] for r in results)
    
    def test_payment(self):
        """测试支付模块"""
        self.log("=== 测试支付模块 ===")
        results = []
        
        if not self.token:
            return False
            
        try:
            # 产品列表
            resp = requests.get(f"{BASE_URL}/api/v1/payment/products", timeout=10)
            results.append(("产品列表", resp.status_code == 200))
            
            # 创建订单
            resp = requests.post(f"{BASE_URL}/api/v1/payment/create-order",
                json={"product_type": "vip_pro"},
                headers=self.get_headers(), timeout=10
            )
            results.append(("创建订单", resp.status_code == 200))
            
            # VIP状态
            resp = requests.get(f"{BASE_URL}/api/v1/payment/vip-status",
                headers=self.get_headers(), timeout=10
            )
            results.append(("VIP状态", resp.status_code == 200))
            
        except Exception as e:
            self.log(f"支付模块异常: {e}")
            results.append(("支付模块", False))
            
        self.test_results["支付"] = results
        return all(r[1] for r in results)
    
    def run_full_test(self):
        """运行完整流程测试"""
        print(f"\n{'='*50}")
        print(f"测试用户: {self.name}")
        print(f"场景: {self.customer['scenario']}")
        print('='*50)
        
        # 认证
        auth_ok = self.test_auth()
        
        # 根据角色测试不同模块
        role = self.profile.get("role", "owner")
        
        if role in ["owner", "worker", "supervisor"]:
            self.test_user_module()
            self.test_inspection()
            self.test_design()
            self.test_construction()
            self.test_supervision()
            self.test_acceptance()
            self.test_payment()
        elif role == "supplier":
            self.test_user_module()
            self.test_payment()
        
        return auth_ok
    
    def get_summary(self):
        """获取测试汇总"""
        total = 0
        passed = 0
        for module, results in self.test_results.items():
            for name, ok in results:
                total += 1
                if ok:
                    passed += 1
        return {"total": total, "passed": passed, "failed": total - passed}


def run_test_for_customer(customer, round_num):
    """为单个客户运行测试"""
    print(f"\n\n{'#'*60}")
    print(f"# 第{round_num}轮 - {customer['name']}")
    print(f"# 场景: {customer['scenario']}")
    print('#'*60)
    
    runner = CustomerTestRunner(customer)
    runner.run_full_test()
    
    summary = runner.get_summary()
    print(f"\n【{customer['name']}】测试结果: {summary['passed']}/{summary['total']} 通过")
    
    return runner, summary


def main():
    print("\n" + "="*60)
    print("= 集装修 5个目标客户全流程测试")
    print("="*60)
    
    all_results = []
    
    # 运行3轮测试
    for round_num in range(1, 4):
        print(f"\n\n{'#'*60}")
        print(f"# 第 {round_num} 轮测试")
        print(f"{'#'*60}")
        
        round_results = []
        
        for customer in CUSTOMERS:
            runner, summary = run_test_for_customer(customer, round_num)
            round_results.append({
                "customer": customer["name"],
                **summary
            })
            all_results.append({
                "round": round_num,
                "customer": customer["name"],
                **summary
            })
        
        # 打印本轮汇总
        print(f"\n{'='*60}")
        print(f"第 {round_num} 轮测试汇总")
        print('='*60)
        
        total_passed = sum(r["passed"] for r in round_results)
        total_failed = sum(r["failed"] for r in round_results)
        total_all = sum(r["total"] for r in round_results)
        
        for r in round_results:
            status = "✅" if r["failed"] == 0 else "❌"
            print(f"  {status} {r['customer']}: {r['passed']}/{r['total']}")
        
        print(f"\n本轮总计: {total_passed}/{total_all} 通过 ({total_passed/total_all*100:.1f}%)")
        
        if total_failed > 0:
            print(f"失败数: {total_failed}")
        
        time.sleep(2)
    
    # 最终汇总
    print(f"\n\n{'#'*60}")
    print("# 最终测试汇总")
    print(f"{'#'*60}")
    
    total_all_results = sum(r["total"] for r in all_results)
    total_all_passed = sum(r["passed"] for r in all_results)
    total_all_failed = sum(r["failed"] for r in all_results)
    
    print(f"\n总测试次数: {total_all_results}")
    print(f"通过次数: {total_all_passed}")
    print(f"失败次数: {total_all_failed}")
    print(f"通过率: {total_all_passed/total_all_results*100:.1f}%")
    
    # 按客户汇总
    print(f"\n按客户汇总:")
    for customer in CUSTOMERS:
        name = customer["name"]
        customer_results = [r for r in all_results if r["customer"] == name]
        passed = sum(r["passed"] for r in customer_results)
        total = sum(r["total"] for r in customer_results)
        status = "✅" if sum(r["failed"] for r in customer_results) == 0 else "❌"
        print(f"  {status} {name}: {passed}/{total}")
    
    # 保存结果
    output = {
        "test_date": datetime.now().isoformat(),
        "customers": [c["name"] for c in CUSTOMERS],
        "rounds": 3,
        "total_tests": total_all_results,
        "total_passed": total_all_passed,
        "total_failed": total_all_failed,
        "pass_rate": total_all_passed/total_all_results*100,
        "results": all_results
    }
    
    with open("/tmp/customer_test_results.json", "w") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    
    print(f"\n结果已保存到 /tmp/customer_test_results.json")
    
    return output


if __name__ == "__main__":
    main()
