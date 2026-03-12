<template>
  <div class="overview-page">
    <!-- 月份选择 -->
    <el-card class="toolbar-card">
      <div class="overview-toolbar">
        <div class="toolbar-title">统计期间</div>
        <el-radio-group v-model="searchForm.type" @change="handleTypeChange">
          <el-radio-button label="month">月度</el-radio-button>
          <el-radio-button label="quarter">季度</el-radio-button>
        </el-radio-group>

        <template v-if="searchForm.type === 'month'">
          <el-date-picker
            v-model="searchForm.period"
            type="month"
            placeholder="选择月份"
            format="YYYY-MM"
            value-format="YYYY-MM"
            clearable
            style="width: 160px"
            @change="loadReports"
          />
          <el-button :icon="Select" @click="setCurrentMonth">本月</el-button>
        </template>

        <template v-else>
          <el-date-picker
            v-model="searchForm.year"
            type="year"
            placeholder="选择年份"
            value-format="YYYY"
            style="width: 120px"
            @change="loadReports"
          />
          <el-select v-model="searchForm.quarter" placeholder="选择季度" style="width: 120px" @change="loadReports">
            <el-option label="第一季度" :value="1" />
            <el-option label="第二季度" :value="2" />
            <el-option label="第三季度" :value="3" />
            <el-option label="第四季度" :value="4" />
          </el-select>
          <el-button :icon="Select" @click="setCurrentQuarter">本季度</el-button>
        </template>

        <el-button type="primary" :icon="Refresh" @click="loadReports">刷新</el-button>
      </div>
    </el-card>

    <!-- 统计卡片 -->
    <div class="stats-cards">
      <el-card class="stat-card">
        <div class="stat-content">
          <div class="stat-icon" style="background: #ecf5ff; color: #409eff;">
            <el-icon><Document /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.total }}</div>
            <div class="stat-label">积极分子总数</div>
          </div>
        </div>
      </el-card>
      
      <el-card class="stat-card">
        <div class="stat-content">
          <div class="stat-icon" style="background: #f0f9ff; color: #67c23a;">
            <el-icon><CircleCheck /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.submitted }}</div>
            <div class="stat-label">已提交</div>
            <div class="stat-detail">
              <span class="detail-item">正在审核: {{ reviewStats.inReview }}</span>
              <span class="detail-item">已通过: {{ reviewStats.passed }}</span>
            </div>
          </div>
        </div>
      </el-card>
      
      <el-card class="stat-card">
        <div class="stat-content">
          <div class="stat-icon" style="background: #fef0f0; color: #f56c6c;">
            <el-icon><Clock /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.missing }}</div>
            <div class="stat-label">未提交</div>
          </div>
        </div>
      </el-card>
      
      <el-card class="stat-card">
        <div class="stat-content">
          <div class="stat-icon" style="background: #fff7e6; color: #e6a23c;">
            <el-icon><DataAnalysis /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ submissionRate }}</div>
            <div class="stat-label">提交率</div>
          </div>
        </div>
      </el-card>
    </div>
     
    <!-- 支部统计 -->
    <el-card class="table-card">
      <template #header>
        <div class="card-header">
          <el-icon><DataAnalysis /></el-icon>
          <span>支部统计（{{ statsPeriodText }}）</span>
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
        v-loading="zzsStatsLoading"
        :data="zhibuStatsRows"
        stripe
        style="width: 100%"
      >
        <el-table-column prop="zhibu" label="支部" min-width="120" />
        <el-table-column prop="activist_count" label="积极分子人数" width="120" />
        <el-table-column prop="submitted_reports" label="本月已交" width="100" />
        <el-table-column prop="missing_activists" label="本月未交" width="100" />
      </el-table>

      <el-empty
        v-if="!zzsStatsLoading && zhibuStatsRows.length === 0"
        description="暂无统计数据"
      />
    </el-card>

    <!-- 未交名单 -->
    <el-card class="table-card">
      <template #header>
        <div class="card-header">
          <el-icon><Clock /></el-icon>
          <span>未交名单（{{ statsPeriodText }}）</span>
        </div>
      </template>

      <el-table
        v-loading="zzsStatsLoading"
        :data="missingRows"
        stripe
        style="width: 100%"
      >
        <el-table-column prop="zhibu" label="支部" width="150" />
        <el-table-column prop="real_name" label="姓名" width="120" />
        <el-table-column prop="trainers" label="培养联系人" min-width="150" />
      </el-table>

      <el-empty
        v-if="!zzsStatsLoading && zzsStats && missingRows.length === 0"
        description="本月全部按时上交"
      />
    </el-card>

  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import {
  DataAnalysis,
  Document,
  Clock,
  CircleCheck,
  CircleClose,
  Refresh,
  Select
} from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { getZzsStats } from '@/api/report'

const zzsStatsLoading = ref(false)
const zzsStats = ref(null)

const searchForm = reactive({
  type: 'month',
  period: '',
  year: String(new Date().getFullYear()),
  quarter: null
})

// 统计数据
const stats = computed(() => {
  if (!zzsStats.value?.overall) {
    return {
      total: 0,
      missing: 0,
      submitted: 0,
      submittedPeople: 0,
      approved: 0,
      approvedPeople: 0
    }
  }
  const overall = zzsStats.value.overall
  return {
    total: overall.activist_count || 0,          // 积极分子总人数
    missing: overall.missing_activists || 0,     // 未交人数（按 user_id 去重）
    submitted: overall.submitted_reports || 0,   // 已交报告数（按 report.id 计数）
    submittedPeople: overall.submitted_activists || 0, // 已交人数（按 user_id 去重）
    approved: overall.approved_reports || 0,     // 最终已通过报告数
    approvedPeople: overall.approved_activists || 0 // 最终已通过人数（按 user_id 去重）
  }
})

// 审核状态统计
const reviewStats = computed(() => {
  const passed = stats.value.approved
  const inReview = Math.max(0, stats.value.submitted - passed)

  return {
    inReview, // 正在审核中（培养人/组织委员/支部书记/党总支待审）
    passed    // 已通过（最终通过）
  }
})

// 提交率
const submissionRate = computed(() => {
  if (!stats.value.total) return '0%'
  const rate = ((stats.value.submittedPeople / stats.value.total) * 100).toFixed(1)
  return `${rate}%`
})

const statsPeriodText = computed(() => {
  if (zzsStats.value?.year) {
    if (zzsStats.value.month) {
      return `${zzsStats.value.year}-${String(zzsStats.value.month).padStart(2, '0')}`
    } else if (zzsStats.value.quarter) {
      return `${zzsStats.value.year}年第${zzsStats.value.quarter}季度`
    }
  }
  return '—'
})

const zhibuStatsRows = computed(() => {
  return zzsStats.value?.by_zhibu || []
})

const missingRows = computed(() => {
  return zzsStats.value?.missing_list || []
})

const loadReports = async () => {
  zzsStatsLoading.value = true
  try {
    const statsParams = {}
    
    if (searchForm.type === 'month') {
      if (searchForm.period) {
        const [y, m] = searchForm.period.split('-')
        statsParams.year = parseInt(y)
        statsParams.month = parseInt(m)
      }
    } else {
      if (searchForm.year && searchForm.quarter) {
        statsParams.year = parseInt(searchForm.year)
        statsParams.quarter = searchForm.quarter
      }
    }

    if (statsParams.year && (statsParams.month || statsParams.quarter)) {
      zzsStats.value = await getZzsStats(statsParams)
    }
  } catch (error) {
    console.error('加载统计数据失败:', error)
    ElMessage.error('加载统计数据失败')
  } finally {
    zzsStatsLoading.value = false
  }
}

const setCurrentMonth = () => {
  const now = new Date()
  const year = now.getFullYear()
  const month = String(now.getMonth() + 1).padStart(2, '0')
  searchForm.period = `${year}-${month}`
  loadReports()
}

const setCurrentQuarter = () => {
  const now = new Date()
  searchForm.year = String(now.getFullYear())
  searchForm.quarter = Math.floor(now.getMonth() / 3) + 1
  loadReports()
}

const handleTypeChange = () => {
  // 切换类型时，重置为当前时间
  if (searchForm.type === 'month') {
    if (!searchForm.period) setCurrentMonth()
  } else {
    if (!searchForm.quarter) setCurrentQuarter()
  }
  loadReports()
}

onMounted(() => {
  setCurrentQuarter()
})
</script>

<style scoped>
.overview-page {
  width: 100%;
}

.toolbar-card {
  margin-bottom: 20px;
}

.overview-toolbar {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.toolbar-title {
  font-weight: 600;
  color: #303133;
}

.stats-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 20px;
  margin-bottom: 20px;
}

.stat-card {
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
}

.stat-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.stat-content {
  display: flex;
  align-items: center;
  gap: 16px;
}

.stat-icon {
  width: 56px;
  height: 56px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 28px;
}

.stat-info {
  flex: 1;
}

.stat-value {
  font-size: 28px;
  font-weight: 600;
  color: #303133;
  line-height: 1;
  margin-bottom: 8px;
}

.stat-label {
  font-size: 14px;
  color: #909399;
}

.stat-detail {
  display: flex;
  gap: 12px;
  margin-top: 8px;
  font-size: 12px;
  color: #606266;
}

.detail-item {
  padding: 2px 8px;
  background: rgba(0, 0, 0, 0.04);
  border-radius: 4px;
}

.table-card {
  margin-top: 20px;
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

@media (max-width: 768px) {
  .stats-cards {
    grid-template-columns: 1fr;
  }
}
</style>
