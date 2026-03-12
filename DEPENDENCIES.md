# 项目依赖说明

本项目采用前后端分离架构，前端和后端有各自独立的依赖配置。

## 📦 后端依赖

**配置文件**: `requirements.txt`

**Python 版本要求**: 3.8+

### 核心依赖

| 包名 | 版本 | 用途 |
|------|------|------|
| fastapi | 0.123.0 | Web 框架，提供 REST API |
| uvicorn | 0.38.0 | ASGI 服务器，运行 FastAPI 应用 |
| sqlmodel | 0.0.27 | ORM 框架，数据库操作 |
| sqlalchemy | 2.0.44 | SQL 工具包（SQLModel 依赖） |

### 认证与安全

| 包名 | 版本 | 用途 |
|------|------|------|
| python-jose | 3.5.0 | JWT Token 生成与验证 |
| passlib | 1.7.4 | 密码哈希（bcrypt） |
| python-multipart | 0.0.20 | 文件上传支持 |

### 配置管理

| 包名 | 版本 | 用途 |
|------|------|------|
| pydantic-settings | 2.12.0 | 配置管理 |
| python-dotenv | 1.2.1 | 环境变量支持 |
| pydantic | 2.12.5 | 数据验证 |

### 安装后端依赖

```bash
# 使用 pip 安装
pip install -r requirements.txt

# 或使用 conda（推荐）
conda create -n sixianghuibao python=3.10
conda activate sixianghuibao
pip install -r requirements.txt
```

### 验证安装

```bash
# 检查 FastAPI 版本
python -c "import fastapi; print(fastapi.__version__)"

# 检查 SQLModel 版本
python -c "import sqlmodel; print(sqlmodel.__version__)"
```

---

## 🎨 前端依赖

**配置文件**: `frontend/package.json`

**Node.js 版本要求**: 16+

### 核心依赖

| 包名 | 版本 | 用途 |
|------|------|------|
| vue | ^3.4.21 | 前端框架 |
| vue-router | ^4.3.0 | 路由管理 |
| pinia | ^2.1.7 | 状态管理 |
| element-plus | ^2.6.2 | UI 组件库 |
| @element-plus/icons-vue | ^2.3.1 | 图标库 |
| axios | ^1.6.7 | HTTP 客户端 |

### 开发依赖

| 包名 | 版本 | 用途 |
|------|------|------|
| vite | ^5.2.0 | 构建工具 |
| @vitejs/plugin-vue | ^5.0.4 | Vue 3 插件 |
| unplugin-auto-import | ^0.17.5 | 自动导入 |
| unplugin-vue-components | ^0.26.0 | 组件自动导入 |

### 安装前端依赖

```bash
cd frontend

# 使用 npm
npm install

# 或使用 yarn
yarn install

# 或使用 pnpm（推荐）
pnpm install
```

### 验证安装

```bash
# 检查 Vue 版本
npm list vue

# 检查 Element Plus 版本
npm list element-plus
```

---

## 🔄 依赖更新

### 后端依赖更新

```bash
# 查看过期的包
pip list --outdated

# 更新所有包到最新版本
pip install --upgrade -r requirements.txt

# 更新单个包
pip install --upgrade fastapi

# 导出当前环境的依赖
pip freeze > requirements-lock.txt
```

### 前端依赖更新

```bash
cd frontend

# 查看过期的包
npm outdated

# 更新所有包到最新版本
npm update

# 更新单个包
npm install vue@latest

# 检查安全漏洞
npm audit

# 修复安全漏洞
npm audit fix
```

---

## 🐳 Docker 部署依赖

### 后端 Dockerfile

```dockerfile
FROM python:3.10-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# 安装 Python 依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . .

# 暴露端口
EXPOSE 8000

# 启动应用
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 前端 Dockerfile

```dockerfile
# 构建阶段
FROM node:18-alpine as build

WORKDIR /app

# 安装依赖
COPY frontend/package*.json ./
RUN npm ci

# 构建应用
COPY frontend/ ./
RUN npm run build

# 生产阶段
FROM nginx:alpine

# 复制构建产物
COPY --from=build /app/dist /usr/share/nginx/html

# 复制 Nginx 配置
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
```

### docker-compose.yml

```yaml
version: '3.8'

services:
  backend:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - ./data:/app/data
    environment:
      - DATABASE_URL=sqlite:///data/app.db
      - SECRET_KEY=your-secret-key
  
  frontend:
    build:
      context: .
      dockerfile: frontend/Dockerfile
    ports:
      - "80:80"
    depends_on:
      - backend
```

---

## ⚠️ 常见问题

### 后端问题

**Q: 安装 passlib[bcrypt] 失败**

A: 需要安装编译工具：
```bash
# Ubuntu/Debian
sudo apt-get install build-essential python3-dev

# CentOS/RHEL
sudo yum install gcc python3-devel

# macOS
xcode-select --install

# Windows
# 下载并安装 Microsoft C++ Build Tools
```

**Q: SQLite 版本过低**

A: 升级 SQLite 或使用 PostgreSQL：
```bash
# 使用 PostgreSQL
pip install psycopg2-binary
# 修改 config.py 中的 DATABASE_URL
```

### 前端问题

**Q: npm install 很慢**

A: 使用国内镜像：
```bash
# 使用淘宝镜像
npm config set registry https://registry.npmmirror.com

# 或使用 cnpm
npm install -g cnpm --registry=https://registry.npmmirror.com
cnpm install
```

**Q: Vite 启动失败**

A: 清理缓存：
```bash
rm -rf node_modules
rm package-lock.json
npm install
```

---

## 📊 依赖分析

### 后端依赖大小

```bash
# 安装 pipdeptree 查看依赖树
pip install pipdeptree
pipdeptree -p fastapi
```

### 前端依赖大小

```bash
# 安装 npm-check
npm install -g npm-check

# 检查依赖
cd frontend
npm-check

# 分析构建产物大小
npm run build
npx vite-bundle-visualizer
```

---

## 🔒 安全建议

1. **定期更新依赖**: 每月检查一次依赖更新
2. **检查安全漏洞**: 使用 `npm audit` 和 `pip check`
3. **锁定版本**: 生产环境使用精确版本号
4. **最小化依赖**: 只安装必要的包
5. **使用虚拟环境**: 后端使用 venv/conda，前端使用独立项目

---

## 📝 版本兼容性

### Python 版本

- **推荐**: Python 3.10
- **最低**: Python 3.8
- **最高**: Python 3.12

### Node.js 版本

- **推荐**: Node.js 18 LTS
- **最低**: Node.js 16
- **最高**: Node.js 20

---

**最后更新**: 2024-12-02  
**文档版本**: v1.0.0



















