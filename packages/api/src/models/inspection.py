"""
验房报告模型
"""
from datetime import datetime
from sqlalchemy import Column, String, Boolean, DateTime, Integer, Text, Enum as SQLEnum, Index, JSON
from sqlalchemy.dialects.postgresql import UUID
import uuid
import enum

from src.core.database import Base


class InspectionStatus(str, enum.Enum):
    """验房状态"""
    PENDING = "pending"      # 待处理
    PROCESSING = "processing"  # 处理中
    COMPLETED = "completed"    # 已完成
    FAILED = "failed"         # 失败


class InspectionRiskLevel(str, enum.Enum):
    """风险等级"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class InspectionReport(Base):
    """验房报告表"""
    __tablename__ = "inspection_reports"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), nullable=False, index=True)
    
    # 房屋信息
    house_type = Column(String(20), nullable=True)  # 毛坯房/二手房
    city = Column(String(50), nullable=True)
    district = Column(String(50), nullable=True)
    area = Column(Integer, nullable=True)  # 面积
    
    # 图片
    layout_image = Column(String(500), nullable=True)  # 户型图
    room_images = Column(JSON, nullable=True)  # 房间照片列表
    
    # AI识别结果
    status = Column(SQLEnum(InspectionStatus), default=InspectionStatus.PENDING)
    ai_result = Column(JSON, nullable=True)  # AI识别结果
    
    # 识别的问题
    issues = Column(JSON, nullable=True)  # 问题列表
    
    # 风险统计
    high_risk_count = Column(Integer, default=0)
    medium_risk_count = Column(Integer, default=0)
    low_risk_count = Column(Integer, default=0)
    
    # 报告
    report_url = Column(String(500), nullable=True)
    report_content = Column(Text, nullable=True)
    
    # 城市高频风险
    city_risks = Column(JSON, nullable=True)
    
    # 人工复核
    review_status = Column(String(20), default="pending")  # pending, done
    review_comment = Column(Text, nullable=True)
    reviewer_id = Column(String(36), nullable=True)
    
    # 时间
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    
    __table_args__ = (
        Index("idx_inspection_user", "user_id"),
        Index("idx_inspection_status", "status"),
        Index("idx_inspection_created", "created_at"),
    )


class HouseIssue(Base):
    """房屋问题表"""
    __tablename__ = "house_issues"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    report_id = Column(String(36), nullable=False, index=True)
    
    # 问题类型
    issue_type = Column(String(50), nullable=False)  # 墙面开裂/防水渗漏/...
    issue_name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    
    # 位置
    location = Column(String(100), nullable=True)  # 客厅/卧室/厨房/...
    position_detail = Column(String(200), nullable=True)  # 具体位置描述
    
    # 风险
    risk_level = Column(SQLEnum(InspectionRiskLevel), default=InspectionRiskLevel.MEDIUM)
    severity = Column(Integer, default=5)  # 1-10
    
    # 整改建议
    suggestion = Column(Text, nullable=True)
    estimated_cost = Column(Integer, nullable=True)  # 预估费用
    
    # 图片标注
    image_url = Column(String(500), nullable=True)
    image_coords = Column(JSON, nullable=True)  # 标注坐标
    
    # AI置信度
    confidence = Column(Integer, nullable=True)  # 0-100
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    __table_args__ = (
        Index("idx_issue_report", "report_id"),
        Index("idx_issue_type", "issue_type"),
    )
