<template>
  <v-app>
    <!-- 全局通知 -->
    <GlobalNotification />

    <!-- 顶部导航栏 -->
    <v-app-bar elevation="2" color="white" height="64">
      <v-container class="d-flex align-center px-4" fluid>
        <div class="d-flex align-center" style="max-width: 1400px; width: 100%; margin: 0 auto;">
          <!-- Logo -->
          <router-link to="/" class="logo text-decoration-none d-flex align-center">
            <v-icon size="28" color="primary">mdi-shopping</v-icon>
            <span class="logo-text ml-3 text-h6 font-weight-bold">校内二手交易平台</span>
          </router-link>

          <v-spacer></v-spacer>

          <!-- 导航菜单 -->
          <v-tabs
            v-model="activeTab"
            color="primary"
            class="nav-tabs"
            density="comfortable"
            show-arrows
          >
            <v-tab value="/" @click="router.push('/')">
              <v-icon start>mdi-home</v-icon>
              <span class="tab-text">首页</span>
            </v-tab>

            <v-tab value="/items" @click="router.push('/items')">
              <v-icon start>mdi-package-variant</v-icon>
              <span class="tab-text">商品</span>
            </v-tab>

            <template v-if="isLoggedIn">
              <v-tab value="/publish" @click="router.push('/publish')">
                <v-icon start>mdi-plus-circle</v-icon>
                <span class="tab-text">发布</span>
              </v-tab>

              <v-tab value="/messages" @click="router.push('/messages')">
                <v-badge
                  :content="unreadCount"
                  :model-value="unreadCount > 0"
                  color="error"
                  overlap
                >
                  <v-icon start>mdi-message</v-icon>
                </v-badge>
                <span class="tab-text ml-2">消息</span>
              </v-tab>

              <v-tab value="/orders" @click="router.push('/orders')">
                <v-icon start>mdi-receipt</v-icon>
                <span class="tab-text">订单</span>
              </v-tab>

              <v-tab value="/wishlist" @click="router.push('/wishlist')">
                <v-icon start>mdi-star</v-icon>
                <span class="tab-text">收藏</span>
              </v-tab>
            </template>
          </v-tabs>

          <v-spacer></v-spacer>

          <!-- 右侧用户区域 -->
          <div class="user-section ml-4">
            <template v-if="isLoggedIn">
              <!-- 用户下拉菜单 -->
              <v-menu offset-y>
                <template v-slot:activator="{ props }">
                  <div class="user-info" v-bind="props">
                    <UserAvatar
                      :avatar="currentUser?.avatar || undefined"
                      :username="currentUser?.username"
                      :size="32"
                      clickable
                    />
                    <span class="username ml-2">{{ currentUser?.username }}</span>
                    <v-icon size="small" class="ml-1">mdi-chevron-down</v-icon>
                  </div>
                </template>

                <v-list density="compact" min-width="180">
                  <v-list-item @click="router.push('/profile')">
                    <template v-slot:prepend>
                      <v-icon>mdi-account</v-icon>
                    </template>
                    <v-list-item-title>个人中心</v-list-item-title>
                  </v-list-item>

                  <v-divider></v-divider>

                  <v-list-item @click="handleLogout">
                    <template v-slot:prepend>
                      <v-icon>mdi-logout</v-icon>
                    </template>
                    <v-list-item-title>退出登录</v-list-item-title>
                  </v-list-item>
                </v-list>
              </v-menu>
            </template>

            <!-- 未登录用户 -->
            <template v-else>
              <v-btn variant="text" @click="router.push('/login')">登录</v-btn>
              <v-btn color="primary" @click="router.push('/register')">注册</v-btn>
            </template>
          </div>
        </div>
      </v-container>
    </v-app-bar>

    <!-- 主内容区域 -->
    <v-main class="app-main">
      <v-container fluid class="pa-6" style="max-width: 1400px;">
        <router-view v-slot="{ Component }">
          <transition name="fade" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </v-container>
    </v-main>

    <!-- 底部 -->
    <v-footer class="app-footer bg-grey-darken-4 text-center" height="auto">
      <v-container>
        <div class="footer-content">
          <p class="mb-2">&copy; 2024-2025 校内二手物品交易平台. All rights reserved.</p>
          <div class="footer-links">
            <a href="/about" class="text-white text-decoration-none">关于我们</a>
            <span class="divider mx-3">|</span>
            <a href="#" class="text-white text-decoration-none">帮助中心</a>
            <span class="divider mx-3">|</span>
            <a href="#" class="text-white text-decoration-none">联系我们</a>
          </div>
        </div>
      </v-container>
    </v-footer>

    <!-- 退出登录确认对话框 -->
    <v-dialog v-model="logoutDialog" max-width="400">
      <v-card>
        <v-card-title class="text-h6">提示</v-card-title>
        <v-card-text>确定要退出登录吗?</v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn variant="text" @click="logoutDialog = false">取消</v-btn>
          <v-btn color="primary" variant="text" @click="confirmLogout">确定</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-app>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { useNotification } from '@/composables/useNotification'
import UserAvatar from '@/components/UserAvatar.vue'
import GlobalNotification from '@/components/GlobalNotification.vue'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()
const notification = useNotification()

const unreadCount = ref(0)
const logoutDialog = ref(false)
const activeTab = ref(route.path)

const isLoggedIn = computed(() => userStore.isLoggedIn)
const currentUser = computed(() => userStore.currentUser)

// 监听路由变化，更新activeTab
watch(() => route.path, (newPath) => {
  activeTab.value = newPath
})

// 处理退出登录
const handleLogout = () => {
  logoutDialog.value = true
}

const confirmLogout = () => {
  userStore.logout()
  notification.success('退出登录成功')
  logoutDialog.value = false
  router.push('/')
}

// 初始化
onMounted(() => {
  userStore.initUser()
  // TODO: 定期获取未读消息数
})
</script>

<style scoped>
.logo {
  display: flex;
  align-items: center;
  color: #303133;
  text-decoration: none;
  transition: color 0.3s;
}

.logo:hover {
  color: #409eff;
}

.logo-text {
  white-space: nowrap;
}

.nav-tabs {
  flex: 1;
  max-width: 600px;
}

.tab-text {
  margin-left: 4px;
}

.user-section {
  display: flex;
  align-items: center;
  gap: 12px;
}

.user-info {
  display: flex;
  align-items: center;
  cursor: pointer;
  padding: 6px 12px;
  border-radius: 20px;
  transition: background-color 0.3s;
}

.user-info:hover {
  background-color: #f5f7fa;
}

.username {
  font-size: 14px;
  font-weight: 500;
  color: #303133;
}

.app-main {
  background-color: #f5f7fa;
  min-height: calc(100vh - 64px - 120px);
}

.footer-content {
  padding: 20px 0;
}

.footer-content p {
  margin: 8px 0;
  font-size: 14px;
  color: white;
}

.footer-links {
  display: flex;
  justify-content: center;
  align-items: center;
}

.divider {
  color: #909399;
}

/* 页面切换动画 */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* 响应式设计 */
@media (max-width: 1024px) {
  .logo-text {
    display: none;
  }

  .tab-text {
    display: none;
  }

  .username {
    display: none;
  }
}

@media (max-width: 768px) {
  .nav-tabs {
    display: none;
  }
}
</style>
