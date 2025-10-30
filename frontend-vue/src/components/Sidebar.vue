<template>
  <aside
    class="sidebar"
    :class="{ collapsed: isCollapsed }"
    @mouseenter="handleMouseEnter"
    @mouseleave="handleMouseLeave"
  >
    <!-- Logo区域 -->
    <div class="sidebar-logo">
      <router-link to="/" class="logo-link">
        <div class="logo-icon-wrapper">
          <el-icon :size="24" class="logo-icon">
            <ShoppingBag />
          </el-icon>
        </div>
        <transition name="fade">
          <span v-show="!isCollapsed" class="logo-text">校园二手</span>
        </transition>
      </router-link>
    </div>

    <!-- 导航菜单 -->
    <nav class="sidebar-nav">
      <router-link
        v-for="item in menuItems"
        :key="item.path"
        :to="item.path"
        class="nav-item"
        :class="{ active: isActive(item.path) }"
      >
        <el-icon :size="24" class="nav-icon">
          <component :is="item.icon" />
        </el-icon>
        <transition name="fade">
          <span v-show="!isCollapsed" class="nav-text">{{ item.label }}</span>
        </transition>
        <el-badge
          v-if="item.badge && unreadCount > 0"
          :value="unreadCount"
          :hidden="isCollapsed"
          class="nav-badge"
        />
      </router-link>
    </nav>

    <!-- 用户区域 -->
    <div class="sidebar-user">
      <template v-if="isLoggedIn">
        <div class="user-info">
          <UserAvatar
            :avatar="currentUser?.avatar || undefined"
            :username="currentUser?.username"
            :size="40"
          />
          <transition name="fade">
            <div v-show="!isCollapsed" class="user-details">
              <div class="username">{{ currentUser?.username }}</div>
              <div class="user-credit">信用分: {{ currentUser?.credit_score || 100 }}</div>
            </div>
          </transition>
        </div>
        <transition name="fade">
          <el-button
            v-show="!isCollapsed"
            circle
            @click="handleLogout"
            class="logout-btn"
            title="退出登录"
          >
            <el-icon><ArrowLeft /></el-icon>
          </el-button>
        </transition>
      </template>

      <template v-else>
        <div class="auth-buttons">
          <el-button
            type="primary"
            :icon="User"
            @click="router.push('/login')"
            :class="{ 'icon-only': isCollapsed }"
          >
            <span v-show="!isCollapsed">登录</span>
          </el-button>
        </div>
      </template>
    </div>
  </aside>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  HomeFilled,
  Goods,
  ChatDotRound,
  User,
  ShoppingBag,
  ArrowLeft
} from '@element-plus/icons-vue'
import UserAvatar from './UserAvatar.vue'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()

const isCollapsed = ref(true)
const unreadCount = ref(0) // TODO: 从API获取

const isLoggedIn = computed(() => userStore.isLoggedIn)
const currentUser = computed(() => userStore.currentUser)

// 菜单项配置
const menuItems = computed(() => {
  const items: Array<{ path: string; label: string; icon: any; badge?: boolean }> = [
    { path: '/', label: '首页', icon: HomeFilled },
    { path: '/items', label: '商品列表', icon: Goods },
  ]

  if (isLoggedIn.value) {
    items.push(
      { path: '/messages', label: '消息', icon: ChatDotRound, badge: true },
      { path: '/profile', label: '个人中心', icon: User }
    )
  }

  return items
})

// 判断路由是否激活
const isActive = (path: string) => {
  if (path === '/') {
    return route.path === '/'
  }
  return route.path.startsWith(path)
}

// 鼠标悬停展开
const handleMouseEnter = () => {
  isCollapsed.value = false
}

// 鼠标离开收起
const handleMouseLeave = () => {
  isCollapsed.value = true
}

// 处理退出登录
const handleLogout = async () => {
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
}
</script>

<style scoped>
.sidebar {
  position: fixed;
  left: 0;
  top: 0;
  height: 100vh;
  background: var(--color-bg-card);
  border-right: 1px solid var(--color-border-light);
  display: flex;
  flex-direction: column;
  padding: var(--spacing-4) 0;
  width: 240px;
  transition: width 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  z-index: 1000;
  overflow: hidden;
}

.sidebar.collapsed {
  width: 72px;
}

/* Logo区域 */
.sidebar-logo {
  padding: 0 var(--spacing-2);
  margin-bottom: var(--spacing-6);
  height: 48px;
  display: flex;
  align-items: center;
}

.logo-link {
  display: flex;
  align-items: center;
  gap: var(--spacing-3);
  text-decoration: none;
  color: var(--color-text-primary);
  font-size: var(--font-size-xl);
  font-weight: var(--font-weight-bold);
  transition: color 0.2s;
  white-space: nowrap;
  width: 100%;
  padding: var(--spacing-3) var(--spacing-4);
  border-radius: var(--radius-lg);
}

.logo-link:hover {
  color: var(--color-primary);
  background: var(--color-bg-hover);
}

.logo-icon-wrapper {
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.logo-icon {
  flex-shrink: 0;
  color: var(--color-primary);
}

.logo-text {
  overflow: hidden;
  white-space: nowrap;
}

/* 导航菜单 */
.sidebar-nav {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: var(--spacing-1);
  padding: 0 var(--spacing-2);
  overflow-y: auto;
  overflow-x: hidden;
}

/* 隐藏滚动条但保持可滚动 */
.sidebar-nav::-webkit-scrollbar {
  width: 0;
  display: none;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: var(--spacing-3);
  padding: var(--spacing-3) var(--spacing-4);
  border-radius: var(--radius-lg);
  text-decoration: none;
  color: var(--color-text-primary);
  font-size: var(--font-size-base);
  font-weight: var(--font-weight-medium);
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  white-space: nowrap;
}

.nav-item:hover {
  background: var(--color-bg-hover);
  color: var(--color-primary);
}

.nav-item.active {
  background: var(--color-primary-lighter);
  color: var(--color-primary);
  font-weight: var(--font-weight-semibold);
}

.nav-icon {
  flex-shrink: 0;
}

.nav-text {
  overflow: hidden;
  white-space: nowrap;
}

.nav-badge {
  margin-left: auto;
}

/* 用户区域 */
.sidebar-user {
  padding: var(--spacing-4);
  border-top: 1px solid var(--color-border-light);
  margin-top: auto;
  display: flex;
  align-items: center;
  gap: var(--spacing-2);
}

.user-info {
  flex: 1;
  display: flex;
  align-items: center;
  gap: var(--spacing-3);
  padding: var(--spacing-2);
  border-radius: var(--radius-lg);
  white-space: nowrap;
  min-width: 0;
}

.user-details {
  flex: 1;
  min-width: 0;
  overflow: hidden;
}

.username {
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.user-credit {
  font-size: var(--font-size-xs);
  color: var(--color-text-secondary);
}

.logout-btn {
  flex-shrink: 0;
  width: 36px;
  height: 36px;
  padding: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 1px solid var(--color-border-base);
  background: var(--color-bg-card);
  color: var(--color-text-secondary);
  transition: all 0.2s;
}

.logout-btn:hover {
  color: var(--color-danger);
  border-color: var(--color-danger);
  background: var(--color-bg-hover);
}

.auth-buttons {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-2);
  width: 100%;
}

.auth-buttons .el-button {
  width: 100%;
  transition: all 0.3s;
}

.auth-buttons .el-button.icon-only {
  padding: var(--spacing-2);
}

/* 渐变动画 */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* 响应式 - 移动端自动收起 */
@media (max-width: 768px) {
  .sidebar {
    width: 72px;
  }

  .sidebar.collapsed {
    width: 72px;
  }

  /* 移动端点击展开 */
  .sidebar:active {
    width: 240px;
  }
}
</style>
