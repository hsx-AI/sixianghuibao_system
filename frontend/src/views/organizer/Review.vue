<template>
  <div class="review-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <el-icon><Document /></el-icon>
          <span>组织委员审核</span>
          <el-button
            type="primary"
            size="small"
            :icon="Refresh"
            circle
            @click="loadReports"
          />
        </div>
      </template>
      
      <!-- 搜索栏 -->
      <div class="search-bar">
        <el-form :inline="true" :model="searchForm" class="search-form">
          <el-form-item label="统计类型">
            <el-radio-group v-model="searchForm.type" @change="handleTypeChange">
              <el-radio-button label="month">月度</el-radio-button>
              <el-radio-button label="quarter">季度</el-radio-button>
            </el-radio-group>
          </el-form-item>

          <el-form-item label="期间" v-if="searchForm.type === 'month'">
            <el-date-picker
              v-model="searchForm.period"
              type="month"
              placeholder="选择月份"
              format="YYYY-MM"
              value-format="YYYY-MM"
              clearable
              @change="handleSearch"
            />
          </el-form-item>

          <template v-else>
            <el-form-item label="年份">
              <el-date-picker
                v-model="searchForm.year"
                type="year"
                placeholder="选择年份"
                value-format="YYYY"
                style="width: 120px"
                @change="handleSearch"
              />
            </el-form-item>
            <el-form-item label="季度">
              <el-select v-model="searchForm.quarter" placeholder="选择季度" style="width: 120px" @change="handleSearch">
                <el-option label="第一季度" :value="1" />
                <el-option label="第二季度" :value="2" />
                <el-option label="第三季度" :value="3" />
                <el-option label="第四季度" :value="4" />
              </el-select>
            </el-form-item>
          </template>
          <el-form-item label="标题">
            <el-input
              v-model="searchForm.title"
              placeholder="搜索标题"
              clearable
            />
          </el-form-item>
          <el-form-item>
            <el-button type="primary" :icon="Search" @click="handleSearch">搜索</el-button>
            <el-button :icon="RefreshLeft" @click="handleReset">重置</el-button>
          </el-form-item>
        </el-form>
      </div>
      
      <!-- 数据表格 -->
      <el-table
        v-loading="loading"
        :data="reports"
        stripe
        style="width: 100%"
      >
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
        <el-table-column prop="submitted_by" label="提交人" width="100" />
        <el-table-column prop="trainers" label="培养人" width="150">
          <template #default="{ row }">
            <span v-if="row.trainers && row.trainers.length > 0">
              {{ row.trainers.join('、') }}
            </span>
            <span v-else style="color: #999">-</span>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="current_step" label="当前步骤" width="140">
          <template #default="{ row }">
            <el-tag type="info" effect="plain">
              {{ getStepText(row.current_step) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button
              type="primary"
              size="small"
              :icon="View"
              @click="handleView(row)"
            >
              查看
            </el-button>
            <el-button
              v-if="canReview(row)"
              type="success"
              size="small"
              :icon="Check"
              @click="handleReview(row, 'approve')"
            >
              通过
            </el-button>
            <el-button
              v-if="canReview(row)"
              type="danger"
              size="small"
              :icon="Close"
              @click="handleReview(row, 'reject')"
            >
              驳回
            </el-button>
          </template>
        </el-table-column>
      </el-table>
      
      <el-empty v-if="!loading && reports.length === 0" description="暂无待审核的汇报" />
    </el-card>
    
    <!-- 审核对话框 -->
    <el-dialog
      v-model="reviewDialogVisible"
      :title="reviewAction === 'approve' ? '通过审核' : '驳回审核'"
      width="500px"
    >
      <el-form :model="reviewForm" label-width="80px">
        <el-form-item label="审核意见">
          <el-input
            v-model="reviewForm.comments"
            type="textarea"
            :rows="4"
            :placeholder="reviewAction === 'approve' ? '请输入审核意见（可选）' : '请输入驳回理由'"
          />
        </el-form-item>
        <el-form-item v-if="reviewAction === 'reject'" label="批注文件">
          <el-upload
            ref="rejectUploadRef"
            :auto-upload="false"
            :limit="1"
            :on-change="handleRejectFileChange"
            :on-remove="handleRejectFileRemove"
            accept=".doc,.docx"
          >
            <el-button type="primary">
              <el-icon style="margin-right: 4px"><Upload /></el-icon>
              上传批注文件
            </el-button>
            <template #tip>
              <div class="upload-tip">可上传带批注的Word文档（可选）</div>
            </template>
          </el-upload>
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="reviewDialogVisible = false">取消</el-button>
        <el-button
          type="primary"
          :loading="reviewLoading"
          @click="handleConfirmReview"
        >
          确定
        </el-button>
      </template>
    </el-dialog>
    
    <!-- 查看详情对话框 -->
    <el-dialog
      v-model="viewDialogVisible"
      title="汇报详情"
      width="600px"
    >
      <el-descriptions :column="1" border v-if="currentReport">
        <el-descriptions-item label="ID">{{ currentReport.id }}</el-descriptions-item>
        <el-descriptions-item label="标题">{{ formatTitle(currentReport) }}</el-descriptions-item>
        <el-descriptions-item label="期间">{{ formatPeriod(currentReport) }}</el-descriptions-item>
        <el-descriptions-item label="提交人">{{ currentReport.submitted_by }}</el-descriptions-item>
        <el-descriptions-item label="培养人">
          <span v-if="currentReport.trainers && currentReport.trainers.length > 0">
            {{ currentReport.trainers.join('、') }}
          </span>
          <span v-else style="color: #999">-</span>
        </el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag :type="getStatusType(currentReport.status)">
            {{ getStatusText(currentReport.status) }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="当前步骤">
          <el-tag type="info" effect="plain">
            {{ getStepText(currentReport.current_step) }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="文档">
          <el-button
            type="primary"
            size="small"
            :icon="Download"
            @click="handleDownload(currentReport.id)"
          >
            下载文档
          </el-button>
          <el-button
            type="success"
            size="small"
            :loading="previewLoading"
            style="margin-left: 8px"
            @click="handlePreview(currentReport.id)"
          >
            在线预览
          </el-button>
        </el-descriptions-item>
      </el-descriptions>
      
      <template #footer>
        <el-button @click="viewDialogVisible = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import {
  Document,
  Refresh,
  Search,
  RefreshLeft,
  View,
  Check,
  Close,
  Download,
  Upload
} from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getPendingReports, reviewReport, downloadReport, rejectReportWithFile } from '@/api/report'
import { handlePreviewReport } from '@/utils/preview'
import {
  REPORT_STATUS,
  REPORT_STATUS_NAMES,
  REPORT_STATUS_TYPES,
  CURRENT_STEP,
  CURRENT_STEP_NAMES
} from '@/utils/constants'

const loading = ref(false)
const reports = ref([])
const reviewDialogVisible = ref(false)
const viewDialogVisible = ref(false)
const reviewLoading = ref(false)
const currentReport = ref(null)
const previewLoading = ref(false)
const reviewAction = ref('')

const now = new Date()
const currentYear = now.getFullYear().toString()
const currentQuarter = Math.ceil((now.getMonth() + 1) / 3)

const searchForm = reactive({
  type: 'quarter',
  period: '',
  year: currentYear,
  quarter: currentQuarter,
  title: ''
})

const reviewForm = reactive({
  comments: '',
  rejectFile: null
})

const rejectUploadRef = ref(null)

const loadReports = async () => {
  loading.value = true
  try {
    // 解析期间参数
    let year = null
    let month = null
    let quarter = null
    
    if (searchForm.type === 'month' && searchForm.period) {
      const [y, m] = searchForm.period.split('-')
      year = parseInt(y)
      month = parseInt(m)
    } else if (searchForm.type === 'quarter') {
      year = parseInt(searchForm.year)
      quarter = searchForm.quarter
    }

    const data = await getPendingReports({
      year,
      month,
      quarter,
      title: searchForm.title || undefined
    })
    reports.value = data
  } catch (error) {
    console.error('加载报告列表失败:', error)
  } finally {
    loading.value = false
  }
}

const handleTypeChange = () => {
  // 切换类型时重置相关字段
  if (searchForm.type === 'month') {
    searchForm.period = ''
  } else {
    const now = new Date()
    searchForm.year = now.getFullYear().toString()
    searchForm.quarter = Math.ceil((now.getMonth() + 1) / 3)
  }
  handleSearch()
}

const handleSearch = () => {
  loadReports()
}

const handleReset = () => {
  searchForm.type = 'quarter'
  const now = new Date()
  searchForm.year = now.getFullYear().toString()
  searchForm.quarter = Math.ceil((now.getMonth() + 1) / 3)
  searchForm.period = ''
  searchForm.title = ''
  loadReports()
}

const canReview = (row) => {
  return row.current_step === CURRENT_STEP.ZZWY && row.status === REPORT_STATUS.PENDING
}

const handleView = (row) => {
  currentReport.value = row
  viewDialogVisible.value = true
}

const handleReview = (row, action) => {
  currentReport.value = row
  reviewAction.value = action
  reviewForm.comments = ''
  reviewForm.rejectFile = null
  if (rejectUploadRef.value) {
    rejectUploadRef.value.clearFiles()
  }
  reviewDialogVisible.value = true
}

const handleRejectFileChange = (file) => {
  reviewForm.rejectFile = file.raw
}

const handleRejectFileRemove = () => {
  reviewForm.rejectFile = null
}

const handleConfirmReview = async () => {
  if (reviewAction.value === 'reject' && !reviewForm.comments) {
    ElMessage.warning('请输入驳回理由')
    return
  }
  
  reviewLoading.value = true
  try {
    // 驳回时如果有文件，使用带文件的接口
    if (reviewAction.value === 'reject' && reviewForm.rejectFile) {
      await rejectReportWithFile(
        currentReport.value.id,
        reviewForm.comments,
        reviewForm.rejectFile
      )
    } else {
      await reviewReport(
        currentReport.value.id,
        reviewAction.value,
        reviewForm.comments
      )
    }
    
    ElMessage.success(reviewAction.value === 'approve' ? '审核通过' : '已驳回')
    reviewDialogVisible.value = false
    loadReports()
  } catch (error) {
    console.error('审核失败:', error)
  } finally {
    reviewLoading.value = false
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

const handlePreview = (id) => {
  handlePreviewReport(id, previewLoading)
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

const formatTitle = (row) => {
  if (row?.title) return row.title
  return `思想汇报 (${row.year}年${row.month}月)`
}

const formatPeriod = (row) => {
  return `${row.year}-${String(row.month).padStart(2, '0')}`
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
.review-page {
  width: 100%;
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

.search-bar {
  margin-bottom: 20px;
}

.search-form {
  margin: 0;
}

.upload-tip {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
}
</style>
