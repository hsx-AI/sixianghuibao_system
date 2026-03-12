<template>
  <div class="organization-container">
    <el-card class="org-card">
      <template #header>
        <div class="card-header">
          <span class="title">
            <el-icon><Share /></el-icon>
            组织架构
          </span>
        </div>
      </template>

      <div v-loading="loading" class="org-tree">
        <!-- 党总支（顶层） -->
        <div class="org-level org-level-top">
          <div class="org-node org-node-zzs">
            <div class="node-title">党总支</div>
            <div class="node-members">
              <div v-for="user in orgData.zzs" :key="user.id" class="member-item">
                <el-avatar :size="40" class="member-avatar">
                  {{ user.real_name?.charAt(0) }}
                </el-avatar>
                <span class="member-name">{{ user.real_name }}</span>
              </div>
              <div v-if="!orgData.zzs?.length" class="no-member">暂无</div>
            </div>
          </div>
        </div>

        <!-- 连接线 -->
        <div class="org-connector">
          <div class="connector-line"></div>
        </div>

        <!-- 支部列表 -->
        <div class="org-level org-level-zhibu">
          <div 
            v-for="zhibu in orgData.zhibu_list" 
            :key="zhibu.name" 
            class="zhibu-card"
          >
            <div class="zhibu-header">
              <el-icon><OfficeBuilding /></el-icon>
              <span>{{ zhibu.name }}</span>
            </div>
            
            <div class="zhibu-content">
              <!-- 支部书记 -->
              <div class="role-section">
                <div class="role-title">
                  <span class="role-badge role-zbsj">支部书记</span>
                </div>
                <div class="role-members">
                  <div 
                    v-for="user in zhibu.zbsj" 
                    :key="user.id" 
                    class="member-chip"
                  >
                    <el-avatar :size="28" class="chip-avatar">
                      {{ user.real_name?.charAt(0) }}
                    </el-avatar>
                    <span>{{ user.real_name }}</span>
                  </div>
                  <span v-if="!zhibu.zbsj?.length" class="no-data">暂无</span>
                </div>
              </div>

              <!-- 组织委员 -->
              <div class="role-section">
                <div class="role-title">
                  <span class="role-badge role-zzwy">组织委员</span>
                </div>
                <div class="role-members">
                  <div 
                    v-for="user in zhibu.zzwy" 
                    :key="user.id" 
                    class="member-chip"
                  >
                    <el-avatar :size="28" class="chip-avatar">
                      {{ user.real_name?.charAt(0) }}
                    </el-avatar>
                    <span>{{ user.real_name }}</span>
                  </div>
                  <span v-if="!zhibu.zzwy?.length" class="no-data">暂无</span>
                </div>
              </div>

              <!-- 培养人 -->
              <div class="role-section">
                <div class="role-title">
                  <span class="role-badge role-pyr">培养人</span>
                </div>
                <div class="role-members">
                  <div 
                    v-for="user in zhibu.pyr" 
                    :key="user.id" 
                    class="member-chip"
                  >
                    <el-avatar :size="28" class="chip-avatar">
                      {{ user.real_name?.charAt(0) }}
                    </el-avatar>
                    <span>{{ user.real_name }}</span>
                  </div>
                  <span v-if="!zhibu.pyr?.length" class="no-data">暂无</span>
                </div>
              </div>

              <!-- 积极分子 -->
              <div class="role-section role-section-activist">
                <div class="role-title">
                  <span class="role-badge role-activist">积极分子</span>
                  <span class="member-count">{{ zhibu.activist?.length || 0 }}人</span>
                </div>
                <div class="activist-list">
                  <div 
                    v-for="user in zhibu.activist" 
                    :key="user.id" 
                    class="activist-item"
                  >
                    <div class="activist-main">
                      <el-avatar :size="32" class="activist-avatar">
                        {{ user.real_name?.charAt(0) }}
                      </el-avatar>
                      <span class="activist-name">{{ user.real_name }}</span>
                    </div>
                    <div class="activist-trainers" v-if="user.pyr1 || user.pyr2">
                      <span class="trainer-label">培养人:</span>
                      <span class="trainer-name" v-if="user.pyr1">{{ user.pyr1 }}</span>
                      <span class="trainer-sep" v-if="user.pyr1 && user.pyr2">、</span>
                      <span class="trainer-name" v-if="user.pyr2">{{ user.pyr2 }}</span>
                    </div>
                  </div>
                  <div v-if="!zhibu.activist?.length" class="no-data">暂无积极分子</div>
                </div>
              </div>
            </div>
          </div>

          <div v-if="!orgData.zhibu_list?.length && !loading" class="empty-state">
            <el-empty description="暂无组织架构数据" />
          </div>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { Share, OfficeBuilding } from '@element-plus/icons-vue'
import { getOrganizationStructure } from '@/api/user'
import { ElMessage } from 'element-plus'

const loading = ref(false)
const orgData = ref({
  zzs: [],
  zhibu_list: []
})

const fetchData = async () => {
  loading.value = true
  try {
    const res = await getOrganizationStructure()
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

.org-tree {
  padding: 24px 0;
}

/* 顶层 - 党总支 */
.org-level-top {
  display: flex;
  justify-content: center;
  margin-bottom: 16px;
}

.org-node-zzs {
  background: linear-gradient(135deg, #dc2626 0%, #b91c1c 100%);
  border-radius: 16px;
  padding: 20px 40px;
  text-align: center;
  box-shadow: 0 8px 24px rgba(220, 38, 38, 0.25);
  min-width: 200px;
}

.org-node-zzs .node-title {
  color: rgba(255, 255, 255, 0.9);
  font-size: 13px;
  font-weight: 500;
  margin-bottom: 12px;
  letter-spacing: 1px;
}

.org-node-zzs .node-members {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 12px;
}

.org-node-zzs .member-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
}

.org-node-zzs .member-avatar {
  background: rgba(255, 255, 255, 0.2);
  color: #fff;
  font-weight: 600;
  border: 2px solid rgba(255, 255, 255, 0.4);
}

.org-node-zzs .member-name {
  color: #fff;
  font-size: 15px;
  font-weight: 600;
}

.org-node-zzs .no-member {
  color: rgba(255, 255, 255, 0.7);
  font-size: 14px;
}

/* 连接线 */
.org-connector {
  display: flex;
  justify-content: center;
  padding: 8px 0;
}

.connector-line {
  width: 2px;
  height: 32px;
  background: linear-gradient(180deg, #dc2626, #64748b);
}

/* 支部层级 */
.org-level-zhibu {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(340px, 1fr));
  gap: 24px;
  padding: 0 8px;
}

.zhibu-card {
  background: #fff;
  border-radius: 16px;
  border: 1px solid rgba(226, 232, 240, 0.8);
  overflow: hidden;
  box-shadow: 0 4px 16px rgba(15, 23, 42, 0.06);
  transition: transform 0.25s ease, box-shadow 0.25s ease;
}

.zhibu-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(15, 23, 42, 0.1);
}

.zhibu-header {
  background: linear-gradient(135deg, #0f172a 0%, #1e3a5f 100%);
  color: #fff;
  padding: 14px 20px;
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 16px;
  font-weight: 600;
}

.zhibu-content {
  padding: 16px 20px;
}

.role-section {
  margin-bottom: 16px;
  padding-bottom: 16px;
  border-bottom: 1px dashed #e2e8f0;
}

.role-section:last-child {
  margin-bottom: 0;
  padding-bottom: 0;
  border-bottom: none;
}

.role-title {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 10px;
}

.role-badge {
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 12px;
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
  font-size: 12px;
}

.role-members {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.member-chip {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 20px;
  padding: 4px 12px 4px 4px;
  font-size: 13px;
  color: #334155;
}

.chip-avatar {
  background: linear-gradient(135deg, #6366f1, #8b5cf6);
  color: #fff;
  font-size: 11px;
  font-weight: 600;
}

.no-data {
  color: #94a3b8;
  font-size: 13px;
  font-style: italic;
}

/* 积极分子列表 */
.activist-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.activist-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: #f8fafc;
  border-radius: 10px;
  padding: 10px 14px;
  border: 1px solid #e2e8f0;
}

.activist-main {
  display: flex;
  align-items: center;
  gap: 10px;
}

.activist-avatar {
  background: linear-gradient(135deg, #8b5cf6, #a78bfa);
  color: #fff;
  font-weight: 600;
}

.activist-name {
  font-size: 14px;
  font-weight: 500;
  color: #1e293b;
}

.activist-trainers {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
}

.trainer-label {
  color: #94a3b8;
}

.trainer-name {
  color: #059669;
  font-weight: 500;
}

.trainer-sep {
  color: #94a3b8;
}

.empty-state {
  grid-column: 1 / -1;
  padding: 40px;
}

@media (max-width: 768px) {
  .org-level-zhibu {
    grid-template-columns: 1fr;
  }
  
  .org-node-zzs {
    min-width: auto;
    padding: 16px 24px;
  }
  
  .activist-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }
}
</style>




