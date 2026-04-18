# 集装修 - 前端项目

> 集装修一站式装修服务平台前端，基于 UniApp + Vue 3 + TypeScript

## 技术栈

- **框架**: UniApp + Vue 3
- **语言**: TypeScript
- **状态管理**: Pinia
- **构建工具**: Vite
- **样式**: SCSS

## 项目结构

```
src/
├── api/                 # API 接口
│   ├── auth.ts         # 认证相关
│   ├── users.ts        # 用户相关
│   ├── inspection.ts   # AI 验房
│   ├── design.ts       # AI 设计+预算
│   ├── construction.ts # 施工/云监工
│   ├── payment.ts      # 支付
│   └── request.ts      # 请求封装
├── components/          # 公共组件
├── config/              # 配置文件
├── hooks/               # 组合式函数
├── pages/               # 页面
│   ├── auth/           # 认证页面
│   ├── home/           # 首页
│   ├── inspection/     # AI 验房
│   ├── design/         # AI 设计
│   ├── construction/   # 施工/云监工
│   └── mine/           # 我的
├── static/              # 静态资源
├── store/               # 状态管理
├── styles/              # 全局样式
├── types/               # 类型定义
└── utils/               # 工具函数
```

## 功能模块

### 1. AI 验房
- 8类装修问题识别
- 智能验房报告生成
- 城市高频风险查询

### 2. AI 设计预算联动
- 3套差异化设计方案
- 装修风格选择
- 实时预算联动

### 3. 云监工
- 标准化施工流程
- 8大核心节点管理
- 延期预警提醒

## 开发

```bash
# 安装依赖
pnpm install

# 开发模式
pnpm dev

# 小程序开发
pnpm dev:mp-weixin

# 构建
pnpm build
```

## 后端 API

- 开发环境: `http://localhost:8000/api/v1`
- 生产环境: `https://api.jizhuang.cn/api/v1`

## License

MIT
