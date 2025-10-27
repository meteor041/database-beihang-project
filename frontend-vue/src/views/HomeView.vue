<template>
  <div class="home">
    <!-- 首页横幅 -->
    <section class="hero">
      <div class="hero-content">
        <h1>校内二手物品交易平台</h1>
        <p>安全、便捷的校园二手交易平台，让闲置物品重新焕发价值</p>
        <div class="hero-actions">
          <el-button type="primary" size="large" @click="router.push('/items')">
            <el-icon><Search /></el-icon>
            浏览商品
          </el-button>
          <el-button
            v-if="isLoggedIn"
            type="success"
            size="large"
            @click="router.push('/publish')"
          >
            <el-icon><Plus /></el-icon>
            发布商品
          </el-button>
          <el-button
            v-else
            type="success"
            size="large"
            plain
            @click="router.push('/register')"
          >
            <el-icon><UserFilled /></el-icon>
            立即注册
          </el-button>
        </div>
      </div>
    </section>

    <!-- 商品分类 -->
    <section class="categories">
      <h2>
        <el-icon><Grid /></el-icon>
        商品分类
      </h2>

      <el-row :gutter="20" v-loading="categoriesLoading">
        <el-col
          v-for="category in categories"
          :key="category.category_id"
          :xs="12"
          :sm="8"
          :md="6"
          :lg="4"
        >
          <el-card
            class="category-card"
            shadow="hover"
            @click="goToCategory(category.category_id)"
          >
            <div class="category-icon">📱</div>
            <h3>{{ category.category_name }}</h3>
            <p>{{ category.item_count || 0 }} 件商品</p>
          </el-card>
        </el-col>
      </el-row>

      <EmptyState
        v-if="!categoriesLoading && categories.length === 0"
        description="暂无分类数据"
      />
    </section>

    <!-- 最新商品 -->
    <section class="latest-items">
      <div class="section-header">
        <h2>
          <el-icon><Clock /></el-icon>
          最新商品
        </h2>
        <el-link type="primary" @click="router.push('/items')">
          查看全部 <el-icon><ArrowRight /></el-icon>
        </el-link>
      </div>

      <div v-loading="itemsLoading">
        <el-row :gutter="20" v-if="latestItems.length > 0">
          <el-col
            v-for="item in latestItems"
            :key="item.item_id"
            :xs="24"
            :sm="12"
            :md="8"
            :lg="6"
          >
            <ItemCard :item="item" @click="goToItem(item.item_id)" />
          </el-col>
        </el-row>

        <EmptyState
          v-else-if="!itemsLoading"
          description="暂无商品"
          action-text="发布商品"
          @action="router.push('/publish')"
        />
      </div>
    </section>

    <!-- 平台特色 -->
    <section class="features">
      <h2>
        <el-icon><Star /></el-icon>
        平台特色
      </h2>

      <el-row :gutter="30">
        <el-col
          v-for="feature in features"
          :key="feature.title"
          :xs="24"
          :sm="12"
          :md="6"
        >
          <el-card class="feature-card" shadow="hover">
            <div class="feature-icon">{{ feature.icon }}</div>
            <h3>{{ feature.title }}</h3>
            <p>{{ feature.description }}</p>
          </el-card>
        </el-col>
      </el-row>
    </section>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { itemAPI } from '@/api'
import { ElMessage } from 'element-plus'
import ItemCard from '@/components/ItemCard.vue'
import EmptyState from '@/components/EmptyState.vue'
import type { Item, Category } from '@/types'

const router = useRouter()
const userStore = useUserStore()

const categories = ref<Category[]>([])
const latestItems = ref<Item[]>([])
const categoriesLoading = ref(false)
const itemsLoading = ref(false)

const isLoggedIn = computed(() => userStore.isLoggedIn)

// 平台特色数据
const features = [
  {
    icon: '🔒',
    title: '安全可靠',
    description: '实名认证，信用评级，保障交易安全'
  },
  {
    icon: '💬',
    title: '便捷沟通',
    description: '内置消息系统，买卖双方实时沟通'
  },
  {
    icon: '🚀',
    title: '快速交易',
    description: '校园内交易，面交更便捷'
  },
  {
    icon: '♻️',
    title: '环保理念',
    description: '让闲置物品重新焕发价值'
  }
]

// 加载分类
const loadCategories = async () => {
  try {
    categoriesLoading.value = true
    const response: any = await itemAPI.getCategories()
    categories.value = response.categories || []
  } catch (error) {
    console.error('Failed to load categories:', error)
    ElMessage.error('加载分类失败')
  } finally {
    categoriesLoading.value = false
  }
}

// 加载最新商品
const loadLatestItems = async () => {
  try {
    itemsLoading.value = true
    const response: any = await itemAPI.getItems({
      page: 1,
      limit: 8,
      sort_by: 'publish_date',
      sort_order: 'DESC',
      status: 'available'
    })
    latestItems.value = response.items || []
  } catch (error) {
    console.error('Failed to load latest items:', error)
    ElMessage.error('加载商品失败')
  } finally {
    itemsLoading.value = false
  }
}

// 跳转到分类页面
const goToCategory = (categoryId: number) => {
  router.push(`/items?category_id=${categoryId}`)
}

// 跳转到商品详情
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
  max-width: 1400px;
  margin: 0 auto;
}

/* 首页横幅 */
.hero {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 80px 40px;
  text-align: center;
  border-radius: 16px;
  margin-bottom: 60px;
  box-shadow: 0 8px 24px rgba(102, 126, 234, 0.3);
}

.hero-content h1 {
  font-size: 3rem;
  margin: 0 0 20px 0;
  font-weight: 700;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.hero-content p {
  font-size: 1.2rem;
  margin: 0 0 40px 0;
  opacity: 0.95;
}

.hero-actions {
  display: flex;
  gap: 16px;
  justify-content: center;
  flex-wrap: wrap;
}

.hero-actions .el-button {
  min-width: 140px;
  transition: transform 0.2s;
}

.hero-actions .el-button:hover {
  transform: translateY(-2px);
}

/* 分类部分 */
.categories {
  margin-bottom: 60px;
}

.categories h2,
.latest-items h2,
.features h2 {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 30px;
  font-size: 1.8rem;
  color: #303133;
  font-weight: 600;
}

.category-card {
  text-align: center;
  cursor: pointer;
  transition: all 0.3s;
  margin-bottom: 20px;
}

.category-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.12);
}

.category-icon {
  font-size: 3rem;
  margin-bottom: 15px;
}

.category-card h3 {
  font-size: 1.1rem;
  color: #303133;
  margin: 0 0 8px 0;
}

.category-card p {
  color: #909399;
  font-size: 0.9rem;
  margin: 0;
}

/* 最新商品 */
.latest-items {
  margin-bottom: 60px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
}

.section-header .el-link {
  font-size: 16px;
  display: flex;
  align-items: center;
  gap: 4px;
}

/* 平台特色 */
.features {
  margin-bottom: 60px;
}

.feature-card {
  text-align: center;
  height: 100%;
  transition: all 0.3s;
}

.feature-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.12);
}

.feature-icon {
  font-size: 3.5rem;
  margin-bottom: 20px;
}

.feature-card h3 {
  font-size: 1.3rem;
  color: #303133;
  margin: 0 0 15px 0;
  font-weight: 600;
}

.feature-card p {
  color: #606266;
  line-height: 1.6;
  font-size: 14px;
  margin: 0;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .hero {
    padding: 60px 20px;
    margin-bottom: 40px;
  }

  .hero-content h1 {
    font-size: 2rem;
  }

  .hero-content p {
    font-size: 1rem;
  }

  .hero-actions {
    flex-direction: column;
    align-items: stretch;
  }

  .hero-actions .el-button {
    width: 100%;
  }

  .categories h2,
  .latest-items h2,
  .features h2 {
    font-size: 1.5rem;
  }

  .section-header {
    flex-direction: column;
    gap: 16px;
    align-items: flex-start;
  }
}
</style>
