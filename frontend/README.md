# 智能制造工艺部党总支积极分子思想汇报审核平台 - 前端

基于 Vue3 + ElementPlus + Vite 构建的现代化前端应用。

## 技术栈

- **Vue 3** - 渐进式 JavaScript 框架
- **Element Plus** - Vue 3 组件库
- **Vue Router** - 官方路由管理器
- **Pinia** - Vue 3 状态管理
- **Axios** - HTTP 客户端
- **Vite** - 下一代前端构建工具

## 快速开始

### 安装依赖

```bash
npm install
# 或
pnpm install
```

### 开发模式

```bash
npm run dev
```

访问 http://localhost:5173

### 生产构建

```bash
npm run build
```

## 项目结构

```
frontend/
├── src/
│   ├── api/              # API 接口定义
│   ├── assets/           # 静态资源
│   ├── components/       # 公共组件
│   ├── layouts/          # 布局组件
│   ├── router/           # 路由配置
│   ├── stores/           # Pinia 状态管理
│   ├── utils/            # 工具函数
│   ├── views/            # 页面组件
│   ├── App.vue           # 根组件
│   └── main.js           # 应用入口
├── index.html            # HTML 入口
├── vite.config.js        # Vite 配置
└── package.json          # 项目配置
```

## 功能特性

- ✅ JWT Token 身份认证
- ✅ 基于角色的权限控制
- ✅ 路由守卫
- ✅ Axios 请求拦截器（自动携带 Token）
- ✅ 响应式布局
- ✅ Element Plus 组件按需导入

## 角色权限

| 角色 | 说明 | 功能 |
|------|------|------|
| activist | 编制人（积极分子） | 提交思想汇报 |
| trainer | 培养人 | 审核第一级 |
| organizer | 组织委员 | 审核第二级 |
| secretary | 支部书记 | 审核第三级 |
| final | 总支书记 | 总览所有汇报 |

## 默认账号

开发环境可使用以下测试账号：

| 用户名 | 密码 | 角色 |
|--------|------|------|
| activist1 | 123456 | 编制人 |
| trainer1 | 123456 | 培养人 |
| organizer1 | 123456 | 组织委员 |
| secretary1 | 123456 | 支部书记 |
| final1 | 123456 | 总支书记 |




















