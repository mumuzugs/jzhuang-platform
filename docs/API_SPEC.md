# 集装修 API 接口文档 V3.0

**版本**：V3.0  
**更新日期**：2026-04-06  
**基础URL**：`http://localhost:8000/api/v1`

---

## 一、接口概览

| 模块 | 接口数 | 认证 |
|------|--------|------|
| 认证 | 8 | ❌ |
| 用户 | 12 | ✅ |
| 验房 | 7 | 部分 |
| 设计 | 11 | ✅ |
| 施工 | 10 | ✅ |
| 云监工 | 5 | ✅ |
| 验收 | 6 | ✅ |
| 支付 | 6 | 部分 |
| **总计** | **65** | - |

---

## 二、认证模块 `/auth`

| 接口 | 方法 | 路径 | 说明 |
|------|------|------|------|
| 发送验证码 | POST | /auth/send-code | 限3次/分钟 |
| 登录 | POST | /auth/login | |
| 微信登录 | POST | /auth/wechat-login | |
| 获取用户 | GET | /auth/me | ≤100ms |
| 刷新Token | POST | /auth/refresh | |
| 修改密码 | POST | /auth/change-password | |
| 重置密码 | POST | /auth/reset-password | |
| 退出登录 | POST | /auth/logout | |

---

## 三、用户模块 `/users`

| 接口 | 方法 | 路径 | 说明 |
|------|------|------|------|
| 获取资料 | GET | /users/profile | |
| 更新资料 | PUT | /users/profile | |
| 获取角色 | GET | /users/roles | 6种角色 |
| 切换角色 | POST | /users/switch-role | |
| 房屋列表 | GET | /users/houses | |
| 添加房屋 | POST | /users/houses | |
| 房屋详情 | GET | /users/houses/{id} | |
| 用户标签 | GET | /users/tags | |
| 添加标签 | POST | /users/tags | |
| 审计日志 | GET | /users/audit-logs | 6个月留存 |
| VIP状态 | GET | /users/vip/status | |
| 注销账号 | DELETE | /users/account | |

---

## 四、验房模块 `/inspection`

**目标**：识别准确率≥90%，响应≤2秒

| 接口 | 方法 | 路径 | 说明 |
|------|------|------|------|
| 问题类型 | GET | /inspection/issue-types | 8类问题 |
| 城市风险 | GET | /inspection/city-risks/{city} | |
| 创建任务 | POST | /inspection/create | |
| 图片分析 | POST | /inspection/analyze | ≤2秒 |
| 报告详情 | GET | /inspection/report/{id} | |
| 报告列表 | GET | /inspection/my-reports | |
| 人工复核 | POST | /inspection/request-review | 高风险100%复核 |

---

## 五、设计模块 `/design`

**目标**：方案生成≤3秒，效果图≤10秒，预算联动≤300ms

| 接口 | 方法 | 路径 | 说明 |
|------|------|------|------|
| 装修风格 | GET | /design/styles | 3种风格 |
| 布局类型 | GET | /design/layouts | 3套方案 |
| 创建项目 | POST | /design/create | |
| 户型识别 | POST | /design/floor-plan | ≤5秒 |
| 生成方案 | POST | /design/generate | ≤3秒 |
| 生成效果图 | POST | /design/render | ≤10秒 |
| 调整设计 | POST | /design/adjust | |
| 计算预算 | POST | /design/budget | ≤300ms |
| 生成施工图 | POST | /design/drawings | 6类图纸 |
| 材料清单 | GET | /design/materials/{plan_id} | |
| 确认方案 | POST | /design/confirm | |

---

## 六、施工模块 `/construction`

**8大核心节点**：开工准备→水电改造→防水工程→泥瓦工程→木工工程→油漆工程→安装工程→竣工验收

| 接口 | 方法 | 路径 | 说明 |
|------|------|------|------|
| 标准节点 | GET | /construction/standard-nodes | 8大节点 |
| 创建项目 | POST | /construction/create | |
| 项目详情 | GET | /construction/project/{id} | |
| 项目进度 | GET | /construction/project/{id}/progress | |
| 更新节点 | POST | /construction/node/update | |
| 通知列表 | GET | /construction/notifications | |
| 我的项目 | GET | /construction/my-projects | |
| 节点验收 | POST | /construction/node/acceptance | |
| 监工上传 | POST | /construction/supervision/upload | |
| AI识别 | POST | /construction/supervision/recognize | |

---

## 七、云监工模块 `/supervision`

**目标**：进度识别≥95%，合规检测≥90%，安全隐患≥92%，响应≤3秒

| 接口 | 方法 | 路径 | 说明 |
|------|------|------|------|
| 进度识别 | POST | /supervision/recognize-progress | ≤3秒 |
| 合规检测 | POST | /supervision/check-compliance | |
| 异常检测 | POST | /supervision/check-anomalies | |
| 预警规则 | GET | /supervision/warning-rules | |
| 添加规则 | POST | /supervision/warning-rules | |
| 预警历史 | GET | /supervision/warnings | |

---

## 八、验收模块 `/acceptance`

**国家标准**：GB 50327-2001等

| 接口 | 方法 | 路径 | 说明 |
|------|------|------|------|
| 验收标准 | GET | /acceptance/standards | 国标库 |
| 节点清单 | GET | /acceptance/node-checklist/{node_id} | |
| 提交验收 | POST | /acceptance/submit | |
| 验收报告 | GET | /acceptance/report/{id} | |
| 报告列表 | GET | /acceptance/my-reports | |
| 维保信息 | GET | /acceptance/warranty/{project_id} | |

---

## 九、支付模块 `/payment`

| 接口 | 方法 | 路径 | 说明 |
|------|------|------|------|
| 产品列表 | GET | /payment/products | |
| 创建订单 | POST | /payment/create-order | |
| 订单详情 | GET | /payment/order/{no} | |
| VIP状态 | GET | /payment/vip-status | |
| 取消订单 | POST | /payment/cancel/{no} | |
| 支付回调 | POST | /payment/notify | |

---

## 十、错误码

| 错误码 | 说明 |
|--------|------|
| 200 | 成功 |
| 400 | 参数错误 |
| 401 | 未认证 |
| 403 | 无权限 |
| 404 | 资源不存在 |
| 429 | 请求过于频繁 |
| 500 | 服务器错误 |

---

## 十一、限流规则

| 接口类型 | 限制 |
|----------|------|
| 普通接口 | 100次/分钟 |
| 发送验证码 | 3次/分钟 |
| AI分析接口 | 20次/小时 |

---

## 十二、性能指标

| 接口类型 | 目标时间 |
|----------|----------|
| 身份认证 | ≤100ms |
| 预算联动 | ≤300ms |
| AI验房单张 | ≤2秒 |
| AI设计方案 | ≤3秒 |
| AI效果图 | ≤10秒 |
| 云监工识别 | ≤3秒 |
| 普通接口 | ≤500ms |

---

*文档版本：V3.0 | 更新日期：2026-04-06*
