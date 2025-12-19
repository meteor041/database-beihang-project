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
            <div class="category-icon">{{ getCategoryIcon(category.category_name) }}</div>
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
            <ItemCard
              :item="item"
              :show-wishlist-count="true"
              :wishlist-count="(item as any).wishlist_count || 0"
              @click="goToItem(item.item_id)"
            />
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
import { Search, Plus, UserFilled, Grid, Clock, ArrowRight, Star } from '@element-plus/icons-vue'
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

// 根据分类名称获取对应图标
const getCategoryIcon = (categoryName: string): string => {
  const iconMap: Record<string, string> = {
    '电子产品': '💻',
    '图书教材': '📚',
    '生活用品': '🛋️',
    '服装配饰': '👔',
    '运动户外': '⚽',
    '其他': '🎁',
    // 更多匹配
    '手机': '📱',
    '电脑': '💻',
    '平板': '📱',
    '耳机': '🎧',
    '相机': '📷',
    '书籍': '📚',
    '教材': '📖',
    '文具': '✏️',
    '家具': '🛋️',
    '家电': '🔌',
    '日用品': '🧴',
    '服装': '👕',
    '鞋子': '👟',
    '包包': '🎒',
    '配饰': '⌚',
    '运动': '🏀',
    '户外': '🏕️',
    '健身': '💪',
    '自行车': '🚲'
  }

  // 尝试精确匹配
  if (iconMap[categoryName]) {
    return iconMap[categoryName]
  }

  // 尝试模糊匹配
  for (const [key, icon] of Object.entries(iconMap)) {
    if (categoryName.includes(key) || key.includes(categoryName)) {
      return icon
    }
  }

  // 默认图标
  return '🏷️'
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
/* 现代扁平化风格 - Twitter/YouTube/Google 风格 */

.home {
  width: 100%;
  padding: var(--spacing-6) var(--spacing-8);
  background: var(--color-bg-page);
  min-height: 100vh;
}

/* 首页横幅 - 扁平简洁 */
.hero {
  background: var(--color-bg-section);
  border: 1px solid var(--color-border-base);
  border-radius: var(--radius-2xl);
  padding: var(--spacing-10) var(--spacing-6);
  text-align: center;
  margin-bottom: var(--spacing-10);
}

.hero-content h1 {
  font-size: var(--font-size-5xl);
  margin: 0 0 var(--spacing-4) 0;
  font-weight: var(--font-weight-bold);
  color: var(--color-text-primary);
}

.hero-content p {
  font-size: var(--font-size-xl);
  margin: 0 0 var(--spacing-8) 0;
  color: var(--color-text-secondary);
  line-height: var(--line-height-relaxed);
}

.hero-actions {
  display: flex;
  gap: var(--spacing-3);
  justify-content: center;
  flex-wrap: wrap;
}

.hero-actions .el-button {
  min-width: 140px;
}

/* 统一的区块样式 */
.categories,
.latest-items,
.features {
  margin-bottom: var(--spacing-10);
}

/* 统一的标题样式 */
.categories h2,
.latest-items h2,
.features h2 {
  display: flex;
  align-items: center;
  gap: var(--spacing-3);
  margin-bottom: var(--spacing-6);
  font-size: var(--font-size-3xl);
  color: var(--color-text-primary);
  font-weight: var(--font-weight-bold);
}

.categories h2 .el-icon,
.latest-items h2 .el-icon,
.features h2 .el-icon {
  color: var(--color-primary);
}

/* 区块头部 */
.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--spacing-6);
}

.section-header .el-link {
  font-size: var(--font-size-base);
  display: flex;
  align-items: center;
  gap: var(--spacing-1);
  font-weight: var(--font-weight-medium);
}

/* 分类卡片 - 扁平带边框 */
.category-card {
  text-align: center;
  cursor: pointer;
  transition: all var(--transition-base);
  margin-bottom: var(--spacing-4);
  background: var(--color-bg-card);
  border: 1px solid var(--color-border-base);
  border-radius: var(--radius-lg);
}

.category-card:hover {
  border-color: var(--color-primary-light);
  box-shadow: var(--shadow-md);
  transform: translateY(-2px);
}

.category-card :deep(.el-card__body) {
  padding: var(--spacing-5) var(--spacing-4);
}

.category-icon {
  font-size: 48px;
  margin-bottom: var(--spacing-3);
}

.category-card h3 {
  font-size: var(--font-size-lg);
  color: var(--color-text-primary);
  margin: 0 0 var(--spacing-2) 0;
  font-weight: var(--font-weight-medium);
}

.category-card p {
  color: var(--color-text-secondary);
  font-size: var(--font-size-sm);
  margin: 0;
}

/* 平台特色卡片 - 扁平带边框 */
.feature-card {
  text-align: center;
  height: 100%;
  transition: all var(--transition-base);
  background: var(--color-bg-card);
  border: 1px solid var(--color-border-base);
  border-radius: var(--radius-lg);
}

.feature-card:hover {
  border-color: var(--color-border-light);
  box-shadow: var(--shadow-md);
  transform: translateY(-2px);
}

.feature-card :deep(.el-card__body) {
  padding: var(--spacing-6) var(--spacing-5);
}

.feature-icon {
  font-size: 56px;
  margin-bottom: var(--spacing-4);
}

.feature-card h3 {
  font-size: var(--font-size-xl);
  color: var(--color-text-primary);
  margin: 0 0 var(--spacing-3) 0;
  font-weight: var(--font-weight-semibold);
}

.feature-card p {
  color: var(--color-text-secondary);
  line-height: var(--line-height-relaxed);
  font-size: var(--font-size-sm);
  margin: 0;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .home {
    padding: var(--spacing-4);
  }

  .hero {
    padding: var(--spacing-8) var(--spacing-4);
    margin-bottom: var(--spacing-8);
  }

  .hero-content h1 {
    font-size: var(--font-size-3xl);
  }

  .hero-content p {
    font-size: var(--font-size-base);
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
    font-size: var(--font-size-2xl);
  }

  .section-header {
    flex-direction: column;
    gap: var(--spacing-3);
    align-items: flex-start;
  }

  .categories,
  .latest-items,
  .features {
    margin-bottom: var(--spacing-8);
  }
}
</style>
