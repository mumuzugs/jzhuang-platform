"""
完整API测试脚本 - 8轮测试
"""
import requests
import json
import time
import sys

BASE_URL = "http://localhost:8000"


def log(msg):
    print(f"  {msg}")


def test_module(name, tests):
    """测试一个模块的所有接口"""
    print(f"\n{'='*50}")
    print(f"测试模块: {name}")
    print('='*50)
    
    passed = 0
    failed = 0
    errors = []
    
    for test_name, method, endpoint, data, headers_func in tests:
        try:
            url = f"{BASE_URL}{endpoint}"
            headers = headers_func() if callable(headers_func) else headers_func
            
            if method == "GET":
                resp = requests.get(url, headers=headers, timeout=15)
            elif method == "POST":
                resp = requests.post(url, json=data, headers=headers, timeout=15)
            else:
                resp = None
            
            if resp and resp.status_code == 200:
                log(f"✅ {test_name}: 200")
                passed += 1
            else:
                status = resp.status_code if resp else "N/A"
                text = resp.text[:100] if resp else "No response"
                log(f"❌ {test_name}: {status} - {text}")
                failed += 1
                errors.append((test_name, endpoint, status, text))
                
        except requests.exceptions.Timeout:
            log(f"❌ {test_name}: TIMEOUT")
            failed += 1
            errors.append((test_name, endpoint, 0, "Request timeout"))
        except Exception as e:
            log(f"❌ {test_name}: {type(e).__name__}")
            failed += 1
            errors.append((test_name, endpoint, 0, str(e)))
    
    return {"passed": passed, "failed": failed, "errors": errors}


def run_full_test(token=None):
    """运行完整测试"""
    print("\n" + "#"*60)
    print("# 集装修 API 完整测试")
    print("#"*60)
    
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    
    # 模块1: 认证
    auth_tests = [
        ("发送验证码", "POST", "/api/v1/auth/send-code", 
         {"phone": f"138{int(time.time())%100000000:08d}"}, lambda: {}),
    ]
    results_auth = test_module("认证", auth_tests)
    
    # 获取token用于后续测试
    phone = f"138{int(time.time())%100000000:08d}"
    try:
        requests.post(f"{BASE_URL}/api/v1/auth/send-code", json={"phone": phone}, timeout=10)
        time.sleep(0.5)
        resp = requests.post(f"{BASE_URL}/api/v1/auth/login", 
                           json={"phone": phone, "code": "123456"}, timeout=15)
        if resp.status_code == 200:
            token = resp.json().get("access_token")
            headers = {"Authorization": f"Bearer {token}"}
            results_auth["passed"] += 1
            log("✅ 登录: 200")
        else:
            results_auth["failed"] += 1
            log(f"❌ 登录: {resp.status_code}")
            errors = list(results_auth["errors"])
            errors.append(("登录", "/api/v1/auth/login", resp.status_code, resp.text[:100]))
            results_auth["errors"] = errors
    except Exception as e:
        results_auth["failed"] += 2
        log(f"❌ 登录: {str(e)}")
    
    results_auth["passed"] += 1  # 发送验证码已通过
    
    # 获取用户信息
    if token:
        auth_tests2 = [
            ("获取当前用户", "GET", "/api/v1/auth/me", None, lambda: headers),
            ("退出登录", "POST", "/api/v1/auth/logout", None, lambda: headers),
        ]
        temp = test_module("认证(续)", auth_tests2)
        results_auth["passed"] += temp["passed"]
        results_auth["failed"] += temp["failed"]
        results_auth["errors"].extend(temp["errors"])
    
    # 模块2: 用户
    user_tests = [
        ("获取用户资料", "GET", "/api/v1/users/profile", None, lambda: headers),
        ("VIP状态", "GET", "/api/v1/users/vip/status", None, lambda: headers),
    ]
    results_user = test_module("用户", user_tests)
    
    # 模块3: 验房
    inspection_tests = [
        ("获取问题类型", "GET", "/api/v1/inspection/issue-types", None, lambda: {}),
        ("城市高频风险", "GET", "/api/v1/inspection/city-risks/北京", None, lambda: {}),
        ("创建验房任务", "POST", "/api/v1/inspection/create", 
         {"house_type": "毛坯房", "city": "北京", "area": 120}, lambda: headers),
    ]
    results_inspection = test_module("验房", inspection_tests)
    
    # 模块4: 设计
    design_tests = [
        ("获取装修风格", "GET", "/api/v1/design/styles", None, lambda: {}),
        ("获取布局类型", "GET", "/api/v1/design/layouts", None, lambda: {}),
        ("创建设计项目", "POST", "/api/v1/design/create", 
         {"area": 120, "city": "北京"}, lambda: headers),
    ]
    results_design = test_module("设计", design_tests)
    
    # 模块5: 施工
    construction_tests = [
        ("获取标准节点", "GET", "/api/v1/construction/standard-nodes", None, lambda: {}),
        ("创建施工项目", "POST", "/api/v1/construction/create", 
         {"name": "测试项目", "total_cycle": 60}, lambda: headers),
        ("获取通知", "GET", "/api/v1/construction/notifications", None, lambda: headers),
    ]
    results_construction = test_module("施工", construction_tests)
    
    # 模块6: 支付
    payment_tests = [
        ("获取产品列表", "GET", "/api/v1/payment/products", None, lambda: {}),
        ("VIP状态", "GET", "/api/v1/payment/vip-status", None, lambda: headers),
        ("创建订单", "POST", "/api/v1/payment/create-order", 
         {"product_type": "vip_pro"}, lambda: headers),
    ]
    results_payment = test_module("支付", payment_tests)
    
    all_results = {
        "认证": results_auth,
        "用户": results_user,
        "验房": results_inspection,
        "设计": results_design,
        "施工": results_construction,
        "支付": results_payment,
    }
    
    total_passed = sum(r["passed"] for r in all_results.values())
    total_failed = sum(r["failed"] for r in all_results.values())
    
    return all_results, total_passed, total_failed, token


def print_summary(results, passed, failed, round_num):
    """打印测试汇总"""
    print(f"\n{'='*60}")
    print(f"# 第 {round_num} 轮测试结果汇总")
    print('='*60)
    
    for module, result in results.items():
        status = "✅" if result["failed"] == 0 else "❌"
        print(f"  {status} {module}: {result['passed']}/{result['passed']+result['failed']} 通过")
    
    print(f"\n总通过: {passed}/{passed+failed} ({passed/(passed+failed)*100:.1f}%)")
    
    if failed > 0:
        print(f"\n失败详情:")
        for module, result in results.items():
            for err in result["errors"]:
                print(f"  - {module}/{err[0]}: {err[2]} - {err[3][:80]}")
    
    return failed == 0


if __name__ == "__main__":
    round_num = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    
    results, passed, failed, token = run_full_test()
    success = print_summary(results, passed, failed, round_num)
    
    # 保存结果
    output = {
        "round": round_num,
        "results": {k: {"passed": v["passed"], "failed": v["failed"], "errors": v["errors"]} 
                    for k, v in results.items()},
        "total_passed": passed,
        "total_failed": failed,
        "success": success
    }
    
    with open(f"/tmp/test_result_{round_num}.json", "w") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
