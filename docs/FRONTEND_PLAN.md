# 「集装修」前端开发方案 V1.1

**文档版本**：V1.1（整合豆包UX深度评审）
**编制日期**：2026-04-06
**编制人**：木腾云
**匹配后端**：jzhuang-platform API V3.0（46接口已通过全链路测试）
**目标终端**：微信小程序（主）+ H5（辅）

---

## 一、技术选型与工程规范

### 1.1 跨端框架选型

| 选项 | 技术栈 | 选择理由 |
|------|--------|----------|
| 主方案 | UniApp + Vue 3 + TypeScript | 一套代码编译至微信小程序/H5/iOS/Android，复用现有后端API |
| 本方案推荐 | UniApp | 符合PRD明确的微信小程序+移动端APP+H5多端需求，生态成熟 |

### 1.2 技术栈清单

```
核心框架    ：UniApp 3.x（Vue 3 Composition API + TypeScript）
状态管理    ：Pinia（轻量、支持持久化）
路由管理    ：UniApp Router（pages.json配置式路由）
网络请求    ：Axios + 请求拦截器（自动携带JWT Token）
AI能力接入  ：图片上传至后端接口
支付接入    ：UniPay（微信小程序内调起JSAPI支付）
本地存储    ：uni-storage（Token、用户偏好缓存）
图标        ：iconfont 定制装修行业图标库
动画        ：uni.createAnimation（页面切换/AI生成/进度条动画）
```

### 1.3 项目工程结构

```
jzhuang-frontend/
src/
  api/         # 接口层：所有后端API一一对应
    auth.ts        认证模块 8个接口
    user.ts        用户模块 12个接口
    inspection.ts  验房模块 7个接口
    design.ts      设计模块 11个接口
    construction.ts 施工模块 10个接口
    supervision.ts 云监工模块 5个接口
    acceptance.ts  验收模块 6个接口
    payment.ts    支付模块 6个接口
  pages/       # 页面（共约29个，与后端模块一一对应）
    auth/       登录注册 3页
    home/       首页 1页
    inspection/ 验房 4页
    design/     AI设计 6页
    construction 施工 5页
    supervision 云监工 3页
    acceptance  验收 4页
    payment/    支付 3页
    user/       个人中心 4页
  components/  # 业务组件库
    ai-avatar/         AI助手形象（亲和力核心）
    inspection-card/   验房结果卡片
    progress-timeline/ 施工进度时间轴
    budget-meter/     预算仪表盘
    upload-zone/      图片上传区（通用）
    pay-wall/         专业版解锁墙
  composables/ 组合式函数
  stores/       Pinia状态管理
  utils/        工具函数
  styles/       全局样式
pages.json      UniApp路由配置
manifest.json   应用配置
```

### 1.4 API层与后端精确对应

所有前端接口严格对应后端 /api/v1/*，禁止自行发明接口：

认证模块8个：POST send-code/login/wechat-login, GET me, POST refresh/change-password/reset-password/logout
用户模块12个：GET/PUT profile, GET roles, POST switch-role, GET/POST houses, GET houses/id, GET/POST tags, GET audit-logs, GET vip/status, DELETE account
验房模块7个：GET issue-types/city-risks/city, POST create/analyze, GET report/id/my-reports, POST request-review
设计模块11个：GET styles/layouts, POST create/floor-plan/generate/render/adjust/budget/drawings/confirm, GET materials/plan_id
施工模块10个：GET standard-nodes/notifications/my-projects, POST create/node/update/acceptance/supervision/upload/supervision/recognize, GET project/id/project/id/progress
云监工模块5个：POST recognize-progress/check-compliance/check-anomalies, GET warning-rules/warnings
验收模块6个：GET standards/node-checklist/node_id/report/id/my-reports/warranty/project_id, POST submit
支付模块6个：GET products/vip-status, POST create-order/cancel/no/notify, GET order/no

---

## 二、设计语言体系

### 2.1 设计理念：「专业可信、温暖可亲」

目标用户：25-35岁首次装修刚需用户，零装修经验，对行业术语陌生，996工作节奏。

设计主张（三感模型）：
专业感：清晰的信息层次、标准化术语翻译（专业+通俗双行显示）、量化数据展示
亲和力：温暖配色、友好引导文案、AI拟人化助手，让用户感到有人帮我
掌控感：实时进度可视化、预算红线预警、节点主动提醒，一切尽在掌握

### 2.2 色彩体系

品牌基础色：

| 角色 | 色值 | 使用场景 |
|------|------|----------|
| 品牌蓝 | #2563EB | 主按钮、导航高亮、链接 |
| 信任绿 | #10B981 | 成功状态、验收通过、预算正常 |
| 警示橙 | #F59E0B | 中风险预警、预算超支提醒 |
| 危险红 | #EF4444 | 高风险隐患、严重问题、已超支 |
| 专业灰 | #64748B | 次要文字、分割线、说明 |
| 温暖底色 | #FFF9F5 | 页面背景（降低装修焦虑感） |
| 纯净白 | #FFFFFF | 卡片背景、内容区背景 |

语义色卡：
正常/完成 → #10B981 验收通过、预算正常
警告/关注 → #F59E0B 中风险、预算接近红线
危险/阻断 → #EF4444 高风险、已超支
信息/引导 → #2563EB AI分析中、链接
未开始 → #E2E8F0 待处理状态
推荐/亮点 → #8B5CF6 AI推荐方案
预算金额 → #059669 深绿专业感

渐变色规范：
brand-gradient: linear-gradient(135deg, #2563EB 0%, #3B82F6 100%)  品牌渐变
success-gradient: linear-gradient(135deg, #10B981 0%, #34D399 100%)  成功渐变
warm-gradient: linear-gradient(180deg, #FFF9F5 0%, #FFEDD5 100%)  温暖渐变
danger-gradient: linear-gradient(135deg, #EF4444 0%, #F87171 100%)  危险渐变

### 2.3 字体规范

font-family: -apple-system, BlinkMacSystemFont, "PingFang SC", "Helvetica Neue", Helvetica, Arial, sans-serif;

| 级别 | 字号 | 字重 | 使用场景 |
|------|------|------|----------|
| Display | 48rpx | 700 | 启动页/大数字 |
| H1 | 40rpx | 700 | 首页大标题、报告封面 |
| H2 | 36rpx | 700 | 模块标题、结果页标题 |
| H3 | 32rpx | 600 | 卡片标题、节点名称 |
| H4 | 28rpx | 600 | 列表项标题、标签名 |
| Body | 28rpx | 400 | 正文内容 |
| Body-Small | 24rpx | 400 | 次要说明、备注 |
| Caption | 22rpx | 400 | 标签、时间戳 |
| Number | 48rpx | 700 | 核心数字（预算/进度） |

### 2.4 间距与圆角

间距基准（8rpx网格）：xs=8rpx, sm=16rpx, md=24rpx, lg=32rpx, xl=48rpx, xxl=64rpx
页面左右边距：32rpx（统一）
卡片间距：24rpx

圆角：大卡片24rpx，按钮16rpx，中卡片/标签12rpx，小标签/徽章8rpx，图片16rpx，头像/AI助手50%圆形

### 2.5 阴影与动效

card-shadow: 0 4rpx 24rpx rgba(37, 99, 235, 0.08)   卡片阴影（专业感）
float-shadow: 0 8rpx 40rpx rgba(0, 0, 0, 0.12)   浮层阴影（弹窗）
generating-shadow: 0 4rpx 24rpx rgba(37, 99, 235, 0.15)  AI生成中阴影

| 动效类型 | 时长 | 场景 |
|----------|------|------|
| 页面切换 | 300ms | 左右滑动 |
| 卡片展开 | 250ms | 折叠展开 |
| 按钮反馈 | 150ms | 点击态 |
| AI脉冲 | 1500ms | 分析中（循环） |
| 进度更新 | 600ms | 进度条增长 |
| 数字跳动 | 400ms | 金额变化 |
| Toast | 200ms | 轻提示 |

---

## 三、核心组件规范

### 3.1 AI助手形象组件（产品亲和力核心）

组件名：ai-avatar
Props：type（idle/thinking/success/warning），message（引导文案），avatarSrc

代码规范：
template:
  view.ai-avatar-wrapper
    image.avatar :src=avatarSrc mode=aspectFill  头像96rpx圆形
    view.thinking-dots v-if=type === thinking  三圆点动画
    view.message-bubble :class=bubble-type  消息气泡

style:
  .avatar: width 96rpx, height 96rpx, border-radius 50%
  .message-bubble: max-width 480rpx, background #2563EB, color #fff, border-radius 24rpx, padding 16rpx 20rpx, font-size 28rpx
  .bubble-success: background #10B981
  .bubble-warning: background #F59E0B
  .thinking-dots: position absolute, left 72rpx top 40rpx, display flex, gap 8rpx
  .dot: width 12rpx, height 12rpx, background #2563EB, border-radius 50%, animation bounce 1.4s infinite
  dot-2 delay 0.2s, dot-3 delay 0.4s

引导语气规范（贯穿全产品，AI说人话）：

| 场景 | 推荐文案 | 语气 |
|------|----------|------|
| 验房上传 | 上传房屋照片，AI帮您找出问题 | 温暖轻松 |
| 验房分析中 | 正在识别问题，请稍候~ | 亲切有耐心 |
| 验房完成 | 发现{n}处问题，已为您标注在图中 | 专业但不说教 |
| 设计上传 | 上传户型图，10秒生成设计方案 | 自信简洁 |
| 设计分析中 | AI正在规划空间布局，稍等片刻 | 轻松愉快 |
| 预算超支 | 检测到超支风险，AI已为您准备替代方案 | 主动关怀 |
| 云监工完成 | 本次施工进度正常，未发现异常 | 让人安心 |
| 云监工发现隐患 | 检测到一处安全隐患，建议立即处理 | 严肃但不吓人 |

### 3.2 验房结果卡片（专业感核心）

组件名：inspection-card
Props：issueType, severity（high/medium/low）, title, description, plainLanguage, location, suggest

代码规范：
template:
  view.inspection-card :class=severity-type
    view.severity-bar  左侧6rpx色条
    view.card-content
      view.card-header
        text.issue-title
        view.severity-badge :class=badge-type  严重程度徽章
      view.location-tag  位置标注
      view.description
        text.desc-main  专业描述
        text.desc-plain  通俗解释行
      view.suggest-box  整改建议

style:
  .inspection-card: display flex, background #fff, border-radius 24rpx, overflow hidden, box-shadow card-shadow, margin-bottom 24rpx
  .severity-bar: width 6rpx, flex-shrink 0
  severity-high: background #EF4444
  severity-medium: background #F59E0B
  severity-low: background #2563EB
  .severity-badge: padding 4rpx 12rpx, border-radius 8rpx, font-size 22rpx, font-weight 600
  badge-high: background #FEE2E2, color #EF4444
  badge-medium: background #FEF3C7, color #D97706
  badge-low: background #DBEAFE, color #2563EB
  .desc-plain: display block, font-size 24rpx, color #64748B, margin-top 8rpx

8类问题通俗翻译对照（设计系统内置）：

| 专业术语 | 通俗翻译 |
|----------|----------|
| 墙面结构性裂缝 | 墙面出现明显裂缝，可能是墙体问题 |
| 地面平整度偏差 | 地面不平，踩上去有高低感 |
| 防水渗漏风险 | 卫生间/厨房有漏水隐患 |
| 门窗密封不良 | 门窗关不严，漏风漏噪音 |
| 水电点位不合规 | 插座/开关位置不对或数量不够 |
| 墙面空鼓 | 墙砖/墙皮贴得不牢，敲起来有空鼓声 |
| 阴阳角不垂直 | 墙角不是90度，影响家具摆放 |
| 下水不畅 | 排水管有点堵，水流得慢 |

### 3.3 施工进度时间轴（掌控感核心）

组件名：progress-timeline
Props：nodes（Array，含8大节点）

代码规范：
template: 垂直时间轴，左侧圆点+右侧信息
  view.timeline
    view.timeline-node :class=status-node.status v-for=(node,index)
      view.connector v-if=index < length-1  连接线
      view.node-dot: image(v-if done)/text(v-if current icon)/(v-else number)  节点圆点32rpx
      view.node-info: text.node-name/text.node-date/text.label-status

style:
  8大节点图标：开工-水电-防水-泥瓦-木工-油漆-安装-竣工
  状态颜色：done信任绿/current品牌蓝+脉冲/pending灰色/delayed危险红
  当前节点脉冲动画：pulse-ring 2s infinite

### 3.4 预算仪表盘（省钱价值核心）

组件名：budget-meter
Props：total（总预算）, used（已用）, breakdown（Array分项）

代码规范：
template:
  view.budget-meter
    view.ring-container: canvas#budgetRing + view.ring-center(总金额+标签)
    view.budget-banner :class=bannerClass  状态横幅
    view.breakdown: 分项柱状图列表

script:
  getBarClass: 0-70%绿/70-90%橙/90-100%红/>100%深红闪烁

圆环颜色逻辑：
0-70%：绿色 #10B981（正常）
70-90%：橙色 #F59E0B + 轻微脉冲（接近红线）
90-100%：红色 #EF4444 + 警示文案接近预算红线
>100%：红色 #EF4444 + 闪烁动画 + 已超预算

### 3.5 图片上传区

组件名：upload-zone
Props：hint, format, maxCount（默认9）
Events：change（files数组变化）

代码规范：
template:
  空状态: 虚线边框区域，上传图标64rpx，引导文案
  预览态: 9宫格缩略图，右上角删除，分析态半透明遮罩+AI头像

关键要点：自动压缩至不超过2M；照片水印（时间+项目名，canvas绘制）；分析态半透明遮罩+AI头像

### 3.6 专业版解锁墙（商业转化核心）

组件名：pay-wall
Events：close，pay

权益清单（5项）：
1. 无限次AI验房 + 高清报告下载
2. 全套AI设计方案 + 实时预算联动
3. 自动施工计划 + 节点主动提醒
4. 无限次云监工 + AI进度识别
5. 工程档案永久存储

代码规范：
全屏半透明黑色遮罩rgba(0,0,0,0.72)，居中白色卡片32rpx圆角
顶部品牌渐变条16rpx，关闭按钮右上角
主标题36rpx/700，价格64rpx/700品牌蓝，原价划线
CTA按钮96rpx高，品牌渐变背景，白色文字32rpx/600
底部文案22rpx灰色，每天不到2元

---

## 四、页面UI规范

### 4.1 首页（/pages/home/index）— 产品价值门户

页面布局：
顶部：状态栏品牌渐变沉浸背景（#2563EB→#3B82F6，高度200rpx），白色Logo+通知+头像
欢迎语区：#FFF9F5温暖底色，32rpx/700品牌蓝欢迎语，28rpx/400#64748B副文案
功能入口：2x2卡片网格，白色背景+card-shadow，图标96rpx，间距24rpx
当前项目进度卡：卡片顶部彩色条带（当前施工阶段颜色）+迷你进度条+迷你预算（仅在有进行中项目时显示）
底部：专业版推广条，固定悬浮，品牌渐变背景，顶部圆角模拟悬浮效果

关键设计点：
功能卡片避免使用焦虑词汇，用帮您/我来/轻松等亲和表达
AI语气贯穿全产品
首页不显示Tabbar数字徽章，通知数在顶部铃铛图标显示红点

### 4.2 登录注册页（/pages/auth/login）— 极简转化

页面布局：
顶部：品牌渐变小背景区（高300rpx，向下圆角延伸），Logo+Slogan
表单区：手机号输入框（48rpx高，24rpx圆角，focus蓝边框）+ 验证码输入框+发送按钮（品牌蓝，60秒倒计时）
主按钮：登录/注册，48rpx高，32rpx圆角，品牌蓝
分隔线：或其他登录方式
次按钮：微信一键登录，白底灰边蓝字
底部：隐私协议小字，协议蓝字可点击

交互规范：
错误反馈：输入框下方红色小字，不用alert弹窗打断
隐私协议：蓝字可点击跳转协议页
倒计时：按钮置灰+59秒后重发

### 4.3 AI验房页（/pages/inspection/index）— 信任建立

验房首页：
顶部导航栏：返回+标题+帮助
AI助手形象区：<ai-avatar>，温暖引导语气
图片上传区：<upload-zone>，虚线边框，提示语
底部固定栏：选中照片数量+开始分析CTA按钮

验房报告页（/pages/inspection/report）：
顶部工具栏：返回+标题+分享+下载（分享和下载在报告页尤为重要）
AI完成态：<ai-avatar type=success>，发现{n}处问题
报告概览卡片：3个数字徽章（高风险1/中风险1/低风险1），数字40rpx/700，标签22rpx
问题列表：<inspection-card>按严重程度分组，高风险默认展开，中低风险折叠
整改建议汇总：AI自动汇总所有整改步骤，按优先级排序
底部双按钮：返回首页（次要按钮）+预约人工复核（主按钮）

### 4.4 AI设计页（/pages/design/index）— 核心价值页

Step1 户型上传：
<ai-avatar>引导+<upload-zone>户型图上传

Step2 方案选择：
顶部导航：返回+标题+实时预算金额（随方案切换实时变化）
<ai-avatar type=success>已生成3套差异化方案
3个方案卡片横向或纵向排列，含效果图缩略图+方案名称+预算金额+选择按钮
AI推荐方案打标（星星标签）

Step3 风格选择：
3种装修风格卡片：现代简约/北欧/新中式
每个风格卡片含风格说明+代表效果图缩略图

Step4 效果图生成：
<ai-avatar type=thinking>AI正在渲染高清效果图，请稍候~
loading态：大图占位+脉冲动画+预计剩余时间
完成态：高清效果图展示，支持左右滑动对比

Step5 预算联动：
<budget-meter>实时展示预算仪表盘
超支预警横幅（超实时变色）
分项柱状图（客厅/厨房/卧室等）
智能优化建议卡片（蓝色边框）：AI推荐替代方案，应用此方案/了解更多

Step6 确认方案：
方案汇总卡片：效果图+设计说明+预算总览+材料清单预览
底部：上一步+生成施工图（次要）+确认方案（主按钮，渐变背景）

### 4.5 施工进度页（/pages/construction/index）— 掌控感核心

页面布局：
顶部导航：返回+标题+切换项目（下拉选择多项目管理）
项目概览卡片：项目名称+总进度条（品牌渐变）+当前节点+剩余天数
<progress-timeline>：8大节点时间轴，当前节点展开详情
当前节点详情卡：节点名称+开工/预计完工日期+状态标签+本阶段任务清单（可勾选）
云监工快捷入口：点击跳转云监工页
底部：上一步节点+节点验收+下一步节点

### 4.6 云监工页（/pages/supervision/index）— 差异化壁垒页

页面布局：
<ai-avatar>引导语：上传工地照片，我来帮您识别施工进度和潜在问题
<upload-zone>：支持单张/批量上传，说明支持照片
上次识别结果卡：当前阶段+完成度进度条+与计划对比状态+合规检测结果
识别历史：横向滚动缩略图列表
待处理预警：有预警时显示高/中/低风险分级卡片，无预警时隐藏此区

### 4.7 验收页（/pages/acceptance/index）— 闭环收尾页

页面布局：
顶部导航：返回+标题+国标参照（GB50327）
验收标准卡片（白色）：本节点国标验收标准列表，标准灰字专业感，点击查看完整PDF
验收项清单：每项含名称+状态（待验收/已通过/未通过）+详情按钮
拍照留证区：每项至少1张照片，照片自动添加时间+项目名水印（canvas绘制）
底部：提交验收按钮（所有必填项完成后可提交）

### 4.8 个人中心（/pages/user/index）— 用户资产页

页面布局：
顶部用户信息区：头像+昵称（手机号脱敏）+VIP身份标识卡（金色边框，专业版有效期内显示）
我的数据资产区：数字徽章网格（验房报告数/设计方案数/装修项目数/云监工照片数/验收报告数）
功能入口列表：我的订单/设计方案/装修项目/我的报告/账号设置
底部：联系客服+关于我们+版本号

---

## 五、关键设计原则总结

### 5.1 专业感实现路径

信息层次分明：H1/H2/H3/H4四级标题体系，视觉层级清晰
术语翻译双行：所有专业术语均配通俗翻译，用颜色#64748B区分主次
量化数据展示：数字使用Number级别字体（48rpx/700），金额使用深绿色#059669
国标背书：在验收模块显著位置标注GB50327等国家标准，增强可信度

### 5.2 亲和力实现路径

AI助手形象：96rpx圆形头像+消息气泡+三圆点动画，全产品一致
温暖配色：页面背景#FFF9F5（米白），避免纯白冷调，降低装修焦虑感
语气规范：AI助手说人话，避免技术术语和焦虑词汇
错误处理：不用alert弹窗，用输入框下方红色小字，友好提示

### 5.3 掌控感实现路径

进度可视化：<progress-timeline>8大节点时间轴，当前节点脉冲动画
预算实时联动：<budget-meter>环形仪表盘，颜色实时变化，超支闪烁预警
节点主动通知：施工6大节点开工前+完工后双渠道推送
数据资产沉淀：个人中心展示所有历史数据，用户感受到积累

### 5.4 开发注意事项

首屏加载≤2秒，二级页面≤1.5秒（4G/5G）
AI分析接口loading态必须展示，不能出现空白等待
预算联动≤300ms，前端做好骨架屏和预计算
图片上传必须压缩+水印，防止超限和篡改
JWT Token自动刷新，前端无感知续期
