<template>
  <div id="app">
    <nav class="navbar">
      <div class="nav-container">
        <router-link to="/" class="nav-logo">
          <h2>校内二手交易平台</h2>
        </router-link>
        
        <div class="nav-menu">
          <router-link to="/" class="nav-link">首页</router-link>
          <router-link to="/items" class="nav-link">商品</router-link>
          
          <div v-if="isLoggedIn" class="nav-user">
            <router-link to="/messages" class="nav-link">消息</router-link>
            <router-link to="/orders" class="nav-link">订单</router-link>
            <router-link to="/wishlist" class="nav-link">收藏</router-link>
            <div class="user-dropdown">
              <span class="user-name">{{ username }}</span>
              <div class="dropdown-menu">
                <router-link to="/profile" class="dropdown-item">个人中心</router-link>
                <router-link to="/publish" class="dropdown-item">发布商品</router-link>
                <a @click="handleLogout" class="dropdown-item">退出登录</a>
              </div>
            </div>
          </div>
          
          <div v-else class="nav-auth">
            <router-link to="/login" class="nav-link">登录</router-link>
            <router-link to="/register" class="nav-link nav-register">注册</router-link>
          </div>
        </div>
      </div>
    </nav>

    <main class="main-content">
      <RouterView />
    </main>

    <footer class="footer">
      <div class="footer-content">
        <p>&copy; 2024 校内二手物品交易平台. All rights reserved.</p>
      </div>
    </footer>
  </div>
</template>

<script setup lang="ts">
import { onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const userStore = useUserStore()

const isLoggedIn = computed(() => userStore.isLoggedIn)
const username = computed(() => userStore.username)

const handleLogout = () => {
  userStore.logout()
  router.push('/')
}

onMounted(() => {
  userStore.initUser()
})
</script>

<style scoped>
#app {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.navbar {
  background: #fff;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  position: sticky;
  top: 0;
  z-index: 100;
}

.nav-container {
  max-width: 1800px;
  margin: 0 auto;
  padding: 0 40px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  height: 70px;
}

.nav-logo h2 {
  color: #2c3e50;
  margin: 0;
  font-size: 1.5rem;
}

.nav-menu {
  display: flex;
  align-items: center;
  gap: 20px;
}

.nav-link {
  color: #2c3e50;
  text-decoration: none;
  padding: 8px 16px;
  border-radius: 4px;
  transition: background-color 0.3s;
}

.nav-link:hover {
  background-color: #f8f9fa;
}

.nav-link.router-link-active {
  background-color: #007bff;
  color: white;
}

.nav-register {
  background-color: #007bff;
  color: white !important;
}

.nav-register:hover {
  background-color: #0056b3 !important;
}

.nav-user {
  display: flex;
  align-items: center;
  gap: 20px;
}

.user-dropdown {
  position: relative;
}

.user-name {
  color: #2c3e50;
  font-weight: 500;
  cursor: pointer;
  padding: 8px 16px;
  border-radius: 4px;
  transition: background-color 0.3s;
}

.user-name:hover {
  background-color: #f8f9fa;
}

.dropdown-menu {
  position: absolute;
  top: 100%;
  right: 0;
  background: white;
  border: 1px solid #ddd;
  border-radius: 4px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  min-width: 120px;
  display: none;
}

.user-dropdown:hover .dropdown-menu {
  display: block;
}

.dropdown-item {
  display: block;
  padding: 8px 16px;
  color: #2c3e50;
  text-decoration: none;
  cursor: pointer;
  transition: background-color 0.3s;
}

.dropdown-item:hover {
  background-color: #f8f9fa;
}

.main-content {
  flex: 1;
  max-width: 1800px;
  margin: 0 auto;
  padding: 30px 40px;
  width: 100%;
  box-sizing: border-box;
}

.footer {
  background: #2c3e50;
  color: white;
  text-align: center;
  padding: 20px 0;
  margin-top: auto;
}

.footer-content {
  max-width: 1800px;
  margin: 0 auto;
  padding: 0 40px;
}

@media (max-width: 1024px) {
  .nav-container {
    flex-direction: column;
    height: auto;
    padding: 15px 30px;
  }
  
  .nav-menu {
    margin-top: 15px;
    flex-wrap: wrap;
    justify-content: center;
  }
  
  .main-content {
    padding: 20px 30px;
  }
}
</style>
