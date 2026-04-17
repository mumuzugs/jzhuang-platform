# 集装修 数据库补充表设计 V2.0

**补充日期**：2026-04-06  
**依据**：架构文档V2.0要求

---

## 一、AI验房模块补充

### 1.1 验房图片表 `inspection_images`

```sql
-- 验房图片表
CREATE TABLE inspection_images (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    report_id           UUID NOT NULL REFERENCES inspection_reports(id),
    
    image_url           VARCHAR(500) NOT NULL,
    thumbnail_url       VARCHAR(500),
    
    image_type          VARCHAR(30) NOT NULL,       -- original/preprocessed/analyzed
    room                VARCHAR(50),                -- 所属房间
    scene               VARCHAR(50),                -- 场景
    
    width               INTEGER,
    height              INTEGER,
    file_size           BIGINT,
    format              VARCHAR(20),
    
    -- AI分析结果
    ai_result           JSONB,                      -- AI识别结果
    has_issue           BOOLEAN DEFAULT FALSE,
    
    -- 关联问题
    issue_id            UUID REFERENCES inspection_issues(id),
    
    uploaded_at         TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    processed_at        TIMESTAMP
);

CREATE INDEX idx_inspection_images_report_id ON inspection_images(report_id);
CREATE INDEX idx_inspection_images_type ON inspection_images(image_type);
```

### 1.2 城市风险配置表 `city_risk_configs`

```sql
-- 城市高频风险配置表
CREATE TABLE city_risk_configs (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    province_code        VARCHAR(10) NOT NULL,
    province_name        VARCHAR(50) NOT NULL,
    city_code            VARCHAR(10) NOT NULL,
    city_name            VARCHAR(50) NOT NULL,
    
    -- 风险类型
    risk_type           VARCHAR(50) NOT NULL,       -- wall_crack/water_leak等
    risk_name           VARCHAR(100) NOT NULL,
    
    -- 统计信息
    occurrence_rate     DECIMAL(5,2),             -- 发生率百分比
    avg_cost            DECIMAL(12,2),            -- 平均维修费用
    complaint_count     INTEGER DEFAULT 0,          -- 投诉次数
    
    data_source         VARCHAR(100),             -- 数据来源
    data_year           INTEGER,                    -- 数据年份
    update_frequency    VARCHAR(20) DEFAULT 'yearly',
    
    status              VARCHAR(20) DEFAULT 'active',
    created_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(city_code, risk_type)
);

CREATE INDEX idx_city_risk_city ON city_risk_configs(city_code);
CREATE INDEX idx_city_risk_type ON city_risk_configs(risk_type);
```

---

## 二、施工管理模块补充

### 2.1 材料进场记录表 `material_records`

```sql
-- 材料进场记录表
CREATE TABLE material_records (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    record_no           VARCHAR(50) UNIQUE NOT NULL,
    
    project_id          UUID NOT NULL REFERENCES construction_projects(id),
    node_id             UUID REFERENCES construction_nodes(id),
    
    -- 材料信息
    material_name       VARCHAR(200) NOT NULL,
    brand               VARCHAR(100),
    model               VARCHAR(100),
    spec                VARCHAR(200),
    unit                VARCHAR(20),
    quantity            DECIMAL(10,2) NOT NULL,
    
    -- 进场信息
    batch_no            VARCHAR(50),               -- 批次号
    supplier_name       VARCHAR(200),              -- 供应商
    purchase_amount     DECIMAL(12,2),            -- 采购金额
    
    -- 验收信息
    inspection_status   VARCHAR(20) DEFAULT 'pending', -- pending/passed/rejected
    inspection_result   TEXT,
    inspection_photos   JSONB DEFAULT '[]',
    inspector_id        UUID,
    inspected_at        TIMESTAMP,
    
    -- 品牌识别（云监工）
    recognized_brand    VARCHAR(100),
    brand_match_result VARCHAR(20),               -- match/mismatch/unknown
    recognition_confidence DECIMAL(5,2),
    
    arrival_date        DATE,
    remark              TEXT,
    
    created_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_material_records_project_id ON material_records(project_id);
CREATE INDEX idx_material_records_node_id ON material_records(node_id);
CREATE INDEX idx_material_records_inspection ON material_records(inspection_status);
```

### 2.2 施工日志表 `construction_daily_logs`

```sql
-- 施工日志表
CREATE TABLE construction_daily_logs (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    log_no              VARCHAR(50) UNIQUE NOT NULL,
    
    project_id          UUID NOT NULL REFERENCES construction_projects(id),
    node_id             UUID REFERENCES construction_nodes(id),
    
    log_date            DATE NOT NULL,
    weather             VARCHAR(30),
    temperature         VARCHAR(20),
    
    -- 日志内容
    log_type            VARCHAR(30) NOT NULL,       -- daily/material/issue/safety/coordinator
    content             TEXT NOT NULL,
    photos              JSONB DEFAULT '[]',
    
    -- 完成工作
    completed_work      TEXT,
    next_plan           TEXT,
    
    -- 问题记录
    issues              JSONB DEFAULT '[]',
    
    -- 人员
    worker_count        INTEGER,
    worker_names        JSONB DEFAULT '[]',
    
    reporter_id         UUID NOT NULL,
    created_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_construction_logs_project_id ON construction_daily_logs(project_id);
CREATE INDEX idx_construction_logs_date ON construction_daily_logs(log_date);
```

### 2.3 施工延期记录表 `construction_delays`

```sql
-- 施工延期记录表
CREATE TABLE construction_delays (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    delay_no            VARCHAR(50) UNIQUE NOT NULL,
    
    project_id          UUID NOT NULL REFERENCES construction_projects(id),
    node_id             UUID REFERENCES construction_nodes(id),
    
    -- 延期信息
    delay_days          INTEGER NOT NULL,           -- 延期天数
    planned_end_date    DATE NOT NULL,
    new_end_date        DATE NOT NULL,
    
    -- 延期原因
    reason_type         VARCHAR(50) NOT NULL,      -- weather/material/labor/design/other
    reason_detail       TEXT NOT NULL,
    
    -- 影响评估
    affect_follow_nodes BOOLEAN DEFAULT FALSE,
    affected_nodes      JSONB DEFAULT '[]',
    additional_cost     DECIMAL(12,2) DEFAULT 0,
    
    -- 处理状态
    status              VARCHAR(20) DEFAULT 'reported', -- reported/approved/processed/closed
    approver_id         UUID,
    approved_at         TIMESTAMP,
    approval_notes      TEXT,
    
    notify_status       VARCHAR(20) DEFAULT 'pending', -- pending/sent
    notify_time         TIMESTAMP,
    
    created_by          UUID NOT NULL,
    created_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_construction_delays_project_id ON construction_delays(project_id);
CREATE INDEX idx_construction_delays_status ON construction_delays(status);
```

---

## 三、AI云监工模块补充

### 3.1 云监工图片表 `supervision_images`

```sql
-- 云监工图片表
CREATE TABLE supervision_images (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    project_id          UUID NOT NULL REFERENCES construction_projects(id),
    node_id             UUID REFERENCES construction_nodes(id),
    
    image_url           VARCHAR(500) NOT NULL,
    thumbnail_url       VARCHAR(500),
    video_url           VARCHAR(500),              -- 视频源
    
    -- 来源信息
    source_type         VARCHAR(30) NOT NULL,       -- upload/camera/timelapse
    upload_by           UUID REFERENCES users(id),
    
    -- 场景信息
    room                VARCHAR(50),
    scene               VARCHAR(50),               -- 客厅/卧室/厨房等
    construction_stage  VARCHAR(50),              -- 当前工序
    
    -- 抽帧信息（如果是视频）
    is_keyframe         BOOLEAN DEFAULT FALSE,
    frame_timestamp     INTEGER,                    -- 秒
    
    -- 清晰度
    clarity_score       INTEGER,                    -- 清晰度评分
    is_blur             BOOLEAN DEFAULT FALSE,
    
    uploaded_at         TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    processed_at        TIMESTAMP
);

CREATE INDEX idx_supervision_images_project_id ON supervision_images(project_id);
CREATE INDEX idx_supervision_images_node_id ON supervision_images(node_id);
CREATE INDEX idx_supervision_images_stage ON supervision_images(construction_stage);
```

### 3.2 监工识别记录表 `supervision_records`

```sql
-- AI监工识别记录表
CREATE TABLE supervision_records (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    record_no           VARCHAR(50) UNIQUE NOT NULL,
    
    project_id          UUID NOT NULL REFERENCES construction_projects(id),
    node_id             UUID REFERENCES construction_nodes(id),
    
    -- 图片
    image_id            UUID REFERENCES supervision_images(id),
    
    -- AI识别结果
    ai_model            VARCHAR(100) NOT NULL,       -- 主模型/备用模型
    
    -- 进度识别
    recognized_stage    VARCHAR(50),               -- 识别的工序
    stage_confidence    INTEGER,                    -- 置信度
    progress_percent    INTEGER,                   -- 进度百分比
    
    -- 合规检测
    compliance_result   JSONB,                      -- 合规检测结果
    is_compliant        BOOLEAN DEFAULT TRUE,
    
    -- 异常识别
    anomalies           JSONB DEFAULT '[]',         -- 识别的异常
    anomaly_count       INTEGER DEFAULT 0,
    high_risk_count     INTEGER DEFAULT 0,
    medium_risk_count   INTEGER DEFAULT 0,
    low_risk_count      INTEGER DEFAULT 0,
    
    -- 安全隐患
    safety_issues       JSONB DEFAULT '[]',
    has_safety_risk     BOOLEAN DEFAULT FALSE,
    
    -- 整体评估
    overall_score       INTEGER,                    -- 整体评分
    
    processing_time_ms  INTEGER,                    -- 处理耗时
    created_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_supervision_records_project_id ON supervision_records(project_id);
CREATE INDEX idx_supervision_records_anomalies ON supervision_records(anomaly_count);
```

### 3.3 预警规则配置表 `warning_rules`

```sql
-- 预警规则配置表
CREATE TABLE warning_rules (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    rule_code           VARCHAR(50) UNIQUE NOT NULL,
    
    rule_name           VARCHAR(200) NOT NULL,
    rule_type           VARCHAR(30) NOT NULL,       -- progress/delay/safety/compliance/material
    
    -- 触发条件
    trigger_condition   JSONB NOT NULL,             -- 触发条件
    trigger_threshold   DECIMAL(12,2),            -- 触发阈值
    
    -- 预警级别
    warning_level       VARCHAR(20) NOT NULL,       -- high/medium/low
    message_template    TEXT NOT NULL,             -- 消息模板
    
    -- 通知配置
    notify_channels     JSONB DEFAULT '["app", "wechat", "sms"]',
    notify_roles        JSONB DEFAULT '[]',        -- 通知角色
    notify_users        JSONB DEFAULT '[]',        -- 指定用户
    
    -- 状态
    is_enabled          BOOLEAN DEFAULT TRUE,
    priority            INTEGER DEFAULT 0,
    
    -- 系统默认/用户自定义
    is_system           BOOLEAN DEFAULT FALSE,
    user_id             UUID REFERENCES users(id),
    
    created_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_warning_rules_type ON warning_rules(rule_type);
CREATE INDEX idx_warning_rules_level ON warning_rules(warning_level);
CREATE INDEX idx_warning_rules_enabled ON warning_rules(is_enabled);
```

### 3.4 预警历史表 `warning_logs`

```sql
-- 预警历史表
CREATE TABLE warning_logs (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    warning_no          VARCHAR(50) UNIQUE NOT NULL,
    
    project_id          UUID NOT NULL REFERENCES construction_projects(id),
    node_id             UUID REFERENCES construction_nodes(id),
    
    -- 预警规则
    rule_id             UUID REFERENCES warning_rules(id),
    rule_type           VARCHAR(30) NOT NULL,
    
    -- 预警内容
    warning_level       VARCHAR(20) NOT NULL,
    title               VARCHAR(200) NOT NULL,
    content             TEXT NOT NULL,
    
    -- 触发数据
    trigger_data        JSONB,                      -- 触发时的数据
    threshold_value     DECIMAL(12,2),            -- 阈值
    actual_value        DECIMAL(12,2),            -- 实际值
    
    -- 处理状态
    status              VARCHAR(20) DEFAULT 'pending', -- pending/viewed/handled/closed
    handle_result       TEXT,
    handled_by          UUID,
    handled_at          TIMESTAMP,
    
    -- 通知状态
    notify_status       JSONB DEFAULT '{}',       -- 各渠道通知状态
    notify_time         TIMESTAMP,
    
    -- 来源
    source_type         VARCHAR(30),              -- manual/auto
    source_id           UUID,                      -- 来源ID
    
    created_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_warning_logs_project_id ON warning_logs(project_id);
CREATE INDEX idx_warning_logs_level ON warning_logs(warning_level);
CREATE INDEX idx_warning_logs_status ON warning_logs(status);
CREATE INDEX idx_warning_logs_created ON warning_logs(created_at);
```

---

## 四、验收模块补充

### 4.1 验收标准库表 `acceptance_standards`

```sql
-- 国家规范验收标准库
CREATE TABLE acceptance_standards (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    standard_code       VARCHAR(50) UNIQUE NOT NULL,
    
    -- 标准信息
    standard_name       VARCHAR(200) NOT NULL,
    standard_type       VARCHAR(50) NOT NULL,       -- electrical/waterproof/tiling等
    standard_type_name VARCHAR(100) NOT NULL,
    
    -- 国标依据
    national_code       VARCHAR(50),               -- GB 50327-2001等
    national_name       VARCHAR(200),
    
    -- 验收项
    item_code           VARCHAR(50),
    item_name           VARCHAR(200) NOT NULL,
    item_type           VARCHAR(20) NOT NULL,      -- main/general 主控项/一般项
    
    -- 验收方法
    check_method        TEXT,                       -- 检测方法
    check_equipment    VARCHAR(200),              -- 检测设备
    sampling_method     VARCHAR(200),              -- 取样方法
    
    -- 合格标准
    qualified_standard  TEXT NOT NULL,             -- 合格判定标准
    unqualified_deal   TEXT,                       -- 不合格处理方式
    
    -- 大白话解读
    user_friendly_desc TEXT,                       -- 用户友好的大白话解读
   合格不合格对比图
    
    -- 版本
    version             VARCHAR(20),
    effective_date      DATE,
    expire_date         DATE,
    
    status              VARCHAR(20) DEFAULT 'active',
    created_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_acceptance_standards_type ON acceptance_standards(standard_type);
CREATE INDEX idx_acceptance_standards_item_type ON acceptance_standards(item_type);
CREATE INDEX idx_acceptance_standards_national ON acceptance_standards(national_code);
```

---

## 五、支付模块补充

### 5.1 分期付款计划表 `payment_installments`

```sql
-- 分期付款计划表
CREATE TABLE payment_installments (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    installment_no      VARCHAR(50) UNIQUE NOT NULL,
    
    project_id          UUID NOT NULL REFERENCES construction_projects(id),
    order_id            UUID REFERENCES orders(id),
    
    -- 分期信息
    total_amount        DECIMAL(12,2) NOT NULL,   -- 总金额
    installment_count    INTEGER NOT NULL,           -- 分期数
    paid_amount         DECIMAL(12,2) DEFAULT 0,   -- 已付金额
    remaining_amount     DECIMAL(12,2),             -- 剩余金额
    
    -- 分期明细
    installments        JSONB NOT NULL,             -- 各期明细
    /*
    [
        {"period": 1, "amount": 10000, "due_date": "2026-05-01", "status": "paid"},
        {"period": 2, "amount": 20000, "due_date": "2026-06-01", "status": "pending"},
        ...
    ]
    */
    
    -- 配置
    down_payment_ratio  DECIMAL(5,2),             -- 首付比例
    payment_method      VARCHAR(30),              -- 支付方式
    
    status              VARCHAR(20) DEFAULT 'active',
    completed_at        TIMESTAMP,
    
    created_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_payment_installments_project_id ON payment_installments(project_id);
CREATE INDEX idx_payment_installments_status ON payment_installments(status);
```

---

## 六、附件表

### 6.1 附件表 `attachments`

```sql
-- 通用附件表
CREATE TABLE attachments (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- 关联信息
    business_type       VARCHAR(50) NOT NULL,       -- inspection_report/design_plan/contract等
    business_id         UUID NOT NULL,
    
    -- 文件信息
    file_name           VARCHAR(255) NOT NULL,
    file_url            VARCHAR(500) NOT NULL,
    file_size           BIGINT,
    file_type           VARCHAR(100),              -- MIME类型
    file_ext            VARCHAR(20),               -- 扩展名
    
    -- 分类
    category            VARCHAR(50),               -- image/document/video
    sub_category        VARCHAR(50),              -- photo/pdf/cad
    
    -- 元数据
    title               VARCHAR(200),
    description         TEXT,
    tags                JSONB DEFAULT '[]',
    
    -- 权限
    is_public          BOOLEAN DEFAULT FALSE,
    expire_time         TIMESTAMP,
    
    uploaded_by         UUID REFERENCES users(id),
    created_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_attachments_business ON attachments(business_type, business_id);
CREATE INDEX idx_attachments_category ON attachments(category);
CREATE INDEX idx_attachments_uploader ON attachments(uploaded_by);
```

---

## 七、补充表清单

| 模块 | 表名 | 说明 | 状态 |
|------|------|------|------|
| 验房 | inspection_images | 验房图片表 | ✅ |
| 验房 | city_risk_configs | 城市风险配置 | ✅ |
| 施工 | material_records | 材料进场记录 | ✅ |
| 施工 | construction_daily_logs | 施工日志 | ✅ |
| 施工 | construction_delays | 延期记录 | ✅ |
| 云监工 | supervision_images | 云监工图片 | ✅ |
| 云监工 | supervision_records | AI识别记录 | ✅ |
| 云监工 | warning_rules | 预警规则配置 | ✅ |
| 云监工 | warning_logs | 预警历史 | ✅ |
| 验收 | acceptance_standards | 国家规范标准库 | ✅ |
| 支付 | payment_installments | 分期付款计划 | ✅ |
| 通用 | attachments | 通用附件表 | ✅ |

---

## 八、最终表统计

| 域 | 原表数 | 补充表数 | 合计 |
|---|---|---|---|
| 用户域 | 5 | 0 | 5 |
| 验房域 | 2 | 2 | 4 |
| 设计域 | 4 | 1 | 5 |
| 预算域 | 7 | 0 | 7 |
| 施工域 | 3 | 3 | 6 |
| 云监工域 | 0 | 4 | 4 |
| 验收域 | 2 | 1 | 3 |
| 支付域 | 3 | 1 | 4 |
| 系统域 | 4 | 0 | 4 |
| **总计** | **30** | **12** | **42** |

---

*补充日期：2026-04-06*
