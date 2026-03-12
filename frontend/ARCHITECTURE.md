# 前端架构说明

## 技术栈

- **Vue 3** - 使用 Composition API
- **Element Plus** - UI 组件库
- **Vue Router** - 路由管理
- **Pinia** - 状态管理
- **Axios** - HTTP 客户端
- **Vite** - 构建工具

## 核心功能

### 1. 身份认证与授权

#### Token 管理
- 使用 JWT Token 进行身份认证
- Token 存储在 localStorage
- Axios 请求拦截器自动携带 Token

```javascript
// src/utils/request.js
request.interceptors.request.use(config => {
  const userStore = useUserStore()
  if (userStore.token) {
    config.headers.Authorization = `Bearer ${userStore.token}`
  }
  return config
})
```

#### 角色权限控制
- 基于角色的访问控制 (RBAC)
- 路由级别权限控制
- 组件级别权限控制

```javascript
// 路由权限配置
{
  path: '/submit',
  meta: { 
    requiresAuth: true,
    roles: [ROLES.ACTIVIST]  // 只有编制人可以访问
  }
}
```

### 2. 状态管理

使用 Pinia 管理全局状态：

#### User Store
- 用户信息
- 登录状态
- Token 管理
- 权限检查

```javascript
// src/stores/user.js
export const useUserStore = defineStore('user', {
  state: () => ({
    token: localStorage.getItem('token') || '',
    userInfo: null
  }),
  getters: {
    isLoggedIn: (state) => !!state.token,
    role: (state) => state.userInfo?.role
  },
  actions: {
    async login(username, password) { ... },
    async getUserInfo() { ... },
    logout() { ... }
  }
})
```

### 3. 路由设计

#### 路由结构
```
/
├── /login              # 登录页（无需认证）
└── /                   # 主布局（需要认证）
    ├── /dashboard      # 首页
    ├── /submit         # 编制人提交页面
    ├── /trainer-review # 培养人审核页面
    ├── /organizer-review # 组织委员审核页面
    ├── /secretary-review # 支部书记审核页面
    └── /final-overview # 总支书记总览页面
```

#### 路由守卫
```javascript
router.beforeEach(async (to, from, next) => {
  // 1. 检查是否需要登录
  // 2. 验证 Token 有效性
  // 3. 检查角色权限
  // 4. 处理重定向
})
```

### 4. API 封装

#### 请求拦截器
- 自动添加 Token
- 统一错误处理
- Loading 状态管理

#### 响应拦截器
- 401: 自动跳转登录
- 403: 权限不足提示
- 500: 服务器错误提示

```javascript
// src/utils/request.js
request.interceptors.response.use(
  response => response.data,
  error => {
    if (error.response?.status === 401) {
      // 自动登出并跳转登录页
      userStore.logout()
      router.push('/login')
    }
    return Promise.reject(error)
  }
)
```

### 5. 页面组件设计

#### 编制人（Activist）
- **提交页面**: 上传 Word 文档
- **历史记录**: 查看自己提交的汇报

#### 审核人员（Trainer/Organizer/Secretary）
- **审核列表**: 显示待审核的汇报
- **搜索过滤**: 按期间、标题筛选
- **审核操作**: 通过/驳回，填写审核意见
- **查看详情**: 查看汇报信息，下载文档

#### 总支书记（Final）
- **统计看板**: 汇报总数、待审核、已通过、已驳回
- **全局视图**: 查看所有汇报
- **高级筛选**: 按状态、期间、标题筛选
- **最终审核**: 对进入最终步骤的汇报进行审核

## 审核流程

```
1. 编制人提交汇报
   ↓ (current_step: trainer, status: pending)
   
2. 培养人审核
   ↓ 通过 → (current_step: organizer, status: pending)
   ↓ 驳回 → (current_step: trainer, status: rejected)
   
3. 组织委员审核
   ↓ 通过 → (current_step: secretary, status: pending)
   ↓ 驳回 → (current_step: organizer, status: rejected)
   
4. 支部书记审核
   ↓ 通过 → (current_step: final, status: pending)
   ↓ 驳回 → (current_step: secretary, status: rejected)
   
5. 总支书记审核
   ↓ 通过 → (status: approved)
   ↓ 驳回 → (status: rejected)
```

## 组件复用

### 审核页面组件模式
培养人、组织委员、支部书记的审核页面使用相同的模式：

1. **搜索栏**: 期间、标题搜索
2. **数据表格**: 显示待审核列表
3. **操作按钮**: 查看、通过、驳回
4. **审核对话框**: 填写审核意见
5. **详情对话框**: 查看汇报详情

### 可优化方向
- 提取通用审核组件
- 使用 Composables 复用逻辑
- 统一表格列配置

## 样式设计

### 布局
- **侧边栏**: 导航菜单，可折叠
- **顶部栏**: 面包屑、用户信息、退出按钮
- **内容区**: 卡片式布局，响应式设计

### 主题
- 主色调: #409eff（Element Plus 默认蓝）
- 渐变背景: 登录页使用紫色渐变
- 卡片阴影: 悬停时提升效果

### 响应式
- 使用 Grid 布局适配不同屏幕
- 移动端优化（表格横向滚动）
- 统计卡片自适应排列

## 错误处理

### 表单验证
```javascript
const rules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' }
  ]
}
```

### 网络错误
- 自动重试机制（可选）
- 友好的错误提示
- 网络断开检测

### 异常捕获
```javascript
try {
  await uploadReport(data)
  ElMessage.success('提交成功')
} catch (error) {
  console.error('提交失败:', error)
  // axios 拦截器已经显示了错误提示
}
```

## 性能优化

### 代码分割
- 路由懒加载
- Element Plus 按需导入

### 打包优化
```javascript
// vite.config.js
build: {
  rollupOptions: {
    output: {
      manualChunks: {
        'element-plus': ['element-plus'],
        'icons': ['@element-plus/icons-vue']
      }
    }
  }
}
```

### 加载优化
- 表格数据分页（待实现）
- 虚拟滚动（大数据量时）
- 图片懒加载

## 安全措施

### XSS 防护
- Vue 自动转义 HTML
- 不使用 v-html（除非必要）

### CSRF 防护
- Token 机制

### 敏感信息
- 密码不存储在前端
- Token 存储使用 localStorage（可升级为 httpOnly Cookie）

## 浏览器兼容性

- Chrome >= 87
- Firefox >= 78
- Safari >= 14
- Edge >= 88

不支持 IE11

## 部署建议

### 环境变量
- `.env.development`: 开发环境
- `.env.production`: 生产环境

### Nginx 配置要点
1. SPA 路由配置（try_files）
2. API 代理配置
3. Gzip 压缩
4. 静态资源缓存

### Docker 部署
```dockerfile
FROM node:18-alpine as build
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
```

## 扩展功能建议

1. **分页**: 表格数据分页加载
2. **导出**: 导出汇报统计数据（Excel）
3. **通知**: 审核状态变更通知
4. **历史记录**: 查看审核历史记录
5. **批量操作**: 批量审核、批量下载
6. **数据可视化**: 图表展示统计数据
7. **搜索增强**: 全文搜索
8. **文件预览**: 在线预览 Word 文档
9. **多语言**: i18n 国际化支持
10. **暗黑模式**: 支持深色主题

## 维护与更新

### 依赖更新
```bash
# 检查过期依赖
npm outdated

# 更新依赖
npm update
```

### 代码质量
- 使用 ESLint 进行代码检查
- 使用 Prettier 统一代码风格
- 编写单元测试（Vitest）

### 文档维护
- 及时更新 API 文档
- 记录重要变更
- 编写组件使用说明





























