// 导入样式文件 - 顺序很重要
import 'element-plus/dist/index.css'
import 'element-plus/theme-chalk/dark/css-vars.css'
import './assets/design-system.css' // 设计系统变量和工具类
import './assets/main.css' // 全局样式覆盖

import { createApp } from 'vue'
import { createPinia } from 'pinia'
import ElementPlus from 'element-plus'
import zhCn from 'element-plus/es/locale/lang/zh-cn'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'

import App from './App.vue'
import router from './router'
import { useUserStore } from '@/stores/user'

const app = createApp(App)

// 注册所有 Element Plus 图标
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}

const pinia = createPinia()
app.use(pinia)
const userStore = useUserStore(pinia)
userStore.initUser()

app.use(router)
app.use(ElementPlus, {
  locale: zhCn,
})

app.mount('#app')
