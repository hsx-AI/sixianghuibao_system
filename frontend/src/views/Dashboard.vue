<template>
  <div class="dashboard">
    <el-card class="welcome-card">
      <template #header>
        <div class="card-header">
          <el-icon class="header-icon"><Promotion /></el-icon>
          <div class="header-text">
            <span class="eyebrow">系统概览</span>
            <span>智能制造工艺部党总支积极分子思想汇报审核平台</span>
          </div>
        </div>
      </template>

      <div class="welcome-content">
        <div class="welcome-top">
          <div>
            <p class="eyebrow">欢迎回来</p>
            <h2>你好，{{ userStore.username }}</h2>
            <p class="role-line">
              当前角色
              <el-tag :type="getRoleTagType()" effect="dark" round>
                {{ getRoleName() }}
              </el-tag>
            </p>
          </div>
          <div class="pill">
            <span class="pill-dot" />
            汇报提交、审核、总览一站式管理
          </div>
        </div>

        <el-divider />

        <div class="quick-actions">
          <h3>快速访问</h3>
          <div class="action-buttons">
            <el-button
              v-if="hasRole(ROLES.ACTIVIST)"
              type="primary"
              @click="router.push('/submit')"
            >
              <el-icon><DocumentAdd /></el-icon>
              提交思想汇报
            </el-button>
            <el-button
              v-if="hasRole(ROLES.PYR)"
              type="success"
              @click="router.push('/pyr-review')"
            >
              <el-icon><Document /></el-icon>
              培养人审核
            </el-button>
            <el-button
              v-if="hasRole(ROLES.ZZWY)"
              type="warning"
              @click="router.push('/zzwy-review')"
            >
              <el-icon><Checked /></el-icon>
              组织委员审核
            </el-button>
            <el-button
              v-if="hasRole(ROLES.ZZWY)"
              type="warning"
              @click="router.push('/zzwy-overview')"
            >
              <el-icon><DataAnalysis /></el-icon>
              组织委员总览
            </el-button>
            <el-button
              v-if="hasRole(ROLES.ZZWY)"
              type="warning"
              @click="router.push('/zzwy-review-reports')"
            >
              <el-icon><Document /></el-icon>
              思想汇报审阅
            </el-button>
            <el-button
              v-if="hasRole(ROLES.ZZWY)"
              type="warning"
              @click="router.push('/zzwy-organization')"
            >
              <el-icon><OfficeBuilding /></el-icon>
              支部组织架构
            </el-button>
            <el-button
              v-if="hasRole(ROLES.ZBSJ)"
              type="danger"
              @click="router.push('/zbsj-review')"
            >
              <el-icon><Stamp /></el-icon>
              支部书记审核
            </el-button>
            <el-button
              v-if="hasRole(ROLES.ZBSJ)"
              type="danger"
              @click="router.push('/zbsj-overview')"
            >
              <el-icon><DataAnalysis /></el-icon>
              支部书记总览
            </el-button>
            <el-button
              v-if="hasRole(ROLES.ZBSJ)"
              type="danger"
              @click="router.push('/zbsj-review-reports')"
            >
              <el-icon><Document /></el-icon>
              思想汇报审阅
            </el-button>
            <el-button
              v-if="hasRole(ROLES.ZBSJ)"
              type="danger"
              @click="router.push('/zbsj-organization')"
            >
              <el-icon><OfficeBuilding /></el-icon>
              支部组织架构
            </el-button>
            <el-button
              v-if="hasRole(ROLES.ZZS)"
              type="info"
              @click="router.push('/zzs-overview')"
            >
              <el-icon><DataAnalysis /></el-icon>
              党总支总览
            </el-button>
            <el-button
              v-if="hasRole(ROLES.ZZS)"
              type="info"
              @click="router.push('/zzs-review')"
            >
              <el-icon><Document /></el-icon>
              党总支审阅
            </el-button>
            <el-button
              v-if="hasRole(ROLES.ZZS)"
              type="info"
              @click="router.push('/zzs-organization')"
            >
              <el-icon><OfficeBuilding /></el-icon>
              组织架构
            </el-button>
          </div>
        </div>
      </div>
    </el-card>

    <!-- 积极分子的汇报审批状态卡片 -->
    <el-card v-if="hasRole(ROLES.ACTIVIST)" class="report-status-card" v-loading="reportsLoading">
      <template #header>
        <div class="card-header">
          <el-icon class="header-icon status"><Clock /></el-icon>
          <div class="header-text">
            <span class="eyebrow">我的汇报</span>
            <span>审批进度追踪</span>
          </div>
          <el-button type="primary" size="small" :icon="Refresh" circle @click="loadReports" style="margin-left: auto;" />
        </div>
      </template>
      
      <div v-if="reports.length === 0" class="empty-reports">
        <el-empty description="暂无汇报记录">
          <el-button type="primary" @click="router.push('/submit')">
            <el-icon><DocumentAdd /></el-icon>
            去提交汇报
          </el-button>
        </el-empty>
      </div>
      
      <div v-else class="reports-list">
        <div v-for="report in reports.slice(0, 5)" :key="report.id" class="report-item">
          <div class="report-header">
            <div class="report-title">
              <span class="title-text">{{ formatTitle(report) }}</span>
              <el-tag :type="getStatusType(report.status, report.current_step)" size="small">
                {{ getStatusText(report.status, report.current_step) }}
              </el-tag>
            </div>
            <span class="report-time">{{ formatPeriod(report) }}</span>
          </div>
          
          <!-- 审批流程步骤条 -->
          <div class="report-workflow">
            <el-steps 
              :active="getActiveStep(report)" 
              :process-status="getProcessStatus(report)"
              finish-status="success"
              simple
              class="mini-steps"
            >
              <el-step title="提交" />
              <el-step title="培养人" />
              <el-step title="组织委员" />
              <el-step title="支部书记" />
              <el-step title="完成" />
            </el-steps>
          </div>
          
          <!-- 当前审批人提示 -->
          <div v-if="report.status === 'pending' && report.current_reviewer_names && report.current_reviewer_names.length > 0" class="reviewer-info">
            <el-icon><User /></el-icon>
            <span>等待 <strong>{{ report.current_reviewer_names.join('、') }}</strong> 审批</span>
          </div>
          
          <!-- 驳回提示 -->
          <div v-if="report.status === 'rejected'" class="reject-info">
            <el-icon><Warning /></el-icon>
            <span>已驳回</span>
            <span v-if="report.reject_comment" class="reject-reason">：{{ report.reject_comment }}</span>
          </div>
          
          <!-- 已通过提示 -->
          <div v-if="report.status === 'approved'" class="approved-info">
            <el-icon><CircleCheck /></el-icon>
            <span>审批已完成</span>
          </div>
        </div>
        
        <div v-if="reports.length > 5" class="view-all">
          <el-button type="primary" link @click="router.push('/submit')">
            查看全部 {{ reports.length }} 条记录 →
          </el-button>
        </div>
      </div>
    </el-card>

    <el-card class="info-card">
      <template #header>
        <div class="card-header">
          <el-icon class="header-icon info"><InfoFilled /></el-icon>
          <div class="header-text">
            <span class="eyebrow">流程与职责</span>
            <span>系统说明</span>
          </div>
        </div>
      </template>
      <div class="info-content">
        <el-timeline>
          <el-timeline-item timestamp="第 1 步" placement="top">
            <p><strong>积极分子</strong> 提交思想汇报文档（Word）</p>
          </el-timeline-item>
          <el-timeline-item timestamp="第 2 步" placement="top">
            <p><strong>培养人</strong> 对汇报进行第一级审核</p>
          </el-timeline-item>
          <el-timeline-item timestamp="第 3 步" placement="top">
            <p><strong>支部组织委员</strong> 对汇报进行第二级审核</p>
          </el-timeline-item>
          <el-timeline-item timestamp="第 4 步" placement="top">
            <p><strong>支部书记</strong> 对汇报进行第三级审核</p>
          </el-timeline-item>
          <el-timeline-item timestamp="第 5 步" placement="top">
            <p><strong>党总支</strong>总览所有汇报，监督审核流程</p>
          </el-timeline-item>
        </el-timeline>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { ROLES, ROLE_NAMES, REPORT_STATUS_NAMES, REPORT_STATUS_TYPES } from '@/utils/constants'
import { getReportList } from '@/api/report'
import {
  Promotion,
  DocumentAdd,
  Document,
  Checked,
  Stamp,
  DataAnalysis,
  InfoFilled,
  OfficeBuilding,
  Clock,
  Refresh,
  User,
  Warning,
  CircleCheck
} from '@element-plus/icons-vue'

const router = useRouter()
const userStore = useUserStore()

// 积极分子的汇报列表
const reports = ref([])
const reportsLoading = ref(false)

const hasRole = (role) => {
  return userStore.role === role
}

const getRoleName = () => {
  return ROLE_NAMES[userStore.role] || '未知角色'
}

const getRoleTagType = () => {
  const typeMap = {
    [ROLES.ACTIVIST]: 'info',
    [ROLES.PYR]: 'success',
    [ROLES.ZZWY]: 'warning',
    [ROLES.ZBSJ]: 'danger',
    [ROLES.ZZS]: ''
  }
  return typeMap[userStore.role] || 'info'
}

// 加载汇报列表（仅积极分子）
const loadReports = async () => {
  if (!hasRole(ROLES.ACTIVIST)) return
  
  reportsLoading.value = true
  try {
    const data = await getReportList()
    reports.value = data
  } catch (error) {
    console.error('加载汇报列表失败:', error)
  } finally {
    reportsLoading.value = false
  }
}

// 格式化标题
const formatTitle = (row) => {
  if (row?.title) return row.title
  if (row?.year && row?.month) return `思想汇报 (${row.year}年${row.month}月)`
  return '思想汇报'
}

// 格式化时间
const formatPeriod = (row) => {
  if (row?.year && row?.month) return `${row.year}-${String(row.month).padStart(2, '0')}`
  return ''
}

// 获取状态文字
const getStatusText = (status, current_step) => {
  if (current_step === 'zzs') return '已通过'
  return REPORT_STATUS_NAMES[status] || status
}

// 获取状态标签类型
const getStatusType = (status, current_step) => {
  if (current_step === 'zzs') return 'success'
  return REPORT_STATUS_TYPES[status] || 'info'
}

// 获取当前步骤索引
const getActiveStep = (row) => {
  if (row.status === 'approved') return 5
  if (row.status === 'rejected') return getStepIndex(row.current_step)
  
  const stepOrder = ['activist', 'pyr', 'zzwy', 'zbsj', 'zzs']
  const idx = stepOrder.indexOf(row.current_step)
  return idx >= 0 ? idx + 1 : 1
}

// 步骤索引映射
const getStepIndex = (step) => {
  const stepOrder = ['activist', 'pyr', 'zzwy', 'zbsj', 'zzs']
  const idx = stepOrder.indexOf(step)
  return idx >= 0 ? idx + 1 : 1
}

// 获取流程状态
const getProcessStatus = (row) => {
  if (row.status === 'rejected') return 'error'
  if (row.status === 'approved') return 'success'
  return 'process'
}

onMounted(() => {
  if (hasRole(ROLES.ACTIVIST)) {
    loadReports()
  }
})
</script>

<style scoped>
.dashboard {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(420px, 1fr));
  gap: 20px;
  position: relative;
  z-index: 2;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 12px;
  font-weight: 700;
}

.header-text {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.header-icon {
  color: #2563eb;
}

.header-icon.info {
  color: #0ea5e9;
}

.eyebrow {
  font-size: 12px;
  color: #6b7280;
  letter-spacing: 0.4px;
}

.welcome-card {
  background: linear-gradient(135deg, #f8fbff 0%, #f5f9ff 50%, #edf5ff 100%);
}

.welcome-content {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.welcome-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
}

.welcome-content h2 {
  font-size: 24px;
  color: #0f172a;
  margin: 4px 0 10px;
}

.welcome-content p {
  font-size: 15px;
  color: #475569;
}

.role-line {
  display: flex;
  align-items: center;
  gap: 10px;
  font-weight: 600;
}

.pill {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  padding: 12px 14px;
  border-radius: 999px;
  background: rgba(37, 99, 235, 0.08);
  color: #1d4ed8;
  font-weight: 600;
  letter-spacing: 0.3px;
}

.pill-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: linear-gradient(135deg, #2563eb, #0ea5e9);
  box-shadow: 0 0 12px rgba(37, 99, 235, 0.5);
}

.quick-actions h3 {
  font-size: 16px;
  color: #0f172a;
  margin-bottom: 12px;
}

.action-buttons {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}

.info-card {
  background: linear-gradient(145deg, rgba(255, 255, 255, 0.96), rgba(244, 248, 255, 0.94));
}

.info-content {
  padding: 10px 0;
}

.info-content p {
  font-size: 14px;
  color: #475569;
}

/* 汇报状态卡片样式 */
.report-status-card {
  background: linear-gradient(145deg, #fff 0%, #f8fafc 100%);
}

.header-icon.status {
  color: #8b5cf6;
}

.empty-reports {
  padding: 20px 0;
}

.reports-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.report-item {
  padding: 16px;
  background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
  border-radius: 12px;
  border: 1px solid #e2e8f0;
  transition: all 0.2s ease;
}

.report-item:hover {
  border-color: #cbd5e1;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}

.report-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 12px;
}

.report-title {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.title-text {
  font-weight: 600;
  color: #1e293b;
  font-size: 14px;
}

.report-time {
  font-size: 12px;
  color: #64748b;
  background: #e2e8f0;
  padding: 2px 8px;
  border-radius: 4px;
}

.report-workflow {
  margin: 12px 0;
}

.mini-steps {
  --el-text-color-placeholder: #94a3b8;
}

:deep(.mini-steps .el-step__title) {
  font-size: 12px !important;
}

:deep(.mini-steps .el-step__head) {
  padding-right: 8px;
}

.reviewer-info {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-top: 10px;
  padding: 8px 12px;
  background: linear-gradient(135deg, #dbeafe 0%, #e0f2fe 100%);
  border-radius: 6px;
  color: #1d4ed8;
  font-size: 13px;
}

.reviewer-info .el-icon {
  font-size: 14px;
}

.reviewer-info strong {
  color: #1e40af;
}

.reject-info {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-top: 10px;
  padding: 8px 12px;
  background: linear-gradient(135deg, #fee2e2 0%, #fecaca 100%);
  border-radius: 6px;
  color: #dc2626;
  font-size: 13px;
}

.reject-info .el-icon {
  font-size: 14px;
}

.reject-reason {
  color: #991b1b;
}

.approved-info {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-top: 10px;
  padding: 8px 12px;
  background: linear-gradient(135deg, #dcfce7 0%, #bbf7d0 100%);
  border-radius: 6px;
  color: #16a34a;
  font-size: 13px;
}

.approved-info .el-icon {
  font-size: 14px;
}

.view-all {
  text-align: center;
  padding-top: 8px;
  border-top: 1px dashed #e2e8f0;
  margin-top: 8px;
}

@media (max-width: 768px) {
  .dashboard {
    grid-template-columns: 1fr;
  }

  .welcome-top {
    flex-direction: column;
    align-items: flex-start;
  }

  .action-buttons {
    flex-direction: column;
  }

  .action-buttons .el-button {
    width: 100%;
  }
}
</style>