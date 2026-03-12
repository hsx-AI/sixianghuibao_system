<template>
  <div class="submit-page">
    <el-card class="submit-card">
      <template #header>
        <div class="card-header">
          <el-icon><DocumentAdd /></el-icon>
          <span>提交思想汇报</span>
        </div>
      </template>
      
      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-width="100px"
        class="submit-form"
      >
        <el-form-item label="汇报标题" prop="title">
          <el-input
            v-model="form.title"
            placeholder="请输入汇报标题"
            clearable
          />
        </el-form-item>
        
        <el-form-item label="汇报时间" prop="period">
          <el-date-picker
            v-model="form.period"
            type="month"
            placeholder="选择月份"
            format="YYYY-MM"
            value-format="YYYY-MM"
            style="width: 100%"
          />
        </el-form-item>
        
        <el-form-item label="上传文档" prop="file">
          <el-upload
            ref="uploadRef"
            :auto-upload="false"
            :limit="1"
            :on-change="handleFileChange"
            :on-exceed="handleExceed"
            :before-remove="handleBeforeRemove"
            accept=".doc,.docx"
            drag
          >
            <el-icon class="el-icon--upload"><UploadFilled /></el-icon>
            <div class="el-upload__text">
              将文件拖到此处，或<em>点击上传</em>
            </div>
            <template #tip>
              <div class="el-upload__tip">
                只能上传 Word 文档（.doc/.docx），且不超过 10MB
              </div>
            </template>
          </el-upload>
        </el-form-item>
        
        <el-form-item>
          <el-button type="primary" :loading="loading" @click="handleSubmit">
            {{ loading ? '提交中...' : '提交汇报' }}
          </el-button>
          <el-button @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>
    
    <el-card class="history-card">
      <template #header>
        <div class="card-header">
          <el-icon><Clock /></el-icon>
          <span>我的汇报记录</span>
          <el-button
            type="primary"
            size="small"
            :icon="Refresh"
            circle
            @click="loadReports"
          />
        </div>
      </template>
      
      <el-table
        v-loading="tableLoading"
        :data="reports"
        stripe
        style="width: 100%"
        row-key="id"
        :expand-row-keys="expandedRows"
        @expand-change="handleExpandChange"
      >
        <el-table-column type="expand">
          <template #default="{ row }">
            <div class="workflow-expand">
              <div class="workflow-title">审批流程</div>
              <el-steps 
                :active="getActiveStep(row)" 
                :process-status="getProcessStatus(row)"
                finish-status="success"
                align-center
                class="workflow-steps"
              >
                <el-step title="提交">
                  <template #description>
                    <span class="step-person">{{ row.submitted_by || '-' }}</span>
                    <span class="step-time">{{ formatUploadTime(row.uploaded_time) }}</span>
                  </template>
                </el-step>
                <el-step title="培养人审核">
                  <template #description>
                    <span class="step-person">{{ getStepReviewerInfo(row, 'pyr').name }}</span>
                    <span v-if="getStepReviewerInfo(row, 'pyr').time" class="step-time">
                      {{ getStepReviewerInfo(row, 'pyr').time }}
                    </span>
                    <span v-else-if="row.current_step === 'pyr' && row.status === 'pending'" class="step-waiting">
                      等待审批
                    </span>
                  </template>
                </el-step>
                <el-step title="组织委员审核">
                  <template #description>
                    <span class="step-person">{{ getStepReviewerInfo(row, 'zzwy').name }}</span>
                    <span v-if="getStepReviewerInfo(row, 'zzwy').time" class="step-time">
                      {{ getStepReviewerInfo(row, 'zzwy').time }}
                    </span>
                    <span v-else-if="row.current_step === 'zzwy' && row.status === 'pending'" class="step-waiting">
                      等待审批
                    </span>
                  </template>
                </el-step>
                <el-step title="支部书记审核">
                  <template #description>
                    <span class="step-person">{{ getStepReviewerInfo(row, 'zbsj').name }}</span>
                    <span v-if="getStepReviewerInfo(row, 'zbsj').time" class="step-time">
                      {{ getStepReviewerInfo(row, 'zbsj').time }}
                    </span>
                    <span v-else-if="row.current_step === 'zbsj' && row.status === 'pending'" class="step-waiting">
                      等待审批
                    </span>
                  </template>
                </el-step>
                <el-step title="完成">
                  <template #description>
                    <span v-if="row.status === 'approved'" class="step-success">审批通过</span>
                    <span v-else class="step-person">-</span>
                  </template>
                </el-step>
              </el-steps>
              
              <!-- 当前等待审批人提示 -->
              <div v-if="row.status === 'pending' && row.current_reviewer_names && row.current_reviewer_names.length > 0" class="current-reviewer-info">
                <el-icon><User /></el-icon>
                <span>当前等待 <strong>{{ row.current_reviewer_names.join('、') }}</strong> 审批</span>
              </div>
              
              <!-- 驳回提示 -->
              <div v-if="row.status === 'rejected'" class="reject-info">
                <el-icon><Warning /></el-icon>
                <span>已被驳回，请修改后重新提交</span>
                <span v-if="row.reject_comment" class="reject-reason">（{{ row.reject_comment }}）</span>
              </div>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="title" label="标题" min-width="180">
          <template #default="{ row }">
            {{ formatTitle(row) }}
          </template>
        </el-table-column>
        <el-table-column prop="period" label="汇报时间" width="100">
          <template #default="{ row }">
            {{ formatPeriod(row) }}
          </template>
        </el-table-column>
        <el-table-column prop="uploaded_time" label="提交时间" width="150">
          <template #default="{ row }">
            {{ formatUploadTime(row.uploaded_time) }}
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tooltip
              v-if="row.status === 'rejected' && row.reject_comment"
              :content="'驳回意见: ' + row.reject_comment"
              placement="top"
              effect="light"
            >
              <el-tag :type="getStatusType(row.status)" style="cursor: pointer;">
                {{ getStatusText(row.status) }}
                <el-icon style="margin-left: 4px;"><Warning /></el-icon>
              </el-tag>
            </el-tooltip>
            <el-tag v-else :type="getStatusType(row.status)">
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="current_step" label="当前进度" width="180">
          <template #default="{ row }">
            <div class="progress-cell">
              <el-tag :type="getProgressTagType(row)" effect="plain">
                {{ getProgressText(row) }}
              </el-tag>
              <div v-if="row.status === 'pending' && row.current_reviewer_names && row.current_reviewer_names.length > 0" class="reviewer-hint">
                → {{ row.current_reviewer_names[0] }}{{ row.current_reviewer_names.length > 1 ? '等' : '' }}
              </div>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="260" fixed="right">
          <template #default="{ row }">
            <el-button
              type="primary"
              size="small"
              :icon="Download"
              @click="handleDownload(row.id)"
            >
              下载
            </el-button>
            <el-button
              v-if="row.reject_has_file"
              type="warning"
              size="small"
              :icon="Document"
              @click="handleDownloadRejectFile(row.reject_review_id)"
            >
              批注
            </el-button>
            <el-button
              type="danger"
              size="small"
              :icon="Delete"
              @click="handleDelete(row.id)"
            >
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
      
      <el-empty v-if="!tableLoading && reports.length === 0" description="暂无汇报记录" />
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { DocumentAdd, Clock, UploadFilled, Refresh, Download, Delete, Warning, Document, User } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { uploadReport, getReportList, downloadReport, deleteReport, downloadRejectFile } from '@/api/report'
import { useUserStore } from '@/stores/user'
import {
  REPORT_STATUS,
  REPORT_STATUS_NAMES,
  REPORT_STATUS_TYPES,
  CURRENT_STEP_NAMES
} from '@/utils/constants'

const userStore = useUserStore()
const formRef = ref(null)
const uploadRef = ref(null)
const loading = ref(false)
const tableLoading = ref(false)
const reports = ref([])
const expandedRows = ref([])

const form = reactive({
  title: '',
  period: '',
  file: null
})

const rules = {
  title: [
    { required: true, message: '请输入汇报标题', trigger: 'blur' }
  ],
  period: [
    { required: true, message: '请选择汇报时间', trigger: 'change' }
  ],
  file: [
    { required: true, message: '请上传汇报文档', trigger: 'change' }
  ]
}

const handleFileChange = (file) => {
  // 验证文件大小
  const isLt10M = file.size / 1024 / 1024 < 10
  if (!isLt10M) {
    ElMessage.error('文件大小不能超过 10MB!')
    uploadRef.value.clearFiles()
    form.file = null
    return
  }
  
  // 验证文件类型
  const isWord = ['application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'].includes(file.raw.type)
  if (!isWord) {
    ElMessage.error('只能上传 Word 文档!')
    uploadRef.value.clearFiles()
    form.file = null
    return
  }
  
  form.file = file.raw
  
  // 如果标题为空，自动使用文件名（去掉扩展名）作为标题
  if (!form.title && file.name) {
    const fileName = file.name
    // 去掉文件扩展名
    const titleFromFile = fileName.replace(/\.(doc|docx)$/i, '')
    form.title = titleFromFile
  }
}

const handleExceed = () => {
  ElMessage.warning('只能上传一个文件')
}

const handleBeforeRemove = () => {
  return ElMessageBox.confirm('确定要移除该文件吗？')
}

const handleSubmit = async () => {
  if (!formRef.value) return
  
  await formRef.value.validate(async (valid) => {
    if (!valid) return
    
    if (!form.file) {
      ElMessage.warning('请上传汇报文档')
      return
    }
    
    loading.value = true
    try {
      await uploadReport({
        title: form.title,
        period: form.period,
        file: form.file
      })
      
      ElMessage.success('提交成功')
      handleReset()
      loadReports()
    } catch (error) {
      console.error('提交失败:', error)
    } finally {
      loading.value = false
    }
  })
}

const handleReset = () => {
  formRef.value?.resetFields()
  uploadRef.value?.clearFiles()
  form.file = null
}

const loadReports = async () => {
  tableLoading.value = true
  try {
    const data = await getReportList()
    reports.value = data
  } catch (error) {
    console.error('加载报告列表失败:', error)
  } finally {
    tableLoading.value = false
  }
}

const handleDownload = async (id) => {
  try {
    const { blob, filename } = await downloadReport(id)
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = filename
    link.click()
    window.URL.revokeObjectURL(url)
    ElMessage.success('下载成功')
  } catch (error) {
    console.error('下载失败:', error)
  }
}

const handleDownloadRejectFile = async (reviewId) => {
  try {
    const { blob, filename } = await downloadRejectFile(reviewId)
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = filename
    link.click()
    window.URL.revokeObjectURL(url)
    ElMessage.success('下载批注文件成功')
  } catch (error) {
    console.error('下载批注文件失败:', error)
    ElMessage.error('下载批注文件失败')
  }
}

const handleDelete = async (id) => {
  try {
    await ElMessageBox.confirm(
      '删除后将无法恢复，确定要删除这份汇报吗？',
      '确认删除',
      {
        confirmButtonText: '确定删除',
        cancelButtonText: '取消',
        type: 'warning',
        confirmButtonClass: 'el-button--danger'
      }
    )
    
    // 执行删除
    await deleteReport(id)
    ElMessage.success('删除成功')
    
    // 刷新列表
    await loadReports()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除失败:', error)
      ElMessage.error('删除失败，请重试')
    }
  }
}

const getStatusText = (status) => {
  return REPORT_STATUS_NAMES[status] || status
}

const getStatusType = (status) => {
  return REPORT_STATUS_TYPES[status] || 'info'
}

const getStepText = (step) => {
  return CURRENT_STEP_NAMES[step] || step
}

// 展开行处理
const handleExpandChange = (row, expandedRowsList) => {
  expandedRows.value = expandedRowsList.map(r => r.id)
}

// 获取当前步骤索引（用于 el-steps 的 active）
const getActiveStep = (row) => {
  if (row.status === 'approved') return 5  // 全部完成
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

// 获取某个步骤的审批人信息
const getStepReviewerInfo = (row, stepRole) => {
  // 从审批历史中查找该步骤的审批记录
  if (row.review_history && row.review_history.length > 0) {
    // 找到该步骤最新的审批记录
    const stepReviews = row.review_history.filter(r => r.step === stepRole)
    if (stepReviews.length > 0) {
      const latest = stepReviews[stepReviews.length - 1]
      return {
        name: latest.reviewer_name || '-',
        time: formatUploadTime(latest.review_time),
        status: latest.status
      }
    }
  }
  
  // 如果是当前步骤且待审批，显示等待的审批人
  if (row.current_step === stepRole && row.status === 'pending' && row.current_reviewer_names) {
    return {
      name: row.current_reviewer_names.join('、') || '-',
      time: null,
      status: null
    }
  }
  
  return { name: '-', time: null, status: null }
}

// 获取进度文本
const getProgressText = (row) => {
  if (row.status === 'approved') return '已完成'
  if (row.status === 'rejected') return '已驳回'
  return getStepText(row.current_step)
}

// 获取进度标签类型
const getProgressTagType = (row) => {
  if (row.status === 'approved') return 'success'
  if (row.status === 'rejected') return 'danger'
  return 'warning'
}

const formatTitle = (row) => {
  if (row?.title) return row.title
  if (row?.year && row?.month) return `思想汇报 (${row.year}年${row.month}月)`
  return '思想汇报'
}

const formatPeriod = (row) => {
  if (row?.year && row?.month) return `${row.year}-${String(row.month).padStart(2, '0')}`
  return ''
}

const formatUploadTime = (timeStr) => {
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
  loadReports()
})
</script>

<style scoped>
.submit-page {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
}

.card-header .el-button {
  margin-left: auto;
}

.submit-card {
  max-width: 900px;
  background: linear-gradient(145deg, rgba(255, 255, 255, 0.96), rgba(244, 248, 255, 0.94));
}

.submit-form {
  max-width: 640px;
  margin-top: 12px;
}

.history-card {
  margin-top: 20px;
}

:deep(.el-upload) {
  width: 100%;
}

:deep(.el-upload-dragger) {
  width: 100%;
  border-radius: 14px;
  border: 1px dashed #a5b4fc;
  background: linear-gradient(135deg, rgba(164, 202, 255, 0.08), rgba(103, 232, 249, 0.08));
  transition: all 0.2s ease;
}

:deep(.el-upload-dragger:hover) {
  border-color: #2563eb;
  background: linear-gradient(135deg, rgba(164, 202, 255, 0.14), rgba(103, 232, 249, 0.14));
}

:deep(.el-table) {
  --el-table-border-color: rgba(226, 232, 240, 0.9);
}

:deep(.el-table__header-wrapper th) {
  background: #f8fafc;
}

:deep(.el-button--primary) {
  box-shadow: 0 10px 28px rgba(37, 99, 235, 0.16);
}

/* 审批流程展开区域样式 */
.workflow-expand {
  padding: 20px 40px;
  background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
  border-radius: 8px;
  margin: 8px 0;
}

.workflow-title {
  font-size: 14px;
  font-weight: 600;
  color: #374151;
  margin-bottom: 20px;
  padding-left: 8px;
  border-left: 3px solid #2563eb;
}

.workflow-steps {
  margin: 0 20px;
}

:deep(.workflow-steps .el-step__description) {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2px;
}

.step-person {
  font-size: 13px;
  color: #374151;
  font-weight: 500;
}

.step-time {
  font-size: 11px;
  color: #9ca3af;
}

.step-waiting {
  font-size: 12px;
  color: #f59e0b;
  font-weight: 500;
}

.step-success {
  font-size: 13px;
  color: #10b981;
  font-weight: 600;
}

.current-reviewer-info {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 20px;
  padding: 12px 16px;
  background: linear-gradient(135deg, #dbeafe 0%, #e0f2fe 100%);
  border-radius: 8px;
  color: #1d4ed8;
  font-size: 14px;
}

.current-reviewer-info .el-icon {
  font-size: 18px;
}

.current-reviewer-info strong {
  color: #1e40af;
}

.reject-info {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 20px;
  padding: 12px 16px;
  background: linear-gradient(135deg, #fee2e2 0%, #fecaca 100%);
  border-radius: 8px;
  color: #dc2626;
  font-size: 14px;
}

.reject-info .el-icon {
  font-size: 18px;
}

.reject-reason {
  color: #991b1b;
  font-size: 13px;
}

/* 进度列样式 */
.progress-cell {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.reviewer-hint {
  font-size: 12px;
  color: #6b7280;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

:deep(.el-table__expanded-cell) {
  padding: 0 !important;
  background: transparent !important;
}

:deep(.el-table__expand-icon) {
  color: #2563eb;
}
</style>
