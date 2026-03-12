from datetime import datetime
from enum import Enum
from typing import List, Optional

from sqlmodel import Field, Relationship, SQLModel

from app.models.user import User


class CurrentStep(str, Enum):
    """当前审核步骤：对应5级审核流程"""
    ACTIVIST = "activist"          # 积极分子提交阶段
    PYR = "pyr"                    # 培养人审核阶段
    ZZWY = "zzwy"                  # 组织委员审核阶段
    ZBSJ = "zbsj"                  # 支部书记审核阶段
    ZZS = "zzs"                    # 总支书终审阶段


class ReportStatus(str, Enum):
    """报告状态"""
    PENDING = "pending"            # 待审核
    REJECTED = "rejected"          # 已驳回
    APPROVED = "approved"          # 已通过


class Report(SQLModel, table=True):
    """思想汇报模型"""
    __tablename__ = "report"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", nullable=False, index=True)  # 提交人ID
    title: Optional[str] = Field(default=None, max_length=200)  # 汇报标题
    year: int = Field(nullable=False, index=True)  # 年份
    month: int = Field(nullable=False, index=True)  # 月份 (1-12)
    file_path: str = Field(nullable=False, max_length=500)  # 文件存储路径
    original_filename: Optional[str] = Field(default=None, max_length=255)  # 原始文件名（用于下载时显示）
    uploaded_time: datetime = Field(default_factory=datetime.utcnow, nullable=False)  # 上传时间
    current_step: CurrentStep = Field(default=CurrentStep.PYR, nullable=False, index=True)  # 当前审核步骤
    status: ReportStatus = Field(default=ReportStatus.PENDING, nullable=False, index=True)  # 状态
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)  # 更新时间

    # 关系
    author: Optional[User] = Relationship(back_populates="reports")
    reviews: List["Review"] = Relationship(back_populates="report")
