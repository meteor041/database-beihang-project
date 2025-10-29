<template>
  <div class="home">
    <!-- 首页横幅 -->
    <section class="hero mb-12">
      <v-container>
        <div class="text-center text-white">
          <h1 class="text-h2 text-md-h1 font-weight-bold mb-4">校内二手物品交易平台</h1>
          <p class="text-h6 text-md-h5 mb-8 opacity-95">安全、便捷的校园二手交易平台，让闲置物品重新焕发价值</p>
          <div class="d-flex flex-column flex-sm-row justify-center ga-4">
            <v-btn
              color="white"
              size="x-large"
              prepend-icon="mdi-magnify"
              @click="router.push('/items')"
            >
              浏览商品
            </v-btn>
            <v-btn
              v-if="isLoggedIn"
              color="success"
              size="x-large"
              prepend-icon="mdi-plus"
              @click="router.push('/publish')"
            >
              发布商品
            </v-btn>
            <v-btn
              v-else
              color="white"
              variant="outlined"
              size="x-large"
              prepend-icon="mdi-account-plus"
              @click="router.push('/register')"
            >
              立即注册
            </v-btn>
          </div>
        </div>
      </v-container>
    </section>

    <v-container>
      <!-- 商品分类 -->
      <section class="categories mb-12">
        <h2 class="text-h4 font-weight-bold mb-6 d-flex align-center">
          <v-icon size="32" color="primary" class="mr-3">mdi-grid</v-icon>
          商品分类
        </h2>

        <v-progress-linear v-if="categoriesLoading" indeterminate color="primary" class="mb-4"></v-progress-linear>

        <v-row v-else-if="categories.length > 0">
          <v-col
            v-for="category in categories"
            :key="category.category_id"
            cols="6"
            sm="4"
            md="3"
            lg="2"
          >
            <v-card
              class="category-card text-center"
              hover
              @click="goToCategory(category.category_id)"
            >
              <v-card-text>
                <div class="category-icon text-h2 mb-3">📱</div>
                <h3 class="text-subtitle-1 font-weight-medium mb-2">{{ category.category_name }}</h3>
                <p class="text-caption text-grey">{{ category.item_count || 0 }} 件商品</p>
              </v-card-text>
            </v-card>
          </v-col>
        </v-row>

        <EmptyState
          v-else
          description="暂无分类数据"
        />
      </section>

      <!-- 最新商品 -->
      <section class="latest-items mb-12">
        <div class="d-flex justify-space-between align-center mb-6">
          <h2 class="text-h4 font-weight-bold d-flex align-center">
            <v-icon size="32" color="primary" class="mr-3">mdi-clock-outline</v-icon>
            最新商品
          </h2>
          <v-btn
            variant="text"
            color="primary"
            append-icon="mdi-arrow-right"
            @click="router.push('/items')"
          >
            查看全部
          </v-btn>
        </div>

        <v-progress-linear v-if="itemsLoading" indeterminate color="primary" class="mb-4"></v-progress-linear>

        <v-row v-else-if="latestItems.length > 0">
          <v-col
            v-for="item in latestItems"
            :key="item.item_id"
            cols="12"
            sm="6"
            md="4"
            lg="3"
          >
            <ItemCard :item="item" @click="goToItem(item.item_id)" />
          </v-col>
        </v-row>

        <EmptyState
          v-else
          description="暂无商品"
          action-text="发布商品"
          @action="router.push('/publish')"
        />
      </section>

      <!-- 平台特色 -->
      <section class="features mb-12">
        <h2 class="text-h4 font-weight-bold mb-6 d-flex align-center">
          <v-icon size="32" color="primary" class="mr-3">mdi-star</v-icon>
          平台特色
        </h2>

        <v-row>
          <v-col
            v-for="feature in features"
            :key="feature.title"
            cols="12"
            sm="6"
            md="3"
          >
            <v-card class="feature-card text-center h-100" hover>
              <v-card-text class="pa-6">
                <div class="feature-icon text-h1 mb-4">{{ feature.icon }}</div>
                <h3 class="text-h6 font-weight-medium mb-3">{{ feature.title }}</h3>
                <p class="text-body-2 text-grey-darken-1">{{ feature.description }}</p>
              </v-card-text>
            </v-card>
          </v-col>
        </v-row>
      </section>
    </v-container>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { useNotification } from '@/composables/useNotification'
import { itemAPI } from '@/api'
import ItemCard from '@/components/ItemCard.vue'
import EmptyState from '@/components/EmptyState.vue'
import type { Item, Category } from '@/types'

const router = useRouter()
const userStore = useUserStore()
const notification = useNotification()

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
    notification.error('加载分类失败')
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
    notification.error('加载商品失败')
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
  width: 100%;
}

/* 首页横幅 */
.hero {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 80px 0;
  border-radius: 16px;
  box-shadow: 0 8px 24px rgba(102, 126, 234, 0.3);
}

.category-card {
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  height: 100%;
}

.category-card:hover {
  transform: translateY(-4px);
}

.feature-card {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.feature-card:hover {
  transform: translateY(-4px);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .hero {
    padding: 60px 0;
  }
}
</style>
