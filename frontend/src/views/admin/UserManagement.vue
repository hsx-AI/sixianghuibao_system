<template>
  <div class="user-management">
    <el-card class="main-card">
      <template #header>
        <div class="card-header">
          <span class="title">
            <el-icon><User /></el-icon>
            人员管理
          </span>
          <el-button type="primary" @click="handleAdd">
            <el-icon><Plus /></el-icon>
            新增人员
          </el-button>
        </div>
      </template>

      <el-table 
        v-loading="loading" 
        :data="userList" 
        stripe 
        border
        style="width: 100%"
      >
        <el-table-column prop="id" label="ID" width="70" align="center" />
        <el-table-column prop="username" label="用户名" width="120" />
        <el-table-column prop="real_name" label="姓名" width="100" />
        <el-table-column prop="role" label="角色" width="100">
          <template #default="{ row }">
            <el-tag :type="getRoleType(row.role)" size="small">
              {{ getRoleName(row.role) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="zhibu" label="所属支部" width="120">
          <template #default="{ row }">
            {{ row.zhibu || '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="pyr1" label="培养人1" width="100">
          <template #default="{ row }">
            {{ row.pyr1 || '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="pyr2" label="培养人2" width="100">
          <template #default="{ row }">
            {{ row.pyr2 || '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="170">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link size="small" @click="handleEdit(row)">
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

    <!-- 新增/编辑对话框 -->
    <el-dialog 
      v-model="dialogVisible" 
      :title="isEdit ? '编辑人员' : '新增人员'"
      width="500px"
      destroy-on-close
    >
      <el-form 
        ref="formRef" 
        :model="formData" 
        :rules="formRules" 
        label-width="100px"
      >
        <el-form-item label="用户名" prop="username">
          <el-input v-model="formData.username" placeholder="请输入用户名" />
        </el-form-item>
        <el-form-item label="密码" :prop="isEdit ? '' : 'password'">
          <el-input 
            v-model="formData.password" 
            type="password" 
            :placeholder="isEdit ? '留空则不修改密码' : '请输入密码'"
            show-password
          />
        </el-form-item>
        <el-form-item label="姓名" prop="real_name">
          <el-input v-model="formData.real_name" placeholder="请输入真实姓名" />
        </el-form-item>
        <el-form-item label="角色" prop="role">
          <el-select v-model="formData.role" placeholder="请选择角色" style="width: 100%">
            <el-option 
              v-for="(name, key) in ROLE_NAMES" 
              :key="key" 
              :label="name" 
              :value="key" 
            />
          </el-select>
        </el-form-item>
        <el-form-item label="所属支部">
          <el-input v-model="formData.zhibu" placeholder="请输入所属支部" />
        </el-form-item>
        <el-form-item label="培养人1" v-if="formData.role === 'activist'">
          <el-input v-model="formData.pyr1" placeholder="请输入培养人1姓名" />
        </el-form-item>
        <el-form-item label="培养人2" v-if="formData.role === 'activist'">
          <el-input v-model="formData.pyr2" placeholder="请输入培养人2姓名" />
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
import { User, Plus, Edit, Delete } from '@element-plus/icons-vue'
import { getUserList, createUser, updateUser, deleteUser } from '@/api/user'
import { ROLE_NAMES } from '@/utils/constants'
import { ElMessage, ElMessageBox } from 'element-plus'

const loading = ref(false)
const submitting = ref(false)
const userList = ref([])
const dialogVisible = ref(false)
const isEdit = ref(false)
const formRef = ref(null)
const currentUserId = ref(null)

const formData = ref({
  username: '',
  password: '',
  real_name: '',
  role: '',
  zhibu: '',
  pyr1: '',
  pyr2: ''
})

const formRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 2, max: 50, message: '长度在 2 到 50 个字符', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 4, max: 50, message: '长度在 4 到 50 个字符', trigger: 'blur' }
  ],
  real_name: [
    { required: true, message: '请输入真实姓名', trigger: 'blur' }
  ],
  role: [
    { required: true, message: '请选择角色', trigger: 'change' }
  ]
}

const getRoleName = (role) => {
  return ROLE_NAMES[role] || role
}

const getRoleType = (role) => {
  const types = {
    admin: 'danger',
    activist: 'info',
    pyr: 'success',
    zzwy: 'warning',
    zbsj: '',
    zzs: 'danger'
  }
  return types[role] || 'info'
}

const formatDate = (dateStr) => {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN')
}

const fetchData = async () => {
  loading.value = true
  try {
    const res = await getUserList()
    userList.value = res.data || res
  } catch (error) {
    console.error('获取用户列表失败:', error)
    ElMessage.error('获取用户列表失败')
  } finally {
    loading.value = false
  }
}

const resetForm = () => {
  formData.value = {
    username: '',
    password: '',
    real_name: '',
    role: '',
    zhibu: '',
    pyr1: '',
    pyr2: ''
  }
}

const handleAdd = () => {
  isEdit.value = false
  currentUserId.value = null
  resetForm()
  dialogVisible.value = true
}

const handleEdit = (row) => {
  isEdit.value = true
  currentUserId.value = row.id
  formData.value = {
    username: row.username,
    password: '',
    real_name: row.real_name,
    role: row.role,
    zhibu: row.zhibu || '',
    pyr1: row.pyr1 || '',
    pyr2: row.pyr2 || ''
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
    const data = { ...formData.value }
    // 编辑时如果密码为空则不传
    if (isEdit.value && !data.password) {
      delete data.password
    }
    
    if (isEdit.value) {
      await updateUser(currentUserId.value, data)
      ElMessage.success('用户更新成功')
    } else {
      await createUser(data)
      ElMessage.success('用户创建成功')
    }
    
    dialogVisible.value = false
    fetchData()
  } catch (error) {
    console.error('操作失败:', error)
    ElMessage.error(error.response?.data?.detail || '操作失败')
  } finally {
    submitting.value = false
  }
}

const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除用户 "${row.real_name}" 吗？此操作不可恢复。`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    await deleteUser(row.id)
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
.user-management {
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

:deep(.el-table) {
  border-radius: 8px;
}

:deep(.el-table th) {
  background: #f8fafc !important;
}
</style>













