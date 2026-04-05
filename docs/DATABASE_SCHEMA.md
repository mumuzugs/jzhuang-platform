# 集装修 数据库设计文档 V2.0

**版本**：V2.0  
**更新日期**：2026-04-06  
**数据库**：PostgreSQL 14+  

---

## 一、数据库架构

### 1.1 库结构

```
jzhuang_platform/
├── public                  # 公共表
├── users                  # 用户域
├── inspection             # 验房域
├── design                 # 设计域
├── construction           # 施工域
├── payment                # 支付域
└── system                 # 系统域
```

### 1.2 命名规范

| 类型 | 规范 | 示例 |
|------|------|------|
| 表名 | 小写下划线 | `user_profile` |
| 主键 | `{table}_id` | `user_id` |
| 外键 | `{ref_table}_id` | `user_id` |
| 索引 | `idx_{table}_{column}` | `idx_user_phone` |
| 时间戳 | `_at` | `created_at` |

---

## 二、表结构设计

### 2.1 用户域表 (users)

#### 2.1.1 用户基础表 `users`

```sql
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
    last_login_at   TIMESTAMP,
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deleted_at      TIMESTAMP
);

CREATE INDEX idx_users_phone ON users(phone);
CREATE INDEX idx_users_wx_openid ON users(wx_openid);
```

#### 2.1.2 用户角色表 `user_roles`

```sql
CREATE TABLE user_roles (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         UUID NOT NULL REFERENCES users(id),
    role            VARCHAR(30) NOT NULL,  -- owner/worker/supplier/operator/supervisor/cs
    permissions     JSONB DEFAULT '[]',
    is_primary      BOOLEAN DEFAULT TRUE,
    status          VARCHAR(20) DEFAULT 'active',
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, role)
);
```

#### 2.1.3 房屋档案表 `house_profiles`

```sql
CREATE TABLE house_profiles (
    id                      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id                 UUID NOT NULL REFERENCES users(id),
    city                    VARCHAR(50) NOT NULL,
    community               VARCHAR(200),
    house_type              VARCHAR(30) NOT NULL,  -- 毛坯房/二手房/精装房
    area                    DECIMAL(10,2),
    room_count              INTEGER,
    decoration_status       VARCHAR(30) DEFAULT '未装修',
    design_project_id       UUID,
    construction_project_id UUID,
    inspection_report_id   UUID,
    created_at              TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at              TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_house_profiles_user_id ON house_profiles(user_id);
```

#### 2.1.4 用户标签表 `user_tags`

```sql
CREATE TABLE user_tags (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         UUID NOT NULL REFERENCES users(id),
    tag_code       VARCHAR(50) NOT NULL,
    tag_name       VARCHAR(100) NOT NULL,
    tag_type       VARCHAR(30) NOT NULL,  -- preference/behavior/demographic
    tag_value      VARCHAR(255),
    weight          DECIMAL(5,2) DEFAULT 1.0,
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, tag_code)
);
```

#### 2.1.5 操作审计日志表 `audit_logs`

```sql
CREATE TABLE audit_logs (
    id              BIGSERIAL PRIMARY KEY,
    user_id         UUID REFERENCES users(id),
    action          VARCHAR(100) NOT NULL,
    module          VARCHAR(50) NOT NULL,
    resource_type   VARCHAR(50),
    resource_id     VARCHAR(100),
    detail          JSONB,
    ip              VARCHAR(50),
    status          VARCHAR(20) DEFAULT 'success',
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_audit_logs_user_id ON audit_logs(user_id);
CREATE INDEX idx_audit_logs_module ON audit_logs(module);
CREATE INDEX idx_audit_logs_created_at ON audit_logs(created_at);
```

---

### 2.2 验房域表 (inspection)

#### 2.2.1 验房报告表 `inspection_reports`

```sql
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
    
    ai_accuracy         INTEGER,
    review_status       VARCHAR(20) DEFAULT 'auto',
    status              VARCHAR(20) DEFAULT 'pending',
    report_content      TEXT,
    pdf_url             VARCHAR(500),
    
    created_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at        TIMESTAMP,
    deleted_at          TIMESTAMP
);

CREATE INDEX idx_inspection_reports_user_id ON inspection_reports(user_id);
CREATE INDEX idx_inspection_reports_status ON inspection_reports(status);
```

#### 2.2.2 验房问题明细表 `inspection_issues`

```sql
CREATE TABLE inspection_issues (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    report_id           UUID NOT NULL REFERENCES inspection_reports(id),
    
    issue_type         VARCHAR(50) NOT NULL,  -- wall_crack/floor_uneven/water_leak等
    issue_name          VARCHAR(100) NOT NULL,
    description         TEXT,
    location            VARCHAR(100),
    severity            VARCHAR(20) NOT NULL,  -- high/medium/low
    confidence          INTEGER,
    
    suggestion          TEXT,
    estimated_cost      DECIMAL(10,2),
    image_urls          JSONB DEFAULT '[]',
    
    need_review        BOOLEAN DEFAULT FALSE,
    created_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_inspection_issues_report_id ON inspection_issues(report_id);
CREATE INDEX idx_inspection_issues_severity ON inspection_issues(severity);
```

---

### 2.3 设计域表 (design)

#### 2.3.1 设计项目表 `design_projects`

```sql
CREATE TABLE design_projects (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_no          VARCHAR(50) UNIQUE NOT NULL,
    user_id             UUID NOT NULL REFERENCES users(id),
    house_id            UUID REFERENCES house_profiles(id),
    
    city                VARCHAR(50),
    area                DECIMAL(10,2),
    rooms               INTEGER,
    house_type          VARCHAR(30),
    
    family_structure    VARCHAR(50),
    selected_style      VARCHAR(50),
    selected_plan_id    UUID,
    
    status              VARCHAR(20) DEFAULT 'draft',
    created_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    confirmed_at        TIMESTAMP,
    deleted_at          TIMESTAMP
);

CREATE INDEX idx_design_projects_user_id ON design_projects(user_id);
```

#### 2.3.2 设计方案表 `design_plans`

```sql
CREATE TABLE design_plans (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id          UUID NOT NULL REFERENCES design_projects(id),
    
    plan_no             VARCHAR(50) NOT NULL,
    plan_name           VARCHAR(100),
    plan_type           VARCHAR(50) NOT NULL,  -- space/family/simple
    
    description         TEXT,
    highlights          JSONB DEFAULT '[]',
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
```

#### 2.3.3 材料清单表 `design_materials`

```sql
CREATE TABLE design_materials (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id          UUID NOT NULL REFERENCES design_projects(id),
    
    category            VARCHAR(50) NOT NULL,
    item_name           VARCHAR(200) NOT NULL,
    brand               VARCHAR(100),
    spec                VARCHAR(200),
    unit                VARCHAR(20),
    quantity            DECIMAL(10,2),
    
    market_price        DECIMAL(10,2),
    purchase_price      DECIMAL(10,2),
    loss_rate           DECIMAL(5,2) DEFAULT 1.05,
    
    room                VARCHAR(50),
    created_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### 2.3.4 施工图纸表 `design_drawings`

```sql
CREATE TABLE design_drawings (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id          UUID NOT NULL REFERENCES design_projects(id),
    
    drawing_type        VARCHAR(50) NOT NULL,  -- floor_plan/demolition/water/electric等
    drawing_name        VARCHAR(200),
    drawing_url         VARCHAR(500),
    pdf_url             VARCHAR(500),
    
    is_compliant        BOOLEAN DEFAULT TRUE,
    compliance_check    JSONB,
    created_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

### 2.4 施工域表 (construction)

#### 2.4.1 施工项目表 `construction_projects`

```sql
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

CREATE INDEX idx_construction_projects_user_id ON construction_projects(user_id);
CREATE INDEX idx_construction_projects_status ON construction_projects(status);
```

#### 2.4.2 施工节点表 `construction_nodes`

```sql
CREATE TABLE construction_nodes (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id          UUID NOT NULL REFERENCES construction_projects(id),
    
    node_code           VARCHAR(50) NOT NULL,  -- preparation/electrical/waterproof等
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

CREATE INDEX idx_construction_nodes_project_id ON construction_nodes(project_id);
```

#### 2.4.3 整改工单表 `rectification_orders`

```sql
CREATE TABLE rectification_orders (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    order_no            VARCHAR(50) UNIQUE NOT NULL,
    project_id          UUID NOT NULL REFERENCES construction_projects(id),
    node_id             UUID REFERENCES construction_nodes(id),
    
    source              VARCHAR(30) NOT NULL,  -- inspection/supervision/acceptance/user
    issue_type          VARCHAR(50) NOT NULL,
    issue_description   TEXT NOT NULL,
    severity            VARCHAR(20) NOT NULL,  -- high/medium/low
    
    photos              JSONB DEFAULT '[]',
    location            VARCHAR(200),
    
    status              VARCHAR(20) DEFAULT 'pending',
    assigned_to         UUID,
    deadline            DATE,
    
    created_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

### 2.5 验收域表 (acceptance)

#### 2.5.1 验收记录表 `acceptance_records`

```sql
CREATE TABLE acceptance_records (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    record_no           VARCHAR(50) UNIQUE NOT NULL,
    project_id          UUID NOT NULL REFERENCES construction_projects(id),
    node_id             UUID REFERENCES construction_nodes(id),
    
    acceptance_type     VARCHAR(30) NOT NULL,  -- node/final
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

CREATE INDEX idx_acceptance_records_project_id ON acceptance_records(project_id);
```

#### 2.5.2 维保记录表 `warranty_records`

```sql
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

---

### 2.6 支付域表 (payment)

#### 2.6.1 产品表 `products`

```sql
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

INSERT INTO products (product_code, product_name, product_type, features, price, price_display, validity_days) VALUES
('vip_pro', '全周期专业版', 'vip', '["无限次AI验房", "全套AI设计", "设计-预算实时联动"]', 29900, '299.00', 180);
```

#### 2.6.2 订单表 `orders`

```sql
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

CREATE INDEX idx_orders_user_id ON orders(user_id);
CREATE INDEX idx_orders_status ON orders(status);
CREATE INDEX idx_orders_wx_transaction_id ON orders(wx_transaction_id);
```

#### 2.6.3 支付记录表 `payment_records`

```sql
CREATE TABLE payment_records (
    id                  BIGSERIAL PRIMARY KEY,
    order_id            UUID NOT NULL REFERENCES orders(id),
    order_no            VARCHAR(50) NOT NULL,
    
    payment_type        VARCHAR(30) NOT NULL,
    transaction_id      VARCHAR(100),
    amount              DECIMAL(12,2) NOT NULL,
    status              VARCHAR(20) DEFAULT 'pending',
    
    callback_data       JSONB,
    callback_time       TIMESTAMP,
    
    created_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

### 2.7 系统域表 (system)

#### 2.7.1 短信验证码表 `sms_codes`

```sql
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

CREATE INDEX idx_sms_codes_phone ON sms_codes(phone);
CREATE INDEX idx_sms_codes_expired_at ON sms_codes(expired_at);
```

#### 2.7.2 区域表 `regions`

```sql
CREATE TABLE regions (
    id                  SERIAL PRIMARY KEY,
    code                VARCHAR(20) UNIQUE NOT NULL,
    name                VARCHAR(100) NOT NULL,
    level               INTEGER NOT NULL,
    parent_code         VARCHAR(20),
    pinyin              VARCHAR(100),
    is_active           BOOLEAN DEFAULT TRUE
);

CREATE INDEX idx_regions_parent_code ON regions(parent_code);
```

#### 2.7.3 材料库表 `material_library`

```sql
CREATE TABLE material_library (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    category            VARCHAR(50) NOT NULL,
    name                VARCHAR(200) NOT NULL,
    brand               VARCHAR(100),
    spec                VARCHAR(200),
    unit                VARCHAR(20),
    
    market_price        DECIMAL(12,2),
    purchase_price      DECIMAL(10,2),
    loss_rate           DECIMAL(5,2) DEFAULT 1.0,
    
    images              JSONB DEFAULT '[]',
    status              VARCHAR(20) DEFAULT 'active',
    created_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_material_library_category ON material_library(category);
```

#### 2.7.4 工序库表 `process_library`

```sql
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
```

---

### 2.7 系统域表 (system)

#### 2.7.1 短信验证码表 `sms_codes`

```sql
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
```

#### 2.7.2 区域表 `regions`

```sql
CREATE TABLE regions (
    id                  SERIAL PRIMARY KEY,
    code                VARCHAR(20) UNIQUE NOT NULL,
    name                VARCHAR(100) NOT NULL,
    level               INTEGER NOT NULL,
    parent_code         VARCHAR(20),
    pinyin              VARCHAR(100),
    is_active           BOOLEAN DEFAULT TRUE
);
```

---

## 三、预算域表 (budget) ⭐ 核心模块

> **架构文档V2.0要求**：预算引擎是核心壁垒，采用DAG工序影响链模型

#### 3.1 预算单主表 `budget_orders`

```sql
-- 预算单主表
CREATE TABLE budget_orders (
    id                      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    budget_no               VARCHAR(50) UNIQUE NOT NULL,  -- 预算单编号
    
    project_id              UUID NOT NULL REFERENCES design_projects(id),  -- 设计项目
    design_plan_id         UUID REFERENCES design_plans(id),
    
    user_id                UUID NOT NULL REFERENCES users(id),
    house_id               UUID REFERENCES house_profiles(id),
    
    city                   VARCHAR(50) NOT NULL,        -- 城市（用于调价）
    
    -- 面积信息
    total_area             DECIMAL(10,2) NOT NULL,     -- 总面积
    room_count             INTEGER,                     -- 房间数
    
    -- 预算金额
    total_amount           DECIMAL(12,2) DEFAULT 0,    -- 预算总额
    material_amount        DECIMAL(12,2) DEFAULT 0,    -- 材料费
    labor_amount           DECIMAL(12,2) DEFAULT 0,    -- 人工费
    management_amount      DECIMAL(12,2) DEFAULT 0,    -- 管理费
    misc_amount            DECIMAL(12,2) DEFAULT 0,     -- 其他费用
    
    -- 调价信息
    adjust_coefficient     DECIMAL(6,4) DEFAULT 1.0000, -- 地区调价系数
    adjust_reason          VARCHAR(200),               -- 调价原因
    
    -- 预算控制
    budget_limit           DECIMAL(12,2),              -- 用户设定的预算上限
    is_exceed_limit       BOOLEAN DEFAULT FALSE,      -- 是否超预算
    exceed_amount          DECIMAL(12,2) DEFAULT 0,   -- 超预算金额
    
    -- 版本控制
    version                INTEGER DEFAULT 1,          -- 版本号
    is_latest              BOOLEAN DEFAULT TRUE,       -- 是否最新版本
    
    -- 状态
    status                 VARCHAR(20) DEFAULT 'draft', -- draft/calculating/completed/confirmed
    calculated_at          TIMESTAMP,                  -- 计算完成时间
    confirmed_at           TIMESTAMP,                  -- 确认时间
    
    created_at             TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at             TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_budget_orders_project_id ON budget_orders(project_id);
CREATE INDEX idx_budget_orders_user_id ON budget_orders(user_id);
CREATE INDEX idx_budget_orders_city ON budget_orders(city);
CREATE INDEX idx_budget_orders_status ON budget_orders(status);
CREATE INDEX idx_budget_orders_is_latest ON budget_orders(is_latest);
```

#### 3.2 预算明细表 `budget_items`

```sql
-- 预算明细表（每个预算单包含多个明细项）
CREATE TABLE budget_items (
    id                      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    budget_id               UUID NOT NULL REFERENCES budget_orders(id),
    project_id              UUID NOT NULL REFERENCES design_projects(id),
    
    -- 工序信息（DAG工序链）
    process_code            VARCHAR(50) NOT NULL,      -- 工序编码
    process_name            VARCHAR(200) NOT NULL,     -- 工序名称
    category                VARCHAR(50) NOT NULL,      -- 工序分类（水电/泥瓦/木工等）
    node_code               VARCHAR(50),               -- 所属节点
    
    -- 材料明细
    material_code           VARCHAR(50),               -- 材料编码
    material_name           VARCHAR(200) NOT NULL,     -- 材料名称
    brand                   VARCHAR(100),              -- 品牌
    spec                    VARCHAR(200),              -- 规格
    unit                    VARCHAR(20),               -- 单位
    
    quantity                DECIMAL(10,2) NOT NULL,    -- 数量
    loss_rate               DECIMAL(5,4) DEFAULT 1.0000, -- 损耗系数
    actual_quantity         DECIMAL(10,2),             -- 实际用量（含损耗）
    
    -- 价格信息
    unit_price              DECIMAL(12,2) NOT NULL,   -- 单价
    market_price            DECIMAL(12,2),            -- 市场价
    purchase_price          DECIMAL(12,2),            -- 采购价
    
    amount                  DECIMAL(12,2) NOT NULL,   -- 小计金额
    
    -- 人工信息
    labor_hours             DECIMAL(8,2),            -- 人工工时
    labor_unit_price        DECIMAL(12,2),           -- 人工单价
    labor_amount            DECIMAL(12,2),           -- 人工费
    
    -- 工序关联（DAG影响链）
    prerequisite_processes  JSONB DEFAULT '[]',      -- 前置工序列表
    affected_processes     JSONB DEFAULT '[]',       -- 受影响工序列表
    
    -- 变更标记
    is_changed              BOOLEAN DEFAULT FALSE,    -- 是否被变更
    change_type             VARCHAR(20),             -- 变更类型（add/update/delete）
    original_item_id       UUID,                     -- 原明细ID
    
    remark                  TEXT,
    created_at              TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at              TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_budget_items_budget_id ON budget_items(budget_id);
CREATE INDEX idx_budget_items_project_id ON budget_items(project_id);
CREATE INDEX idx_budget_items_category ON budget_items(category);
CREATE INDEX idx_budget_items_process_code ON budget_items(process_code);
```

#### 3.3 人工成本库 `labor_cost_library`

```sql
-- 人工成本库（全国31省市分地区指导价）
CREATE TABLE labor_cost_library (
    id                      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    province_code            VARCHAR(10) NOT NULL,     -- 省代码
    province_name            VARCHAR(50) NOT NULL,     -- 省名称
    city_code                VARCHAR(10),             -- 市代码（可为NULL表示省级统一价）
    city_name                VARCHAR(50),             -- 市名称
    
    -- 工种
    work_type               VARCHAR(50) NOT NULL,     -- 工种（水电工/泥瓦工/木工等）
    work_type_name          VARCHAR(100) NOT NULL,    -- 工种名称
    
    -- 价格
    unit_price              DECIMAL(10,2) NOT NULL,  -- 单价（元/工日）
    unit                    VARCHAR(20) DEFAULT '工日',
    
    -- 系数
    difficulty_factor       DECIMAL(4,2) DEFAULT 1.00, -- 难度系数
    season_factor           DECIMAL(4,2) DEFAULT 1.00, -- 季节系数
    
    effective_date          DATE NOT NULL,            -- 生效日期
    expire_date             DATE,                     -- 失效日期
    
    source                  VARCHAR(100),             -- 数据来源
    is_local_avg            BOOLEAN DEFAULT FALSE,    -- 是否本地均价
    
    status                  VARCHAR(20) DEFAULT 'active',
    created_at              TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at              TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(province_code, city_code, work_type, effective_date)
);

CREATE INDEX idx_labor_cost_province ON labor_cost_library(province_code);
CREATE INDEX idx_labor_cost_city ON labor_cost_library(city_code);
CREATE INDEX idx_labor_cost_work_type ON labor_cost_library(work_type);
CREATE INDEX idx_labor_cost_effective ON labor_cost_library(effective_date);

-- 初始化示例数据
INSERT INTO labor_cost_library (province_code, province_name, city_code, city_name, work_type, work_type_name, unit_price) VALUES
('110000', '北京市', '110100', '北京市', 'electrician', '水电工', 450.00),
('110000', '北京市', '110100', '北京市', 'tiler', '泥瓦工', 420.00),
('110000', '北京市', '110100', '北京市', 'carpenter', '木工', 400.00),
('310000', '上海市', '310100', '上海市', 'electrician', '水电工', 480.00),
('310000', '上海市', '310100', '上海市', 'tiler', '泥瓦工', 450.00),
('440100', '广东省', '440100', '广州市', 'electrician', '水电工', 380.00),
('440100', '广东省', '440100', '广州市', 'tiler', '泥瓦工', 350.00);
```

#### 3.4 地区调价系数库 `region_adjustment`

```sql
-- 地区调价系数库
CREATE TABLE region_adjustment (
    id                      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    province_code            VARCHAR(10) NOT NULL,
    province_name            VARCHAR(50) NOT NULL,
    city_code                VARCHAR(10),
    city_name                VARCHAR(50),
    
    -- 调价类型
    adjust_type             VARCHAR(30) NOT NULL,     -- material/labor/transport/tax/season
    adjust_type_name        VARCHAR(100) NOT NULL,   -- 材料/人工/运输/税费/季节
    
    -- 系数
    coefficient              DECIMAL(8,4) NOT NULL,  -- 调价系数
    description             VARCHAR(200),            -- 说明
    
    -- 时间范围
    effective_date          DATE NOT NULL,
    expire_date             DATE,
    
    -- 备注
    reason                  TEXT,
    source                  VARCHAR(100),
    
    status                  VARCHAR(20) DEFAULT 'active',
    created_at              TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at              TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_region_adjust_province ON region_adjustment(province_code);
CREATE INDEX idx_region_adjust_city ON region_adjustment(city_code);
CREATE INDEX idx_region_adjust_type ON region_adjustment(adjust_type);
CREATE INDEX idx_region_adjust_effective ON region_adjustment(effective_date);

-- 初始化示例数据
INSERT INTO region_adjustment (province_code, province_name, city_code, city_name, adjust_type, adjust_type_name, coefficient, description) VALUES
('110000', '北京市', NULL, NULL, 'material', '材料费调价', 1.1500, '北京地区材料价格指数'),
('110000', '北京市', NULL, NULL, 'labor', '人工费调价', 1.2000, '北京地区人工成本'),
('310000', '上海市', NULL, NULL, 'material', '材料费调价', 1.1800, '上海地区材料价格指数'),
('310000', '上海市', NULL, NULL, 'labor', '人工费调价', 1.2500, '上海地区人工成本'),
('440000', '广东省', NULL, NULL, 'material', '材料费调价', 1.0000, '广东地区材料价格（基准）'),
('440000', '广东省', NULL, NULL, 'labor', '人工费调价', 1.0000, '广东地区人工成本（基准）');
```

#### 3.5 预算变更记录表 `budget_change_logs`

```sql
-- 预算变更记录表（记录每次预算变更）
CREATE TABLE budget_change_logs (
    id                      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    budget_id               UUID NOT NULL REFERENCES budget_orders(id),
    project_id              UUID NOT NULL REFERENCES design_projects(id),
    
    change_no               VARCHAR(50) NOT NULL,     -- 变更单号
    
    -- 变更前
    before_total            DECIMAL(12,2),            -- 变更前总额
    before_items            JSONB,                    -- 变更前明细
    
    -- 变更后
    after_total             DECIMAL(12,2),            -- 变更后总额
    after_items             JSONB,                    -- 变更后明细
    
    -- 变更差异
    diff_amount             DECIMAL(12,2) NOT NULL,  -- 差额
    diff_rate               DECIMAL(6,4),            -- 变化率
    
    -- 变更原因
    change_reason           VARCHAR(100) NOT NULL,   -- 变更原因
    change_reason_detail    TEXT,                    -- 变更详情
    
    -- 变更类型
    change_type             VARCHAR(30) NOT NULL,    -- design_change/material_change/process_change
    related_item_id         UUID,                    -- 关联的明细项
    
    -- 触发条件
    trigger_source          VARCHAR(50),            -- 触发来源（design/adjust/manual）
    design_change_desc      TEXT,                    -- 设计变更描述
    
    -- 处理方式
    handle_type             VARCHAR(30),             -- 处理方式（accept/reject/modify）
    handle_notes            TEXT,
    
    -- 审批
    need_approve            BOOLEAN DEFAULT FALSE,
    approve_status          VARCHAR(20),             -- pending/approved/rejected
    approver_id             UUID,
    approved_at             TIMESTAMP,
    
    created_by              UUID NOT NULL,
    created_at              TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_budget_change_budget_id ON budget_change_logs(budget_id);
CREATE INDEX idx_budget_change_project_id ON budget_change_logs(project_id);
CREATE INDEX idx_budget_change_type ON budget_change_logs(change_type);
CREATE INDEX idx_budget_change_created_at ON budget_change_logs(created_at);
```

#### 3.6 预算红线配置表 `budget_red_lines`

```sql
-- 预算红线配置表
CREATE TABLE budget_red_lines (
    id                      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    user_id                 UUID REFERENCES users(id),  -- 用户专属配置（可选）
    
    city                    VARCHAR(50),               -- 城市
    house_type              VARCHAR(30),              -- 房屋类型
    
    -- 红线类型
    line_type               VARCHAR(30) NOT NULL,     -- total/material/labor
    line_type_name          VARCHAR(100) NOT NULL,   -- 总额红线/材料费红线/人工费红线
    
    -- 阈值
    threshold_value         DECIMAL(12,2) NOT NULL, -- 红线阈值
    threshold_type          VARCHAR(20) DEFAULT 'fixed', -- fixed/percentage
    
    -- 预警配置
    warning_level           VARCHAR(20) DEFAULT 'medium', -- high/medium/low
    warning_threshold       DECIMAL(5,2) DEFAULT 80.00, -- 预警比例（如80%）
    enable_warning          BOOLEAN DEFAULT TRUE,
    
    -- 操作配置
    allow_exceed            BOOLEAN DEFAULT FALSE,   -- 是否允许超过红线
    require_confirm         BOOLEAN DEFAULT TRUE,    -- 超过是否需要确认
    
    status                  VARCHAR(20) DEFAULT 'active',
    created_at              TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at              TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_budget_red_lines_user_id ON budget_red_lines(user_id);
CREATE INDEX idx_budget_red_lines_city ON budget_red_lines(city);
CREATE INDEX idx_budget_red_lines_type ON budget_red_lines(line_type);
```

#### 3.7 预算统计报表表 `budget_reports`

```sql
-- 预算统计报表表
CREATE TABLE budget_reports (
    id                      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    report_no               VARCHAR(50) UNIQUE NOT NULL,
    
    project_id              UUID NOT NULL REFERENCES design_projects(id),
    budget_id               UUID REFERENCES budget_orders(id),
    user_id                 UUID NOT NULL REFERENCES users(id),
    
    -- 统计周期
    report_date             DATE NOT NULL,
    period_type             VARCHAR(20),             -- daily/weekly/monthly
    
    -- 预算数据
    budget_amount           DECIMAL(12,2),           -- 预算金额
    actual_amount           DECIMAL(12,2),          -- 实际金额
    variance_amount         DECIMAL(12,2),          -- 差异金额
    variance_rate           DECIMAL(6,4),           -- 差异率
    
    -- 分类统计
    material_budget         DECIMAL(12,2),
    material_actual         DECIMAL(12,2),
    material_variance       DECIMAL(12,2),
    
    labor_budget            DECIMAL(12,2),
    labor_actual            DECIMAL(12,2),
    labor_variance          DECIMAL(12,2),
    
    management_budget       DECIMAL(12,2),
    management_actual       DECIMAL(12,2),
    
    -- 完成度
    completion_rate         DECIMAL(5,2),           -- 完成率
    
    remark                  TEXT,
    created_at              TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_budget_reports_project_id ON budget_reports(project_id);
CREATE INDEX idx_budget_reports_report_date ON budget_reports(report_date);
```

---

## 四、预算引擎DAG工序链

### 4.1 DAG工序影响链模型

```
设计变更 → 工序识别 → 影响链遍历 → 增量计算 → 预算更新
              ↓
         变更传播路径:
         ┌─────────────────────────────────────────────────┐
         │ 设计变更 ─→ 水电改造 ─→ 防水工程 ─→ 泥瓦工程   │
         │      ↓                                         │
         │      └→ 拆除工程 ─→ 墙体改造 ─→ 油漆工程       │
         └─────────────────────────────────────────────────┘
```

### 4.2 工序关联表（实现DAG）

| 工序编码 | 工序名称 | 前置工序 | 影响工序 |
|----------|----------|----------|----------|
| demolition | 拆除工程 | - | wall_change |
| wall_change | 墙体改造 | demolition | waterproof, tiling |
| electrical | 水电改造 | wall_change | waterproof |
| waterproof | 防水工程 | wall_change, electrical | tiling |
| tiling | 泥瓦工程 | waterproof, wall_change | carpentry, painting |
| carpentry | 木工工程 | tiling | painting, installation |
| painting | 油漆工程 | carpentry | installation |
| installation | 安装工程 | carpentry, painting | acceptance |

---

## 五、表关系图（完整版）

```
┌─────────────┐
│   users     │
└──────┬──────┘
       │
       ├──< user_roles
       ├──< house_profiles
       │
       ├──< budget_orders >────────── budget_items
       │        │                        │
       │        └──< budget_change_logs │
       │        └──< budget_red_lines   │
       │        └──< budget_reports    │
       │
       ├──< inspection_reports >──< inspection_issues
       │
       ├──< design_projects >──< design_plans >──< design_materials
       │                              └──< design_drawings
       │
       ├──< construction_projects >──< construction_nodes >──< rectification_orders
       │                              └──< acceptance_records
       │
       └──< orders >──< payment_records
```

---

## 六、DDL初始化脚本

```sql
-- 创建数据库
CREATE DATABASE jzhuang_platform;

\c jzhuang_platform;

-- 启用UUID扩展
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 执行上述所有表结构...
```

| 类型 | PostgreSQL类型 | 说明 |
|------|---------------|------|
| 主键 | UUID | 全局唯一标识 |
| 时间戳 | TIMESTAMP | 带时区时间 |
| 日期 | DATE | 仅日期 |
| 金额 | DECIMAL(12,2) | 精确到分 |
| 百分比 | DECIMAL(5,2) | 0.00-100.00 |
| JSON | JSONB | 二进制JSON，支持索引 |
| 大文本 | TEXT | 无长度限制文本 |

---

## 五、索引策略

### 5.1 必须索引

| 表 | 索引 | 类型 | 用途 |
|---|---|---|---|
| users | phone | UNIQUE | 手机号登录 |
| users | wx_openid | UNIQUE | 微信登录 |
| orders | order_no | UNIQUE | 订单查询 |
| audit_logs | (user_id, created_at) | COMPOSITE | 日志查询 |

### 5.2 外键索引

所有外键字段自动创建索引，确保关联查询性能。

---

## 六、DDL初始化脚本

```sql
-- 创建数据库
CREATE DATABASE jzhuang_platform;

-- 连接数据库后执行
\c jzhuang_platform;

-- 启用UUID扩展
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 执行上述所有表结构...
```

---

*文档版本：V2.0 | 更新日期：2026-04-06*
