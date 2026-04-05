# 集装修 数据库设计文档 V3.0（5轮审核迭代版）

**版本**：V3.0  
**更新日期**：2026-04-06  
**数据库**：PostgreSQL 14+  
**审核状态**：进行中...

---

## 一、架构文档V2.0核对清单

### 8大核心模块核对

| 模块 | 架构要求子模块数 | 数据库表数 | API接口数 | 符合度 |
|------|------------------|-----------|-----------|--------|
| 1.用户全域管理 | 6 | 5 | 12 | ⚠️ |
| 2.AI智能验房 | 4 | 4 | 7 | ✅ |
| 3.AI设计与预算 | 5 | 12 | 11 | ⚠️ |
| 4.施工管理 | 6 | 6 | 10 | ✅ |
| 5.AI云监工 | 5 | 4 | 5 | ⚠️ |
| 6.验收模块 | 5 | 3 | 6 | ⚠️ |
| 7.支付模块 | 4 | 4 | 6 | ✅ |
| 8.合规安全 | 6 | 1 | 0 | ❌ |

---

## 二、用户全域管理模块

### 2.1 表结构

```sql
-- 用户基础表
CREATE TABLE users (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    phone           VARCHAR(20) NOT NULL UNIQUE,
    nickname        VARCHAR(50),
    avatar          VARCHAR(500),
    password_hash   VARCHAR(255),
    status          VARCHAR(20) DEFAULT 'active',
    is_pro          BOOLEAN DEFAULT FALSE,
    pro_expire_time TIMESTAMP,
    source          VARCHAR(20) DEFAULT 'phone',
    wx_openid       VARCHAR(100),
    wx_unionid      VARCHAR(100),
    last_login_at   TIMESTAMP,
    last_login_ip   VARCHAR(50),
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deleted_at      TIMESTAMP
);

-- 用户角色表（支持多角色）
CREATE TABLE user_roles (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         UUID NOT NULL REFERENCES users(id),
    role            VARCHAR(30) NOT NULL,
    role_name       VARCHAR(50),
    permissions     JSONB DEFAULT '[]',
    is_primary      BOOLEAN DEFAULT TRUE,
    status          VARCHAR(20) DEFAULT 'active',
    verified_at     TIMESTAMP,
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, role)
);

-- 房屋档案表
CREATE TABLE house_profiles (
    id                      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id                 UUID NOT NULL REFERENCES users(id),
    city                    VARCHAR(50) NOT NULL,
    district                VARCHAR(50),
    community               VARCHAR(200),
    building                VARCHAR(50),
    unit                    VARCHAR(20),
    room_number             VARCHAR(30),
    address                 VARCHAR(500),
    house_type              VARCHAR(30) NOT NULL,
    area                    DECIMAL(10,2),
    room_count              INTEGER,
    build_year              INTEGER,
    property_type           VARCHAR(30),
    decoration_status       VARCHAR(30) DEFAULT '未装修',
    design_project_id       UUID,
    construction_project_id UUID,
    inspection_report_id    UUID,
    created_at              TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at              TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 用户标签表
CREATE TABLE user_tags (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         UUID NOT NULL REFERENCES users(id),
    tag_code       VARCHAR(50) NOT NULL,
    tag_name       VARCHAR(100) NOT NULL,
    tag_type       VARCHAR(30) NOT NULL,
    tag_value      VARCHAR(255),
    weight          DECIMAL(5,2) DEFAULT 1.0,
    source          VARCHAR(30) DEFAULT 'system',
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, tag_code)
);

-- 操作审计日志表（6个月留存）
CREATE TABLE audit_logs (
    id              BIGSERIAL PRIMARY KEY,
    user_id         UUID REFERENCES users(id),
    action          VARCHAR(100) NOT NULL,
    module          VARCHAR(50) NOT NULL,
    resource_type   VARCHAR(50),
    resource_id     VARCHAR(100),
    detail          JSONB,
    ip              VARCHAR(50),
    device_info     JSONB,
    status          VARCHAR(20) DEFAULT 'success',
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_audit_logs_user_id ON audit_logs(user_id);
CREATE INDEX idx_audit_logs_module ON audit_logs(module);
CREATE INDEX idx_audit_logs_created_at ON audit_logs(created_at);
```

### 2.2 API接口

| 接口 | 方法 | 路径 | 说明 |
|------|------|------|------|
| 发送验证码 | POST | /auth/send-code | |
| 登录 | POST | /auth/login | |
| 微信登录 | POST | /auth/wechat-login | |
| 获取用户 | GET | /auth/me | |
| 刷新Token | POST | /auth/refresh | |
| 修改密码 | POST | /auth/change-password | |
| 重置密码 | POST | /auth/reset-password | |
| 退出登录 | POST | /auth/logout | |
| 获取资料 | GET | /users/profile | |
| 更新资料 | PUT | /users/profile | |
| 获取角色 | GET | /users/roles | 6种角色 |
| 切换角色 | POST | /users/switch-role | |
| 房屋列表 | GET | /users/houses | |
| 添加房屋 | POST | /users/houses | |
| 房屋详情 | GET | /users/houses/{id} | |
| 用户标签 | GET/POST | /users/tags | |
| 审计日志 | GET | /users/audit-logs | 6个月 |
| VIP状态 | GET | /users/vip/status | |
| 注销账号 | DELETE | /users/account | |

---

## 三、AI智能验房模块

### 3.1 表结构

```sql
-- 验房报告表
CREATE TABLE inspection_reports (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    report_no           VARCHAR(50) UNIQUE NOT NULL,
    user_id             UUID NOT NULL REFERENCES users(id),
    house_id            UUID REFERENCES house_profiles(id),
    city                VARCHAR(50),
    house_type          VARCHAR(30) NOT NULL,
    area                DECIMAL(10,2),
    total_issues        INTEGER DEFAULT 0,
    high_risk_count     INTEGER DEFAULT 0,
    medium_risk_count   INTEGER DEFAULT 0,
    low_risk_count      INTEGER DEFAULT 0,
    total_estimated_cost DECIMAL(12,2) DEFAULT 0,
    ai_model            VARCHAR(100),
    ai_accuracy         INTEGER,
    review_status       VARCHAR(20) DEFAULT 'auto',
    status              VARCHAR(20) DEFAULT 'pending',
    report_content      TEXT,
    pdf_url             VARCHAR(500),
    share_url           VARCHAR(500),
    created_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at        TIMESTAMP,
    deleted_at          TIMESTAMP
);

-- 验房问题明细表（8类问题）
CREATE TABLE inspection_issues (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    report_id           UUID NOT NULL REFERENCES inspection_reports(id),
    issue_type         VARCHAR(50) NOT NULL,
    issue_name          VARCHAR(100) NOT NULL,
    description         TEXT,
    location            VARCHAR(100),
    room                VARCHAR(50),
    severity            VARCHAR(20) NOT NULL,
    confidence          INTEGER,
    suggestion          TEXT,
    national_standard   VARCHAR(200),
    estimated_cost      DECIMAL(10,2),
    image_urls          JSONB DEFAULT '[]',
    ai_model            VARCHAR(100),
    need_review        BOOLEAN DEFAULT FALSE,
    review_result       VARCHAR(20),
    created_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 验房图片表
CREATE TABLE inspection_images (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    report_id           UUID NOT NULL REFERENCES inspection_reports(id),
    issue_id            UUID REFERENCES inspection_issues(id),
    image_url           VARCHAR(500) NOT NULL,
    thumbnail_url       VARCHAR(500),
    image_type          VARCHAR(30),
    room                VARCHAR(50),
    ai_result           JSONB,
    has_issue           BOOLEAN DEFAULT FALSE,
    uploaded_at         TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 城市高频风险配置表
CREATE TABLE city_risk_configs (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    city_code            VARCHAR(10) NOT NULL,
    city_name            VARCHAR(50) NOT NULL,
    risk_type           VARCHAR(50) NOT NULL,
    risk_name           VARCHAR(100) NOT NULL,
    occurrence_rate     DECIMAL(5,2),
    avg_cost            DECIMAL(12,2),
    complaint_count     INTEGER DEFAULT 0,
    UNIQUE(city_code, risk_type)
);
```

### 3.2 API接口

| 接口 | 方法 | 路径 | 说明 |
|------|------|------|------|
| 问题类型 | GET | /inspection/issue-types | 8类问题 |
| 城市风险 | GET | /inspection/city-risks/{city} | |
| 创建任务 | POST | /inspection/create | |
| 图片分析 | POST | /inspection/analyze | ≤2秒 |
| 报告详情 | GET | /inspection/report/{id} | |
| 报告列表 | GET | /inspection/my-reports | |
| 人工复核 | POST | /inspection/request-review | 100%复核 |

---

## 四、AI设计与预算联动模块

### 4.1 表结构

```sql
-- 设计项目表
CREATE TABLE design_projects (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_no          VARCHAR(50) UNIQUE NOT NULL,
    user_id             UUID NOT NULL REFERENCES users(id),
    house_id            UUID REFERENCES house_profiles(id),
    inspection_report_id UUID REFERENCES inspection_reports(id),
    city                VARCHAR(50),
    area                DECIMAL(10,2),
    rooms               INTEGER,
    house_type          VARCHAR(30),
    family_structure    VARCHAR(50),
    selected_style      VARCHAR(50),
    selected_layout     VARCHAR(50),
    selected_plan_id    UUID,
    status              VARCHAR(20) DEFAULT 'draft',
    created_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    confirmed_at        TIMESTAMP,
    deleted_at          TIMESTAMP
);

-- 设计方案表（每个项目3套方案）
CREATE TABLE design_plans (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id          UUID NOT NULL REFERENCES design_projects(id),
    plan_no             VARCHAR(50) NOT NULL,
    plan_name           VARCHAR(100),
    plan_type           VARCHAR(50) NOT NULL,
    description         TEXT,
    highlights          JSONB DEFAULT '[]',
    suitable_for         JSONB DEFAULT '[]',
    layout_data         JSONB,
    floor_plan_url      VARCHAR(500),
    style               VARCHAR(50),
    colors              JSONB DEFAULT '[]',
    materials           JSONB DEFAULT '[]',
    render_images       JSONB DEFAULT '[]',
    estimated_budget    DECIMAL(12,2),
    is_selected         BOOLEAN DEFAULT FALSE,
    created_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 户型识别表
CREATE TABLE floor_plan_recognitions (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id          UUID NOT NULL REFERENCES design_projects(id),
    original_url        VARCHAR(500) NOT NULL,
    processed_url       VARCHAR(500),
    recognized_data      JSONB NOT NULL,
    total_area          DECIMAL(10,2),
    room_count          INTEGER,
    accuracy            INTEGER,
    ai_model            VARCHAR(100),
    status              VARCHAR(20) DEFAULT 'pending',
    created_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 材料清单表
CREATE TABLE design_materials (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id          UUID NOT NULL REFERENCES design_projects(id),
    plan_id             UUID REFERENCES design_plans(id),
    category            VARCHAR(50) NOT NULL,
    item_name           VARCHAR(200) NOT NULL,
    brand               VARCHAR(100),
    spec                VARCHAR(200),
    unit                VARCHAR(20),
    quantity            DECIMAL(10,2),
    market_price        DECIMAL(12,2),
    purchase_price      DECIMAL(12,2),
    loss_rate           DECIMAL(5,4) DEFAULT 1.0500,
    room                VARCHAR(50),
    created_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 施工图纸表（6类核心图纸）
CREATE TABLE design_drawings (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id          UUID NOT NULL REFERENCES design_projects(id),
    plan_id             UUID REFERENCES design_plans(id),
    drawing_type        VARCHAR(50) NOT NULL,
    drawing_name        VARCHAR(200),
    drawing_url         VARCHAR(500),
    pdf_url             VARCHAR(500),
    compliance_check    JSONB,
    is_compliant        BOOLEAN DEFAULT TRUE,
    created_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 4.2 预算模块表结构

```sql
-- 预算单主表
CREATE TABLE budget_orders (
    id                      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    budget_no               VARCHAR(50) UNIQUE NOT NULL,
    project_id              UUID NOT NULL REFERENCES design_projects(id),
    design_plan_id         UUID REFERENCES design_plans(id),
    user_id                UUID NOT NULL REFERENCES users(id),
    city                   VARCHAR(50) NOT NULL,
    total_area             DECIMAL(10,2) NOT NULL,
    room_count             INTEGER,
    total_amount           DECIMAL(12,2) DEFAULT 0,
    material_amount        DECIMAL(12,2) DEFAULT 0,
    labor_amount           DECIMAL(12,2) DEFAULT 0,
    management_amount      DECIMAL(12,2) DEFAULT 0,
    misc_amount            DECIMAL(12,2) DEFAULT 0,
    adjust_coefficient     DECIMAL(8,4) DEFAULT 1.0000,
    budget_limit           DECIMAL(12,2),
    is_exceed_limit       BOOLEAN DEFAULT FALSE,
    exceed_amount          DECIMAL(12,2) DEFAULT 0,
    version                INTEGER DEFAULT 1,
    is_latest              BOOLEAN DEFAULT TRUE,
    status                 VARCHAR(20) DEFAULT 'draft',
    calculated_at          TIMESTAMP,
    confirmed_at           TIMESTAMP,
    created_at             TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 预算明细表
CREATE TABLE budget_items (
    id                      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    budget_id               UUID NOT NULL REFERENCES budget_orders(id),
    project_id              UUID NOT NULL REFERENCES design_projects(id),
    process_code            VARCHAR(50) NOT NULL,
    process_name            VARCHAR(200) NOT NULL,
    category                VARCHAR(50) NOT NULL,
    node_code               VARCHAR(50),
    material_name           VARCHAR(200) NOT NULL,
    brand                   VARCHAR(100),
    spec                    VARCHAR(200),
    unit                    VARCHAR(20),
    quantity                DECIMAL(10,2) NOT NULL,
    loss_rate               DECIMAL(5,4) DEFAULT 1.0000,
    unit_price              DECIMAL(12,2) NOT NULL,
    amount                  DECIMAL(12,2) NOT NULL,
    labor_hours             DECIMAL(8,2),
    labor_unit_price        DECIMAL(12,2),
    labor_amount            DECIMAL(12,2),
    prerequisite_processes  JSONB DEFAULT '[]',
    affected_processes     JSONB DEFAULT '[]',
    is_changed              BOOLEAN DEFAULT FALSE,
    change_type             VARCHAR(20),
    created_at              TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 人工成本库
CREATE TABLE labor_cost_library (
    id                      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    province_code            VARCHAR(10) NOT NULL,
    province_name            VARCHAR(50) NOT NULL,
    city_code                VARCHAR(10),
    city_name                VARCHAR(50),
    work_type               VARCHAR(50) NOT NULL,
    work_type_name          VARCHAR(100) NOT NULL,
    unit_price              DECIMAL(10,2) NOT NULL,
    unit                    VARCHAR(20) DEFAULT '工日',
    difficulty_factor        DECIMAL(4,2) DEFAULT 1.00,
    season_factor            DECIMAL(4,2) DEFAULT 1.00,
    effective_date          DATE NOT NULL,
    expire_date             DATE,
    UNIQUE(province_code, city_code, work_type, effective_date)
);

-- 地区调价系数库
CREATE TABLE region_adjustment (
    id                      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    province_code            VARCHAR(10) NOT NULL,
    province_name            VARCHAR(50) NOT NULL,
    city_code                VARCHAR(10),
    city_name                VARCHAR(50),
    adjust_type             VARCHAR(30) NOT NULL,
    adjust_type_name        VARCHAR(100) NOT NULL,
    coefficient              DECIMAL(8,4) NOT NULL,
    effective_date          DATE NOT NULL,
    expire_date             DATE
);

-- 预算变更记录表
CREATE TABLE budget_change_logs (
    id                      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    budget_id               UUID NOT NULL REFERENCES budget_orders(id),
    project_id              UUID NOT NULL REFERENCES design_projects(id),
    change_no               VARCHAR(50) NOT NULL,
    before_total            DECIMAL(12,2),
    after_total             DECIMAL(12,2) NOT NULL,
    diff_amount             DECIMAL(12,2) NOT NULL,
    diff_rate               DECIMAL(6,4),
    change_reason           VARCHAR(100) NOT NULL,
    change_type             VARCHAR(30) NOT NULL,
    trigger_source          VARCHAR(50),
    handle_type             VARCHAR(30),
    need_approve            BOOLEAN DEFAULT FALSE,
    approve_status          VARCHAR(20),
    created_by              UUID NOT NULL,
    created_at              TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 预算红线配置表
CREATE TABLE budget_red_lines (
    id                      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id                 UUID REFERENCES users(id),
    city                    VARCHAR(50),
    house_type              VARCHAR(30),
    line_type               VARCHAR(30) NOT NULL,
    threshold_value         DECIMAL(12,2) NOT NULL,
    warning_level           VARCHAR(20) DEFAULT 'medium',
    warning_threshold       DECIMAL(5,2) DEFAULT 80.00,
    allow_exceed            BOOLEAN DEFAULT FALSE,
    created_at              TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 4.3 API接口

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

## 五、施工全流程管理模块

### 5.1 表结构

```sql
-- 施工项目表
CREATE TABLE construction_projects (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_no          VARCHAR(50) UNIQUE NOT NULL,
    user_id             UUID NOT NULL REFERENCES users(id),
    house_id            UUID REFERENCES house_profiles(id),
    design_project_id   UUID REFERENCES design_projects(id),
    name                VARCHAR(200) NOT NULL,
    address             VARCHAR(500),
    area                DECIMAL(10,2),
    contract_no         VARCHAR(50),
    contract_amount     DECIMAL(12,2),
    contract_url        VARCHAR(500),
    signed_at           TIMESTAMP,
    total_cycle         INTEGER,
    start_date          DATE,
    end_date            DATE,
    worker_id           UUID,
    supervisor_id       UUID,
    status              VARCHAR(20) DEFAULT 'pending',
    created_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at        TIMESTAMP,
    deleted_at          TIMESTAMP
);

-- 施工节点表（8大核心节点）
CREATE TABLE construction_nodes (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id          UUID NOT NULL REFERENCES construction_projects(id),
    node_code           VARCHAR(50) NOT NULL,
    node_name           VARCHAR(100) NOT NULL,
    node_order          INTEGER NOT NULL,
    planned_start_date  DATE,
    planned_end_date    DATE,
    actual_start_date   DATE,
    actual_end_date     DATE,
    planned_cycle       INTEGER,
    progress            INTEGER DEFAULT 0,
    status              VARCHAR(20) DEFAULT 'pending',
    acceptance_status   VARCHAR(20),
    payment_percent     DECIMAL(5,2),
    created_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(project_id, node_code)
);

-- 节点进度记录表
CREATE TABLE node_progress_logs (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    node_id             UUID NOT NULL REFERENCES construction_nodes(id),
    project_id          UUID NOT NULL REFERENCES construction_projects(id),
    progress            INTEGER NOT NULL,
    status              VARCHAR(20),
    photos              JSONB DEFAULT '[]',
    notes               TEXT,
    reporter_id         UUID NOT NULL,
    created_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 整改工单表
CREATE TABLE rectification_orders (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    order_no            VARCHAR(50) UNIQUE NOT NULL,
    project_id          UUID NOT NULL REFERENCES construction_projects(id),
    node_id             UUID REFERENCES construction_nodes(id),
    source              VARCHAR(30) NOT NULL,
    issue_type          VARCHAR(50) NOT NULL,
    issue_description   TEXT NOT NULL,
    severity            VARCHAR(20) NOT NULL,
    photos              JSONB DEFAULT '[]',
    location            VARCHAR(200),
    status              VARCHAR(20) DEFAULT 'pending',
    assigned_to         UUID,
    deadline            DATE,
    processing_photos  JSONB DEFAULT '[]',
    completed_at        TIMESTAMP,
    review_status       VARCHAR(20),
    created_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 材料进场记录表
CREATE TABLE material_records (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    record_no           VARCHAR(50) UNIQUE NOT NULL,
    project_id          UUID NOT NULL REFERENCES construction_projects(id),
    node_id             UUID REFERENCES construction_nodes(id),
    material_name       VARCHAR(200) NOT NULL,
    brand               VARCHAR(100),
    model               VARCHAR(100),
    spec                VARCHAR(200),
    unit                VARCHAR(20),
    quantity            DECIMAL(10,2) NOT NULL,
    batch_no            VARCHAR(50),
    supplier_name       VARCHAR(200),
    inspection_status   VARCHAR(20) DEFAULT 'pending',
    arrival_date        DATE,
    created_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 施工日志表
CREATE TABLE construction_daily_logs (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    log_no              VARCHAR(50) UNIQUE NOT NULL,
    project_id          UUID NOT NULL REFERENCES construction_projects(id),
    node_id             UUID REFERENCES construction_nodes(id),
    log_date            DATE NOT NULL,
    weather             VARCHAR(30),
    log_type            VARCHAR(30) NOT NULL,
    content             TEXT NOT NULL,
    photos              JSONB DEFAULT '[]',
    completed_work      TEXT,
    next_plan           TEXT,
    issues              JSONB DEFAULT '[]',
    worker_count        INTEGER,
    reporter_id         UUID NOT NULL,
    created_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 5.2 API接口

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

## 六、AI云监工模块

### 6.1 表结构

```sql
-- 云监工图片表
CREATE TABLE supervision_images (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id          UUID NOT NULL REFERENCES construction_projects(id),
    node_id             UUID REFERENCES construction_nodes(id),
    image_url           VARCHAR(500) NOT NULL,
    thumbnail_url       VARCHAR(500),
    source_type         VARCHAR(30) NOT NULL,
    upload_by           UUID REFERENCES users(id),
    room                VARCHAR(50),
    construction_stage  VARCHAR(50),
    is_keyframe         BOOLEAN DEFAULT FALSE,
    clarity_score       INTEGER,
    is_blur             BOOLEAN DEFAULT FALSE,
    created_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- AI识别记录表
CREATE TABLE supervision_records (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    record_no           VARCHAR(50) UNIQUE NOT NULL,
    project_id          UUID NOT NULL REFERENCES construction_projects(id),
    node_id             UUID REFERENCES construction_nodes(id),
    image_id            UUID REFERENCES supervision_images(id),
    ai_model            VARCHAR(100) NOT NULL,
    recognized_stage    VARCHAR(50),
    stage_confidence    INTEGER,
    progress_percent    INTEGER,
    compliance_result   JSONB,
    is_compliant        BOOLEAN DEFAULT TRUE,
    anomalies           JSONB DEFAULT '[]',
    safety_issues       JSONB DEFAULT '[]',
    has_safety_risk     BOOLEAN DEFAULT FALSE,
    overall_score       INTEGER,
    processing_time_ms INTEGER,
    created_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 预警规则配置表
CREATE TABLE warning_rules (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    rule_code           VARCHAR(50) UNIQUE NOT NULL,
    rule_name           VARCHAR(200) NOT NULL,
    rule_type           VARCHAR(30) NOT NULL,
    trigger_condition   JSONB NOT NULL,
    warning_level       VARCHAR(20) NOT NULL,
    message_template    TEXT NOT NULL,
    notify_channels     JSONB DEFAULT '["app", "wechat", "sms"]',
    notify_roles        JSONB DEFAULT '[]',
    is_enabled          BOOLEAN DEFAULT TRUE,
    is_system           BOOLEAN DEFAULT FALSE,
    user_id             UUID REFERENCES users(id),
    created_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 预警历史表
CREATE TABLE warning_logs (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    warning_no          VARCHAR(50) UNIQUE NOT NULL,
    project_id          UUID NOT NULL REFERENCES construction_projects(id),
    node_id             UUID REFERENCES construction_nodes(id),
    rule_id             UUID REFERENCES warning_rules(id),
    rule_type           VARCHAR(30) NOT NULL,
    warning_level       VARCHAR(20) NOT NULL,
    title               VARCHAR(200) NOT NULL,
    content             TEXT NOT NULL,
    trigger_data        JSONB,
    threshold_value     DECIMAL(12,2),
    actual_value        DECIMAL(12,2),
    status              VARCHAR(20) DEFAULT 'pending',
    handle_result       TEXT,
    handled_by          UUID,
    handled_at          TIMESTAMP,
    created_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 6.2 API接口

| 接口 | 方法 | 路径 | 说明 |
|------|------|------|------|
| 进度识别 | POST | /supervision/recognize-progress | ≤3秒 |
| 合规检测 | POST | /supervision/check-compliance | |
| 异常检测 | POST | /supervision/check-anomalies | |
| 预警规则 | GET/POST | /supervision/warning-rules | |
| 预警历史 | GET | /supervision/warnings | |

---

## 七、标准化验收模块

### 7.1 表结构

```sql
-- 验收标准库表
CREATE TABLE acceptance_standards (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    standard_code       VARCHAR(50) UNIQUE NOT NULL,
    standard_type       VARCHAR(50) NOT NULL,
    item_code           VARCHAR(50),
    item_name           VARCHAR(200) NOT NULL,
    item_type           VARCHAR(20) NOT NULL,
    check_method        TEXT,
    qualified_standard  TEXT NOT NULL,
    unqualified_deal   TEXT,
    user_friendly_desc TEXT,
    national_code       VARCHAR(50),
    version             VARCHAR(20),
    status              VARCHAR(20) DEFAULT 'active',
    created_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 验收记录表
CREATE TABLE acceptance_records (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    record_no           VARCHAR(50) UNIQUE NOT NULL,
    project_id          UUID NOT NULL REFERENCES construction_projects(id),
    node_id             UUID REFERENCES construction_nodes(id),
    acceptance_type     VARCHAR(30) NOT NULL,
    node_name           VARCHAR(100),
    check_items         JSONB NOT NULL,
    passed_items        INTEGER,
    total_items         INTEGER,
    pass_rate           DECIMAL(5,2),
    status              VARCHAR(20) DEFAULT 'pending',
    result              VARCHAR(20),
    photos              JSONB DEFAULT '[]',
    notes               TEXT,
    applicant_id        UUID NOT NULL,
    acceptor_id         UUID,
    accepted_at         TIMESTAMP,
    created_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 维保记录表
CREATE TABLE warranty_records (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    record_no           VARCHAR(50) UNIQUE NOT NULL,
    project_id          UUID NOT NULL REFERENCES construction_projects(id),
    warranty_start      DATE NOT NULL,
    warranty_end        DATE NOT NULL,
    warranty_period     INTEGER,
    scope               JSONB DEFAULT '[]',
    exclusions          JSONB DEFAULT '[]',
    deposit_amount      DECIMAL(12,2),
    deposit_status      VARCHAR(20),
    status              VARCHAR(20) DEFAULT 'active',
    created_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 7.2 API接口

| 接口 | 方法 | 路径 | 说明 |
|------|------|------|------|
| 验收标准 | GET | /acceptance/standards | 国标库 |
| 节点清单 | GET | /acceptance/node-checklist/{node_id} | |
| 提交验收 | POST | /acceptance/submit | |
| 验收报告 | GET | /acceptance/report/{id} | |
| 报告列表 | GET | /acceptance/my-reports | |
| 维保信息 | GET | /acceptance/warranty/{project_id} | |

---

## 八、支付模块

### 8.1 表结构

```sql
-- 产品表
CREATE TABLE products (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    product_code        VARCHAR(50) UNIQUE NOT NULL,
    product_name        VARCHAR(200) NOT NULL,
    product_type        VARCHAR(30) NOT NULL,
    description         TEXT,
    features            JSONB DEFAULT '[]',
    price               DECIMAL(12,2) NOT NULL,
    price_display       VARCHAR(20),
    validity_days       INTEGER,
    status              VARCHAR(20) DEFAULT 'active',
    created_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 订单表
CREATE TABLE orders (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    order_no            VARCHAR(50) UNIQUE NOT NULL,
    user_id             UUID NOT NULL REFERENCES users(id),
    product_id          UUID REFERENCES products(id),
    product_type        VARCHAR(30) NOT NULL,
    product_name        VARCHAR(200),
    amount              DECIMAL(12,2) NOT NULL,
    discount_amount     DECIMAL(12,2) DEFAULT 0,
    actual_amount       DECIMAL(12,2) NOT NULL,
    status              VARCHAR(20) DEFAULT 'pending',
    payment_method      VARCHAR(30),
    paid_at             TIMESTAMP,
    wx_prepay_id        VARCHAR(100),
    wx_transaction_id   VARCHAR(100),
    wx_pay_time         TIMESTAMP,
    expire_time         TIMESTAMP,
    created_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 分期付款计划表
CREATE TABLE payment_installments (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    installment_no      VARCHAR(50) UNIQUE NOT NULL,
    project_id          UUID NOT NULL REFERENCES construction_projects(id),
    order_id            UUID REFERENCES orders(id),
    total_amount        DECIMAL(12,2) NOT NULL,
    installment_count   INTEGER NOT NULL,
    paid_amount         DECIMAL(12,2) DEFAULT 0,
    remaining_amount    DECIMAL(12,2),
    installments        JSONB NOT NULL,
    status              VARCHAR(20) DEFAULT 'active',
    created_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 8.2 API接口

| 接口 | 方法 | 路径 | 说明 |
|------|------|------|------|
| 产品列表 | GET | /payment/products | |
| 创建订单 | POST | /payment/create-order | |
| 订单详情 | GET | /payment/order/{no} | |
| VIP状态 | GET | /payment/vip-status | |
| 取消订单 | POST | /payment/cancel/{no} | |
| 支付回调 | POST | /payment/notify | |

---

## 九、系统域表

```sql
-- 短信验证码表
CREATE TABLE sms_codes (
    id                  BIGSERIAL PRIMARY KEY,
    phone               VARCHAR(20) NOT NULL,
    code                VARCHAR(10) NOT NULL,
    type                VARCHAR(30) NOT NULL,
    used                BOOLEAN DEFAULT FALSE,
    expired_at          TIMESTAMP NOT NULL,
    used_at             TIMESTAMP,
    ip                  VARCHAR(50),
    created_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 区域表
CREATE TABLE regions (
    id                  SERIAL PRIMARY KEY,
    code                VARCHAR(20) UNIQUE NOT NULL,
    name                VARCHAR(100) NOT NULL,
    level               INTEGER NOT NULL,
    parent_code         VARCHAR(20),
    pinyin              VARCHAR(100),
    is_active           BOOLEAN DEFAULT TRUE
);

-- 材料库表
CREATE TABLE material_library (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    category            VARCHAR(50) NOT NULL,
    name                VARCHAR(200) NOT NULL,
    brand               VARCHAR(100),
    spec                VARCHAR(200),
    unit                VARCHAR(20),
    market_price        DECIMAL(12,2),
    purchase_price      DECIMAL(12,2),
    loss_rate           DECIMAL(5,2) DEFAULT 1.0,
    images              JSONB DEFAULT '[]',
    status              VARCHAR(20) DEFAULT 'active',
    created_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 工序库表
CREATE TABLE process_library (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    process_code        VARCHAR(50) NOT NULL,
    process_name        VARCHAR(200) NOT NULL,
    category            VARCHAR(50),
    node_code           VARCHAR(50),
    standard_hours      DECIMAL(8,2),
    standard_cost       DECIMAL(12,2),
    prerequisites       JSONB DEFAULT '[]',
    followups           JSONB DEFAULT '[]',
    national_standard   VARCHAR(200),
    quality_standard    TEXT,
    safety_requirements TEXT,
    status              VARCHAR(20) DEFAULT 'active',
    created_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 通用附件表
CREATE TABLE attachments (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    business_type       VARCHAR(50) NOT NULL,
    business_id         UUID NOT NULL,
    file_name           VARCHAR(255) NOT NULL,
    file_url            VARCHAR(500) NOT NULL,
    file_size           BIGINT,
    file_type           VARCHAR(100),
    category            VARCHAR(50),
    title               VARCHAR(200),
    is_public          BOOLEAN DEFAULT FALSE,
    uploaded_by         UUID REFERENCES users(id),
    created_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_attachments_business ON attachments(business_type, business_id);
```

---

## 十、表统计

| 域 | 表数 |
|---|---|
| 用户域 | 5 |
| 验房域 | 4 |
| 设计域 | 5 |
| 预算域 | 6 |
| 施工域 | 6 |
| 云监工域 | 4 |
| 验收域 | 3 |
| 支付域 | 3 |
| 系统域 | 5 |
| 通用 | 1 |
| **总计** | **42** |

---

*文档版本：V3.0 | 审核日期：2026-04-06*
