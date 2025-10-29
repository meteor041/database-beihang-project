<template>
  <el-config-provider :locale="locale">
    <div id="app">
      <!-- 顶部导航栏 -->
      <el-header class="app-header">
        <div class="header-container">
          <!-- Logo -->
          <router-link to="/" class="logo">
            <el-icon :size="28"><ShoppingBag /></el-icon>
            <span class="logo-text">校内二手交易平台</span>
          </router-link>

          <!-- 导航菜单 -->
          <el-menu
            :default-active="activeRoute"
            mode="horizontal"
            :ellipsis="false"
            class="nav-menu"
            router
          >
            <el-menu-item index="/">
              <el-icon><HomeFilled /></el-icon>
              <span>首页</span>
            </el-menu-item>

            <el-menu-item index="/items">
              <el-icon><Goods /></el-icon>
              <span>商品</span>
            </el-menu-item>

            <!-- 已登录用户菜单 -->
            <template v-if="isLoggedIn">
              <el-menu-item index="/publish">
                <el-icon><Plus /></el-icon>
                <span>发布</span>
              </el-menu-item>

              <el-menu-item index="/messages">
                <el-badge :value="unreadCount" :hidden="unreadCount === 0" class="message-badge">
                  <el-icon><ChatDotRound /></el-icon>
                  <span>消息</span>
                </el-badge>
              </el-menu-item>

              <el-menu-item index="/orders">
                <el-icon><Tickets /></el-icon>
                <span>订单</span>
              </el-menu-item>

              <el-menu-item index="/wishlist">
                <el-icon><Star /></el-icon>
                <span>收藏</span>
              </el-menu-item>
            </template>
          </el-menu>

          <!-- 右侧用户区域 -->
          <div class="user-section">
            <template v-if="isLoggedIn">
              <!-- 用户下拉菜单 -->
              <el-dropdown trigger="click" @command="handleCommand">
                <div class="user-info">
                  <UserAvatar
                    :avatar="currentUser?.avatar || undefined"
                    :username="currentUser?.username"
                    :size="32"
                    clickable
                  />
                  <span class="username">{{ currentUser?.username }}</span>
                  <el-icon><ArrowDown /></el-icon>
                </div>

                <template #dropdown>
                  <el-dropdown-menu>
                    <el-dropdown-item command="profile">
                      <el-icon><User /></el-icon>
                      个人中心
                    </el-dropdown-item>
                    <el-dropdown-item divided command="logout">
                      <el-icon><SwitchButton /></el-icon>
                      退出登录
                    </el-dropdown-item>
                  </el-dropdown-menu>
                </template>
              </el-dropdown>
            </template>

            <!-- 未登录用户 -->
            <template v-else>
              <el-button @click="router.push('/login')">登录</el-button>
              <el-button type="primary" @click="router.push('/register')">注册</el-button>
            </template>
          </div>
        </div>
      </el-header>

      <!-- 主内容区域 -->
      <el-main class="app-main">
        <router-view v-slot="{ Component }">
          <transition name="fade" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </el-main>

      <!-- 底部 -->
      <el-footer class="app-footer">
        <div class="footer-content">
          <p>&copy; 2024-2025 校内二手物品交易平台. All rights reserved.</p>
          <p class="footer-links">
            <a href="/about">关于我们</a>
            <span class="divider">|</span>
            <a href="#">帮助中心</a>
            <span class="divider">|</span>
            <a href="#">联系我们</a>
          </p>
        </div>
      </el-footer>
    </div>
  </el-config-provider>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { ElMessage, ElMessageBox } from 'element-plus'
import zhCn from 'element-plus/es/locale/lang/zh-cn'
import UserAvatar from '@/components/UserAvatar.vue'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()
const locale = zhCn

const unreadCount = ref(0)

const isLoggedIn = computed(() => userStore.isLoggedIn)
const currentUser = computed(() => userStore.currentUser)
const activeRoute = computed(() => route.path)

// 处理下拉菜单命令
const handleCommand = async (command: string) => {
  switch (command) {
    case 'profile':
      router.push('/profile')
      break
    case 'logout':
      try {
        await ElMessageBox.confirm('确定要退出登录吗?', '提示', {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        })

        userStore.logout()
        ElMessage.success('退出登录成功')
        router.push('/')
      } catch {
        // 用户取消操作
      }
      break
  }
}

// 初始化
onMounted(() => {
  userStore.initUser()
  // TODO: 定期获取未读消息数
})
</script>

<style scoped>
/* 使用设计系统变量重构的样式 */

#app {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background-color: var(--color-bg-page);
}

.app-header {
  background: var(--color-bg-card);
  box-shadow: var(--shadow-header);
  position: sticky;
  top: 0;
  z-index: var(--z-index-sticky);
  padding: 0;
  height: 64px;
  line-height: 64px;
}

.header-container {
  max-width: var(--container-max-width);
  margin: 0 auto;
  padding: 0 var(--container-padding);
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 100%;
}

.logo {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
  text-decoration: none;
  color: var(--color-text-primary);
  font-size: var(--font-size-xl);
  font-weight: var(--font-weight-semibold);
  margin-right: var(--spacing-3xl);
  white-space: nowrap;
  transition: color var(--transition-base);
}

.logo:hover {
  color: var(--color-primary);
}

.logo-text {
  display: inline-block;
}

.nav-menu {
  flex: 1;
  border-bottom: none;
  background: transparent;
}

.nav-menu :deep(.el-menu-item) {
  padding: 0 var(--spacing-lg);
}

.message-badge {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
}

.user-section {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
  margin-left: var(--spacing-lg);
}

.user-info {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  cursor: pointer;
  padding: var(--spacing-sm) var(--spacing-md);
  border-radius: var(--radius-full);
  transition: background-color var(--transition-base);
}

.user-info:hover {
  background-color: var(--color-bg-hover);
}

.username {
  font-size: var(--font-size-base);
  font-weight: var(--font-weight-medium);
  color: var(--color-text-primary);
}

.app-main {
  flex: 1;
  max-width: var(--container-max-width);
  width: 100%;
  margin: 0 auto;
  padding: var(--container-padding);
}

.app-footer {
  background: var(--color-text-primary);
  color: var(--color-bg-card);
  text-align: center;
  height: auto;
  padding: var(--spacing-3xl) var(--spacing-lg);
}

.footer-content {
  max-width: var(--container-max-width);
  margin: 0 auto;
}

.footer-content p {
  margin: var(--spacing-sm) 0;
  font-size: var(--font-size-base);
}

.footer-links a {
  color: var(--color-bg-card);
  text-decoration: none;
  transition: color var(--transition-base);
}

.footer-links a:hover {
  color: var(--color-primary-light);
}

.divider {
  margin: 0 var(--spacing-md);
  color: var(--color-text-secondary);
}

/* 页面切换动画 */
.fade-enter-active,
.fade-leave-active {
  transition: opacity var(--transition-base);
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* 响应式设计 */
@media (max-width: 1024px) {
  .header-container {
    padding: 0 var(--spacing-base);
  }

  .logo {
    margin-right: var(--spacing-lg);
  }

  .logo-text {
    display: none;
  }

  .nav-menu :deep(.el-menu-item) {
    padding: 0 var(--spacing-md);
  }

  .nav-menu :deep(.el-menu-item span) {
    display: none;
  }

  .username {
    display: none;
  }
}

@media (max-width: 768px) {
  .app-header {
    height: auto;
    line-height: normal;
  }

  .header-container {
    flex-wrap: wrap;
    padding: var(--spacing-md);
  }

  .nav-menu {
    width: 100%;
    order: 3;
    margin-top: var(--spacing-md);
  }

  .app-main {
    padding: var(--spacing-base);
  }
}
</style>
