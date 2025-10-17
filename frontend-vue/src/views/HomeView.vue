<template>
  <div class="home">
    <!-- 首页横幅 -->
    <section class="hero">
      <div class="hero-content">
        <h1>校内二手物品交易平台</h1>
        <p>安全、便捷的校园二手交易平台，让闲置物品重新焕发价值</p>
        <div class="hero-actions">
          <router-link to="/items" class="btn btn-primary">浏览商品</router-link>
          <router-link v-if="isLoggedIn" to="/publish" class="btn btn-secondary">发布商品</router-link>
          <router-link v-else to="/register" class="btn btn-secondary">立即注册</router-link>
        </div>
      </div>
    </section>

    <!-- 商品分类 -->
    <section class="categories">
      <h2>商品分类</h2>
      <div class="category-grid">
        <div 
          v-for="category in categories" 
          :key="(category as any).category_id"
          class="category-card"
          @click="goToCategory(category.category_id)"
        >
          <div class="category-icon">📱</div>
          <h3>{{ category.category_name }}</h3>
          <p>{{ category.item_count }} 件商品</p>
        </div>
      </div>
    </section>

    <!-- 最新商品 -->
    <section class="latest-items">
      <div class="section-header">
        <h2>最新商品</h2>
        <router-link to="/items" class="view-all">查看全部</router-link>
      </div>
      <div class="items-grid">
        <div 
          v-for="item in latestItems" 
          :key="item.item_id"
          class="item-card"
          @click="goToItem(item.item_id)"
        >
          <div class="item-image">
            <img 
              :src="item.images && item.images[0] ? item.images[0] : '/placeholder.jpg'" 
              :alt="item.title"
            />
          </div>
          <div class="item-info">
            <h3>{{ item.title }}</h3>
            <p class="item-price">¥{{ item.price }}</p>
            <p class="item-seller">{{ item.username }}</p>
          </div>
        </div>
      </div>
    </section>

    <!-- 平台特色 -->
    <section class="features">
      <h2>平台特色</h2>
      <div class="features-grid">
        <div class="feature-card">
          <div class="feature-icon">🔒</div>
          <h3>安全可靠</h3>
          <p>实名认证，信用评级，保障交易安全</p>
        </div>
        <div class="feature-card">
          <div class="feature-icon">💬</div>
          <h3>便捷沟通</h3>
          <p>内置消息系统，买卖双方实时沟通</p>
        </div>
        <div class="feature-card">
          <div class="feature-icon">🚀</div>
          <h3>快速交易</h3>
          <p>校园内交易，面交更便捷</p>
        </div>
        <div class="feature-card">
          <div class="feature-icon">♻️</div>
          <h3>环保理念</h3>
          <p>让闲置物品重新焕发价值</p>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { itemAPI } from '@/api'

const router = useRouter()
const userStore = useUserStore()

const categories = ref([])
const latestItems = ref([])

const isLoggedIn = computed(() => userStore.isLoggedIn)

const loadCategories = async () => {
  try {
    const response = await itemAPI.getCategories()
    categories.value = response.categories || []
  } catch (error) {
    console.error('Failed to load categories:', error)
  }
}

const loadLatestItems = async () => {
  try {
    const response = await itemAPI.getItems({ 
      page: 1, 
      limit: 8, 
      sort_by: 'publish_date',
      sort_order: 'DESC'
    })
    latestItems.value = response.items || []
  } catch (error) {
    console.error('Failed to load latest items:', error)
  }
}

const goToCategory = (categoryId: number) => {
  router.push(`/items?category_id=${categoryId}`)
}

const goToItem = (itemId: number) => {
  router.push(`/items/${itemId}`)
}

onMounted(() => {
  loadCategories()
  loadLatestItems()
})
</script>

<style scoped>
.home {
  max-width: 1800px;
  margin: 0 auto;
}

/* 首页横幅 */
.hero {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 100px 40px;
  text-align: center;
  border-radius: 12px;
  margin-bottom: 80px;
}

.hero-content h1 {
  font-size: 3.5rem;
  margin-bottom: 25px;
  font-weight: 700;
}

.hero-content p {
  font-size: 1.2rem;
  margin-bottom: 40px;
  opacity: 0.9;
}

.hero-actions {
  display: flex;
  gap: 20px;
  justify-content: center;
  flex-wrap: wrap;
}

.btn {
  padding: 12px 30px;
  border-radius: 6px;
  text-decoration: none;
  font-weight: 500;
  transition: all 0.3s;
}

.btn-primary {
  background: white;
  color: #667eea;
}

.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0,0,0,0.2);
}

.btn-secondary {
  background: transparent;
  color: white;
  border: 2px solid white;
}

.btn-secondary:hover {
  background: white;
  color: #667eea;
}

/* 分类部分 */
.categories {
  margin-bottom: 60px;
}

.categories h2 {
  text-align: center;
  margin-bottom: 40px;
  color: #2c3e50;
  font-size: 2rem;
}

.category-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 30px;
}

.category-card {
  background: white;
  padding: 30px 20px;
  border-radius: 8px;
  text-align: center;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  cursor: pointer;
  transition: all 0.3s;
}

.category-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 4px 16px rgba(0,0,0,0.15);
}

.category-icon {
  font-size: 2.5rem;
  margin-bottom: 15px;
}

.category-card h3 {
  color: #2c3e50;
  margin-bottom: 10px;
}

.category-card p {
  color: #6c757d;
  font-size: 0.9rem;
}

/* 最新商品 */
.latest-items {
  margin-bottom: 60px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 40px;
}

.section-header h2 {
  color: #2c3e50;
  font-size: 2rem;
}

.view-all {
  color: #007bff;
  text-decoration: none;
  font-weight: 500;
}

.view-all:hover {
  text-decoration: underline;
}

.items-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 30px;
}

.item-card {
  background: white;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  cursor: pointer;
  transition: all 0.3s;
}

.item-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 4px 16px rgba(0,0,0,0.15);
}

.item-image {
  height: 200px;
  overflow: hidden;
}

.item-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.item-info {
  padding: 15px;
}

.item-info h3 {
  color: #2c3e50;
  margin-bottom: 8px;
  font-size: 1.1rem;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.item-price {
  color: #e74c3c;
  font-weight: 600;
  font-size: 1.2rem;
  margin-bottom: 5px;
}

.item-seller {
  color: #6c757d;
  font-size: 0.9rem;
}

/* 平台特色 */
.features {
  margin-bottom: 60px;
}

.features h2 {
  text-align: center;
  margin-bottom: 40px;
  color: #2c3e50;
  font-size: 2rem;
}

.features-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 40px;
}

.feature-card {
  text-align: center;
  padding: 40px 30px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.08);
  transition: all 0.3s;
}

.feature-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 20px rgba(0,0,0,0.12);
}

.feature-icon {
  font-size: 3.5rem;
  margin-bottom: 25px;
}

.feature-card h3 {
  color: #2c3e50;
  margin-bottom: 18px;
  font-size: 1.4rem;
}

.feature-card p {
  color: #6c757d;
  line-height: 1.6;
  font-size: 1rem;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .hero-content h1 {
    font-size: 2rem;
  }
  
  .hero-content p {
    font-size: 1rem;
  }
  
  .hero-actions {
    flex-direction: column;
    align-items: center;
  }
  
  .btn {
    width: 200px;
  }
  
  .section-header {
    flex-direction: column;
    gap: 20px;
    text-align: center;
  }
}
</style>
