import { defineStore } from 'pinia'
import { login, getCurrentUser } from '@/api/auth'
import { ElMessage } from 'element-plus'

export const useUserStore = defineStore('user', {
  state: () => ({
    token: localStorage.getItem('token') || '',
    userInfo: null
  }),
  
  getters: {
    isLoggedIn: (state) => !!state.token,
    role: (state) => state.userInfo?.role || null,
    username: (state) => state.userInfo?.username || ''
  },
  
  actions: {
    // 登录
    async login(username, password) {
      try {
        const data = await login(username, password)
        this.token = data.access_token
        localStorage.setItem('token', data.access_token)
        
        // 获取用户信息
        await this.getUserInfo()
        
        ElMessage.success('登录成功')
        return true
      } catch (error) {
        console.error('登录失败:', error)
        return false
      }
    },
    
    // 获取用户信息
    async getUserInfo() {
      try {
        const data = await getCurrentUser()
        this.userInfo = data
        return data
      } catch (error) {
        console.error('获取用户信息失败:', error)
        this.logout()
        throw error
      }
    },
    
    // 登出
    logout() {
      this.token = ''
      this.userInfo = null
      localStorage.removeItem('token')
    },
    
    // 检查权限
    hasRole(role) {
      return this.role === role
    },
    
    // 检查是否有多个角色中的任意一个
    hasAnyRole(roles) {
      return roles.includes(this.role)
    }
  }
})





























