<template>
  <el-config-provider :locale="locale">
    <div id="app">
      <!-- 左侧导航栏 - 登录页和注册页不显示 -->
      <Sidebar v-if="!isAuthPage" />

      <!-- 主内容区域 -->
      <div class="app-content" :class="{ 'auth-page': isAuthPage }">
        <router-view v-slot="{ Component }">
          <transition name="fade" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </div>
    </div>
  </el-config-provider>
</template>

<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useUserStore } from '@/stores/user'
import zhCn from 'element-plus/es/locale/lang/zh-cn'
import Sidebar from '@/components/Sidebar.vue'

const route = useRoute()
const userStore = useUserStore()
const locale = zhCn

// 判断是否为登录/注册页面
const isAuthPage = computed(() => {
  return route.path === '/login' || route.path === '/register'
})

// 初始化
onMounted(() => {
  userStore.initUser()
})
</script>

<style scoped>
/* 现代简约风格 - YouTube/Twitter 布局 */

#app {
  min-height: 100vh;
  display: flex;
  background-color: var(--color-bg-page);
}

/* 主内容区域 */
.app-content {
  flex: 1;
  margin-left: 72px; /* 收起状态的侧边栏宽度 */
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  transition: margin-left 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

/* 登录/注册页面占满全屏 */
.app-content.auth-page {
  margin-left: 0;
}

/* 页面切换动画 - 平滑淡入淡出 */
.fade-enter-active {
  transition: opacity 0.3s ease, transform 0.3s ease;
}

.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from {
  opacity: 0;
  transform: translateY(10px);
}

.fade-leave-to {
  opacity: 0;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .app-content {
    margin-left: 72px; /* 移动端也保持侧边栏 */
  }
}
</style>
