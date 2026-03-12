# 前端开发指南

本文档详细说明思想汇报管理系统前端的架构设计和开发指南。

## 🏗️ 技术栈

- **框架**: Vue 3.4+ (Composition API)
- **UI 组件库**: Element Plus 2.6+
- **路由管理**: Vue Router 4.3+
- **状态管理**: Pinia 2.1+
- **HTTP 客户端**: Axios 1.6+
- **构建工具**: Vite 5.2+
- **图标**: @element-plus/icons-vue

## 📁 项目结构

```
frontend/
├── public/                     # 静态资源
│   └── logo.svg               # Logo 图标
│
├── src/
│   ├── api/                    # API 接口层
│   │   ├── auth.js            # 认证 API
│   │   └── report.js          # 报告 API
│   │
│   ├── assets/                 # 资源文件
│   │
│   ├── layouts/                # 布局组件
│   │   └── MainLayout.vue     # 主布局（侧边栏+顶栏）
│   │
│   ├── router/                 # 路由配置
│   │   └── index.js           # 路由定义与权限控制
│   │
│   ├── stores/                 # Pinia 状态管理
│   │   └── user.js            # 用户状态（登录、权限）
│   │
│   ├── utils/                  # 工具函数
│   │   ├── constants.js       # 常量定义
│   │   └── request.js         # Axios 封装
│   │
│   ├── views/                  # 页面组件
│   │   ├── Login.vue          # 登录页
│   │   ├── Dashboard.vue      # 首页
│   │   │
│   │   ├── activist/          # 积极分子页面
│   │   │   └── Submit.vue     # 提交汇报
│   │   │
│   │   ├── trainer/           # 培养人页面
│   │   │   └── Review.vue     # 审核页面
│   │   │
│   │   ├── organizer/         # 组织委员页面
│   │   │   └── Review.vue     # 审核页面
│   │   │
│   │   ├── secretary/         # 支部书记页面
│   │   │   └── Review.vue     # 审核页面
│   │   │
│   │   └── final/             # 总支书记页面
│   │       └── Overview.vue   # 总览页面
│   │
│   ├── App.vue                 # 根组件
│   └── main.js                 # 应用入口
│
├── index.html                  # HTML 入口
├── vite.config.js             # Vite 配置
├── package.json               # 依赖配置
└── README.md                  # 项目说明
```

## 🚀 快速开始

### 安装依赖

```bash
cd frontend
npm install
```

### 开发模式

```bash
npm run dev
```

访问：http://localhost:5173

### 生产构建

```bash
npm run build
```

构建产物在 `dist/` 目录。

### 预览生产构建

```bash
npm run preview
```

---

## 🔐 认证与授权

### 1. Axios 请求封装

**文件**: `src/utils/request.js`

```javascript
import axios from 'axios'
import { ElMessage } from 'element-plus'
import router from '@/router'

const request = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api',
  timeout: 10000
})

// 请求拦截器：添加 Token
request.interceptors.request.use(
  config => {
    const token = localStorage.getItem('access_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  error => {
    return Promise.reject(error)
  }
)

// 响应拦截器：处理错误
request.interceptors.response.use(
  response => response.data,
  error => {
    if (error.response?.status === 401) {
      // Token 失效，跳转到登录页
      localStorage.removeItem('access_token')
      router.push('/login')
      ElMessage.error('登录已过期，请重新登录')
    } else {
      ElMessage.error(error.response?.data?.detail || '请求失败')
    }
    return Promise.reject(error)
  }
)

export default request
```

### 2. 用户状态管理

**文件**: `src/stores/user.js`

```javascript
import { defineStore } from 'pinia'
import { login as loginApi, getCurrentUser } from '@/api/auth'
import router from '@/router'

export const useUserStore = defineStore('user', {
  state: () => ({
    token: localStorage.getItem('access_token') || '',
    userInfo: null,
    isLoggedIn: false
  }),
  
  getters: {
    role: (state) => state.userInfo?.role || '',
    username: (state) => state.userInfo?.username || '',
    realName: (state) => state.userInfo?.real_name || ''
  },
  
  actions: {
    // 登录
    async login(username, password) {
      try {
        const data = await loginApi(username, password)
        this.token = data.access_token
        localStorage.setItem('access_token', data.access_token)
        
        // 获取用户信息
        await this.fetchUserInfo()
        
        this.isLoggedIn = true
        return true
      } catch (error) {
        return false
      }
    },
    
    // 获取用户信息
    async fetchUserInfo() {
      try {
        const data = await getCurrentUser()
        this.userInfo = data
      } catch (error) {
        this.logout()
      }
    },
    
    // 登出
    logout() {
      this.token = ''
      this.userInfo = null
      this.isLoggedIn = false
      localStorage.removeItem('access_token')
      router.push('/login')
    }
  }
})
```

### 3. 路由守卫

**文件**: `src/router/index.js`

```javascript
import { createRouter, createWebHistory } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { ROLES } from '@/utils/constants'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/Login.vue'),
    meta: { title: '登录' }
  },
  {
    path: '/',
    component: () => import('@/layouts/MainLayout.vue'),
    meta: { requiresAuth: true },
    children: [
      {
        path: '',
        name: 'Dashboard',
        component: () => import('@/views/Dashboard.vue'),
        meta: { title: '首页' }
      },
      {
        path: 'submit',
        name: 'Submit',
        component: () => import('@/views/activist/Submit.vue'),
        meta: { 
          title: '提交汇报',
          roles: [ROLES.ACTIVIST]
        }
      },
      {
        path: 'trainer-review',
        name: 'TrainerReview',
        component: () => import('@/views/trainer/Review.vue'),
        meta: { 
          title: '培养人审核',
          roles: [ROLES.TRAINER]
        }
      },
      // ... 其他路由
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 全局前置守卫
router.beforeEach(async (to, from, next) => {
  const userStore = useUserStore()
  
  // 设置页面标题
  document.title = to.meta.title || '思想汇报管理系统'
  
  // 检查是否需要认证
  if (to.meta.requiresAuth) {
    if (!userStore.token) {
      next('/login')
      return
    }
    
    // 获取用户信息
    if (!userStore.userInfo) {
      await userStore.fetchUserInfo()
    }
    
    // 检查角色权限
    if (to.meta.roles && !to.meta.roles.includes(userStore.role)) {
      ElMessage.error('无权限访问该页面')
      next('/')
      return
    }
  }
  
  next()
})

export default router
```

---

## 🎨 核心页面实现

### 1. 登录页面

**文件**: `src/views/Login.vue`

```vue
<template>
  <div class="login-container">
    <el-card class="login-card">
      <h2>思想汇报管理系统</h2>
      <el-form :model="form" :rules="rules" ref="formRef">
        <el-form-item prop="username">
          <el-input
            v-model="form.username"
            placeholder="用户名"
            prefix-icon="User"
          />
        </el-form-item>
        <el-form-item prop="password">
          <el-input
            v-model="form.password"
            type="password"
            placeholder="密码"
            prefix-icon="Lock"
            @keyup.enter="handleLogin"
          />
        </el-form-item>
        <el-button
          type="primary"
          @click="handleLogin"
          :loading="loading"
          style="width: 100%"
        >
          登录
        </el-button>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { ElMessage } from 'element-plus'

const router = useRouter()
const userStore = useUserStore()
const formRef = ref(null)
const loading = ref(false)

const form = ref({
  username: '',
  password: ''
})

const rules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }]
}

const handleLogin = async () => {
  await formRef.value.validate()
  loading.value = true
  
  try {
    const success = await userStore.login(form.value.username, form.value.password)
    if (success) {
      ElMessage.success('登录成功')
      router.push('/')
    } else {
      ElMessage.error('用户名或密码错误')
    }
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.login-card {
  width: 400px;
  padding: 20px;
}

h2 {
  text-align: center;
  margin-bottom: 30px;
}
</style>
```

### 2. 审核页面

**文件**: `src/views/trainer/Review.vue`

```vue
<template>
  <div>
    <el-card>
      <template #header>
        <span>待审核报告列表</span>
        <el-button
          type="primary"
          @click="fetchPendingReports"
          :icon="Refresh"
          style="float: right"
        >
          刷新
        </el-button>
      </template>
      
      <el-table :data="reports" v-loading="loading">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column label="提交人" width="120">
          <template #default="{ row }">
            {{ row.author?.real_name }}
          </template>
        </el-table-column>
        <el-table-column label="时间" width="150">
          <template #default="{ row }">
            {{ row.year }}年{{ row.month }}月
          </template>
        </el-table-column>
        <el-table-column label="上传时间" width="180">
          <template #default="{ row }">
            {{ formatDate(row.uploaded_time) }}
          </template>
        </el-table-column>
        <el-table-column label="当前步骤">
          <template #default="{ row }">
            <el-tag>{{ STEP_NAMES[row.current_step] }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="220">
          <template #default="{ row }">
            <el-button
              type="success"
              size="small"
              @click="handleReview(row, 'approved')"
            >
              通过
            </el-button>
            <el-button
              type="danger"
              size="small"
              @click="handleReview(row, 'rejected')"
            >
              退回
            </el-button>
            <el-button
              type="info"
              size="small"
              @click="handleDownload(row)"
            >
              下载
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
    
    <!-- 审核对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="500px"
    >
      <el-form :model="reviewForm">
        <el-form-item label="审核意见">
          <el-input
            v-model="reviewForm.comment"
            type="textarea"
            :rows="4"
            placeholder="请输入审核意见（选填）"
          />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button
          type="primary"
          @click="submitReview"
          :loading="submitting"
        >
          确定
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Refresh } from '@element-plus/icons-vue'
import { getPendingReports, reviewReport, downloadReport } from '@/api/report'
import { STEP_NAMES } from '@/utils/constants'

const loading = ref(false)
const reports = ref([])
const dialogVisible = ref(false)
const dialogTitle = ref('')
const submitting = ref(false)

const reviewForm = ref({
  reportId: null,
  status: '',
  comment: ''
})

// 获取待审核报告
const fetchPendingReports = async () => {
  loading.value = true
  try {
    reports.value = await getPendingReports()
  } catch (error) {
    ElMessage.error('获取报告列表失败')
  } finally {
    loading.value = false
  }
}

// 处理审核
const handleReview = async (report, status) => {
  dialogVisible.value = true
  dialogTitle.value = status === 'approved' ? '审核通过' : '退回报告'
  reviewForm.value = {
    reportId: report.id,
    status,
    comment: ''
  }
}

// 提交审核
const submitReview = async () => {
  submitting.value = true
  try {
    const result = await reviewReport(
      reviewForm.value.reportId,
      reviewForm.value.status,
      reviewForm.value.comment
    )
    
    ElMessage.success(result.message)
    dialogVisible.value = false
    fetchPendingReports()
  } catch (error) {
    ElMessage.error('审核失败')
  } finally {
    submitting.value = false
  }
}

// 下载报告
const handleDownload = async (report) => {
  try {
    await downloadReport(report.id)
  } catch (error) {
    ElMessage.error('下载失败')
  }
}

// 格式化日期
const formatDate = (dateStr) => {
  return new Date(dateStr).toLocaleString('zh-CN')
}

onMounted(() => {
  fetchPendingReports()
})
</script>
```

---

## 🔌 API 接口层

### 认证 API

**文件**: `src/api/auth.js`

```javascript
import request from '@/utils/request'

// 登录
export function login(username, password) {
  const formData = new URLSearchParams()
  formData.append('username', username)
  formData.append('password', password)
  
  return request({
    url: '/auth/token',
    method: 'post',
    data: formData,
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded'
    }
  })
}

// 获取当前用户信息
export function getCurrentUser() {
  return request({
    url: '/auth/me',
    method: 'get'
  })
}
```

### 报告 API

**文件**: `src/api/report.js`

```javascript
import request from '@/utils/request'

// 提交报告
export function submitReport(data) {
  const formData = new FormData()
  formData.append('year', data.year)
  formData.append('month', data.month)
  formData.append('file', data.file)
  
  return request({
    url: '/reports',
    method: 'post',
    data: formData,
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}

// 获取待审核报告
export function getPendingReports() {
  return request({
    url: '/reports/pending/list',
    method: 'get'
  })
}

// 审核报告
export function reviewReport(reportId, status, comment) {
  return request({
    url: `/reports/${reportId}/review`,
    method: 'post',
    data: { status, comment }
  })
}

// 下载报告
export function downloadReport(reportId) {
  return request({
    url: `/reports/${reportId}/download`,
    method: 'get',
    responseType: 'blob'
  }).then(blob => {
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `report_${reportId}.pdf`
    link.click()
    window.URL.revokeObjectURL(url)
  })
}

// 获取我的报告列表
export function getMyReports(params) {
  return request({
    url: '/reports/my/list',
    method: 'get',
    params
  })
}

// 获取审核记录
export function getReviewHistory(reportId) {
  return request({
    url: `/reports/${reportId}/reviews`,
    method: 'get'
  })
}
```

---

## 📚 最佳实践

### 1. 组件化开发

```vue
<!-- 创建可复用组件 -->
<template>
  <el-card class="report-card">
    <slot></slot>
  </el-card>
</template>
```

### 2. 使用 Composition API

```javascript
import { ref, computed, watch, onMounted } from 'vue'

export default {
  setup() {
    const count = ref(0)
    const double = computed(() => count.value * 2)
    
    watch(count, (newVal) => {
      console.log(`count changed to ${newVal}`)
    })
    
    onMounted(() => {
      console.log('Component mounted')
    })
    
    return { count, double }
  }
}
```

### 3. 环境变量

创建 `.env.development` 和 `.env.production`:

```bash
# .env.development
VITE_API_BASE_URL=http://localhost:8000/api

# .env.production
VITE_API_BASE_URL=https://api.example.com/api
```

---

## 🎨 样式规范

### 1. 使用 Scoped CSS

```vue
<style scoped>
.my-component {
  color: red;
}
</style>
```

### 2. Element Plus 主题定制

```javascript
// main.js
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'

app.use(ElementPlus, {
  size: 'default',
  zIndex: 3000
})
```

---

## 🚀 性能优化

1. **路由懒加载**: 使用 `() => import()`
2. **组件按需导入**: 使用 `unplugin-auto-import`
3. **图片懒加载**: 使用 `v-lazy`
4. **虚拟滚动**: 大列表使用 `el-virtual-list`
5. **代码分割**: Vite 自动分割

---

## 📦 部署

### Nginx 配置

```nginx
server {
    listen 80;
    server_name example.com;
    root /var/www/html;
    index index.html;
    
    location / {
        try_files $uri $uri/ /index.html;
    }
    
    location /api {
        proxy_pass http://localhost:8000;
    }
}
```

---

**最后更新**: 2024-12-02  
**前端版本**: v1.0.0





























