<template>
  <div class="report-management">
    <el-card class="main-card">
      <template #header>
        <div class="card-header">
          <span class="title">
            <el-icon><Document /></el-icon>
            文件管理
          </span>
          <div class="filters">
            <el-radio-group v-model="filterType" style="margin-right: 15px" @change="handleTypeChange">
              <el-radio-button label="month">月度</el-radio-button>
              <el-radio-button label="quarter">季度</el-radio-button>
            </el-radio-group>

            <template v-if="filterType === 'month'">
              <el-date-picker
                v-model="filterMonth"
                type="month"
                placeholder="选择月份"
                format="YYYY年MM月"
                value-format="YYYY-MM"
                clearable
                style="width: 150px; margin-right: 10px"
                @change="fetchData"
              />
            </template>
            <template v-else>
               <el-date-picker
                v-model="filterYear"
                type="year"
                placeholder="选择年份"
                value-format="YYYY"
                style="width: 120px; margin-right: 10px"
                @change="fetchData"
              />
              <el-select v-model="filterQuarter" placeholder="选择季度" style="width: 120px; margin-right: 10px" @change="fetchData">
                <el-option label="第一季度" :value="1" />
                <el-option label="第二季度" :value="2" />
                <el-option label="第三季度" :value="3" />
                <el-option label="第四季度" :value="4" />
              </el-select>
            </template>

            <el-select 
              v-model="filterStatus" 
              placeholder="状态筛选" 
              clearable 
              style="width: 120px"
              @change="fetchData"
            >
              <el-option label="待审核" value="pending" />
              <el-option label="已通过" value="approved" />
              <el-option label="已驳回" value="rejected" />
            </el-select>
          </div>
        </div>
      </template>

      <el-table 
        v-loading="loading" 
        :data="reportList" 
        stripe 
        border
        style="width: 100%"
      >
        <el-table-column prop="id" label="ID" width="70" align="center" />
        <el-table-column prop="submitted_by" label="提交人" width="100" />
        <el-table-column prop="zhibu" label="支部" width="120">
          <template #default="{ row }">
            {{ row.zhibu || '-' }}
          </template>
        </el-table-column>
        <el-table-column label="汇报时间" width="110">
          <template #default="{ row }">
            {{ row.year }}年{{ row.month }}月
          </template>
        </el-table-column>
        <el-table-column prop="current_step" label="当前步骤" width="120">
          <template #default="{ row }">
            <el-tag size="small" type="info">
              {{ getStepName(row.current_step) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)" size="small">
              {{ getStatusName(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="uploaded_time" label="上传时间" width="170">
          <template #default="{ row }">
            {{ formatDate(row.uploaded_time) }}
          </template>
        </el-table-column>
        <el-table-column prop="file_path" label="文件路径" min-width="200">
          <template #default="{ row }">
            <span class="file-path">{{ row.file_path }}</span>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link size="small" @click="handlePreview(row)">
              <el-icon><View /></el-icon>
              预览
            </el-button>
            <el-button type="warning" link size="small" @click="handleEdit(row)">
              <el-icon><Edit /></el-icon>
              编辑
            </el-button>
            <el-button type="danger" link size="small" @click="handleDelete(row)">
              <el-icon><Delete /></el-icon>
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 编辑对话框 -->
    <el-dialog 
      v-model="dialogVisible" 
      title="编辑报告"
      width="450px"
      destroy-on-close
    >
      <el-form 
        ref="formRef" 
        :model="formData" 
        :rules="formRules" 
        label-width="100px"
      >
        <el-form-item label="年份" prop="year">
          <el-input-number v-model="formData.year" :min="2020" :max="2100" style="width: 100%" />
        </el-form-item>
        <el-form-item label="月份" prop="month">
          <el-input-number v-model="formData.month" :min="1" :max="12" style="width: 100%" />
        </el-form-item>
        <el-form-item label="当前步骤" prop="current_step">
          <el-select v-model="formData.current_step" style="width: 100%">
            <el-option label="培养人审核" value="pyr" />
            <el-option label="组织委员审核" value="zzwy" />
            <el-option label="支部书记审核" value="zbsj" />
            <el-option label="党总支查看" value="zzs" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态" prop="status">
          <el-select v-model="formData.status" style="width: 100%">
            <el-option label="待审核" value="pending" />
            <el-option label="已通过" value="approved" />
            <el-option label="已驳回" value="rejected" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="submitting">
          确定
        </el-button>
      </template>
    </el-dialog>


  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { Document, View, Edit, Delete, Loading } from '@element-plus/icons-vue'
import { getAdminReportList, adminUpdateReport, adminDeleteReport } from '@/api/report'
import { handlePreviewReport } from '@/utils/preview'
import { CURRENT_STEP_NAMES, REPORT_STATUS_NAMES, REPORT_STATUS_TYPES } from '@/utils/constants'
import { ElMessage, ElMessageBox } from 'element-plus'

const loading = ref(false)
const submitting = ref(false)
const reportList = ref([])
const dialogVisible = ref(false)
const formRef = ref(null)
const currentReportId = ref(null)

// 初始化默认时间
const now = new Date()
const currentYearStr = now.getFullYear().toString()
const currentQuarterVal = Math.ceil((now.getMonth() + 1) / 3)

const filterType = ref('quarter')
const filterYear = ref(currentYearStr)
const filterQuarter = ref(currentQuarterVal)
const filterMonth = ref('')
const filterStatus = ref('')

const previewLoading = ref(false)

const formData = ref({
  year: 2024,
  month: 1,
  current_step: '',
  status: ''
})

const formRules = {
  year: [{ required: true, message: '请输入年份', trigger: 'blur' }],
  month: [{ required: true, message: '请输入月份', trigger: 'blur' }]
}

const getStepName = (step) => {
  return CURRENT_STEP_NAMES[step] || step
}

const getStatusName = (status) => {
  return REPORT_STATUS_NAMES[status] || status
}

const getStatusType = (status) => {
  return REPORT_STATUS_TYPES[status] || 'info'
}

const formatDate = (dateStr) => {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN')
}

const fetchData = async () => {
  loading.value = true
  try {
    const params = {}
    
    if (filterType.value === 'month' && filterMonth.value) {
      const [year, month] = filterMonth.value.split('-')
      params.year = parseInt(year)
      params.month = parseInt(month)
    } else if (filterType.value === 'quarter') {
      if (filterYear.value) params.year = parseInt(filterYear.value)
      if (filterQuarter.value) params.quarter = filterQuarter.value
    }

    if (filterStatus.value) {
      params.status_filter = filterStatus.value
    }
    
    const res = await getAdminReportList(params)
    reportList.value = res.data || res
  } catch (error) {
    console.error('获取报告列表失败:', error)
    ElMessage.error('获取报告列表失败')
  } finally {
    loading.value = false
  }
}

const handleTypeChange = () => {
  if (filterType.value === 'quarter') {
    if (!filterYear.value) filterYear.value = currentYearStr
    if (!filterQuarter.value) filterQuarter.value = currentQuarterVal
  }
  fetchData()
}

const handlePreview = (row) => {
  handlePreviewReport(row.id, previewLoading)
}

const handleEdit = (row) => {
  currentReportId.value = row.id
  formData.value = {
    year: row.year,
    month: row.month,
    current_step: row.current_step,
    status: row.status
  }
  dialogVisible.value = true
}

const handleSubmit = async () => {
  if (!formRef.value) return
  
  try {
    await formRef.value.validate()
  } catch {
    return
  }
  
  submitting.value = true
  try {
    await adminUpdateReport(currentReportId.value, formData.value)
    ElMessage.success('报告更新成功')
    dialogVisible.value = false
    fetchData()
  } catch (error) {
    console.error('更新失败:', error)
    ElMessage.error(error.response?.data?.detail || '更新失败')
  } finally {
    submitting.value = false
  }
}

const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除 ${row.submitted_by} 的 ${row.year}年${row.month}月 报告吗？此操作将同时删除文件，不可恢复。`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    await adminDeleteReport(row.id)
    ElMessage.success('删除成功')
    fetchData()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除失败:', error)
      ElMessage.error(error.response?.data?.detail || '删除失败')
    }
  }
}

onMounted(() => {
  fetchData()
})
</script>

<style scoped>
.report-management {
  min-height: calc(100vh - 180px);
}

.main-card {
  background: linear-gradient(145deg, rgba(255, 255, 255, 0.98), rgba(248, 250, 255, 0.95));
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.card-header .title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 18px;
  font-weight: 600;
  color: #1e293b;
}

.filters {
  display: flex;
  gap: 12px;
}

:deep(.el-table) {
  border-radius: 8px;
}

:deep(.el-table th) {
  background: #f8fafc !important;
}

.file-path {
  font-size: 12px;
  color: #64748b;
  word-break: break-all;
}


</style>




