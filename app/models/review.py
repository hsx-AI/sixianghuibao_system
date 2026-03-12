from datetime import datetime
from enum import Enum
from typing import Optional

from sqlmodel import Field, Relationship, SQLModel

from app.models.report import Report
from app.models.user import Role, User


class ReviewStatus(str, Enum):
    """审核状态"""
    PENDING = "pending"            # 待审核
    APPROVED = "approved"          # 通过
    REJECTED = "rejected"          # 驳回


class Review(SQLModel, table=True):
    """审核记录模型"""
    __tablename__ = "review"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    report_id: int = Field(foreign_key="report.id", nullable=False, index=True)  # 报告ID
    reviewer_id: int = Field(foreign_key="user.id", nullable=False, index=True)  # 审核人ID
    role: Role = Field(nullable=False, index=True)  # 审核人角色（在审核时的角色）
    status: ReviewStatus = Field(nullable=False)  # 审核状态
    comment: Optional[str] = Field(default=None, max_length=1000)  # 审核意见
    reject_file_path: Optional[str] = Field(default=None, max_length=500)  # 驳回时上传的批注文件路径
    reject_original_filename: Optional[str] = Field(default=None, max_length=255)  # 批注文件的原始文件名
    review_time: datetime = Field(default_factory=datetime.utcnow, nullable=False)  # 审核时间

    # 关系
    report: Optional[Report] = Relationship(back_populates="reviews")
    reviewer: Optional[User] = Relationship(back_populates="reviews")
