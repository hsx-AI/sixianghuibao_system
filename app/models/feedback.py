from datetime import datetime
from enum import Enum
from typing import Optional

from sqlmodel import Field, Relationship, SQLModel

from app.models.user import User


class FeedbackStatus(str, Enum):
    """反馈状态"""
    PENDING = "pending"      # 待处理
    PROCESSED = "processed"  # 已处理
    ARCHIVED = "archived"    # 已归档


class FeedbackType(str, Enum):
    """反馈类型"""
    BUG = "bug"              # Bug 报告
    FEATURE = "feature"      # 功能建议
    QUESTION = "question"    # 问题咨询
    OTHER = "other"          # 其他


class Feedback(SQLModel, table=True):
    """用户反馈模型"""
    __tablename__ = "feedback"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", nullable=False, index=True)  # 提交人ID
    feedback_type: FeedbackType = Field(default=FeedbackType.OTHER, nullable=False)  # 反馈类型
    title: str = Field(nullable=False, max_length=200)  # 反馈标题
    content: str = Field(nullable=False, max_length=2000)  # 反馈内容
    status: FeedbackStatus = Field(default=FeedbackStatus.PENDING, nullable=False, index=True)  # 处理状态
    admin_reply: Optional[str] = Field(default=None, max_length=1000)  # 管理员回复
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)  # 创建时间
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)  # 更新时间

    # 关系
    user: Optional[User] = Relationship()







