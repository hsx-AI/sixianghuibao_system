<template>
  <el-container class="layout-container">
    <!-- 侧边栏 -->
    <el-aside :width="isCollapse ? '64px' : '200px'" class="layout-aside">
      <div class="logo">
        <img v-if="!isCollapse" src="/logo.svg" alt="Logo" />
        <span v-if="!isCollapse">思想汇报</span>
      </div>

      <el-menu
        :default-active="activeMenu"
        :collapse="isCollapse"
        :unique-opened="true"
        router
      >
        <!-- 积极分子菜单 -->
        <el-menu-item v-if="hasRole(ROLES.ACTIVIST)" index="/submit">
          <el-icon><DocumentAdd /></el-icon>
          <template #title>提交汇报</template>
        </el-menu-item>

        <!-- 培养人菜单 -->
        <el-menu-item v-if="hasRole(ROLES.PYR) || hasRole(ROLES.ZZWY) || hasRole(ROLES.ZBSJ)" index="/pyr-review">
          <el-icon><Document /></el-icon>
          <template #title>培养人审核</template>
        </el-menu-item>

        <!-- 组织委员菜单 -->
        <el-menu-item v-if="hasRole(ROLES.ZZWY)" index="/zzwy-review">
          <el-icon><Checked /></el-icon>
          <template #title>组织委员审核</template>
        </el-menu-item>
        
        <el-menu-item v-if="hasRole(ROLES.ZZWY)" index="/zzwy-overview">
          <el-icon><DataAnalysis /></el-icon>
          <template #title>总览</template>
        </el-menu-item>
        
        <el-menu-item v-if="hasRole(ROLES.ZZWY)" index="/zzwy-review-reports">
          <el-icon><EditPen /></el-icon>
          <template #title>审阅</template>
        </el-menu-item>
        
        <el-menu-item v-if="hasRole(ROLES.ZZWY)" index="/zzwy-organization">
          <el-icon><Share /></el-icon>
          <template #title>组织架构</template>
        </el-menu-item>

        <!-- 支部书记菜单 -->
        <el-menu-item v-if="hasRole(ROLES.ZBSJ)" index="/zbsj-review">
          <el-icon><Stamp /></el-icon>
          <template #title>支部书记审核</template>
        </el-menu-item>
        
        <el-menu-item v-if="hasRole(ROLES.ZBSJ)" index="/zbsj-overview">
          <el-icon><DataAnalysis /></el-icon>
          <template #title>总览</template>
        </el-menu-item>
        
        <el-menu-item v-if="hasRole(ROLES.ZBSJ)" index="/zbsj-review-reports">
          <el-icon><EditPen /></el-icon>
          <template #title>审阅</template>
        </el-menu-item>
        
        <el-menu-item v-if="hasRole(ROLES.ZBSJ)" index="/zbsj-organization">
          <el-icon><Share /></el-icon>
          <template #title>组织架构</template>
        </el-menu-item>

        <!-- 党总支菜单 -->
        <el-menu-item v-if="hasRole(ROLES.ZZS)" index="/zzs-overview">
          <el-icon><DataAnalysis /></el-icon>
          <template #title>总览</template>
        </el-menu-item>
        
        <el-menu-item v-if="hasRole(ROLES.ZZS)" index="/zzs-review">
          <el-icon><EditPen /></el-icon>
          <template #title>审阅</template>
        </el-menu-item>
        
        <el-menu-item v-if="hasRole(ROLES.ZZS)" index="/zzs-organization">
          <el-icon><Share /></el-icon>
          <template #title>组织架构</template>
        </el-menu-item>

        <!-- 管理员菜单 -->
        <el-menu-item v-if="hasRole(ROLES.ADMIN)" index="/admin-users">
          <el-icon><User /></el-icon>
          <template #title>人员管理</template>
        </el-menu-item>
        
        <el-menu-item v-if="hasRole(ROLES.ADMIN)" index="/admin-reports">
          <el-icon><Folder /></el-icon>
          <template #title>文件管理</template>
        </el-menu-item>
        
        <el-menu-item v-if="hasRole(ROLES.ADMIN)" index="/admin-feedback">
          <el-icon><ChatLineRound /></el-icon>
          <template #title>意见反馈</template>
        </el-menu-item>
      </el-menu>
    </el-aside>

    <!-- 主内容区 -->
    <el-container class="layout-surface">
      <!-- 顶部导航栏 -->
      <el-header class="layout-header">
        <div class="header-left">
          <el-icon class="collapse-icon" @click="toggleCollapse">
            <component :is="isCollapse ? 'Expand' : 'Fold'" />
          </el-icon>
          <el-breadcrumb separator="/">
            <el-breadcrumb-item :to="{ path: '/' }">首页</el-breadcrumb-item>
            <el-breadcrumb-item v-if="currentRouteName">{{ currentRouteName }}</el-breadcrumb-item>
          </el-breadcrumb>
        </div>

        <div class="header-right">
          <el-tag :type="getRoleTagType(userStore.role)" effect="plain" class="role-tag">
            {{ getRoleName(userStore.role) }}
          </el-tag>

          <el-dropdown @command="handleCommand">
            <div class="user-info">
              <el-avatar :size="32" :icon="UserFilled" />
              <span class="username">{{ userStore.username }}</span>
              <el-icon><ArrowDown /></el-icon>
            </div>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="logout">
                  <el-icon><SwitchButton /></el-icon>
                  退出登录
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>

      <!-- 内容区域 -->
      <el-main class="layout-main">
        <div class="bg-bubble bubble-1" />
        <div class="bg-bubble bubble-2" />
        <router-view v-slot="{ Component }">
          <transition name="fade" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
        
        <!-- 落款 -->
        <div class="footer-credit">
          智能制造工艺部智能制造技术室能做科技团队
        </div>
      </el-main>
    </el-container>
    
    <!-- 意见反馈悬浮按钮 -->
    <div class="feedback-fab" @click="openFeedbackDialog">
      <el-tooltip content="意见反馈" placement="left">
        <el-icon :size="24"><ChatLineRound /></el-icon>
      </el-tooltip>
    </div>
    
    <!-- 意见反馈对话框 -->
    <el-dialog
      v-model="feedbackDialogVisible"
      title="意见反馈"
      width="520px"
      :close-on-click-modal="false"
    >
      <el-tabs v-model="feedbackTab">
        <el-tab-pane label="提交反馈" name="submit">
          <el-form
            ref="feedbackFormRef"
            :model="feedbackForm"
            :rules="feedbackRules"
            label-width="80px"
          >
            <el-form-item label="反馈类型" prop="feedback_type">
              <el-select v-model="feedbackForm.feedback_type" placeholder="请选择反馈类型" style="width: 100%">
                <el-option label="🐛 Bug 报告" value="bug" />
                <el-option label="💡 功能建议" value="feature" />
                <el-option label="❓ 问题咨询" value="question" />
                <el-option label="📝 其他" value="other" />
              </el-select>
            </el-form-item>
            <el-form-item label="标题" prop="title">
              <el-input v-model="feedbackForm.title" placeholder="请简要描述您的反馈" maxlength="200" show-word-limit />
            </el-form-item>
            <el-form-item label="详细内容" prop="content">
              <el-input
                v-model="feedbackForm.content"
                type="textarea"
                :rows="5"
                placeholder="请详细描述您的问题或建议..."
                maxlength="2000"
                show-word-limit
              />
            </el-form-item>
          </el-form>
        </el-tab-pane>
        
        <el-tab-pane label="我的反馈" name="history">
          <div v-loading="myFeedbackLoading" class="my-feedback-list">
            <el-empty v-if="myFeedbackList.length === 0" description="暂无反馈记录" />
            <div v-else class="feedback-items">
              <div v-for="item in myFeedbackList" :key="item.id" class="feedback-item">
                <div class="feedback-item-header">
                  <span class="feedback-title">{{ item.title }}</span>
                  <el-tag :type="getFeedbackStatusType(item.status)" size="small">
                    {{ getFeedbackStatusText(item.status) }}
                  </el-tag>
                </div>
                <div class="feedback-item-meta">
                  <el-tag size="small" effect="plain">{{ getFeedbackTypeText(item.feedback_type) }}</el-tag>
                  <span class="feedback-time">{{ formatTime(item.created_at) }}</span>
                </div>
                <div class="feedback-item-content">{{ item.content }}</div>
                <div v-if="item.admin_reply" class="feedback-reply">
                  <div class="reply-label">
                    <el-icon><Service /></el-icon>
                    管理员回复
                  </div>
                  <div class="reply-content">{{ item.admin_reply }}</div>
                </div>
              </div>
            </div>
          </div>
        </el-tab-pane>
      </el-tabs>
      
      <template #footer>
        <span v-if="feedbackTab === 'submit'" class="dialog-footer">
          <el-button @click="feedbackDialogVisible = false">取消</el-button>
          <el-button type="primary" :loading="feedbackSubmitting" @click="handleSubmitFeedback">
            提交反馈
          </el-button>
        </span>
        <span v-else class="dialog-footer">
          <el-button @click="feedbackDialogVisible = false">关闭</el-button>
          <el-button type="primary" :icon="Refresh" @click="loadMyFeedback">刷新</el-button>
        </span>
      </template>
    </el-dialog>
  </el-container>
</template>

<script setup>
import { ref, reactive, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { ROLES, ROLE_NAMES } from '@/utils/constants'
import { submitFeedback, getMyFeedback } from '@/api/feedback'
import {
  DocumentAdd,
  Document,
  Checked,
  Stamp,
  DataAnalysis,
  EditPen,
  Fold,
  Expand,
  UserFilled,
  ArrowDown,
  SwitchButton,
  Share,
  User,
  Folder,
  ChatLineRound,
  Refresh,
  Service
} from '@element-plus/icons-vue'
import { ElMessageBox, ElMessage } from 'element-plus'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()

const isCollapse = ref(false)

const activeMenu = computed(() => route.path)
const currentRouteName = computed(() => route.meta.title || '')

const toggleCollapse = () => {
  isCollapse.value = !isCollapse.value
}

const hasRole = (role) => {
  return userStore.role === role
}

const getRoleName = (role) => {
  return ROLE_NAMES[role] || '未知角色'
}

const getRoleTagType = (role) => {
  const typeMap = {
    [ROLES.ACTIVIST]: 'info',
    [ROLES.PYR]: 'success',
    [ROLES.ZZWY]: 'warning',
    [ROLES.ZBSJ]: 'danger',
    [ROLES.ZZS]: ''
  }
  return typeMap[role] || 'info'
}

const handleCommand = (command) => {
  if (command === 'logout') {
    ElMessageBox.confirm('确定要退出登录吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
      .then(() => {
        userStore.logout()
        router.push('/login')
      })
      .catch(() => {})
  }
}

// ==================== 意见反馈 ====================
const feedbackDialogVisible = ref(false)
const feedbackTab = ref('submit')
const feedbackFormRef = ref(null)
const feedbackSubmitting = ref(false)
const myFeedbackLoading = ref(false)
const myFeedbackList = ref([])

const feedbackForm = reactive({
  feedback_type: 'other',
  title: '',
  content: ''
})

const feedbackRules = {
  feedback_type: [{ required: true, message: '请选择反馈类型', trigger: 'change' }],
  title: [{ required: true, message: '请输入标题', trigger: 'blur' }],
  content: [{ required: true, message: '请输入详细内容', trigger: 'blur' }]
}

const openFeedbackDialog = () => {
  feedbackDialogVisible.value = true
  feedbackTab.value = 'submit'
  // 重置表单
  feedbackForm.feedback_type = 'other'
  feedbackForm.title = ''
  feedbackForm.content = ''
}

const handleSubmitFeedback = async () => {
  if (!feedbackFormRef.value) return
  
  await feedbackFormRef.value.validate(async (valid) => {
    if (!valid) return
    
    feedbackSubmitting.value = true
    try {
      await submitFeedback(feedbackForm)
      ElMessage.success('反馈提交成功，感谢您的意见！')
      feedbackDialogVisible.value = false
      // 重置表单
      feedbackForm.feedback_type = 'other'
      feedbackForm.title = ''
      feedbackForm.content = ''
    } catch (error) {
      console.error('提交反馈失败:', error)
    } finally {
      feedbackSubmitting.value = false
    }
  })
}

const loadMyFeedback = async () => {
  myFeedbackLoading.value = true
  try {
    const data = await getMyFeedback()
    myFeedbackList.value = data
  } catch (error) {
    console.error('加载反馈列表失败:', error)
  } finally {
    myFeedbackLoading.value = false
  }
}

// 切换到历史记录时自动加载
const onTabChange = (tab) => {
  if (tab === 'history') {
    loadMyFeedback()
  }
}

// 监听 tab 变化
import { watch } from 'vue'
watch(feedbackTab, onTabChange)

const getFeedbackStatusType = (status) => {
  const map = {
    pending: 'warning',
    processed: 'success',
    archived: 'info'
  }
  return map[status] || 'info'
}

const getFeedbackStatusText = (status) => {
  const map = {
    pending: '待处理',
    processed: '已回复',
    archived: '已归档'
  }
  return map[status] || status
}

const getFeedbackTypeText = (type) => {
  const map = {
    bug: '🐛 Bug',
    feature: '💡 建议',
    question: '❓ 问题',
    other: '📝 其他'
  }
  return map[type] || type
}

const formatTime = (timeStr) => {
  if (!timeStr) return '-'
  const date = new Date(timeStr)
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  const hour = String(date.getHours()).padStart(2, '0')
  const minute = String(date.getMinutes()).padStart(2, '0')
  return `${year}-${month}-${day} ${hour}:${minute}`
}
</script>

<style scoped>
.layout-container {
  width: 100%;
  height: 100%;
  position: relative;
  overflow: hidden;
}

.layout-aside {
  background: linear-gradient(180deg, #0f172a 0%, #0b1f3a 60%, #0c2f55 100%);
  border-right: 1px solid rgba(255, 255, 255, 0.06);
  transition: width 0.3s, background 0.3s;
  overflow: hidden;
  position: relative;
  box-shadow: 12px 0 30px rgba(10, 25, 56, 0.2);
}

.logo {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 64px;
  padding: 0 16px;
  color: #e5e7eb;
  font-size: 19px;
  font-weight: 600;
  overflow: hidden;
  white-space: nowrap;
  letter-spacing: 0.5px;
}

.logo img {
  width: 34px;
  height: 34px;
  margin-right: 10px;
  filter: drop-shadow(0 8px 20px rgba(14, 165, 233, 0.35));
}

:deep(.el-menu) {
  border-right: none;
  background: transparent;
  padding: 6px 8px 16px;
}

:deep(.el-menu-item) {
  color: rgba(255, 255, 255, 0.7);
  height: 46px;
  margin: 4px 0;
  border-radius: 12px;
  transition: all 0.25s ease;
}

:deep(.el-menu-item:hover) {
  color: #e5f1ff;
  background: rgba(255, 255, 255, 0.08) !important;
  transform: translateX(3px);
}

:deep(.el-menu-item.is-active) {
  color: #e0e7ff;
  background: linear-gradient(90deg, rgba(37, 99, 235, 0.25), rgba(14, 165, 233, 0.18)) !important;
  box-shadow: 0 10px 24px rgba(14, 165, 233, 0.18);
  transform: translateX(3px);
}

.layout-surface {
  position: relative;
}

.layout-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: rgba(255, 255, 255, 0.9);
  border-bottom: 1px solid rgba(229, 231, 235, 0.8);
  padding: 0 24px;
  backdrop-filter: blur(12px);
  box-shadow: 0 12px 30px rgba(15, 23, 42, 0.08);
}

.header-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.collapse-icon {
  font-size: 22px;
  cursor: pointer;
  transition: color 0.3s, transform 0.3s;
  color: #475569;
}

.collapse-icon:hover {
  color: var(--brand-primary);
  transform: translateY(-1px);
}

.header-right {
  display: flex;
  align-items: center;
  gap: 16px;
}

.role-tag {
  border-radius: 999px;
  padding: 6px 12px;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  padding: 8px 12px;
  border-radius: 12px;
  transition: background 0.3s, transform 0.3s;
}

.user-info:hover {
  background: rgba(37, 99, 235, 0.06);
  transform: translateY(-1px);
}

.username {
  font-size: 14px;
  color: #1f2937;
  font-weight: 600;
}

.layout-main {
  background: radial-gradient(1400px at 85% 10%, rgba(14, 165, 233, 0.07) 0, transparent 40%),
    radial-gradient(1200px at 10% 30%, rgba(37, 99, 235, 0.09) 0, transparent 40%),
    rgba(248, 250, 255, 0.92);
  padding: 28px;
  overflow-y: auto;
  position: relative;
}

.bg-bubble {
  position: absolute;
  filter: blur(40px);
  opacity: 0.3;
  z-index: 0;
}

.bubble-1 {
  width: 280px;
  height: 280px;
  background: #a5b4fc;
  top: 40px;
  right: 80px;
}

.bubble-2 {
  width: 320px;
  height: 320px;
  background: #7dd3fc;
  bottom: 40px;
  left: 40px;
}

:deep(.layout-main .el-card) {
  border: 1px solid rgba(226, 232, 240, 0.8);
  border-radius: 16px;
  box-shadow: 0 18px 40px rgba(15, 23, 42, 0.08);
  background: linear-gradient(145deg, rgba(255, 255, 255, 0.96), rgba(244, 248, 255, 0.9));
  transition: transform 0.25s ease, box-shadow 0.25s ease, border-color 0.25s ease;
  position: relative;
  z-index: 1;
}

:deep(.layout-main .el-card:hover) {
  transform: translateY(-3px);
  box-shadow: 0 22px 50px rgba(15, 23, 42, 0.1);
  border-color: rgba(37, 99, 235, 0.2);
}

/* 页面切换动画 */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

@media (max-width: 768px) {
  .layout-aside {
    box-shadow: none;
  }

  .layout-header {
    padding: 0 16px;
  }

  .layout-main {
    padding: 18px;
  }
}

.footer-credit {
  text-align: center;
  font-size: 12px;
  color: #94a3b8;
  padding: 20px 0;
  margin-top: 20px;
}

/* 意见反馈悬浮按钮 */
.feedback-fab {
  position: fixed;
  right: 24px;
  bottom: 80px;
  width: 56px;
  height: 56px;
  border-radius: 50%;
  background: linear-gradient(135deg, #2563eb 0%, #0ea5e9 100%);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  box-shadow: 0 8px 24px rgba(37, 99, 235, 0.35);
  transition: all 0.3s ease;
  z-index: 1000;
}

.feedback-fab:hover {
  transform: scale(1.1) translateY(-2px);
  box-shadow: 0 12px 32px rgba(37, 99, 235, 0.45);
}

.feedback-fab:active {
  transform: scale(0.95);
}

/* 反馈列表样式 */
.my-feedback-list {
  max-height: 400px;
  overflow-y: auto;
}

.feedback-items {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.feedback-item {
  padding: 16px;
  background: #f8fafc;
  border-radius: 12px;
  border: 1px solid #e2e8f0;
}

.feedback-item-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.feedback-title {
  font-weight: 600;
  color: #1e293b;
  font-size: 14px;
}

.feedback-item-meta {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 8px;
}

.feedback-time {
  font-size: 12px;
  color: #94a3b8;
}

.feedback-item-content {
  font-size: 13px;
  color: #475569;
  line-height: 1.6;
  margin-bottom: 8px;
}

.feedback-reply {
  margin-top: 12px;
  padding: 12px;
  background: linear-gradient(135deg, #dcfce7 0%, #d1fae5 100%);
  border-radius: 8px;
  border-left: 3px solid #10b981;
}

.reply-label {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: #059669;
  font-weight: 600;
  margin-bottom: 6px;
}

.reply-content {
  font-size: 13px;
  color: #047857;
  line-height: 1.6;
}
</style>
