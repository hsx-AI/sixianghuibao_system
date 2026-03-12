import { createRouter, createWebHistory } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { ElMessage } from 'element-plus'
import { ROLES } from '@/utils/constants'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/Login.vue'),
    meta: { requiresAuth: false }
  },
  {
    path: '/',
    component: () => import('@/layouts/MainLayout.vue'),
    redirect: '/dashboard',
    meta: { requiresAuth: true },
    children: [
      // 编制人（积极分子）- 提交页面
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: () => import('@/views/Dashboard.vue'),
        meta: { 
          requiresAuth: true,
          title: '首页'
        }
      },
      {
        path: 'submit',
        name: 'Submit',
        component: () => import('@/views/activist/Submit.vue'),
        meta: { 
          requiresAuth: true,
          roles: [ROLES.ACTIVIST],
          title: '提交思想汇报'
        }
      },
      // 培养人审核页面
      {
        path: 'pyr-review',
        name: 'PyrReview',
        component: () => import('@/views/trainer/Review.vue'),
        meta: { 
          requiresAuth: true,
          roles: [ROLES.PYR, ROLES.ZZWY, ROLES.ZBSJ],
          title: '培养人审核'
        }
      },
      // 组织委员审核页面
      {
        path: 'zzwy-review',
        name: 'ZzwyReview',
        component: () => import('@/views/organizer/Review.vue'),
        meta: { 
          requiresAuth: true,
          roles: [ROLES.ZZWY],
          title: '组织委员审核'
        }
      },
      // 组织委员总览页面
      {
        path: 'zzwy-overview',
        name: 'ZzwyOverview',
        component: () => import('@/views/organizer/Overview.vue'),
        meta: { 
          requiresAuth: true,
          roles: [ROLES.ZZWY],
          title: '组织委员总览'
        }
      },
      // 组织委员审阅页面
      {
        path: 'zzwy-review-reports',
        name: 'ZzwyReviewReports',
        component: () => import('@/views/organizer/ReviewReports.vue'),
        meta: { 
          requiresAuth: true,
          roles: [ROLES.ZZWY],
          title: '思想汇报审阅'
        }
      },
      // 组织委员组织架构页面
      {
        path: 'zzwy-organization',
        name: 'ZzwyOrganization',
        component: () => import('@/views/organizer/Organization.vue'),
        meta: { 
          requiresAuth: true,
          roles: [ROLES.ZZWY],
          title: '支部组织架构'
        }
      },
      // 支部书记审核页面
      {
        path: 'zbsj-review',
        name: 'ZbsjReview',
        component: () => import('@/views/secretary/Review.vue'),
        meta: { 
          requiresAuth: true,
          roles: [ROLES.ZBSJ],
          title: '支部书记审核'
        }
      },
      // 支部书记总览页面
      {
        path: 'zbsj-overview',
        name: 'ZbsjOverview',
        component: () => import('@/views/secretary/Overview.vue'),
        meta: { 
          requiresAuth: true,
          roles: [ROLES.ZBSJ],
          title: '支部书记总览'
        }
      },
      // 支部书记审阅页面
      {
        path: 'zbsj-review-reports',
        name: 'ZbsjReviewReports',
        component: () => import('@/views/secretary/ReviewReports.vue'),
        meta: { 
          requiresAuth: true,
          roles: [ROLES.ZBSJ],
          title: '思想汇报审阅'
        }
      },
      // 支部书记组织架构页面
      {
        path: 'zbsj-organization',
        name: 'ZbsjOrganization',
        component: () => import('@/views/organizer/Organization.vue'),
        meta: { 
          requiresAuth: true,
          roles: [ROLES.ZBSJ],
          title: '支部组织架构'
        }
      },
      // 党总支总览页面
      {
        path: 'zzs-overview',
        name: 'ZzsOverview',
        component: () => import('@/views/final/Overview.vue'),
        meta: { 
          requiresAuth: true,
          roles: [ROLES.ZZS],
          title: '党总支总览'
        }
      },
      // 党总支审阅页面
      {
        path: 'zzs-review',
        name: 'ZzsReview',
        component: () => import('@/views/final/ReviewReports.vue'),
        meta: { 
          requiresAuth: true,
          roles: [ROLES.ZZS],
          title: '思想汇报审阅'
        }
      },
      // 党总支组织架构页面
      {
        path: 'zzs-organization',
        name: 'ZzsOrganization',
        component: () => import('@/views/final/Organization.vue'),
        meta: { 
          requiresAuth: true,
          roles: [ROLES.ZZS],
          title: '组织架构'
        }
      },
      // 管理员人员管理页面
      {
        path: 'admin-users',
        name: 'AdminUsers',
        component: () => import('@/views/admin/UserManagement.vue'),
        meta: { 
          requiresAuth: true,
          roles: [ROLES.ADMIN],
          title: '人员管理'
        }
      },
      // 管理员文件管理页面
      {
        path: 'admin-reports',
        name: 'AdminReports',
        component: () => import('@/views/admin/ReportManagement.vue'),
        meta: { 
          requiresAuth: true,
          roles: [ROLES.ADMIN],
          title: '文件管理'
        }
      },
      // 管理员意见反馈页面
      {
        path: 'admin-feedback',
        name: 'AdminFeedback',
        component: () => import('@/views/admin/FeedbackManagement.vue'),
        meta: { 
          requiresAuth: true,
          roles: [ROLES.ADMIN],
          title: '意见反馈'
        }
      }
    ]
  },
  {
    path: '/:pathMatch(.*)*',
    redirect: '/'
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守卫
router.beforeEach(async (to, from, next) => {
  const userStore = useUserStore()
  
  // 设置页面标题
  document.title = to.meta.title ? `${to.meta.title} - 智能制造工艺部党总支积极分子思想汇报审核平台` : '智能制造工艺部党总支积极分子思想汇报审核平台'
  
  // 检查是否需要登录
  if (to.meta.requiresAuth) {
    if (!userStore.isLoggedIn) {
      ElMessage.warning('请先登录')
      next('/login')
      return
    }
    
    // 如果还没有用户信息，先获取
    if (!userStore.userInfo) {
      try {
        await userStore.getUserInfo()
      } catch (error) {
        next('/login')
        return
      }
    }
    
    // 检查角色权限
    if (to.meta.roles && to.meta.roles.length > 0) {
      if (!userStore.hasAnyRole(to.meta.roles)) {
        ElMessage.error('没有权限访问该页面')
        next(from.path || '/')
        return
      }
    }
  }
  
  // 已登录用户访问登录页，重定向到首页
  if (to.path === '/login' && userStore.isLoggedIn) {
    next('/')
    return
  }
  
  next()
})

export default router














