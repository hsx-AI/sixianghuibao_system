# 思想汇报管理系统

一个基于 FastAPI + Vue 3 的思想汇报审核管理系统，支持完整的四级审核流程。

## 🚀 快速开始

### 后端启动

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 初始化数据库
python init_db.pycd

# 3. 启动后端服务
python main.py
```

后端服务运行在：http://localhost:8000

### 前端启动

```bash
# 1. 进入前端目录
cd frontend

# 2. 安装依赖
npm install

# 3. 启动开发服务器
npm run dev
```

前端服务运行在：http://localhost:5173

## 📋 系统概述

### 审核流程

```
积极分子提交 → 培养人审核 → 组织委员审核 → 支部书记审核 → 最终审核 → 完成
```

### 用户角色

| 角色 | 英文标识 | 权限 |
|------|---------|------|
| 积极分子 | activist | 提交思想汇报 |
| 培养人 | trainer | 第一级审核 |
| 组织委员 | organizer | 第二级审核 |
| 支部书记 | secretary | 第三级审核 |
| 总支书记 | final | 最终审核 |

### 测试账号

所有账号密码均为：`123456`

| 用户名 | 角色 |
|--------|------|
| activist1 | 积极分子 |
| trainer1 | 培养人 |
| organizer1 | 组织委员 |
| secretary1 | 支部书记 |
| final1 | 总支书记 |

## 🏗️ 技术栈

### 后端
- **FastAPI** - Web 框架
- **SQLModel** - ORM（基于 SQLAlchemy + Pydantic）
- **SQLite** - 数据库
- **JWT** - 身份认证
- **Uvicorn** - ASGI 服务器

### 前端
- **Vue 3** - 渐进式框架
- **Element Plus** - UI 组件库
- **Vue Router** - 路由管理
- **Pinia** - 状态管理
- **Axios** - HTTP 客户端
- **Vite** - 构建工具

## 📁 项目结构

```
sixianghuibao/
├── app/                        # 后端应用
│   ├── auth/                   # 认证模块
│   ├── models/                 # 数据模型
│   ├── routes/                 # API 路由
│   ├── services/               # 业务逻辑
│   └── utils/                  # 工具函数
├── frontend/                   # 前端应用
│   ├── src/
│   │   ├── api/               # API 接口
│   │   ├── views/             # 页面组件
│   │   ├── stores/            # 状态管理
│   │   └── router/            # 路由配置
│   └── package.json
├── data/                       # 数据目录
│   ├── app.db                 # SQLite 数据库
│   └── reports/               # 报告文件存储
├── docs/                       # 文档目录
│   ├── API.md                 # API 文档
│   ├── BACKEND.md             # 后端开发指南
│   ├── FRONTEND.md            # 前端开发指南
│   └── DATABASE.md            # 数据库模型文档
├── requirements.txt            # Python 依赖
├── main.py                     # 后端入口
└── init_db.py                  # 数据库初始化脚本
```

## 📖 详细文档

- [API 接口文档](docs/API.md) - REST API 使用指南
- [后端开发指南](docs/BACKEND.md) - 后端架构和开发说明
- [前端开发指南](docs/FRONTEND.md) - 前端架构和组件说明
- [数据库文档](docs/DATABASE.md) - 数据模型和关系说明

## 🔧 开发指南

### 后端开发

```bash
# 激活虚拟环境（如果使用）
conda activate sixianghuibao

# 安装开发依赖
pip install -r requirements.txt

# 运行测试
python test_review_workflow.py

# 启动开发服务器（热重载）
python main.py
```

### 前端开发

```bash
cd frontend

# 安装依赖
npm install

# 开发模式（热重载）
npm run dev

# 构建生产版本
npm run build

# 预览生产构建
npm run preview
```

## 🌟 核心功能

### ✅ 已实现功能

- [x] 用户认证（JWT）
- [x] 四级审核流程
- [x] 报告上传与管理
- [x] 审核记录追踪
- [x] 退回重审机制
- [x] 角色权限控制
- [x] 报告查询与过滤
- [x] 审核历史记录
- [x] 响应式前端界面

### 🔮 未来计划

- [ ] WebSocket 实时通知
- [ ] 文件在线预览
- [ ] 批量审核操作
- [ ] 数据统计报表
- [ ] 邮件通知
- [ ] 移动端适配
- [ ] 暗黑模式
- [ ] 国际化支持

## 🧪 测试

### 后端测试

```bash
# 运行审核流程测试
python test_review_workflow.py

# 运行查询示例
python query_examples.py
```

### 前端测试

```bash
cd frontend
# TODO: 添加单元测试
```

## 🚀 部署

### 后端部署

```bash
# 使用 Uvicorn
uvicorn main:app --host 0.0.0.0 --port 8000

# 或使用 Gunicorn + Uvicorn Workers
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### 前端部署

```bash
cd frontend

# 构建生产版本
npm run build

# dist/ 目录可部署到任何静态服务器
# 推荐：Nginx, Apache, Caddy
```

### Docker 部署

```bash
# TODO: 添加 Dockerfile 和 docker-compose.yml
```

## 🤝 贡献指南

1. Fork 本项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 📝 更新日志

### v1.0.0 (2024-12-02)

- ✅ 完成基础审核流程
- ✅ 实现前后端分离架构
- ✅ 支持四级审核流程
- ✅ 完善文档和测试

## 📄 许可证

MIT License

## 👥 开发团队

- 后端开发：FastAPI + SQLModel
- 前端开发：Vue 3 + Element Plus
- AI 辅助：Claude AI Assistant

## 🙏 致谢

感谢以下开源项目：

- [FastAPI](https://fastapi.tiangolo.com/)
- [Vue.js](https://vuejs.org/)
- [Element Plus](https://element-plus.org/)
- [SQLModel](https://sqlmodel.tiangolo.com/)

## 📮 联系方式

如有问题或建议，欢迎提交 Issue。

---

**开发环境**：Python 3.8+ / Node.js 16+  
**最后更新**：2024-12-02  
**版本**：v1.0.0


