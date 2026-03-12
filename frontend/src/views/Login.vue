<template>
  <div class="login-container">
    <div class="orb orb-1" />
    <div class="orb orb-2" />
    <div class="login-grid">
      <div class="login-hero">
        <div class="hero-badge">Ideological Report</div>
        <h2>智能制造工艺部党总支<br>积极分子思想汇报审核平台</h2>
        <p>专注于汇报、审核、进度的全流程管理，让信息传递和反馈清晰可循。</p>
        <div class="hero-stats">
          <div class="stat">
            <span class="stat-value">3</span>
            <span class="stat-label">级审核流程</span>
          </div>
          <div class="stat">
            <span class="stat-value">实时</span>
            <span class="stat-label">进度可视</span>
          </div>
          <div class="stat">
            <span class="stat-value">安全</span>
            <span class="stat-label">文档管理</span>
          </div>
        </div>
      </div>

      <div class="login-box">
        <div class="login-header">
          <h1>智能制造工艺部党总支积极分子思想汇报审核平台</h1>
          <p>Ideological Report Management System</p>
        </div>

        <el-form
          ref="loginFormRef"
          :model="loginForm"
          :rules="rules"
          class="login-form"
          @keyup.enter="handleLogin"
        >
          <el-form-item prop="username">
            <el-input
              v-model="loginForm.username"
              placeholder="请输入用户名"
              size="large"
              clearable
            >
              <template #prefix>
                <el-icon><User /></el-icon>
              </template>
            </el-input>
          </el-form-item>

          <el-form-item prop="password">
            <el-input
              v-model="loginForm.password"
              type="password"
              placeholder="请输入密码"
              size="large"
              show-password
              clearable
            >
              <template #prefix>
                <el-icon><Lock /></el-icon>
              </template>
            </el-input>
          </el-form-item>

          <el-form-item>
            <el-button
              type="primary"
              size="large"
              :loading="loading"
              class="login-button"
              @click="handleLogin"
            >
              {{ loading ? '登录中...' : '登录' }}
            </el-button>
          </el-form-item>
        </el-form>

        <div class="login-actions">
          <el-button type="text" class="action-link" @click="openChangePassword">
            修改密码
          </el-button>
        </div>

        <div class="login-tips">
          <el-divider>开发环境测试账号</el-divider>
          <div class="tips-content">
            账号为本人汉语姓名，初始密码为123456
          </div>
        </div>
      </div>
    </div>

    <el-dialog v-model="changePasswordVisible" title="修改密码" width="420px">
      <el-form ref="changeFormRef" :model="changeForm" :rules="changeRules" label-width="96px">
        <el-form-item label="用户名" prop="username">
          <el-input v-model="changeForm.username" placeholder="请输入用户名" clearable />
        </el-form-item>
        <el-form-item label="原密码" prop="oldPassword">
          <el-input
            v-model="changeForm.oldPassword"
            type="password"
            placeholder="请输入原密码"
            show-password
            clearable
          />
        </el-form-item>
        <el-form-item label="新密码" prop="newPassword">
          <el-input
            v-model="changeForm.newPassword"
            type="password"
            placeholder="请输入新密码"
            show-password
            clearable
          />
        </el-form-item>
        <el-form-item label="确认新密码" prop="confirmPassword">
          <el-input
            v-model="changeForm.confirmPassword"
            type="password"
            placeholder="请再次输入新密码"
            show-password
            clearable
          />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="changePasswordVisible = false">取消</el-button>
        <el-button type="primary" :loading="changeLoading" @click="submitChangePassword">确定</el-button>
      </template>
    </el-dialog>

    <!-- 落款 -->
    <div class="footer-credit">
      智能制造工艺部智能制造技术室能做科技团队
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { User, Lock } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { changePassword } from '@/api/auth'

const router = useRouter()
const userStore = useUserStore()

const loginFormRef = ref(null)
const loading = ref(false)

const changePasswordVisible = ref(false)
const changeLoading = ref(false)
const changeFormRef = ref(null)

const loginForm = reactive({
  username: '',
  password: ''
})

const changeForm = reactive({
  username: '',
  oldPassword: '',
  newPassword: '',
  confirmPassword: ''
})

const rules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码长度不能少于6位', trigger: 'blur' }
  ]
}

const changeRules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  oldPassword: [{ required: true, message: '请输入原密码', trigger: 'blur' }],
  newPassword: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 6, message: '密码长度不能少于6位', trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, message: '请再次输入新密码', trigger: 'blur' },
    {
      validator: (rule, value, callback) => {
        if (!value) return callback()
        if (value !== changeForm.newPassword) return callback(new Error('两次输入的密码不一致'))
        callback()
      },
      trigger: 'blur'
    }
  ]
}

const openChangePassword = () => {
  changeForm.username = loginForm.username || ''
  changeForm.oldPassword = ''
  changeForm.newPassword = ''
  changeForm.confirmPassword = ''
  changePasswordVisible.value = true
}

const submitChangePassword = async () => {
  if (!changeFormRef.value) return

  await changeFormRef.value.validate(async (valid) => {
    if (!valid) return

    changeLoading.value = true
    try {
      await changePassword({
        username: changeForm.username,
        old_password: changeForm.oldPassword,
        new_password: changeForm.newPassword
      })

      ElMessage.success('密码修改成功')
      changePasswordVisible.value = false

      loginForm.username = changeForm.username
      loginForm.password = changeForm.newPassword
    } catch (error) {
      console.error('修改密码失败:', error)
    } finally {
      changeLoading.value = false
    }
  })
}

const handleLogin = async () => {
  if (!loginFormRef.value) return

  await loginFormRef.value.validate(async (valid) => {
    if (!valid) return

    loading.value = true
    try {
      const success = await userStore.login(loginForm.username, loginForm.password)
      if (success) {
        // 统一跳转到首页
        router.push('/')
      }
    } finally {
      loading.value = false
    }
  })
}
</script>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  width: 100%;
  min-height: 100vh;
  padding: 48px 20px;
  background: radial-gradient(1200px at 20% 20%, rgba(37, 99, 235, 0.14) 0, transparent 40%),
    radial-gradient(1000px at 85% 10%, rgba(14, 165, 233, 0.14) 0, transparent 38%),
    linear-gradient(135deg, #f6f9ff 0%, #eef4ff 45%, #e7f7f5 100%);
  position: relative;
  overflow: hidden;
}

.orb {
  position: absolute;
  border-radius: 50%;
  filter: blur(50px);
  opacity: 0.4;
  z-index: 0;
}

.orb-1 {
  width: 340px;
  height: 340px;
  background: #93c5fd;
  top: -40px;
  left: -60px;
}

.orb-2 {
  width: 320px;
  height: 320px;
  background: #67e8f9;
  bottom: -20px;
  right: 40px;
}

.login-grid {
  display: grid;
  grid-template-columns: 1.1fr 0.9fr;
  gap: 26px;
  width: min(1100px, 98%);
  position: relative;
  z-index: 1;
}

.login-hero {
  background: linear-gradient(145deg, #0f172a, #0b1f3a 60%, #0c2f55);
  border-radius: 20px;
  padding: 36px;
  color: #e5e7eb;
  border: 1px solid rgba(255, 255, 255, 0.06);
  box-shadow: 0 28px 60px rgba(15, 23, 42, 0.3);
  position: relative;
  overflow: hidden;
}

.login-hero::after {
  content: '';
  position: absolute;
  inset: 0;
  background: radial-gradient(circle at 20% 20%, rgba(14, 165, 233, 0.2), transparent 45%),
    radial-gradient(circle at 80% 0%, rgba(37, 99, 235, 0.2), transparent 40%);
  pointer-events: none;
}

.hero-badge {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 8px 14px;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.08);
  color: #bfdbfe;
  font-size: 13px;
  border: 1px solid rgba(255, 255, 255, 0.08);
}

.login-hero h2 {
  font-size: 30px;
  margin: 18px 0 8px;
  letter-spacing: 0.4px;
}

.login-hero p {
  color: #cbd5e1;
  font-size: 15px;
  max-width: 520px;
  line-height: 1.7;
}

.hero-stats {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 14px;
  margin-top: 26px;
}

.stat {
  padding: 16px;
  border-radius: 14px;
  background: rgba(255, 255, 255, 0.07);
  border: 1px solid rgba(255, 255, 255, 0.08);
}

.stat-value {
  display: block;
  font-size: 18px;
  font-weight: 700;
  color: #fff;
}

.stat-label {
  color: #cbd5e1;
  font-size: 13px;
}

.login-box {
  width: 100%;
  padding: 32px 32px 24px;
  background: rgba(255, 255, 255, 0.9);
  border-radius: 20px;
  box-shadow: 0 22px 50px rgba(15, 23, 42, 0.15);
  border: 1px solid rgba(226, 232, 240, 0.9);
  backdrop-filter: blur(12px);
}

.login-header {
  text-align: left;
  margin-bottom: 30px;
}

.login-header h1 {
  font-size: 26px;
  color: #0f172a;
  margin-bottom: 6px;
  font-weight: 700;
}

.login-header p {
  font-size: 14px;
  color: #6b7280;
  font-weight: 500;
}

.login-form {
  margin-top: 10px;
}

.login-button {
  width: 100%;
  margin-top: 6px;
  height: 44px;
  border-radius: 12px;
  font-weight: 700;
  letter-spacing: 0.3px;
  box-shadow: 0 12px 26px rgba(37, 99, 235, 0.25);
}

.login-actions {
  display: flex;
  justify-content: flex-end;
  margin-top: 6px;
}

.action-link {
  padding: 0;
}

.login-tips {
  margin-top: 22px;
}

.tips-content {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  justify-content: flex-start;
  padding: 10px 0;
  color: #475569;
}

:deep(.el-divider__text) {
  font-size: 12px;
  color: #6b7280;
}

:deep(.el-input__wrapper) {
  border-radius: 12px;
  padding: 8px 12px;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.04);
}

:deep(.el-input__inner) {
  height: 44px;
}

@media (max-width: 960px) {
  .login-grid {
    grid-template-columns: 1fr;
  }

  .login-hero {
    order: 2;
  }

  .login-box {
    order: 1;
  }
}

@media (max-width: 600px) {
  .login-container {
    padding: 24px 14px;
  }

  .login-box {
    padding: 26px 22px 20px;
  }

  .hero-stats {
    grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
  }
}

.footer-credit {
  position: fixed;
  bottom: 20px;
  left: 50%;
  transform: translateX(-50%);
  font-size: 12px;
  color: rgba(118, 178, 234, 0.6);
  text-align: center;
  z-index: 10;
}
</style>











