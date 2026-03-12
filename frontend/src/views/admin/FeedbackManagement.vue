<template>
  <div class="feedback-management">
    <!-- 统计卡片 -->
    <div class="stats-cards">
      <el-card class="stat-card">
        <div class="stat-content">
          <div class="stat-icon total"><el-icon><ChatLineSquare /></el-icon></div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.total }}</div>
            <div class="stat-label">全部反馈</div>
          </div>
        </div>
      </el-card>
      <el-card class="stat-card">
        <div class="stat-content">
          <div class="stat-icon pending"><el-icon><Clock /></el-icon></div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.pending }}</div>
            <div class="stat-label">待处理</div>
          </div>
        </div>
      </el-card>
      <el-card class="stat-card">
        <div class="stat-content">
          <div class="stat-icon processed"><el-icon><CircleCheck /></el-icon></div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.processed }}</div>
            <div class="stat-label">已回复</div>
          </div>
        </div>
      </el-card>
      <el-card class="stat-card">
        <div class="stat-content">
          <div class="stat-icon archived"><el-icon><FolderChecked /></el-icon></div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.archived }}</div>
            <div class="stat-label">已归档</div>
          </div>
        </div>
      </el-card>
    </div>

    <!-- 筛选和列表 -->
    <el-card class="list-card">
      <template #header>
        <div class="card-header">
          <el-icon><ChatLineSquare /></el-icon>
          <span>意见反馈管理</span>
          <div class="header-actions">
            <el-select v-model="statusFilter" placeholder="状态筛选" clearable style="width: 120px" @change="loadFeedback">
              <el-option label="全部" value="" />
              <el-option label="待处理" value="pending" />
              <el-option label="已回复" value="processed" />
              <el-option label="已归档" value="archived" />
            </el-select>
            <el-button type="primary" :icon="Refresh" @click="refresh">刷新</el-button>
          </div>
        </div>
      </template>

      <el-table v-loading="loading" :data="feedbackList" stripe style="width: 100%">
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="real_name" label="提交人" width="100">
          <template #default="{ row }">
            <div class="user-cell">
              <span>{{ row.real_name || row.username }}</span>
              <el-tag size="small" effect="plain">{{ getRoleText(row.user_role) }}</el-tag>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="feedback_type" label="类型" width="100">
          <template #default="{ row }">
            <el-tag :type="getTypeTagType(row.feedback_type)" size="small">
              {{ getTypeText(row.feedback_type) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="title" label="标题" min-width="180">
          <template #default="{ row }">
            <el-tooltip :content="row.content" placement="top" :show-after="500">
              <span class="title-cell">{{ row.title }}</span>
            </el-tooltip>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusTagType(row.status)" size="small">
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="提交时间" width="160">
          <template #default="{ row }">
            {{ formatTime(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" size="small" @click="handleView(row)">
              查看
            </el-button>
            <el-button 
              v-if="row.status === 'pending'" 
              type="success" 
              size="small" 
              @click="handleReply(row)"
            >
              回复
            </el-button>
            <el-button type="danger" size="small" @click="handleDelete(row)">
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <el-empty v-if="!loading && feedbackList.length === 0" description="暂无反馈" />
    </el-card>

    <!-- 查看/回复对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogMode === 'view' ? '查看反馈' : '回复反馈'"
      width="600px"
    >
      <div v-if="currentFeedback" class="feedback-detail">
        <div class="detail-header">
          <div class="detail-title">{{ currentFeedback.title }}</div>
          <el-tag :type="getStatusTagType(currentFeedback.status)">
            {{ getStatusText(currentFeedback.status) }}
          </el-tag>
        </div>
        
        <div class="detail-meta">
          <span>提交人：{{ currentFeedback.real_name || currentFeedback.username }}</span>
          <span>类型：{{ getTypeText(currentFeedback.feedback_type) }}</span>
          <span>时间：{{ formatTime(currentFeedback.created_at) }}</span>
        </div>
        
        <div class="detail-content">
          <div class="content-label">反馈内容</div>
          <div class="content-text">{{ currentFeedback.content }}</div>
        </div>
        
        <div v-if="currentFeedback.admin_reply" class="detail-reply">
          <div class="reply-label">
            <el-icon><Service /></el-icon>
            管理员回复
          </div>
          <div class="reply-text">{{ currentFeedback.admin_reply }}</div>
        </div>
        
        <div v-if="dialogMode === 'reply'" class="reply-form">
          <el-divider />
          <el-form :model="replyForm" label-width="80px">
            <el-form-item label="回复内容">
              <el-input
                v-model="replyForm.reply"
                type="textarea"
                :rows="4"
                placeholder="请输入回复内容..."
                maxlength="1000"
                show-word-limit
              />
            </el-form-item>
            <el-form-item label="状态">
              <el-select v-model="replyForm.status" style="width: 100%">
                <el-option label="已回复" value="processed" />
                <el-option label="已归档" value="archived" />
              </el-select>
            </el-form-item>
          </el-form>
        </div>
      </div>
      
      <template #footer>
        <el-button @click="dialogVisible = false">关闭</el-button>
        <el-button 
          v-if="dialogMode === 'view' && currentFeedback?.status === 'pending'" 
          type="primary" 
          @click="dialogMode = 'reply'"
        >
          回复
        </el-button>
        <el-button 
          v-if="dialogMode === 'reply'" 
          type="primary" 
          :loading="submitting"
          @click="submitReply"
        >
          提交回复
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { 
  ChatLineSquare, 
  Clock, 
  CircleCheck, 
  FolderChecked, 
  Refresh,
  Service
} from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getAdminFeedbackList, getAdminFeedbackStats, replyFeedback, deleteFeedback } from '@/api/feedback'

const loading = ref(false)
const feedbackList = ref([])
const statusFilter = ref('')
const stats = ref({
  total: 0,
  pending: 0,
  processed: 0,
  archived: 0
})

const dialogVisible = ref(false)
const dialogMode = ref('view')
const currentFeedback = ref(null)
const submitting = ref(false)

const replyForm = reactive({
  reply: '',
  status: 'processed'
})

const loadStats = async () => {
  try {
    const data = await getAdminFeedbackStats()
    stats.value = data
  } catch (error) {
    console.error('加载统计数据失败:', error)
  }
}

const loadFeedback = async () => {
  loading.value = true
  try {
    const data = await getAdminFeedbackList({ status_filter: statusFilter.value || undefined })
    feedbackList.value = data
  } catch (error) {
    console.error('加载反馈列表失败:', error)
  } finally {
    loading.value = false
  }
}

const refresh = () => {
  loadStats()
  loadFeedback()
}

const handleView = (row) => {
  currentFeedback.value = row
  dialogMode.value = 'view'
  dialogVisible.value = true
}

const handleReply = (row) => {
  currentFeedback.value = row
  dialogMode.value = 'reply'
  replyForm.reply = row.admin_reply || ''
  replyForm.status = 'processed'
  dialogVisible.value = true
}

const submitReply = async () => {
  if (!replyForm.reply.trim()) {
    ElMessage.warning('请输入回复内容')
    return
  }
  
  submitting.value = true
  try {
    await replyFeedback(currentFeedback.value.id, replyForm)
    ElMessage.success('回复成功')
    dialogVisible.value = false
    refresh()
  } catch (error) {
    console.error('回复失败:', error)
  } finally {
    submitting.value = false
  }
}

const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm('确定要删除这条反馈吗？', '确认删除', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    await deleteFeedback(row.id)
    ElMessage.success('删除成功')
    refresh()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除失败:', error)
    }
  }
}

const getRoleText = (role) => {
  const map = {
    admin: '管理员',
    activist: '积极分子',
    pyr: '培养人',
    zzwy: '组织委员',
    zbsj: '支部书记',
    zzs: '党总支'
  }
  return map[role] || role
}

const getTypeText = (type) => {
  const map = {
    bug: '🐛 Bug',
    feature: '💡 建议',
    question: '❓ 问题',
    other: '📝 其他'
  }
  return map[type] || type
}

const getTypeTagType = (type) => {
  const map = {
    bug: 'danger',
    feature: 'success',
    question: 'warning',
    other: 'info'
  }
  return map[type] || 'info'
}

const getStatusText = (status) => {
  const map = {
    pending: '待处理',
    processed: '已回复',
    archived: '已归档'
  }
  return map[status] || status
}

const getStatusTagType = (status) => {
  const map = {
    pending: 'warning',
    processed: 'success',
    archived: 'info'
  }
  return map[status] || 'info'
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

onMounted(() => {
  refresh()
})
</script>

<style scoped>
.feedback-management {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.stats-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
}

.stat-card {
  background: linear-gradient(145deg, #fff 0%, #f8fafc 100%);
}

.stat-content {
  display: flex;
  align-items: center;
  gap: 16px;
}

.stat-icon {
  width: 56px;
  height: 56px;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
}

.stat-icon.total {
  background: linear-gradient(135deg, #dbeafe 0%, #bfdbfe 100%);
  color: #2563eb;
}

.stat-icon.pending {
  background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
  color: #d97706;
}

.stat-icon.processed {
  background: linear-gradient(135deg, #dcfce7 0%, #bbf7d0 100%);
  color: #16a34a;
}

.stat-icon.archived {
  background: linear-gradient(135deg, #e0e7ff 0%, #c7d2fe 100%);
  color: #6366f1;
}

.stat-info {
  flex: 1;
}

.stat-value {
  font-size: 28px;
  font-weight: 700;
  color: #1e293b;
}

.stat-label {
  font-size: 13px;
  color: #64748b;
  margin-top: 2px;
}

.list-card {
  background: linear-gradient(145deg, #fff 0%, #f8fafc 100%);
}

.card-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
}

.header-actions {
  margin-left: auto;
  display: flex;
  gap: 12px;
}

.user-cell {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.title-cell {
  cursor: pointer;
  color: #1e293b;
}

.title-cell:hover {
  color: #2563eb;
}

/* 详情对话框样式 */
.feedback-detail {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.detail-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.detail-title {
  font-size: 18px;
  font-weight: 600;
  color: #1e293b;
}

.detail-meta {
  display: flex;
  gap: 20px;
  font-size: 13px;
  color: #64748b;
}

.detail-content {
  background: #f8fafc;
  padding: 16px;
  border-radius: 12px;
  border: 1px solid #e2e8f0;
}

.content-label {
  font-size: 12px;
  color: #94a3b8;
  margin-bottom: 8px;
}

.content-text {
  font-size: 14px;
  color: #334155;
  line-height: 1.8;
  white-space: pre-wrap;
}

.detail-reply {
  background: linear-gradient(135deg, #dcfce7 0%, #d1fae5 100%);
  padding: 16px;
  border-radius: 12px;
  border-left: 4px solid #10b981;
}

.reply-label {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  color: #059669;
  font-weight: 600;
  margin-bottom: 8px;
}

.reply-text {
  font-size: 14px;
  color: #047857;
  line-height: 1.6;
}

.reply-form {
  margin-top: 8px;
}
</style>







