# 数据库模型文档

本文档详细说明思想汇报管理系统的数据库设计和模型关系。

## 📊 数据库概述

- **数据库类型**: SQLite
- **ORM 框架**: SQLModel (基于 SQLAlchemy + Pydantic)
- **文件位置**: `data/app.db`

## 🔄 审核流程

```
积极分子(Activist) 提交
    ↓
培养人(Trainer) 审核
    ↓
组织员(Organizer) 审核
    ↓
书记(Secretary) 审核
    ↓
终审(Final) 审核
    ↓
完成
```

## 📋 数据模型

### 1. User (用户表)

**表名**: `user`

| 字段 | 类型 | 说明 | 约束 |
|------|------|------|------|
| id | int | 用户ID | 主键，自增 |
| username | str | 用户名 | 唯一，索引，最大50字符 |
| password_hash | str | 密码哈希 | 非空，最大255字符 |
| role | Role | 用户角色 | 枚举值，索引 |
| real_name | str | 真实姓名 | 非空，最大50字符 |
| created_at | datetime | 创建时间 | 默认当前时间 |

**Role 枚举值**:
- `activist`: 积极分子
- `trainer`: 培养人
- `organizer`: 组织员
- `secretary`: 书记
- `final`: 终审

**关系**:
- `reports`: 该用户提交的所有报告 (一对多)
- `reviews`: 该用户作为审核人的所有审核记录 (一对多)

**模型定义**:

```python
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from enum import Enum

class Role(str, Enum):
    ACTIVIST = "activist"
    TRAINER = "trainer"
    ORGANIZER = "organizer"
    SECRETARY = "secretary"
    FINAL = "final"

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(max_length=50, unique=True, index=True)
    password_hash: str = Field(max_length=255)
    role: Role = Field(index=True)
    real_name: str = Field(max_length=50)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # 关系
    reports: List["Report"] = Relationship(back_populates="author")
    reviews: List["Review"] = Relationship(back_populates="reviewer")
```

---

### 2. Report (报告表)

**表名**: `report`

| 字段 | 类型 | 说明 | 约束 |
|------|------|------|------|
| id | int | 报告ID | 主键，自增 |
| user_id | int | 提交人ID | 外键 -> user.id，索引 |
| year | int | 年份 | 非空，索引 |
| month | int | 月份 | 非空 (1-12)，索引 |
| file_path | str | 文件路径 | 非空，最大500字符 |
| uploaded_time | datetime | 上传时间 | 默认当前时间 |
| current_step | CurrentStep | 当前审核步骤 | 枚举值，索引，默认trainer |
| status | ReportStatus | 报告状态 | 枚举值，索引，默认pending |
| updated_at | datetime | 更新时间 | 默认当前时间 |

**CurrentStep 枚举值**:
- `activist`: 积极分子提交阶段
- `trainer`: 培养人审核阶段
- `organizer`: 组织员审核阶段
- `secretary`: 书记审核阶段
- `final`: 终审阶段

**ReportStatus 枚举值**:
- `pending`: 待审核
- `rejected`: 已驳回
- `approved`: 已通过

**关系**:
- `author`: 报告提交人 (多对一 -> User)
- `reviews`: 该报告的所有审核记录 (一对多)

**模型定义**:

```python
class CurrentStep(str, Enum):
    ACTIVIST = "activist"
    TRAINER = "trainer"
    ORGANIZER = "organizer"
    SECRETARY = "secretary"
    FINAL = "final"

class ReportStatus(str, Enum):
    PENDING = "pending"
    REJECTED = "rejected"
    APPROVED = "approved"

class Report(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", index=True)
    year: int = Field(index=True)
    month: int = Field(ge=1, le=12, index=True)
    file_path: str = Field(max_length=500)
    uploaded_time: datetime = Field(default_factory=datetime.utcnow)
    current_step: CurrentStep = Field(default=CurrentStep.TRAINER, index=True)
    status: ReportStatus = Field(default=ReportStatus.PENDING, index=True)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # 关系
    author: Optional[User] = Relationship(back_populates="reports")
    reviews: List["Review"] = Relationship(back_populates="report")
```

---

### 3. Review (审核记录表)

**表名**: `review`

| 字段 | 类型 | 说明 | 约束 |
|------|------|------|------|
| id | int | 审核ID | 主键，自增 |
| report_id | int | 报告ID | 外键 -> report.id，索引 |
| reviewer_id | int | 审核人ID | 外键 -> user.id，索引 |
| role | Role | 审核人角色 | 枚举值，索引 |
| status | ReviewStatus | 审核状态 | 枚举值 |
| comment | str | 审核意见 | 可选，最大1000字符 |
| review_time | datetime | 审核时间 | 默认当前时间 |

**ReviewStatus 枚举值**:
- `pending`: 待审核
- `approved`: 通过
- `rejected`: 驳回

**关系**:
- `report`: 被审核的报告 (多对一 -> Report)
- `reviewer`: 审核人 (多对一 -> User)

**模型定义**:

```python
class ReviewStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"

class Review(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    report_id: int = Field(foreign_key="report.id", index=True)
    reviewer_id: int = Field(foreign_key="user.id", index=True)
    role: Role = Field(index=True)
    status: ReviewStatus
    comment: Optional[str] = Field(default=None, max_length=1000)
    review_time: datetime = Field(default_factory=datetime.utcnow)
    
    # 关系
    report: Optional[Report] = Relationship(back_populates="reviews")
    reviewer: Optional[User] = Relationship(back_populates="reviews")
```

---

## 🔗 外键关系图

```
User (用户)
 │
 ├──(1:N)──> Report (报告)
 │              │
 │              └──(1:N)──> Review (审核记录)
 │                             │
 └──(1:N)──────────────────────┘
    (作为审核人)
```

**关系说明**:
1. 一个用户可以提交多个报告 (User → Report: 1:N)
2. 一个报告有多条审核记录 (Report → Review: 1:N)
3. 一个用户可以审核多个报告 (User → Review: 1:N)

---

## 📈 索引说明

为了优化查询性能，以下字段创建了索引：

### User 表
- `username`: 唯一索引，用于登录查询
- `role`: 索引，用于按角色筛选用户

### Report 表
- `user_id`: 索引，用于查询用户的所有报告
- `year`: 索引，用于按年份筛选
- `month`: 索引，用于按月份筛选
- `current_step`: 索引，用于查询特定审核阶段的报告
- `status`: 索引，用于查询特定状态的报告

### Review 表
- `report_id`: 索引，用于查询报告的审核记录
- `reviewer_id`: 索引，用于查询审核人的审核历史
- `role`: 索引，用于按审核角色筛选

**组合索引建议**:
```python
# 在 Report 模型中添加组合索引
__table_args__ = (
    Index('idx_report_step_status', 'current_step', 'status'),
    Index('idx_report_user_time', 'user_id', 'year', 'month'),
)
```

---

## 💾 数据库初始化

### 方法 1: 使用初始化脚本

```bash
python init_db.py
```

这将：
1. 创建所有数据库表
2. 显示数据库模式信息
3. 创建示例用户（密码均为: 123456）

### 方法 2: 通过应用启动

```bash
python main.py
```

应用启动时会自动调用 `init_db()` 创建表。

### 方法 3: 手动创建

```python
from sqlmodel import SQLModel
from app.database import engine
from app.models import User, Report, Review

# 创建所有表
SQLModel.metadata.create_all(engine)
```

---

## 📝 使用示例

### 创建用户

```python
from sqlmodel import Session
from app.database import engine
from app.models import User, Role
from app.auth.security import get_password_hash

with Session(engine) as session:
    user = User(
        username="zhangsan",
        password_hash=get_password_hash("password123"),
        role=Role.ACTIVIST,
        real_name="张三"
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    print(f"创建用户: {user.real_name} (ID: {user.id})")
```

### 提交报告

```python
from app.models import Report, CurrentStep, ReportStatus

with Session(engine) as session:
    report = Report(
        user_id=1,
        year=2024,
        month=12,
        file_path="data/reports/2024-12-user1.docx",
        current_step=CurrentStep.TRAINER,
        status=ReportStatus.PENDING
    )
    session.add(report)
    session.commit()
    print(f"提交报告: ID={report.id}")
```

### 审核报告

```python
from app.models import Review, ReviewStatus, Role

with Session(engine) as session:
    # 创建审核记录
    review = Review(
        report_id=1,
        reviewer_id=2,  # 培养人ID
        role=Role.TRAINER,
        status=ReviewStatus.APPROVED,
        comment="内容充实，思想积极向上，同意通过。"
    )
    session.add(review)
    
    # 更新报告状态
    report = session.get(Report, 1)
    report.current_step = CurrentStep.ORGANIZER  # 进入下一步
    report.updated_at = datetime.utcnow()
    session.add(report)
    
    session.commit()
    print("审核完成，报告已流转到下一步")
```

### 查询报告及关联数据

```python
with Session(engine) as session:
    # 查询报告及其作者
    report = session.get(Report, 1)
    print(f"报告由 {report.author.real_name} 提交")
    print(f"当前步骤: {report.current_step.value}")
    print(f"当前状态: {report.status.value}")
    
    # 查询报告的所有审核记录
    print("\n审核记录:")
    for review in report.reviews:
        print(f"- {review.reviewer.real_name} ({review.role.value}): "
              f"{review.status.value} - {review.comment}")
```

### 查询待审核报告

```python
from sqlmodel import select

with Session(engine) as session:
    # 查询培养人需要审核的报告
    statement = select(Report).where(
        Report.current_step == CurrentStep.TRAINER,
        Report.status == ReportStatus.PENDING
    )
    reports = session.exec(statement).all()
    
    print(f"待审核报告数量: {len(reports)}")
    for report in reports:
        print(f"- 报告 {report.id}: {report.author.real_name} - "
              f"{report.year}年{report.month}月")
```

### 查询用户的审核历史

```python
with Session(engine) as session:
    user = session.get(User, 2)  # 培养人
    
    print(f"{user.real_name} 的审核历史:")
    for review in user.reviews:
        print(f"- 报告 {review.report_id}: {review.status.value} - "
              f"{review.review_time.strftime('%Y-%m-%d %H:%M')}")
```

---

## 🔄 状态流转逻辑

### Report 表状态变化

| 审核动作 | current_step 变化 | status 变化 |
|---------|------------------|------------|
| 培养人通过 | TRAINER → ORGANIZER | PENDING → PENDING |
| 组织委员通过 | ORGANIZER → SECRETARY | PENDING → PENDING |
| 支部书记通过 | SECRETARY → FINAL | PENDING → PENDING |
| 最终审核通过 | FINAL → FINAL | PENDING → APPROVED |
| 任意步骤退回 | 当前步骤 → 上一步骤 | PENDING → REJECTED |

### 工作流映射

```python
# 审核流程步骤映射
WORKFLOW_MAP = {
    CurrentStep.TRAINER: CurrentStep.ORGANIZER,
    CurrentStep.ORGANIZER: CurrentStep.SECRETARY,
    CurrentStep.SECRETARY: CurrentStep.FINAL,
    CurrentStep.FINAL: None,  # 最终步骤
}

# 反向映射：用于退回
REVERSE_WORKFLOW_MAP = {
    CurrentStep.ORGANIZER: CurrentStep.TRAINER,
    CurrentStep.SECRETARY: CurrentStep.ORGANIZER,
    CurrentStep.FINAL: CurrentStep.SECRETARY,
    CurrentStep.TRAINER: CurrentStep.TRAINER,  # 第一步
}
```

---

## ⚠️ 注意事项

1. **密码安全**: 密码使用 bcrypt 哈希存储，不存储明文密码
2. **时间戳**: 所有时间字段使用 UTC 时间
3. **外键约束**: 数据库会自动维护外键关系的完整性
4. **级联删除**: 默认情况下，删除用户或报告时需要先删除相关记录
5. **事务处理**: 所有数据库操作都应在事务中进行，确保数据一致性
6. **枚举类型**: 所有枚举值存储为字符串，便于数据库迁移

---

## 🔧 数据库迁移

### SQLite 迁移到其他数据库

如需迁移到 PostgreSQL 或 MySQL，只需修改 `app/config.py` 中的数据库 URL：

```python
# SQLite (开发环境)
DATABASE_URL = "sqlite:///data/app.db"

# PostgreSQL (生产环境)
DATABASE_URL = "postgresql://user:password@localhost/dbname"

# MySQL (生产环境)
DATABASE_URL = "mysql://user:password@localhost/dbname"
```

模型代码无需修改，SQLModel 会自动适配。

### 备份和恢复

```bash
# SQLite 备份
cp data/app.db data/app.db.backup.$(date +%Y%m%d)

# 恢复
cp data/app.db.backup.20241202 data/app.db

# 导出为 SQL
sqlite3 data/app.db .dump > backup.sql

# 从 SQL 恢复
sqlite3 data/app.db < backup.sql
```

---

## 📊 数据库查询优化建议

1. **使用索引**: 在查询条件中使用已建立索引的字段
2. **预加载关系**: 使用 `selectinload()` 避免 N+1 查询问题
3. **限制结果集**: 使用 `LIMIT` 限制查询结果数量
4. **避免全表扫描**: 在 WHERE 子句中使用索引字段
5. **使用连接池**: 在生产环境配置数据库连接池

```python
from sqlmodel import select
from sqlalchemy.orm import selectinload

# 优化示例：预加载关系
statement = select(Report).options(
    selectinload(Report.author),
    selectinload(Report.reviews)
).where(Report.status == ReportStatus.PENDING).limit(10)
```

---

**最后更新**: 2024-12-02  
**数据库版本**: v1.0.0





























