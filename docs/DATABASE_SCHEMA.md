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

## 三、表关系图

```
users (1) ──────< user_roles
  │
  ├──< house_profiles ──────< inspection_reports ──────< inspection_issues
  │                              │
  │                              └──< design_projects ──────< design_plans
  │                                                         │
  │                                                         └──< design_materials
  │                                                         └──< design_drawings
  │
  ├──< orders ──────< payment_records
  │
  └──< construction_projects ──────< construction_nodes
                                      │
                                      └──< rectification_orders
                                      └──< acceptance_records
                                      └──< warranty_records
```

---

## 四、字段类型规范

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
