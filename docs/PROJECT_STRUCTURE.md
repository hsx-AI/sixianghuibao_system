# 项目结构说明

本文档说明思想汇报管理系统的完整项目结构。

## 📁 项目目录树

```
sixianghuibao/
│
├── app/                        # 后端应用目录
│   ├── __init__.py
│   ├── config.py              # 配置文件（数据库URL、JWT密钥等）
│   ├── database.py            # 数据库连接和会话管理
│   │
│   ├── auth/                  # 认证模块
│   │   ├── __init__.py
│   │   ├── security.py       # 密码加密、Token生成
│   │   └── dependencies.py   # 认证依赖（获取当前用户）
│   │
│   ├── models/                # 数据模型
│   │   ├── __init__.py
│   │   ├── user.py           # 用户模型（User）
│   │   ├── report.py         # 报告模型（Report）
│   │   └── review.py         # 审核记录模型（Review）
│   │
│   ├── routes/                # API 路由
│   │   ├── __init__.py
│   │   ├── auth.py           # 认证路由（登录、获取用户信息）
│   │   └── reports.py        # 报告路由（提交、审核、查询）
│   │
│   ├── services/              # 业务逻辑层
│   │   ├── __init__.py
│   │   └── report_service.py # 报告审核业务逻辑
│   │
│   └── utils/                 # 工具函数
│       ├── __init__.py
│       ├── file_utils.py     # 文件处理工具
│       └── workflow.py       # 工作流配置
│
├── frontend/                   # 前端应用目录
│   ├── public/                # 静态资源
│   │   └── logo.svg
│   │
│   ├── src/
│   │   ├── api/               # API 接口层
│   │   │   ├── auth.js       # 认证 API
│   │   │   └── report.js     # 报告 API
│   │   │
│   │   ├── assets/            # 资源文件
│   │   │
│   │   ├── layouts/           # 布局组件
│   │   │   └── MainLayout.vue # 主布局
│   │   │
│   │   ├── router/            # 路由配置
│   │   │   └── index.js      # 路由定义与权限控制
│   │   │
│   │   ├── stores/            # 状态管理
│   │   │   └── user.js       # 用户状态
│   │   │
│   │   ├── utils/             # 工具函数
│   │   │   ├── constants.js  # 常量定义
│   │   │   └── request.js    # Axios 封装
│   │   │
│   │   ├── views/             # 页面组件
│   │   │   ├── Login.vue     # 登录页
│   │   │   ├── Dashboard.vue # 首页
│   │   │   │
│   │   │   ├── activist/     # 积极分子页面
│   │   │   │   └── Submit.vue
│   │   │   │
│   │   │   ├── trainer/      # 培养人页面
│   │   │   │   └── Review.vue
│   │   │   │
│   │   │   ├── organizer/    # 组织委员页面
│   │   │   │   └── Review.vue
│   │   │   │
│   │   │   ├── secretary/    # 支部书记页面
│   │   │   │   └── Review.vue
│   │   │   │
│   │   │   └── final/        # 总支书记页面
│   │   │       └── Overview.vue
│   │   │
│   │   ├── App.vue           # 根组件
│   │   └── main.js           # 应用入口
│   │
│   ├── index.html             # HTML 入口
│   ├── vite.config.js        # Vite 配置
│   ├── package.json          # 前端依赖配置
│   ├── QUICKSTART.md         # 前端快速开始
│   ├── ARCHITECTURE.md       # 前端架构说明
│   └── README.md             # 前端项目说明
│
├── data/                      # 数据目录
│   ├── app.db                # SQLite 数据库文件
│   └── reports/              # 报告文件存储
│       └── 2024/
│           └── 12/
│
├── docs/                      # 文档目录
│   ├── API.md                # API 接口文档
│   ├── BACKEND.md            # 后端开发指南
│   ├── FRONTEND.md           # 前端开发指南
│   ├── DATABASE.md           # 数据库模型文档
│   └── PROJECT_STRUCTURE.md  # 项目结构说明（本文档）
│
├── venv/                      # Python 虚拟环境（.gitignore）
│
├── main.py                    # 后端应用入口
├── init_db.py                # 数据库初始化脚本
├── query_examples.py         # 数据库查询示例
├── test_review_workflow.py   # 审核流程测试
│
├── requirements.txt           # 后端依赖配置
├── DEPENDENCIES.md           # 依赖说明文档
├── README.md                 # 项目主文档
├── .gitignore                # Git 忽略文件
└── .env                      # 环境变量配置（不提交到 Git）
```

---

## 📂 核心目录说明

### 后端目录

#### `app/` - 后端应用根目录

所有后端代码都在此目录下，采用分层架构：

1. **models/** - 数据模型层
   - 定义数据库表结构
   - 使用 SQLModel (ORM)
   - 包含 User、Report、Review 三个核心模型

2. **routes/** - API 路由层
   - 处理 HTTP 请求
   - 参数验证
   - 调用 Service 层

3. **services/** - 业务逻辑层
   - 核心业务逻辑
   - 审核流程控制
   - 数据处理

4. **auth/** - 认证模块
   - JWT Token 生成与验证
   - 密码加密（bcrypt）
   - 用户权限检查

5. **utils/** - 工具模块
   - 文件处理
   - 工作流配置
   - 通用工具函数

#### `data/` - 数据存储目录

- **app.db**: SQLite 数据库文件
- **reports/**: 上传的报告文件存储目录
  - 按年份/月份组织

### 前端目录

#### `frontend/` - 前端应用根目录

采用 Vue 3 + Element Plus 技术栈：

1. **src/api/** - API 接口层
   - 封装所有后端 API 调用
   - 使用 Axios 进行 HTTP 请求

2. **src/views/** - 页面组件
   - 按角色组织页面
   - 每个角色有独立的功能页面

3. **src/stores/** - 状态管理
   - 使用 Pinia 管理全局状态
   - 用户信息、登录状态等

4. **src/router/** - 路由配置
   - Vue Router 路由定义
   - 路由守卫（权限控制）

5. **src/layouts/** - 布局组件
   - 主布局（侧边栏+顶栏）
   - 可复用的布局组件

6. **src/utils/** - 工具函数
   - Axios 请求封装
   - 常量定义
   - 通用工具函数

### 文档目录

#### `docs/` - 项目文档

所有文档集中在此目录：

- **API.md**: REST API 接口文档
- **BACKEND.md**: 后端开发指南
- **FRONTEND.md**: 前端开发指南
- **DATABASE.md**: 数据库模型文档
- **PROJECT_STRUCTURE.md**: 项目结构说明

---

## 🔄 数据流转

### 请求处理流程

```
前端页面
    ↓ (用户操作)
前端 API 层 (src/api/)
    ↓ (HTTP 请求)
后端路由层 (app/routes/)
    ↓ (认证检查)
认证中间件 (app/auth/dependencies.py)
    ↓ (业务处理)
业务逻辑层 (app/services/)
    ↓ (数据操作)
数据模型层 (app/models/)
    ↓ (SQL)
数据库 (data/app.db)
```

### 审核流程

```
积极分子提交报告
    ↓ (POST /api/reports)
保存到数据库 (Report 表)
    ↓ (current_step = trainer)
培养人审核
    ↓ (POST /api/reports/{id}/review)
创建审核记录 (Review 表)
    ↓ (status = approved)
更新报告状态 (current_step = organizer)
    ↓
组织委员审核
    ↓
支部书记审核
    ↓
最终审核
    ↓ (status = approved)
审核完成
```

---

## 🗂️ 文件类型说明

### Python 文件

- **`.py`**: Python 源代码文件
- **`__init__.py`**: Python 包标识文件

### JavaScript/Vue 文件

- **`.js`**: JavaScript 源代码文件
- **`.vue`**: Vue 单文件组件
- **`.json`**: JSON 配置文件

### 配置文件

- **`requirements.txt`**: Python 依赖配置
- **`package.json`**: Node.js 依赖配置
- **`vite.config.js`**: Vite 构建配置
- **`.env`**: 环境变量配置

### 文档文件

- **`.md`**: Markdown 文档

---

## 🔍 关键文件说明

### 后端关键文件

| 文件 | 说明 | 重要性 |
|------|------|--------|
| `main.py` | 应用入口，启动服务 | ⭐⭐⭐⭐⭐ |
| `app/config.py` | 配置管理 | ⭐⭐⭐⭐⭐ |
| `app/database.py` | 数据库连接 | ⭐⭐⭐⭐⭐ |
| `app/services/report_service.py` | 审核核心逻辑 | ⭐⭐⭐⭐⭐ |
| `app/routes/reports.py` | 报告 API | ⭐⭐⭐⭐ |
| `app/auth/security.py` | 认证安全 | ⭐⭐⭐⭐ |
| `init_db.py` | 数据库初始化 | ⭐⭐⭐ |

### 前端关键文件

| 文件 | 说明 | 重要性 |
|------|------|--------|
| `frontend/src/main.js` | 应用入口 | ⭐⭐⭐⭐⭐ |
| `frontend/src/router/index.js` | 路由配置 | ⭐⭐⭐⭐⭐ |
| `frontend/src/stores/user.js` | 用户状态 | ⭐⭐⭐⭐⭐ |
| `frontend/src/utils/request.js` | 请求封装 | ⭐⭐⭐⭐ |
| `frontend/src/api/report.js` | 报告 API | ⭐⭐⭐⭐ |
| `frontend/vite.config.js` | 构建配置 | ⭐⭐⭐ |

---

## 📦 模块依赖关系

### 后端模块依赖

```
main.py
  ├── app.routes.auth
  │     ├── app.auth.security
  │     └── app.models.user
  │
  └── app.routes.reports
        ├── app.services.report_service
        │     ├── app.models.report
        │     ├── app.models.review
        │     └── app.utils.workflow
        │
        └── app.auth.dependencies
              └── app.auth.security
```

### 前端模块依赖

```
main.js
  ├── App.vue
  │     └── router
  │           ├── layouts/MainLayout.vue
  │           └── views/**/*.vue
  │                 ├── api/*.js
  │                 │     └── utils/request.js
  │                 │
  │                 └── stores/user.js
  │
  └── stores (Pinia)
```

---

## 🎯 开发建议

### 添加新功能

1. **后端**:
   - 在 `app/models/` 添加数据模型
   - 在 `app/services/` 添加业务逻辑
   - 在 `app/routes/` 添加 API 端点

2. **前端**:
   - 在 `src/api/` 添加 API 调用
   - 在 `src/views/` 添加页面组件
   - 在 `src/router/` 添加路由

### 修改现有功能

1. 先查看相关文档 (`docs/`)
2. 定位到对应的文件
3. 理解现有逻辑
4. 进行修改并测试

---

## 📝 命名约定

### 后端

- **文件名**: 小写下划线 (`user_service.py`)
- **类名**: 大驼峰 (`UserService`)
- **函数名**: 小写下划线 (`get_user_by_id`)
- **常量**: 大写下划线 (`MAX_FILE_SIZE`)

### 前端

- **文件名**: 
  - 组件: 大驼峰 (`UserCard.vue`)
  - 工具: 小写短横线 (`request.js`)
- **组件名**: 大驼峰 (`UserCard`)
- **函数名**: 小驼峰 (`getUserById`)
- **常量**: 大写下划线 (`MAX_FILE_SIZE`)

---

**最后更新**: 2024-12-02  
**项目版本**: v1.0.0





























