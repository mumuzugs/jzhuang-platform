# 集装修 - 一站式装修服务平台

<div align="center">

**国内首个AI全链路赋能的装修新手零门槛一站式服务平台**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![Go](https://img.shields.io/badge/Go-1.21+-blue.svg)](https://go.dev/)
[![React](https://img.shields.io/badge/React-18-blue.svg)](https://reactjs.org/)

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
| 🤖 AI验房 | 拍照识别8类房屋问题，生成专业报告 | ✅ 已完成 |
| 🎨 AI设计 | 户型图→平面方案→效果图→施工图 | ✅ 已完成 |
| 💰 预算联动 | 设计参数实时联动预算，秒级响应 | ✅ 已完成 |
| 👷 云监工 | AI识别施工进度，节点自动通知 | ✅ 已完成 |
| ✅ 施工计划 | 自动生成施工计划，节点管理 | ✅ 已完成 |

## 📂 项目结构

```
jzhuang-platform/
├── docs/                    # 项目文档
│   ├── PRD.md              # MVP产品需求文档
│   └── ARCHITECTURE.md     # 技术架构方案
├── packages/
│   ├── web/               # 微信小程序前端 (Taro)
│   ├── admin/             # PC管理后台 (React + Ant Design)
│   ├── api/               # 后端API服务 (Python FastAPI)
│   ├── engine/            # 预算计算引擎 (Go)
│   └── ai/                # AI服务封装
├── scripts/                # 工具脚本
├── configs/                # 配置文件
├── docker-compose.yml      # Docker编排
└── README.md
```

## 🚀 快速开始

### 环境要求

- Node.js >= 18
- Python >= 3.11
- Go >= 1.21
- Docker >= 24

### 本地开发

```bash
# 克隆仓库
git clone https://github.com/mumuzugs/jzhuang-platform.git
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
cd packages/api && uvicorn src.main:app --reload
```

### API文档

启动服务后访问：`http://localhost:8000/docs`

## 📖 文档

| 文档 | 说明 |
|------|------|
| [PRD.md](docs/PRD.md) | MVP产品需求文档 |
| [ARCHITECTURE.md](docs/ARCHITECTURE.md) | 商用级技术架构方案 |

## 🔧 技术栈

### 后端
- **Python FastAPI** - AI服务对接、业务快速迭代
- **Go Gin** - 高并发服务（预算引擎、支付）
- **PostgreSQL** - 主数据库
- **Redis** - 缓存

### 前端
- **Taro** - 微信小程序
- **React** - PC管理后台
- **Flutter** - 移动APP

### AI能力
- **智谱GLM-4.5** - 智能对话、设计建议
- **阿里云视觉** - 图像识别
- **自研引擎** - 预算联动、施工进度识别

## 📊 API接口

| 模块 | 端点数 | 说明 |
|------|--------|------|
| 认证 | 8 | 登录/注册/Token |
| 用户 | 4 | 资料/VIP状态 |
| 验房 | 7 | AI验房/报告 |
| 设计 | 11 | AI设计/预算 |
| 施工 | 10 | 施工计划/节点 |
| 支付 | 6 | 订单/微信支付 |

## 📅 开发计划

| 阶段 | 周期 | 目标 |
|------|------|------|
| MVP开发 | 14周 | 完成核心功能内测 |
| Beta测试 | 2周 | 1000用户测试 |
| 正式上线 | - | 全渠道发布 |

## 🤝 贡献指南

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件

---

**© 2026 集装修 - 让装修像点外卖一样简单可控**
