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

        <!-- 底部 - 只在非登录注册页显示 -->
        <footer v-if="!isAuthPage" class="app-footer">
          <div class="footer-content">
            <p>&copy; 2024-2025 校内二手物品交易平台. All rights reserved.</p>
            <p class="footer-links">
              <router-link to="/about">关于我们</router-link>
              <span class="divider">|</span>
              <a href="#">帮助中心</a>
              <span class="divider">|</span>
              <a href="#">联系我们</a>
            </p>
          </div>
        </footer>
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

/* 底部 */
.app-footer {
  background: var(--color-bg-card);
  border-top: 1px solid var(--color-border-light);
  text-align: center;
  padding: var(--spacing-6) var(--spacing-4);
  margin-top: auto;
}

.footer-content {
  max-width: var(--container-max-width);
  margin: 0 auto;
}

.footer-content p {
  margin: var(--spacing-2) 0;
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
}

.footer-links {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: var(--spacing-2);
  flex-wrap: wrap;
}

.footer-links a {
  color: var(--color-text-secondary);
  text-decoration: none;
  transition: color var(--transition-base);
}

.footer-links a:hover {
  color: var(--color-primary);
}

.divider {
  color: var(--color-border-base);
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

  .footer-content p {
    font-size: var(--font-size-xs);
  }
}

@media (max-width: 480px) {
  .footer-links {
    flex-direction: column;
    gap: var(--spacing-1);
  }

  .divider {
    display: none;
  }
}
</style>
