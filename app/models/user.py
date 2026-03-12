from datetime import datetime
from enum import Enum
from typing import List, Optional

from sqlalchemy import Column, String
from sqlmodel import Field, Relationship, SQLModel


class Role(str, Enum):
    """用户角色枚举：对应分级审核流程"""

    ADMIN = "admin"  # 管理员
    ACTIVIST = "activist"  # 积极分子
    PYR = "pyr"  # 培养人
    ZZWY = "zzwy"  # 组织委员
    ZBSJ = "zbsj"  # 支部书记
    ZZ = "zz"  # 总支（兼容旧数据）
    ZZS = "zzs"  # 总支书记


class User(SQLModel, table=True):
    """用户模型"""

    __tablename__ = "user"

    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True, nullable=False, max_length=50)
    password_hash: str = Field(nullable=False, max_length=255)
    role: Role = Field(index=True, nullable=False)
    real_name: str = Field(nullable=False, max_length=50)  # 真实姓名
    zhibu: Optional[str] = Field(default=None, max_length=50)  # 所属支部

    # 为每个积极分子(activist)指定培养人（数据库字段为大写 PYR1/PYR2）
    pyr1: Optional[str] = Field(default=None, sa_column=Column("PYR1", String(50)))
    pyr2: Optional[str] = Field(default=None, sa_column=Column("PYR2", String(50)))

    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    reports: List["Report"] = Relationship(back_populates="author")
    reviews: List["Review"] = Relationship(back_populates="reviewer")
