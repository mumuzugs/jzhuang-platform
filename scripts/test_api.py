"""
API 自动化测试脚本
"""
import requests
import json
import time

BASE_URL = "http://localhost:8000"


def test_auth_module():
    """测试认证模块"""
    print("\n" + "="*50)
    print("测试认证模块")
    print("="*50)
    
    # 1. 发送验证码
    print("\n1. 发送验证码")
    phone = f"138{int(time.time()) % 100000000:08d}"  # 生成11位手机号
    resp = requests.post(
        f"{BASE_URL}/api/v1/auth/send-code",
        json={"phone": phone},
        timeout=10
    )
    print(f"   手机号: {phone}")
    print(f"   状态码: {resp.status_code}")
    print(f"   响应: {resp.json()}")
    assert resp.status_code == 200, f"发送验证码失败: {resp.text}"
    
    # 2. 登录
    print("\n2. 手机号验证码登录")
    resp = requests.post(
        f"{BASE_URL}/api/v1/auth/login",
        json={"phone": phone, "code": "123456"},
        timeout=10
    )
    print(f"   状态码: {resp.status_code}")
    data = resp.json()
    print(f"   响应: {json.dumps(data, ensure_ascii=False)[:200]}...")
    assert resp.status_code == 200, f"登录失败: {resp.text}"
    
    token = data.get("access_token")
    assert token, "未获取到token"
    
    # 3. 获取当前用户
    print("\n3. 获取当前用户信息")
    resp = requests.get(
        f"{BASE_URL}/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"},
        timeout=10
    )
    print(f"   状态码: {resp.status_code}")
    print(f"   响应: {resp.json()}")
    assert resp.status_code == 200, f"获取用户信息失败: {resp.text}"
    
    return token


def test_user_module(token):
    """测试用户模块"""
    print("\n" + "="*50)
    print("测试用户模块")
    print("="*50)
    
    # 1. 获取用户资料
    print("\n1. 获取用户资料")
    resp = requests.get(
        f"{BASE_URL}/api/v1/users/profile",
        headers={"Authorization": f"Bearer {token}"},
        timeout=10
    )
    print(f"   状态码: {resp.status_code}")
    print(f"   响应: {resp.json()}")
    assert resp.status_code == 200, f"获取用户资料失败: {resp.text}"
    
    # 2. VIP状态
    print("\n2. VIP状态")
    resp = requests.get(
        f"{BASE_URL}/api/v1/users/vip/status",
        headers={"Authorization": f"Bearer {token}"},
        timeout=10
    )
    print(f"   状态码: {resp.status_code}")
    print(f"   响应: {resp.json()}")
    assert resp.status_code == 200, f"获取VIP状态失败: {resp.text}"


def test_inspection_module(token):
    """测试验房模块"""
    print("\n" + "="*50)
    print("测试验房模块")
    print("="*50)
    
    # 1. 获取问题类型
    print("\n1. 获取支持的问题类型")
    resp = requests.get(
        f"{BASE_URL}/api/v1/inspection/issue-types",
        timeout=10
    )
    print(f"   状态码: {resp.status_code}")
    data = resp.json()
    print(f"   问题类型数量: {len(data.get('types', {}))}")
    assert resp.status_code == 200, f"获取问题类型失败: {resp.text}"
    
    # 2. 城市高频风险
    print("\n2. 获取城市高频风险")
    resp = requests.get(
        f"{BASE_URL}/api/v1/inspection/city-risks/北京",
        timeout=10
    )
    print(f"   状态码: {resp.status_code}")
    print(f"   响应: {resp.json()}")
    assert resp.status_code == 200, f"获取城市风险失败: {resp.text}"
    
    # 3. 创建验房
    print("\n3. 创建验房任务")
    resp = requests.post(
        f"{BASE_URL}/api/v1/inspection/create",
        json={"house_type": "毛坯房", "city": "北京", "area": 120},
        headers={"Authorization": f"Bearer {token}"},
        timeout=10
    )
    print(f"   状态码: {resp.status_code}")
    data = resp.json()
    print(f"   响应: {data}")
    report_id = data.get("report_id")
    assert resp.status_code == 200, f"创建验房失败: {resp.text}"
    
    # 4. 获取验房报告
    print("\n4. 获取验房报告")
    resp = requests.get(
        f"{BASE_URL}/api/v1/inspection/report/{report_id}",
        headers={"Authorization": f"Bearer {token}"},
        timeout=10
    )
    print(f"   状态码: {resp.status_code}")
    print(f"   响应: {json.dumps(resp.json(), ensure_ascii=False)[:200]}")
    assert resp.status_code == 200, f"获取报告失败: {resp.text}"


def test_design_module(token):
    """测试设计模块"""
    print("\n" + "="*50)
    print("测试设计模块")
    print("="*50)
    
    # 1. 获取装修风格
    print("\n1. 获取装修风格列表")
    resp = requests.get(
        f"{BASE_URL}/api/v1/design/styles",
        timeout=10
    )
    print(f"   状态码: {resp.status_code}")
    data = resp.json()
    print(f"   风格数量: {len(data)}")
    assert resp.status_code == 200, f"获取风格列表失败: {resp.text}"
    
    # 2. 获取布局类型
    print("\n2. 获取布局类型")
    resp = requests.get(
        f"{BASE_URL}/api/v1/design/layouts",
        timeout=10
    )
    print(f"   状态码: {resp.status_code}")
    print(f"   布局类型: {list(resp.json().keys())}")
    assert resp.status_code == 200, f"获取布局类型失败: {resp.text}"
    
    # 3. 创建设计项目
    print("\n3. 创建设计项目")
    resp = requests.post(
        f"{BASE_URL}/api/v1/design/create",
        json={"house_type": "三室两厅", "area": 120, "city": "北京"},
        headers={"Authorization": f"Bearer {token}"},
        timeout=10
    )
    print(f"   状态码: {resp.status_code}")
    data = resp.json()
    print(f"   响应: {data}")
    project_id = data.get("project_id")
    assert resp.status_code == 200, f"创建项目失败: {resp.text}"
    
    # 4. 生成布局方案
    print("\n4. 生成3套布局方案")
    resp = requests.post(
        f"{BASE_URL}/api/v1/design/generate-layouts",
        json={"project_id": project_id, "area": 120, "rooms": 3, "style": "modern_simple"},
        headers={"Authorization": f"Bearer {token}"},
        timeout=10
    )
    print(f"   状态码: {resp.status_code}")
    data = resp.json()
    layouts = data.get("layouts", [])
    print(f"   方案数量: {len(layouts)}")
    assert resp.status_code == 200, f"生成布局失败: {resp.text}"
    
    # 5. 计算预算
    print("\n5. 计算预算")
    resp = requests.post(
        f"{BASE_URL}/api/v1/design/calculate-budget",
        json={
            "project_id": project_id,
            "materials": [
                {"category": "地面", "space": "客厅", "item": "瓷砖", "quantity": 40, "estimated_price": 15000}
            ],
            "city": "北京"
        },
        headers={"Authorization": f"Bearer {token}"},
        timeout=10
    )
    print(f"   状态码: {resp.status_code}")
    data = resp.json()
    print(f"   总价: {data.get('summary', {}).get('total_cost', 0)}")
    assert resp.status_code == 200, f"计算预算失败: {resp.text}"


def test_construction_module(token):
    """测试施工模块"""
    print("\n" + "="*50)
    print("测试施工模块")
    print("="*50)
    
    # 1. 获取标准节点
    print("\n1. 获取标准施工节点")
    resp = requests.get(
        f"{BASE_URL}/api/v1/construction/standard-nodes",
        timeout=10
    )
    print(f"   状态码: {resp.status_code}")
    data = resp.json()
    print(f"   节点数量: {len(data)}")
    assert resp.status_code == 200, f"获取节点失败: {resp.text}"
    
    # 2. 创建施工项目
    print("\n2. 创建施工项目")
    resp = requests.post(
        f"{BASE_URL}/api/v1/construction/create",
        json={"name": "我的新家装修", "total_cycle": 60, "address": "北京市朝阳区"},
        headers={"Authorization": f"Bearer {token}"},
        timeout=10
    )
    print(f"   状态码: {resp.status_code}")
    data = resp.json()
    print(f"   项目ID: {data.get('project_id')}")
    project_id = data.get("project_id")
    assert resp.status_code == 200, f"创建项目失败: {resp.text}"
    
    # 3. 获取项目详情
    print("\n3. 获取项目详情")
    resp = requests.get(
        f"{BASE_URL}/api/v1/construction/project/{project_id}",
        headers={"Authorization": f"Bearer {token}"},
        timeout=10
    )
    print(f"   状态码: {resp.status_code}")
    print(f"   响应: {resp.json()}")
    assert resp.status_code == 200, f"获取项目失败: {resp.text}"


def test_payment_module(token):
    """测试支付模块"""
    print("\n" + "="*50)
    print("测试支付模块")
    print("="*50)
    
    # 1. 获取产品列表
    print("\n1. 获取产品列表")
    resp = requests.get(
        f"{BASE_URL}/api/v1/payment/products",
        timeout=10
    )
    print(f"   状态码: {resp.status_code}")
    data = resp.json()
    print(f"   产品: {list(data.get('products', {}).keys())}")
    assert resp.status_code == 200, f"获取产品失败: {resp.text}"
    
    # 2. VIP状态
    print("\n2. VIP状态检查")
    resp = requests.get(
        f"{BASE_URL}/api/v1/payment/vip-status",
        headers={"Authorization": f"Bearer {token}"},
        timeout=10
    )
    print(f"   状态码: {resp.status_code}")
    print(f"   响应: {resp.json()}")
    assert resp.status_code == 200, f"获取VIP状态失败: {resp.text}"


def run_all_tests():
    """运行所有测试"""
    print("\n" + "#"*60)
    print("# 集装修 API 自动化测试")
    print("#"*60)
    
    success_count = 0
    fail_count = 0
    
    for i in range(1, 6):
        print(f"\n\n{'#'*60}")
        print(f"# 第 {i}/5 轮测试")
        print(f"{'#'*60}")
        
        try:
            token = test_auth_module()
            test_user_module(token)
            test_inspection_module(token)
            test_design_module(token)
            test_construction_module(token)
            test_payment_module(token)
            
            print(f"\n✅ 第 {i} 轮测试通过!")
            success_count += 1
            
        except AssertionError as e:
            print(f"\n❌ 第 {i} 轮测试失败: {e}")
            fail_count += 1
        except Exception as e:
            print(f"\n❌ 第 {i} 轮测试异常: {e}")
            import traceback
            traceback.print_exc()
            fail_count += 1
        
        # 每轮测试后等待2秒
        if i < 5:
            time.sleep(2)
    
    print("\n" + "="*60)
    print("测试结果汇总")
    print("="*60)
    print(f"总测试轮数: 5")
    print(f"成功: {success_count}")
    print(f"失败: {fail_count}")
    print(f"成功率: {success_count/5*100:.1f}%")
    print("="*60)
    
    return fail_count == 0


if __name__ == "__main__":
    run_all_tests()
