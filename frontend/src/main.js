import { createApp } from 'vue'
import { createPinia } from 'pinia'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import 'element-plus/theme-chalk/dark/css-vars.css'
import zhCn from 'element-plus/dist/locale/zh-cn.mjs'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'
import App from './App.vue'
import router from './router'

// SSO 回调：在 Vue/Router 初始化之前处理，避免 redirect 导致 query 丢失
;(function handleSsoCallback() {
  const params = new URLSearchParams(window.location.search)
  const ssoToken = params.get('sso_token')
  if (ssoToken) {
    localStorage.setItem('token', ssoToken)
    window.history.replaceState({}, '', '/dashboard')
  }
})()

const app = createApp(App)
const pinia = createPinia()

// 注册所有图标
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}

app.use(pinia)
app.use(router)
app.use(ElementPlus, {
  locale: zhCn,
})

app.mount('#app')





























