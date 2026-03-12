<template>
  <div class="organization-container">
    <el-card class="org-card">
      <template #header>
        <div class="card-header">
          <span class="title">
            <el-icon><Share /></el-icon>
            {{ orgData.name ? `${orgData.name} - 组织架构` : '支部组织架构' }}
          </span>
        </div>
      </template>

      <div v-loading="loading" class="org-content">
        <div v-if="orgData.name" class="zhibu-structure">
          <!-- 支部书记 -->
          <div class="role-section">
            <div class="role-header">
              <span class="role-badge role-zbsj">支部书记</span>
              <span class="member-count">{{ orgData.zbsj?.length || 0 }}人</span>
            </div>
            <div class="role-members">
              <div 
                v-for="user in orgData.zbsj" 
                :key="user.id" 
                class="member-card member-leader"
              >
                <el-avatar :size="48" class="member-avatar avatar-zbsj">
                  {{ user.real_name?.charAt(0) }}
                </el-avatar>
                <div class="member-info">
                  <span class="member-name">{{ user.real_name }}</span>
                  <span class="member-role">支部书记</span>
                </div>
              </div>
              <div v-if="!orgData.zbsj?.length" class="no-data">暂无支部书记</div>
            </div>
          </div>

          <!-- 组织委员 -->
          <div class="role-section">
            <div class="role-header">
              <span class="role-badge role-zzwy">组织委员</span>
              <span class="member-count">{{ orgData.zzwy?.length || 0 }}人</span>
            </div>
            <div class="role-members">
              <div 
                v-for="user in orgData.zzwy" 
                :key="user.id" 
                class="member-card member-leader"
              >
                <el-avatar :size="48" class="member-avatar avatar-zzwy">
                  {{ user.real_name?.charAt(0) }}
                </el-avatar>
                <div class="member-info">
                  <span class="member-name">{{ user.real_name }}</span>
                  <span class="member-role">组织委员</span>
                </div>
              </div>
              <div v-if="!orgData.zzwy?.length" class="no-data">暂无组织委员</div>
            </div>
          </div>

          <!-- 培养人 -->
          <div class="role-section">
            <div class="role-header">
              <span class="role-badge role-pyr">培养人</span>
              <span class="member-count">{{ orgData.pyr?.length || 0 }}人</span>
            </div>
            <div class="role-members">
              <div 
                v-for="user in orgData.pyr" 
                :key="user.id" 
                class="member-card"
              >
                <el-avatar :size="40" class="member-avatar avatar-pyr">
                  {{ user.real_name?.charAt(0) }}
                </el-avatar>
                <div class="member-info">
                  <span class="member-name">{{ user.real_name }}</span>
                  <span class="member-role">培养人</span>
                </div>
              </div>
              <div v-if="!orgData.pyr?.length" class="no-data">暂无培养人</div>
            </div>
          </div>

          <!-- 积极分子 -->
          <div class="role-section role-section-activist">
            <div class="role-header">
              <span class="role-badge role-activist">积极分子</span>
              <span class="member-count">{{ orgData.activist?.length || 0 }}人</span>
            </div>
            <div class="activist-grid">
              <div 
                v-for="user in orgData.activist" 
                :key="user.id" 
                class="activist-card"
              >
                <div class="activist-main">
                  <el-avatar :size="40" class="member-avatar avatar-activist">
                    {{ user.real_name?.charAt(0) }}
                  </el-avatar>
                  <span class="activist-name">{{ user.real_name }}</span>
                </div>
                <div class="activist-trainers" v-if="user.pyr1 || user.pyr2">
                  <el-icon><Connection /></el-icon>
                  <span class="trainer-label">培养人:</span>
                  <span class="trainer-names">
                    <span v-if="user.pyr1">{{ user.pyr1 }}</span>
                    <span v-if="user.pyr1 && user.pyr2">、</span>
                    <span v-if="user.pyr2">{{ user.pyr2 }}</span>
                  </span>
                </div>
                <div class="activist-trainers no-trainer" v-else>
                  <span class="trainer-label">暂无培养人</span>
                </div>
              </div>
              <div v-if="!orgData.activist?.length" class="no-data full-width">暂无积极分子</div>
            </div>
          </div>
        </div>

        <div v-else-if="!loading" class="empty-state">
          <el-empty description="暂无组织架构数据" />
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { Share, Connection } from '@element-plus/icons-vue'
import { getZhibuOrganization } from '@/api/user'
import { ElMessage } from 'element-plus'

const loading = ref(false)
const orgData = ref({
  name: '',
  zbsj: [],
  zzwy: [],
  pyr: [],
  activist: []
})

const fetchData = async () => {
  loading.value = true
  try {
    const res = await getZhibuOrganization()
    orgData.value = res.data || res
  } catch (error) {
    console.error('获取组织架构失败:', error)
    ElMessage.error('获取组织架构数据失败')
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchData()
})
</script>

<style scoped>
.organization-container {
  min-height: calc(100vh - 180px);
}

.org-card {
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

.org-content {
  padding: 8px 0;
}

.zhibu-structure {
  display: flex;
  flex-direction: column;
  gap: 28px;
}

.role-section {
  background: #f8fafc;
  border-radius: 16px;
  padding: 20px;
  border: 1px solid #e2e8f0;
}

.role-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px dashed #e2e8f0;
}

.role-badge {
  padding: 6px 16px;
  border-radius: 20px;
  font-size: 14px;
  font-weight: 600;
}

.role-zbsj {
  background: linear-gradient(135deg, #fef3c7, #fde68a);
  color: #92400e;
}

.role-zzwy {
  background: linear-gradient(135deg, #dbeafe, #bfdbfe);
  color: #1e40af;
}

.role-pyr {
  background: linear-gradient(135deg, #d1fae5, #a7f3d0);
  color: #065f46;
}

.role-activist {
  background: linear-gradient(135deg, #e0e7ff, #c7d2fe);
  color: #3730a3;
}

.member-count {
  color: #64748b;
  font-size: 13px;
}

.role-members {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
}

.member-card {
  display: flex;
  align-items: center;
  gap: 12px;
  background: #fff;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  padding: 12px 16px;
  min-width: 180px;
  transition: transform 0.2s, box-shadow 0.2s;
}

.member-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(15, 23, 42, 0.08);
}

.member-leader {
  background: linear-gradient(135deg, #fff 0%, #f8fafc 100%);
  border-color: #cbd5e1;
}

.member-avatar {
  font-weight: 600;
  color: #fff;
}

.avatar-zbsj {
  background: linear-gradient(135deg, #f59e0b, #d97706);
}

.avatar-zzwy {
  background: linear-gradient(135deg, #3b82f6, #2563eb);
}

.avatar-pyr {
  background: linear-gradient(135deg, #10b981, #059669);
}

.avatar-activist {
  background: linear-gradient(135deg, #8b5cf6, #7c3aed);
}

.member-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.member-name {
  font-size: 15px;
  font-weight: 600;
  color: #1e293b;
}

.member-role {
  font-size: 12px;
  color: #64748b;
}

.no-data {
  color: #94a3b8;
  font-size: 14px;
  font-style: italic;
  padding: 8px;
}

.full-width {
  width: 100%;
  text-align: center;
}

/* 积极分子网格 */
.activist-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 16px;
}

.activist-card {
  background: #fff;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  padding: 14px 16px;
  display: flex;
  flex-direction: column;
  gap: 10px;
  transition: transform 0.2s, box-shadow 0.2s;
}

.activist-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(15, 23, 42, 0.08);
}

.activist-main {
  display: flex;
  align-items: center;
  gap: 12px;
}

.activist-name {
  font-size: 15px;
  font-weight: 600;
  color: #1e293b;
}

.activist-trainers {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 12px;
  background: #f0fdf4;
  border-radius: 8px;
  font-size: 13px;
}

.activist-trainers .el-icon {
  color: #059669;
}

.trainer-label {
  color: #64748b;
}

.trainer-names {
  color: #059669;
  font-weight: 500;
}

.no-trainer {
  background: #f8fafc;
}

.no-trainer .trainer-label {
  color: #94a3b8;
  font-style: italic;
}

.empty-state {
  padding: 40px;
}

@media (max-width: 768px) {
  .activist-grid {
    grid-template-columns: 1fr;
  }
  
  .member-card {
    min-width: auto;
    flex: 1;
  }
}
</style>













