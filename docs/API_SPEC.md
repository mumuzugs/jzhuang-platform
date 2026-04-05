# 集装修 API 接口文档 V2.0

**版本**：V2.0  
**更新日期**：2026-04-06  
**基础URL**：`http://localhost:8000/api/v1`

---

## 一、接口概览

| 模块 | 接口数 | 认证 |
|------|--------|------|
| 认证 | 8 | ❌ |
| 用户 | 11 | ✅ |
| 验房 | 7 | 部分 |
| 设计 | 11 | ✅ |
| 施工 | 10 | ✅ |
| 监工 | 5 | ✅ |
| 验收 | 6 | ✅ |
| 支付 | 6 | 部分 |
| **总计** | **69** | - |

---

## 二、认证说明

### 2.1 Token格式

```
Authorization: Bearer <access_token>
```

### 2.2 错误码

| 错误码 | 说明 |
|--------|------|
| 200 | 成功 |
| 400 | 请求参数错误 |
| 401 | 未认证/Token无效 |
| 403 | 无权限 |
| 404 | 资源不存在 |
| 500 | 服务器内部错误 |

---

## 三、认证模块 `/auth`

**说明**：用户登录注册相关接口，无需认证

### 3.1 发送验证码

```
POST /auth/send-code
```

**请求参数**：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| phone | string | ✅ | 手机号（1开头11位） |

**请求示例**：
```json
{
  "phone": "13812345678"
}
```

**响应示例**：
```json
{
  "success": true,
  "message": "验证码发送成功",
  "expires_in": 300
}
```

---

### 3.2 用户登录

```
POST /auth/login
```

**请求参数**：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| phone | string | ✅ | 手机号 |
| code | string | ✅ | 验证码 |

**请求示例**：
```json
{
  "phone": "13812345678",
  "code": "123456"
}
```

**响应示例**：
```json
{
  "success": true,
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "Bearer",
  "expires_in": 7200
}
```

---

### 3.3 获取当前用户

```
GET /auth/me
```

**认证**：✅ 需要

**响应示例**：
```json
{
  "success": true,
  "user": {
    "id": "user_001",
    "phone": "13812345678",
    "nickname": "装修达人",
    "role": "owner",
    "is_pro": true
  }
}
```

---

### 3.4 退出登录

```
POST /auth/logout
```

**认证**：✅ 需要

**响应示例**：
```json
{
  "success": true,
  "message": "退出成功"
}
```

---

### 3.5 刷新Token

```
POST /auth/refresh
```

**认证**：✅ 需要

**响应示例**：
```json
{
  "success": true,
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "expires_in": 7200
}
```

---

### 3.6 修改密码

```
POST /auth/change-password
```

**认证**：✅ 需要

**请求参数**：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| old_password | string | ✅ | 旧密码 |
| new_password | string | ✅ | 新密码 |

---

### 3.7 重置密码

```
POST /auth/reset-password
```

**请求参数**：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| phone | string | ✅ | 手机号 |
| code | string | ✅ | 验证码 |
| new_password | string | ✅ | 新密码 |

---

### 3.8 微信登录

```
POST /auth/wechat-login
```

**请求参数**：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| code | string | ✅ | 微信授权码 |

**响应示例**：
```json
{
  "success": true,
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "is_new_user": true
}
```

---

## 四、用户模块 `/users`

**说明**：用户资料、角色、房屋档案管理

### 4.1 获取用户资料

```
GET /users/profile
```

**认证**：✅ 需要

**响应示例**：
```json
{
  "id": "user_001",
  "phone": "13812345678",
  "nickname": "装修达人",
  "role": "owner",
  "roles": ["owner"],
  "is_pro": true,
  "avatar": "https://...",
  "create_time": "2026-04-01T10:00:00Z"
}
```

---

### 4.2 更新用户资料

```
PUT /users/profile
```

**认证**：✅ 需要

**请求参数**：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| nickname | string | ❌ | 昵称 |
| avatar | string | ❌ | 头像URL |

---

### 4.3 获取用户角色

```
GET /users/roles
```

**认证**：✅ 需要

**响应示例**：
```json
{
  "success": true,
  "current_role": "owner",
  "roles": [
    {"role": "owner", "name": "业主", "description": "装修业主"},
    {"role": "worker", "name": "工长", "description": "装修工长/装修公司"},
    {"role": "supplier", "name": "材料供应商", "description": "材料供应商"},
    {"role": "operator", "name": "平台运营", "description": "平台运营人员"},
    {"role": "supervisor", "name": "监理", "description": "工程监理"},
    {"role": "cs", "name": "客服", "description": "客户服务"}
  ]
}
```

---

### 4.4 切换角色

```
POST /users/switch-role
```

**认证**：✅ 需要

**请求参数**：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| role | string | ✅ | 角色代码 |

---

### 4.5 获取房屋档案列表

```
GET /users/houses
```

**认证**：✅ 需要

**响应示例**：
```json
{
  "success": true,
  "houses": [
    {
      "house_id": "house_001",
      "city": "北京",
      "community": "XX小区",
      "house_type": "毛坯房",
      "area": 120,
      "decoration_status": "未装修"
    }
  ]
}
```

---

### 4.6 添加房屋档案

```
POST /users/houses
```

**认证**：✅ 需要

**请求参数**：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| city | string | ✅ | 城市 |
| community | string | ❌ | 小区名称 |
| building | string | ❌ | 楼栋 |
| unit | string | ❌ | 单元 |
| room_number | string | ❌ | 房号 |
| house_type | string | ✅ | 房屋类型 |
| area | float | ✅ | 面积 |
| build_year | int | ❌ | 建成年份 |
| property_type | string | ❌ | 产权类型 |

---

### 4.7 获取房屋详情

```
GET /users/houses/{house_id}
```

**认证**：✅ 需要

---

### 4.8 获取用户标签

```
GET /users/tags
```

**认证**：✅ 需要

**响应示例**：
```json
{
  "success": true,
  "tags": [
    {"tag_id": "tag_001", "tag_name": "装修新手", "tag_type": "demographic", "value": "true"}
  ],
  "total": 3
}
```

---

### 4.9 添加用户标签

```
POST /users/tags
```

**认证**：✅ 需要

**请求参数**：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| tag_name | string | ✅ | 标签名称 |
| tag_type | string | ✅ | 标签类型 |
| value | string | ✅ | 标签值 |
| weight | float | ❌ | 权重 |

---

### 4.10 获取操作审计日志

```
GET /users/audit-logs
```

**认证**：✅ 需要

**查询参数**：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| module | string | ❌ | 模块筛选 |
| start_date | string | ❌ | 开始日期 |
| end_date | string | ❌ | 结束日期 |
| limit | int | ❌ | 数量限制 |
| offset | int | ❌ | 偏移量 |

---

### 4.11 获取VIP状态

```
GET /users/vip/status
```

**认证**：✅ 需要

**响应示例**：
```json
{
  "is_pro": true,
  "role": "pro",
  "pro_expire_time": "2026-10-01T00:00:00Z",
  "permissions": ["全部功能"]
}
```

---

### 4.12 注销账号

```
DELETE /users/account
```

**认证**：✅ 需要

---

## 五、验房模块 `/inspection`

**说明**：AI智能验房，8类问题识别

### 5.1 获取问题类型

```
GET /inspection/issue-types
```

**认证**：❌ 不需要

**响应示例**：
```json
{
  "total": 8,
  "types": [
    {
      "code": "wall_crack",
      "name": "墙面开裂",
      "description": "墙面出现裂缝",
      "ai_model": "wall_detection_v2",
      "estimated_range": [200, 2000]
    }
  ]
}
```

---

### 5.2 获取城市高频风险

```
GET /inspection/city-risks/{city}
```

**认证**：❌ 不需要

**响应示例**：
```json
{
  "city": "北京",
  "risk_count": 3,
  "risks": ["墙面开裂", "门窗密封不良", "水电隐患"],
  "risk_details": [...]
}
```

---

### 5.3 创建验房任务

```
POST /inspection/create
```

**认证**：✅ 需要

**请求参数**：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| house_type | string | ✅ | 房屋类型 |
| city | string | ❌ | 城市 |
| district | string | ❌ | 区县 |
| area | int | ❌ | 面积 |

**响应示例**：
```json
{
  "success": true,
  "report_id": "inspection_abc123",
  "status": "pending"
}
```

---

### 5.4 上传图片AI分析

```
POST /inspection/analyze
```

**认证**：✅ 需要

**请求参数**：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| report_id | string | ✅ | 验房报告ID |
| files | File[] | ✅ | 图片文件（最多20张） |

**响应示例**：
```json
{
  "success": true,
  "report_id": "inspection_abc123",
  "issue_count": 5,
  "high_risk_count": 1,
  "medium_risk_count": 2,
  "low_risk_count": 2,
  "total_estimated_cost": 3500,
  "ai_accuracy": 92,
  "response_time_ms": 5000
}
```

---

### 5.5 获取验房报告

```
GET /inspection/report/{report_id}
```

**认证**：✅ 需要

---

### 5.6 获取验房报告列表

```
GET /inspection/my-reports
```

**认证**：✅ 需要

---

### 5.7 申请人工复核

```
POST /inspection/request-review
```

**认证**：✅ 需要

**请求参数**：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| report_id | string | ✅ | 报告ID |
| reason | string | ❌ | 复核原因 |

---

## 六、设计模块 `/design`

**说明**：AI设计方案生成，效果图渲染，设计-预算联动

### 6.1 获取装修风格

```
GET /design/styles
```

**认证**：❌ 不需要

**响应示例**：
```json
{
  "total": 3,
  "styles": [
    {
      "code": "modern_simple",
      "name": "现代简约",
      "description": "简洁实用",
      "colors": ["白色", "灰色", "米色"],
      "price_range": [800, 1500]
    }
  ]
}
```

---

### 6.2 获取布局类型

```
GET /design/layouts
```

**认证**：❌ 不需要

**响应示例**：
```json
{
  "total": 3,
  "layouts": [
    {
      "code": "space",
      "name": "极致空间利用率",
      "description": "最大化收纳空间",
      "suitable_for": ["小户型"]
    }
  ]
}
```

---

### 6.3 创建设计项目

```
POST /design/create
```

**认证**：✅ 需要

**请求参数**：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| house_type | string | ❌ | 房屋类型 |
| area | int | ❌ | 面积 |
| city | string | ❌ | 城市 |

---

### 6.4 上传户型图识别

```
POST /design/floor-plan
```

**认证**：✅ 需要

**请求参数**：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| file | File | ✅ | 户型图文件 |
| city | string | ❌ | 城市 |

---

### 6.5 生成设计方案

```
POST /design/generate
```

**认证**：✅ 需要

**请求参数**：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| project_id | string | ✅ | 项目ID |
| area | int | ✅ | 面积 |
| rooms | int | ✅ | 房间数 |
| style | string | ❌ | 风格 |
| layout_type | string | ❌ | 布局类型 |
| family_structure | string | ❌ | 家庭结构 |

---

### 6.6 生成效果图

```
POST /design/render
```

**认证**：✅ 需要

**请求参数**：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| project_id | string | ✅ | 项目ID |
| plan_id | string | ✅ | 方案ID |
| style | string | ✅ | 装修风格 |
| room | string | ❌ | 房间 |

---

### 6.7 调整设计方案

```
POST /design/adjust
```

**认证**：✅ 需要

**请求参数**：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| project_id | string | ✅ | 项目ID |
| plan_id | string | ✅ | 方案ID |
| changes | array | ✅ | 调整项 |

---

### 6.8 计算预算

```
POST /design/budget
```

**认证**：✅ 需要

**请求参数**：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| project_id | string | ✅ | 项目ID |
| materials | array | ✅ | 材料清单 |
| city | string | ❌ | 城市 |
| budget_limit | int | ❌ | 预算上限 |

---

### 6.9 生成施工图

```
POST /design/drawings
```

**认证**：✅ 需要

**请求参数**：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| project_id | string | ✅ | 项目ID |
| drawing_types | array | ❌ | 图纸类型 |

---

### 6.10 生成材料清单

```
GET /design/materials/{plan_id}
```

**认证**：✅ 需要

---

### 6.11 确认设计方案

```
POST /design/confirm
```

**认证**：✅ 需要

**请求参数**：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| project_id | string | ✅ | 项目ID |
| plan_id | string | ✅ | 方案ID |

---

## 七、施工模块 `/construction`

**说明**：装修项目全流程管理，8大节点管控

### 7.1 获取标准节点

```
GET /construction/standard-nodes
```

**认证**：❌ 不需要

**响应示例**：
```json
{
  "total": 8,
  "nodes": [
    {"id": "preparation", "name": "开工准备", "cycle": 3},
    {"id": "electrical", "name": "水电改造", "cycle": 7},
    {"id": "waterproof", "name": "防水工程", "cycle": 5},
    {"id": "tiling", "name": "泥瓦工程", "cycle": 10},
    {"id": "carpentry", "name": "木工工程", "cycle": 12},
    {"id": "painting", "name": "油漆工程", "cycle": 8},
    {"id": "installation", "name": "安装工程", "cycle": 5},
    {"id": "acceptance", "name": "竣工验收", "cycle": 5}
  ]
}
```

---

### 7.2 创建施工项目

```
POST /construction/create
```

**认证**：✅ 需要

**请求参数**：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| name | string | ✅ | 项目名称 |
| design_project_id | string | ❌ | 设计项目ID |
| address | string | ❌ | 地址 |
| area | int | ❌ | 面积 |
| total_cycle | int | ❌ | 总工期 |
| start_date | string | ❌ | 开工日期 |

---

### 7.3 获取项目详情

```
GET /construction/project/{project_id}
```

**认证**：✅ 需要

---

### 7.4 获取项目进度

```
GET /construction/project/{project_id}/progress
```

**认证**：✅ 需要

---

### 7.5 更新节点进度

```
POST /construction/node/update
```

**认证**：✅ 需要

**请求参数**：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| node_id | string | ✅ | 节点ID |
| progress | int | ✅ | 进度(0-100) |
| status | string | ❌ | 状态 |

---

### 7.6 获取通知

```
GET /construction/notifications
```

**认证**：✅ 需要

---

### 7.7 获取我的项目

```
GET /construction/my-projects
```

**认证**：✅ 需要

---

### 7.8 提交节点验收

```
POST /construction/node/acceptance
```

**认证**：✅ 需要

**请求参数**：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| node_id | string | ✅ | 节点ID |
| project_id | string | ✅ | 项目ID |
| photos | array | ❌ | 验收照片 |
| notes | string | ❌ | 备注 |

---

### 7.9 上传云监工图片

```
POST /construction/supervision/upload
```

**认证**：✅ 需要

**请求参数**：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| project_id | string | ✅ | 项目ID |
| node_id | string | ✅ | 节点ID |
| files | File[] | ✅ | 图片 |

---

### 7.10 AI识别监工图片

```
POST /construction/supervision/recognize
```

**认证**：✅ 需要

---

## 八、验收模块 `/acceptance`

**说明**：标准化节点验收、竣工验收、维保服务

### 8.1 获取验收标准

```
GET /acceptance/standards
```

**认证**：✅ 需要

**响应示例**：
```json
{
  "success": true,
  "total": 5,
  "standards": {
    "水电改造": {
      "name": "水电改造验收标准",
      "standards": [
        {"type": "主控项", "item": "电线必须穿管保护", "method": "目视检查"}
      ]
    }
  }
}
```

---

### 8.2 获取节点验收清单

```
GET /acceptance/node-checklist/{node_id}
```

**认证**：✅ 需要

---

### 8.3 提交验收

```
POST /acceptance/submit
```

**认证**：✅ 需要

**请求参数**：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| node_id | string | ✅ | 节点ID |
| project_id | string | ✅ | 项目ID |
| check_items | array | ❌ | 检查项结果 |
| photos | array | ❌ | 照片 |
| notes | string | ❌ | 备注 |

---

### 8.4 获取验收报告

```
GET /acceptance/report/{report_id}
```

**认证**：✅ 需要

---

### 8.5 获取验收报告列表

```
GET /acceptance/my-reports
```

**认证**：✅ 需要

---

### 8.6 获取维保信息

```
GET /acceptance/warranty/{project_id}
```

**认证**：✅ 需要

**响应示例**：
```json
{
  "success": true,
  "project_id": "project_001",
  "warranty_start": "2026-04-01",
  "warranty_end": "2028-03-31",
  "warranty_period": "2年",
  "scope": ["水路工程质保", "防水工程质保(5年)"],
  "status": "active"
}
```

---

## 九、支付模块 `/payment`

**说明**：订单管理、微信支付

### 9.1 获取产品列表

```
GET /payment/products
```

**认证**：❌ 不需要

**响应示例**：
```json
{
  "success": true,
  "products": [
    {
      "id": "vip_pro",
      "name": "全周期专业版",
      "price_display": "299.00",
      "features": ["无限次AI验房", "全套AI设计"]
    }
  ]
}
```

---

### 9.2 创建订单

```
POST /payment/create-order
```

**认证**：✅ 需要

**请求参数**：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| product_type | string | ✅ | 产品类型 |

---

### 9.3 获取订单

```
GET /payment/order/{order_no}
```

**认证**：✅ 需要

---

### 9.4 获取VIP状态

```
GET /payment/vip-status
```

**认证**：✅ 需要

---

### 9.5 取消订单

```
POST /payment/cancel/{order_no}
```

**认证**：✅ 需要

---

### 9.6 支付回调

```
POST /payment/notify
```

**说明**：微信支付回调通知

---

## 十、公共响应格式

### 10.1 成功响应

```json
{
  "success": true,
  "data": {}
}
```

### 10.2 错误响应

```json
{
  "success": false,
  "error": {
    "code": "INVALID_PARAMETER",
    "message": "参数错误"
  }
}
```

---

## 十一、限流说明

| 接口类型 | 限制 |
|----------|------|
| 普通接口 | 100次/分钟 |
| 发送验证码 | 3次/分钟 |
| AI分析接口 | 20次/小时 |

---

*文档版本：V2.0 | 更新日期：2026-04-06*
