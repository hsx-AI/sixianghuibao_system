<template>
  <div class="review-page">
    <!-- 数据表格 -->
    <el-card class="table-card">
      <template #header>
        <div class="card-header">
          <el-icon><EditPen /></el-icon>
          <span>思想汇报审阅</span>
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

          <el-form-item label="提交人">
            <el-input
              v-model="searchForm.submitter"
              placeholder="搜索提交人"
              clearable
            />
          </el-form-item>
          <el-form-item label="状态">
            <el-select
              v-model="searchForm.status"
              placeholder="选择状态"
              clearable
              style="width: 120px"
            >
              <el-option label="待审核" value="pending" />
              <el-option label="已通过" value="approved" />
              <el-option label="已驳回" value="rejected" />
            </el-select>
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
        :data="filteredReports"
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
        <el-table-column prop="zhibu" label="所在支部" width="120">
          <template #default="{ row }">
            {{ row.zhibu || '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status, row.current_step)">
              {{ getStatusText(row.status, row.current_step) }}
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
              type="success"
              size="small"
              :icon="Download"
              @click="handleDownload(row.id)"
            >
              下载
            </el-button>
          </template>
        </el-table-column>
      </el-table>
      
      <el-empty v-if="!loading && filteredReports.length === 0" description="暂无汇报数据" />
    </el-card>
    
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
        <el-descriptions-item label="状态">
          <el-tag :type="getStatusType(currentReport.status, currentReport.current_step)">
            {{ getStatusText(currentReport.status, currentReport.current_step) }}
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
import { ref, reactive, computed, onMounted } from 'vue'
import {
  EditPen,
  Refresh,
  Search,
  RefreshLeft,
  View,
  Download
} from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getAllReports, downloadReport } from '@/api/report'
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
const viewDialogVisible = ref(false)
const currentReport = ref(null)
const previewLoading = ref(false)

const now = new Date()
const currentYear = now.getFullYear().toString()
const currentQuarter = Math.ceil((now.getMonth() + 1) / 3)

const searchForm = reactive({
  type: 'quarter',
  period: '',
  year: currentYear,
  quarter: currentQuarter,
  submitter: '',
  status: ''
})

// 过滤后的报告列表
const filteredReports = computed(() => {
  let result = reports.value
  
  // 按提交人过滤
  if (searchForm.submitter) {
    const keyword = searchForm.submitter.toLowerCase()
    result = result.filter(r => 
      r.submitted_by && r.submitted_by.toLowerCase().includes(keyword)
    )
  }
  
  return result
})

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
    
    // 获取所有报告
    const data = await getAllReports({
      year,
      month,
      quarter,
      status_filter: searchForm.status || undefined
    })
    
    reports.value = data
  } catch (error) {
    console.error('加载报告列表失败:', error)
    ElMessage.error('加载报告列表失败')
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  loadReports()
}

const handleTypeChange = () => {
  // 切换类型时，重置相关字段或保持当前时间
  if (searchForm.type === 'quarter') {
     if (!searchForm.year) searchForm.year = currentYear
     if (!searchForm.quarter) searchForm.quarter = currentQuarter
  }
  loadReports()
}

const handleReset = () => {
  searchForm.type = 'quarter'
  searchForm.year = currentYear
  searchForm.quarter = currentQuarter
  searchForm.period = ''
  searchForm.submitter = ''
  searchForm.status = ''
  loadReports()
}

const handleView = (row) => {
  currentReport.value = row
  viewDialogVisible.value = true
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

const getStatusText = (status, current_step) => {
  if (current_step === 'zzs') return '已通过'
  return REPORT_STATUS_NAMES[status] || status
}

const getStatusType = (status, current_step) => {
  if (current_step === 'zzs') return 'success'
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
  return `${row.year}-${row.month.toString().padStart(2, '0')}`
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

.table-card {
  margin-top: 0;
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

</style>
