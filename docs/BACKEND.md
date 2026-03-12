# 后端开发指南

本文档详细说明思想汇报管理系统后端的架构设计和开发指南。

## 🏗️ 技术栈

- **Web 框架**: FastAPI 0.123.0
- **ORM**: SQLModel 0.0.27 (基于 SQLAlchemy 2.0)
- **数据库**: SQLite (可轻松迁移到 PostgreSQL/MySQL)
- **认证**: JWT (python-jose)
- **密码加密**: Bcrypt (passlib)
- **ASGI 服务器**: Uvicorn 0.38.0
- **数据验证**: Pydantic 2.12

## 📁 项目结构

```
app/
├── __init__.py           # 应用初始化
├── config.py             # 配置文件
├── database.py           # 数据库连接
│
├── auth/                 # 认证模块
│   ├── __init__.py
│   ├── security.py       # 密码加密、Token 生成
│   └── dependencies.py   # 认证依赖（获取当前用户）
│
├── models/               # 数据模型
│   ├── __init__.py
│   ├── user.py          # 用户模型
│   ├── report.py        # 报告模型
│   └── review.py        # 审核记录模型
│
├── routes/               # API 路由
│   ├── __init__.py
│   ├── auth.py          # 认证路由（登录、获取用户信息）
│   └── reports.py       # 报告路由（提交、审核、查询）
│
├── services/             # 业务逻辑层
│   ├── __init__.py
│   └── report_service.py # 报告审核业务逻辑
│
└── utils/                # 工具函数
    ├── __init__.py
    ├── file_utils.py    # 文件处理工具
    └── workflow.py      # 工作流配置
```

## 🔄 应用架构

### 分层架构

```
┌─────────────────────────────────────┐
│         API Layer (Routes)          │  ← FastAPI 路由，处理 HTTP 请求
├─────────────────────────────────────┤
│      Service Layer (Services)       │  ← 业务逻辑层，实现核心功能
├─────────────────────────────────────┤
│       Data Layer (Models)           │  ← 数据模型，ORM 映射
├─────────────────────────────────────┤
│       Database (SQLite)             │  ← 数据持久化
└─────────────────────────────────────┘
```

### 请求处理流程

```
HTTP 请求
    ↓
FastAPI 路由 (routes/)
    ↓
认证中间件 (get_current_user)
    ↓
业务逻辑 (services/)
    ↓
数据库操作 (models/ + database.py)
    ↓
返回 JSON 响应
```

---

## 🔐 认证系统

### JWT Token 认证

**文件**: `app/auth/security.py`

```python
from jose import jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta

# 密码加密上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """生成密码哈希"""
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """创建 JWT Token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(days=30))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
```

### 获取当前用户

**文件**: `app/auth/dependencies.py`

```python
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/token")

def get_current_user(
    token: str = Depends(oauth2_scheme),
    session: Session = Depends(get_session)
) -> User:
    """从 Token 获取当前用户"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = session.get(User, user_id)
    if user is None:
        raise credentials_exception
    
    return user
```

### 登录接口

**文件**: `app/routes/auth.py`

```python
@router.post("/token")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: Session = Depends(get_session)
):
    """用户登录，返回 JWT Token"""
    # 查询用户
    statement = select(User).where(User.username == form_data.username)
    user = session.exec(statement).first()
    
    # 验证密码
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误"
        )
    
    # 生成 Token
    access_token = create_access_token(data={"sub": str(user.id)})
    
    return {"access_token": access_token, "token_type": "bearer"}
```

---

## 📊 核心业务逻辑

### 审核流程实现

**文件**: `app/services/report_service.py`

#### 工作流配置

```python
from app.models import CurrentStep, Role

# 审核流程步骤映射
WORKFLOW_MAP = {
    CurrentStep.TRAINER: CurrentStep.ORGANIZER,      # 培养人 → 组织委员
    CurrentStep.ORGANIZER: CurrentStep.SECRETARY,    # 组织委员 → 支部书记
    CurrentStep.SECRETARY: CurrentStep.FINAL,        # 支部书记 → 最终完成
    CurrentStep.FINAL: None,                         # 最终步骤
}

# 反向映射：用于退回
REVERSE_WORKFLOW_MAP = {
    CurrentStep.ORGANIZER: CurrentStep.TRAINER,
    CurrentStep.SECRETARY: CurrentStep.ORGANIZER,
    CurrentStep.FINAL: CurrentStep.SECRETARY,
    CurrentStep.TRAINER: CurrentStep.TRAINER,        # 第一步
}

# 步骤对应的审核角色
STEP_ROLE_MAP = {
    CurrentStep.TRAINER: Role.TRAINER,
    CurrentStep.ORGANIZER: Role.ORGANIZER,
    CurrentStep.SECRETARY: Role.SECRETARY,
    CurrentStep.FINAL: Role.FINAL,
}
```

#### 核心审核函数

```python
def review_report(
    session: Session,
    report_id: int,
    reviewer_id: int,
    review_status: str,
    comment: Optional[str] = None
) -> Dict:
    """
    审核报告
    
    Args:
        session: 数据库会话
        report_id: 报告ID
        reviewer_id: 审核人ID
        review_status: 审核状态 (approved/rejected)
        comment: 审核意见
        
    Returns:
        包含审核结果的字典
        
    Raises:
        HTTPException: 参数错误、权限不足等
    """
    # 1. 验证参数
    if review_status not in ["approved", "rejected"]:
        raise HTTPException(400, "审核状态必须是 'approved' 或 'rejected'")
    
    # 2. 查询报告和审核人
    report = session.get(Report, report_id)
    if not report:
        raise HTTPException(404, f"报告 ID {report_id} 不存在")
    
    reviewer = session.get(User, reviewer_id)
    if not reviewer:
        raise HTTPException(404, "审核人不存在")
    
    # 3. 检查报告状态
    if report.status == ReportStatus.APPROVED:
        raise HTTPException(400, "该报告已经完成全部审核流程")
    
    # 4. 检查审核权限
    required_role = STEP_ROLE_MAP.get(report.current_step)
    if reviewer.role != required_role:
        raise HTTPException(
            403,
            f"当前步骤需要 {required_role.value} 角色审核，"
            f"您的角色是 {reviewer.role.value}"
        )
    
    # 5. 根据审核结果更新报告状态
    if review_status == "approved":
        # 通过：流转到下一步
        next_step = WORKFLOW_MAP.get(report.current_step)
        if next_step is None:
            # 最终审核通过
            report.status = ReportStatus.APPROVED
            message = "报告已通过全部审核流程"
        else:
            report.current_step = next_step
            report.status = ReportStatus.PENDING
            message = f"报告已通过当前审核，流转至 {next_step.value} 步骤"
    else:
        # 退回：返回上一步
        prev_step = REVERSE_WORKFLOW_MAP.get(report.current_step)
        report.current_step = prev_step
        report.status = ReportStatus.REJECTED
        message = f"报告被退回，返回至 {prev_step.value} 步骤"
    
    report.updated_at = datetime.utcnow()
    
    # 6. 创建审核记录
    review = Review(
        report_id=report_id,
        reviewer_id=reviewer_id,
        role=reviewer.role,
        status=ReviewStatus.APPROVED if review_status == "approved" else ReviewStatus.REJECTED,
        comment=comment,
        review_time=datetime.utcnow()
    )
    
    # 7. 提交数据库
    session.add(report)
    session.add(review)
    session.commit()
    session.refresh(report)
    session.refresh(review)
    
    # 8. 返回结果
    return {
        "success": True,
        "message": message,
        "data": {
            "report_id": report.id,
            "current_step": report.current_step.value,
            "status": report.status.value,
            "updated_at": report.updated_at.isoformat(),
            "review": {
                "id": review.id,
                "reviewer_id": reviewer.id,
                "reviewer_name": reviewer.real_name,
                "reviewer_role": reviewer.role.value,
                "status": review.status.value,
                "comment": review.comment,
                "review_time": review.review_time.isoformat()
            }
        }
    }
```

---

## 🛣️ API 路由设计

### 路由结构

```python
# app/routes/reports.py
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

router = APIRouter(prefix="/api/reports", tags=["reports"])

@router.post("/{report_id}/review")
def review_report_endpoint(
    report_id: int,
    payload: ReviewRequest,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """审核报告 API"""
    return report_service.review_report(
        session=session,
        report_id=report_id,
        reviewer_id=current_user.id,
        review_status=payload.status,
        comment=payload.comment
    )
```

### 路由注册

```python
# main.py
from app.routes import auth, reports

app = FastAPI()
app.include_router(auth.router)
app.include_router(reports.router)
```

---

## 🗄️ 数据库操作

### 数据库连接

**文件**: `app/database.py`

```python
from sqlmodel import SQLModel, Session, create_engine
from app.config import DATABASE_URL

engine = create_engine(DATABASE_URL, echo=False)

def init_db():
    """初始化数据库，创建所有表"""
    SQLModel.metadata.create_all(engine)

def get_session():
    """获取数据库会话（依赖注入）"""
    with Session(engine) as session:
        yield session
```

### 数据查询示例

```python
from sqlmodel import select

# 查询单个对象
user = session.get(User, user_id)

# 条件查询
statement = select(User).where(User.username == "activist1")
user = session.exec(statement).first()

# 查询列表
statement = select(Report).where(
    Report.current_step == CurrentStep.TRAINER,
    Report.status == ReportStatus.PENDING
)
reports = session.exec(statement).all()

# 关联查询（预加载）
from sqlalchemy.orm import selectinload

statement = select(Report).options(
    selectinload(Report.author),
    selectinload(Report.reviews)
).where(Report.id == report_id)
report = session.exec(statement).first()
```

---

## 🧪 测试

### 单元测试示例

**文件**: `test_review_workflow.py`

```python
import pytest
from sqlmodel import Session, create_engine
from app.models import User, Report, Review
from app.services.report_service import review_report

def test_review_workflow():
    """测试完整审核流程"""
    # 创建测试数据库
    engine = create_engine("sqlite:///test.db")
    SQLModel.metadata.create_all(engine)
    
    with Session(engine) as session:
        # 创建用户和报告
        activist = User(...)
        trainer = User(...)
        report = Report(...)
        session.add_all([activist, trainer, report])
        session.commit()
        
        # 测试审核通过
        result = review_report(
            session=session,
            report_id=report.id,
            reviewer_id=trainer.id,
            review_status="approved",
            comment="审核通过"
        )
        
        assert result["success"] == True
        assert report.current_step == CurrentStep.ORGANIZER
```

### 运行测试

```bash
# 运行审核流程测试
python test_review_workflow.py

# 使用 pytest（推荐）
pip install pytest
pytest test_review_workflow.py -v
```

---

## 🔧 配置管理

**文件**: `app/config.py`

```python
import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """应用配置"""
    DATABASE_URL: str = "sqlite:///data/app.db"
    SECRET_KEY: str = "your-secret-key-here"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 43200  # 30 天
    
    class Config:
        env_file = ".env"

settings = Settings()
```

### 环境变量

创建 `.env` 文件：

```bash
DATABASE_URL=sqlite:///data/app.db
SECRET_KEY=your-secret-key-change-this-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=43200
```

---

## 🚀 启动应用

### 开发模式

```bash
# 方式 1：直接运行
python main.py

# 方式 2：使用 uvicorn 命令
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 生产模式

```bash
# 使用 Gunicorn + Uvicorn Workers
pip install gunicorn
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000

# 或使用 Uvicorn（推荐）
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

---

## 📝 最佳实践

### 1. 错误处理

```python
from fastapi import HTTPException, status

# 使用标准 HTTP 状态码
raise HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail="资源不存在"
)
```

### 2. 数据验证

```python
from pydantic import BaseModel, Field, validator

class ReviewRequest(BaseModel):
    status: str = Field(..., pattern="^(approved|rejected)$")
    comment: Optional[str] = Field(None, max_length=1000)
    
    @validator('status')
    def validate_status(cls, v):
        if v not in ['approved', 'rejected']:
            raise ValueError('状态必须是 approved 或 rejected')
        return v
```

### 3. 依赖注入

```python
from fastapi import Depends

def get_current_admin_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """获取管理员用户"""
    if current_user.role not in [Role.SECRETARY, Role.FINAL]:
        raise HTTPException(403, "需要管理员权限")
    return current_user
```

### 4. 日志记录

```python
import logging

logger = logging.getLogger(__name__)

@router.post("/reports/{report_id}/review")
def review_report(report_id: int, ...):
    logger.info(f"用户 {current_user.id} 审核报告 {report_id}")
    try:
        result = report_service.review_report(...)
        logger.info(f"审核成功: {result}")
        return result
    except Exception as e:
        logger.error(f"审核失败: {e}")
        raise
```

---

## 🔍 调试技巧

### 1. 启用 SQL 日志

```python
engine = create_engine(DATABASE_URL, echo=True)
```

### 2. 使用 FastAPI 交互式文档

访问 `http://localhost:8000/docs` 查看 Swagger UI

### 3. 使用调试器

```python
import pdb; pdb.set_trace()  # 在需要调试的位置插入断点
```

---

## 📚 扩展功能建议

1. **缓存**: 使用 Redis 缓存用户信息和待审核报告列表
2. **异步任务**: 使用 Celery 处理耗时任务（如文件转换）
3. **WebSocket**: 实现实时通知功能
4. **日志**: 集成 ELK 日志系统
5. **监控**: 使用 Prometheus + Grafana 监控应用性能
6. **限流**: 使用 slowapi 实现 API 限流
7. **文档**: 使用 Sphinx 生成 API 文档

---

**最后更新**: 2024-12-02  
**后端版本**: v1.0.0





























