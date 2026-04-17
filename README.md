# 集装修 - 一站式装修服务平台

<div align="center">

![Logo](docs/images/logo.png)

**国内首个AI全链路赋能的装修新手零门槛一站式服务平台**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![React](https://img.shields.io/badge/React-18-blue.svg)](https://reactjs.org/)
[![Flutter](https://img.shields.io/badge/Flutter-3.0-blue.svg)](https://flutter.dev/)

</div>

---

## 🎯 项目简介

**集装修** 旨在解决装修新手面临的核心痛点：

- 🏠 **不懂设计** → AI一键生成设计方案，效果图实时预览
- 💰 **预算超支** → 设计-预算实时联动，预算红线预警
- 👷 **没时间盯工地** → AI云监工，进度自动识别

## 📋 核心功能

| 模块 | 功能 | 状态 |
|------|------|------|
| 🤖 AI验房 | 拍照识别8类房屋问题，生成专业报告 | 🔨 开发中 |
| 🎨 AI设计 | 户型图→平面方案→效果图→施工图 | 🔨 开发中 |
| 💰 预算联动 | 设计参数实时联动预算，秒级响应 | 🔨 开发中 |
| 👷 云监工 | AI识别施工进度，节点自动通知 | 🔨 开发中 |
| ✅ 验收指导 | 分阶段验收清单，AI辅助验收 | 📋 规划中 |

## 🏗️ 技术架构

```
┌─────────────────────────────────────────────────────────────┐
│                      接入层                                  │
│    微信小程序(Taro)    │    PC管理后台(React)    │   APP(Flutter)   │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                      API网关层 (Nginx/APISIX)               │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                      应用服务层                              │
│  用户服务  │  验房服务  │  设计服务  │  预算引擎  │  监工服务  │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                      AI能力层                               │
│    智谱GLM-4.5    │    阿里云视觉    │    预算联动引擎(Go)    │
└─────────────────────────────────────────────────────────────┘
```

## 📂 项目结构

```
jzhuang-platform/
├── packages/
│   ├── web/           # 微信小程序前端 (Taro)
│   ├── admin/         # PC管理后台 (React + Ant Design)
│   ├── api/           # 后端API服务 (Python FastAPI)
│   ├── engine/        # 预算计算引擎 (Go)
│   └── ai/            # AI服务封装
├── docs/              # 项目文档
├── scripts/           # 脚本工具
├── configs/           # 配置文件
├── docker-compose.yml # Docker编排
└── README.md
```

## 🚀 快速开始

### 环境要求

- Node.js >= 18
- Python >= 3.11
- Go >= 1.21
- Docker >= 24
- PostgreSQL >= 15
- Redis >= 7

### 本地开发

```bash
# 克隆仓库
git clone https://github.com/你的用户名/jzhuang-platform.git
cd jzhuang-platform

# 启动基础设施
docker-compose up -d postgres redis

# 安装前端依赖
cd packages/web && npm install
cd packages/admin && npm install

# 安装后端依赖
cd packages/api && pip install -r requirements.txt

# 启动开发服务
cd packages/web && npm run dev
cd packages/api && uvicorn main:app --reload
```

## 📅 开发计划

| 阶段 | 周期 | 目标 |
|------|------|------|
| MVP开发 | 14周 | 完成核心功能内测 |
| Beta测试 | 2周 | 1000用户测试 |
| 正式上线 | - | 全渠道发布 |

## 📖 文档

- [产品需求文档(PRD)](docs/prd.md)
- [技术架构方案](docs/architecture.md)
- [API接口文档](docs/api.md)
- [数据库设计](docs/database.md)
- [部署文档](docs/deployment.md)

## 🤝 贡献指南

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件

---

**© 2026 集装修 - 让装修像点外卖一样简单可控**
