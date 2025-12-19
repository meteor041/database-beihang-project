<template>
  <div class="items-view">
    <!-- 页面头部 - 简化现代化 -->
    <div class="page-header">
      <div class="header-text">
        <h1 class="page-title">商品市场</h1>
        <p class="page-subtitle">发现 {{ pagination.total }} 件优质好物</p>
      </div>
      <el-button type="primary" size="large" @click="router.push('/publish')" :icon="Plus">
        发布商品
      </el-button>
    </div>

    <!-- 搜索栏 - 突出显示 -->
    <div class="search-section">
      <div class="search-container">
        <el-input
          v-model="searchKeyword"
          placeholder="搜索你想要的商品..."
          size="large"
          clearable
          @keyup.enter="handleSearch"
          @clear="handleSearch"
          class="search-input"
        >
          <template #prefix>
            <el-icon class="search-icon"><Search /></el-icon>
          </template>
        </el-input>
        <el-button type="primary" size="large" :icon="Search" @click="handleSearch">
          搜索
        </el-button>
      </div>
    </div>

    <!-- 筛选器卡片 - 集中布局 -->
    <el-card class="filter-card" shadow="never">
      <div class="filter-grid">
        <div class="filter-group">
          <label class="filter-label">
            <el-icon><Goods /></el-icon>
            分类
          </label>
          <el-select
            v-model="selectedCategory"
            placeholder="全部分类"
            @change="applyFilters"
            clearable
            size="default"
          >
            <el-option
              v-for="category in categories"
              :key="category.category_id"
              :value="category.category_id"
              :label="category.category_name"
            />
          </el-select>
        </div>

        <div class="filter-group">
          <label class="filter-label">
            <el-icon><Money /></el-icon>
            价格
          </label>
          <div class="price-inputs">
            <el-input
              v-model="minPrice"
              type="number"
              placeholder="最低"
              size="default"
              @change="applyFilters"
              clearable
            />
            <span class="price-divider">-</span>
            <el-input
              v-model="maxPrice"
              type="number"
              placeholder="最高"
              size="default"
              @change="applyFilters"
              clearable
            />
          </div>
        </div>

        <div class="filter-group">
          <label class="filter-label">
            <el-icon><Sort /></el-icon>
            排序
          </label>
          <div class="sort-controls">
            <el-select
              v-model="sortBy"
              @change="applyFilters"
              size="default"
            >
              <el-option value="publish_date" label="最新发布" />
              <el-option value="price" label="价格" />
              <el-option value="view_count" label="浏览量" />
              <el-option value="wishlist_count" label="收藏数" />
            </el-select>
            <el-select
              v-model="sortOrder"
              @change="applyFilters"
              size="default"
              style="width: 90px"
            >
              <el-option value="DESC" label="↓" />
              <el-option value="ASC" label="↑" />
            </el-select>
          </div>
        </div>

        <div class="filter-group">
          <el-button
            @click="resetFilters"
            size="default"
            style="margin-top: 24px"
          >
            <el-icon><RefreshLeft /></el-icon>
            重置
          </el-button>
        </div>
      </div>
    </el-card>

    <!-- 加载状态 -->
    <div v-if="loading" class="loading-container" v-loading="loading" element-loading-text="加载中...">
      <div style="height: 400px"></div>
    </div>

    <!-- 空状态 -->
    <el-empty
      v-else-if="items.length === 0"
      description="暂无商品"
      :image-size="100"
    >
      <el-button type="primary" @click="router.push('/publish')">
        发布商品
      </el-button>
    </el-empty>

    <!-- 商品网格 -->
    <div v-else class="items-grid">
      <ItemCard
        v-for="item in items"
        :key="item.item_id"
        :item="item"
        :show-wishlist-count="true"
        :wishlist-count="(item as any).wishlist_count || 0"
        @click="goToItem(item.item_id)"
      />
    </div>

    <!-- 分页 -->
    <div v-if="pagination.pages > 1" class="pagination-wrapper">
      <el-pagination
        v-model:current-page="page"
        :page-size="pagination.limit"
        :total="pagination.total"
        layout="prev, pager, next"
        @current-change="changePage"
        background
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { itemAPI } from '@/api'
import { ElMessage } from 'element-plus'
import { Search, Goods, Money, Sort, RefreshLeft, Plus } from '@element-plus/icons-vue'
import ItemCard from '@/components/ItemCard.vue'
import type { Item, Category } from '@/types'

interface Pagination {
  page: number
  limit: number
  total: number
  pages: number
}

const router = useRouter()
const route = useRoute()

const items = ref<Item[]>([])
const categories = ref<Category[]>([])
const loading = ref(false)
const pagination = ref<Pagination>({
  page: 1,
  limit: 20,
  total: 0,
  pages: 0
})

const searchKeyword = ref('')
const selectedCategory = ref('')
const minPrice = ref('')
const maxPrice = ref('')
const sortBy = ref('publish_date')
const sortOrder = ref('DESC')
const page = ref(1)

const conditionMap: Record<string, string> = {
  'brand_new': '全新',
  'like_new': '几乎全新',
  'very_good': '非常好',
  'good': '良好',
  'acceptable': '可接受'
}

const getConditionText = (condition: string): string => {
  return conditionMap[condition] || condition
}

const loadCategories = async () => {
  try {
    const response = await itemAPI.getCategories()
    categories.value = response.categories || []
  } catch (error) {
    console.error('Failed to load categories:', error)
  }
}

const loadItems = async () => {
  loading.value = true
  try {
    const params: Record<string, string | number> = {
      page: page.value,
      limit: pagination.value.limit,
      sort_by: sortBy.value,
      sort_order: sortOrder.value
    }

    if (selectedCategory.value) {
      params.category_id = selectedCategory.value
    }
    if (minPrice.value) {
      params.min_price = minPrice.value
    }
    if (maxPrice.value) {
      params.max_price = maxPrice.value
    }

    const response = await itemAPI.getItems(params)
    items.value = response.items || []
    pagination.value = response.pagination || pagination.value
  } catch (error) {
    console.error('Failed to load items:', error)
  } finally {
    loading.value = false
  }
}

const handleSearch = async (): Promise<void> => {
  if (!searchKeyword.value.trim()) {
    loadItems()
    return
  }

  loading.value = true
  try {
    const params: any = {
      keyword: searchKeyword.value,
      page: 1,
      limit: pagination.value.limit,
      sort_by: sortBy.value,
      sort_order: sortOrder.value
    }

    if (selectedCategory.value) {
      params.category_id = selectedCategory.value
    }
    if (minPrice.value) {
      params.min_price = minPrice.value
    }
    if (maxPrice.value) {
      params.max_price = maxPrice.value
    }

    const response = await itemAPI.searchItems(params)
    items.value = response.items || []
    page.value = 1
  } catch (error) {
    console.error('Failed to search items:', error)
  } finally {
    loading.value = false
  }
}

const applyFilters = (): void => {
  page.value = 1
  handleSearch()
}

const resetFilters = (): void => {
  searchKeyword.value = ''
  selectedCategory.value = ''
  minPrice.value = ''
  maxPrice.value = ''
  sortBy.value = 'publish_date'
  sortOrder.value = 'DESC'
  page.value = 1
  loadItems()
}

const changePage = (newPage: number): void => {
  if (newPage >= 1 && newPage <= pagination.value.pages) {
    page.value = newPage
    loadItems()
  }
}

const goToItem = (itemId: number): void => {
  router.push(`/items/${itemId}`)
}

// 监听路由参数变化
watch(() => route.query, (newQuery) => {
  if (newQuery.category_id) {
    selectedCategory.value = newQuery.category_id as string
  }
  loadItems()
}, { immediate: true })

onMounted(() => {
  loadCategories()
  
  // 从路由参数获取分类ID
  if (route.query.category_id) {
    selectedCategory.value = route.query.category_id as string
  }
  
  loadItems()
})
</script>

<style scoped>
.items-view {
  width: 100%;
  padding: var(--spacing-6) var(--spacing-8);
  background: var(--color-bg-page);
  min-height: 100vh;
}

/* 页面头部 - 现代化 */
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--spacing-8);
  gap: var(--spacing-4);
}

.header-text {
  flex: 1;
}

.page-title {
  font-size: var(--font-size-4xl);
  font-weight: var(--font-weight-bold);
  color: var(--color-text-primary);
  margin: 0 0 var(--spacing-2) 0;
  background: linear-gradient(135deg, var(--color-primary) 0%, var(--color-primary-dark) 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.page-subtitle {
  font-size: var(--font-size-base);
  color: var(--color-text-secondary);
  margin: 0;
}

/* 搜索区域 - 突出显示 */
.search-section {
  margin-bottom: var(--spacing-6);
}

.search-container {
  max-width: 100%;
  margin: 0 auto;
  display: flex;
  gap: var(--spacing-3);
  padding: var(--spacing-6);
  background: linear-gradient(135deg, rgba(64, 158, 255, 0.05) 0%, rgba(64, 158, 255, 0.02) 100%);
  border-radius: var(--radius-xl);
  border: 1px solid var(--color-border-light);
}

.search-input {
  flex: 1;
}

.search-input :deep(.el-input__wrapper) {
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.search-icon {
  color: var(--color-primary);
  font-size: 18px;
}

/* 筛选卡片 - 集中布局 */
.filter-card {
  margin-bottom: var(--spacing-6);
  border: 1px solid var(--color-border-base);
}

.filter-card :deep(.el-card__body) {
  padding: var(--spacing-5);
}

.filter-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: var(--spacing-5);
  align-items: start;
}

.filter-group {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-2);
}

.filter-label {
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-medium);
  color: var(--color-text-secondary);
  display: flex;
  align-items: center;
  gap: var(--spacing-1);
}

.filter-label .el-icon {
  color: var(--color-primary);
}

.price-inputs {
  display: flex;
  align-items: center;
  gap: var(--spacing-2);
}

.price-inputs .el-input {
  flex: 1;
}

.price-divider {
  color: var(--color-text-secondary);
}

.sort-controls {
  display: flex;
  gap: var(--spacing-2);
}

.sort-controls .el-select {
  flex: 1;
}

/* 加载状态 */
.loading-container {
  min-height: 400px;
  display: flex;
  align-items: center;
  justify-content: center;
}

/* 商品网格 */
.items-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  gap: var(--spacing-5);
  margin-bottom: var(--spacing-8);
}

/* 分页 */
.pagination-wrapper {
  display: flex;
  justify-content: center;
  padding: var(--spacing-6) 0;
}

/* 响应式 */
@media (max-width: 768px) {
  .items-view {
    padding: var(--spacing-4);
  }

  .page-header {
    flex-direction: column;
    align-items: flex-start;
    gap: var(--spacing-3);
  }

  .page-header .el-button {
    width: 100%;
  }

  .page-title {
    font-size: var(--font-size-3xl);
  }

  .search-container {
    flex-direction: column;
    padding: var(--spacing-4);
  }

  .filter-grid {
    grid-template-columns: 1fr;
    gap: var(--spacing-4);
  }

  .items-grid {
    grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
    gap: var(--spacing-3);
  }
}
</style>