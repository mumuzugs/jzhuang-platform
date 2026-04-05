# 集装修 - 一站式装修服务平台

<div align="center">

**国内首个AI全链路赋能的装修新手零门槛一站式服务平台**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![Go](https://img.shields.io/badge/Go-1.21+-blue.svg)](https://go.dev/)

**架构版本：V2.0**

</div>

---

## 🎯 项目简介

**集装修** 旨在解决装修新手面临的核心痛点：

- 🏠 **不懂设计** → AI一键生成设计方案，效果图实时预览
- 💰 **预算超支** → 设计-预算实时联动，预算红线预警
- 👷 **没时间盯工地** → AI云监工，进度自动识别

## 📋 核心功能（8大模块）

| 模块 | 功能 | 状态 |
|------|------|------|
| 🤖 AI智能验房 | 拍照识别8类房屋问题，生成专业报告 | ✅ |
| 🎨 AI设计与预算联动 | 户型→方案→效果图→预算实时联动 | ✅ |
| 👷 施工全流程管理 | 计划生成、进度管控、节点验收 | ✅ |
| 📹 AI云监工 | 施工进度识别、合规检测、预警推送 | ✅ |
| ✅ 标准化验收 | 国家规范库、节点验收、维保服务 | ✅ |
| 💳 订单与支付 | 微信支付、分期付款、资金管控 | ✅ |
| 👤 用户全域管理 | 身份认证、权限控制、房屋档案 | ✅ |
| 🔐 合规与安全 | 三级等保、数据安全、操作审计 | 🔨 |

## 📂 项目结构

```
jzhuang-platform/
├── docs/                    # 项目文档
│   ├── PRD.md              # MVP产品需求文档
│   ├── ARCHITECTURE.md     # 技术架构方案 V2.0
│   └── TEST_REPORT.md      # 测试报告
├── packages/
│   ├── api/               # 后端API服务 (Python FastAPI)
│   ├── engine/             # 预算引擎 (Go)
│   ├── web/               # 微信小程序 (Taro)
│   └── admin/             # PC管理后台 (React)
├── scripts/                # 工具脚本
└── docker-compose.yml
```

## 🚀 快速开始

```bash
# 克隆仓库
git clone https://github.com/mumuzugs/jzhuang-platform.git
cd jzhuang-platform

# 启动基础设施
docker-compose up -d postgres redis

# 安装后端依赖
cd packages/api && pip install -r requirements.txt

# 启动后端
uvicorn src.main:app --reload --port 8000
```

## 🔧 技术栈

| 层级 | 技术选型 | 说明 |
|------|----------|------|
| 后端 | Python FastAPI | AI服务对接、业务快速迭代 |
| 高并发 | Go Gin | 预算引擎、支付服务 |
| 数据库 | PostgreSQL + Redis | 主库 + 缓存 |
| 前端 | Taro + React | 小程序 + 管理后台 |

## 📊 API接口统计

| 模块 | 接口数 | 说明 |
|------|--------|------|
| 认证 | 8 | 登录/注册/Token |
| 用户 | 4 | 资料/权限/VIP状态 |
| 验房 | 7 | AI验房/报告 |
| 设计 | 11 | AI设计/预算 |
| 施工 | 10 | 施工计划/节点 |
| 监工 | 5 | 进度识别/预警 |
| 验收 | 6 | 验收流程/维保 |
| 支付 | 6 | 订单/微信支付 |
| **总计** | **57** | - |

## 📅 开发计划

| 阶段 | 周期 | 目标 |
|------|------|------|
| MVP开发 | 14周 | 完成核心功能内测 |
| Beta测试 | 2周 | 1000用户测试 |
| 正式上线 | - | 全渠道发布 |

## 🤝 贡献指南

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

MIT License

---

**© 2026 集装修 - 让装修像点外卖一样简单可控**
