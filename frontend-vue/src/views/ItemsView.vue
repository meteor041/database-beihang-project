<template>
  <div class="items-view">
    <!-- 页面头部 -->
    <div class="page-header">
      <h1 class="page-title">
        <el-icon><Goods /></el-icon>
        商品列表
      </h1>
      <p class="page-meta">{{ pagination.total }} 件商品</p>
    </div>

    <!-- 搜索栏 -->
    <div class="search-section">
      <el-input
        v-model="searchKeyword"
        placeholder="搜索商品标题、描述..."
        size="large"
        clearable
        @keyup.enter="handleSearch"
        class="search-input"
      >
        <template #prefix>
          <el-icon><Search /></el-icon>
        </template>
        <template #append>
          <el-button :icon="Search" @click="handleSearch">
            搜索
          </el-button>
        </template>
      </el-input>
    </div>

    <!-- 筛选栏 -->
    <div class="filter-bar">
      <div class="filter-item">
        <span class="filter-label">分类</span>
        <el-select
          v-model="selectedCategory"
          placeholder="全部"
          @change="applyFilters"
          clearable
          size="default"
          style="width: 160px"
        >
          <el-option
            v-for="category in categories"
            :key="category.category_id"
            :value="category.category_id"
            :label="category.category_name"
          />
        </el-select>
      </div>

      <div class="filter-item">
        <span class="filter-label">价格范围</span>
        <el-input
          v-model="minPrice"
          type="number"
          placeholder="最低价"
          size="default"
          style="width: 100px"
          clearable
        />
        <span class="filter-divider">-</span>
        <el-input
          v-model="maxPrice"
          type="number"
          placeholder="最高价"
          size="default"
          style="width: 100px"
          clearable
        />
      </div>

      <div class="filter-item">
        <span class="filter-label">排序</span>
        <el-select
          v-model="sortBy"
          @change="applyFilters"
          size="default"
          style="width: 120px"
        >
          <el-option value="publish_date" label="发布时间" />
          <el-option value="price" label="价格" />
          <el-option value="view_count" label="浏览量" />
        </el-select>
        <el-select
          v-model="sortOrder"
          @change="applyFilters"
          size="default"
          style="width: 90px"
        >
          <el-option value="DESC" label="降序" />
          <el-option value="ASC" label="升序" />
        </el-select>
      </div>

      <el-button
        type="primary"
        @click="applyFilters"
        :icon="Filter"
        class="filter-apply-btn"
      >
        应用筛选
      </el-button>
    </div>

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
import { Search, Filter, Goods } from '@element-plus/icons-vue'
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
/* 现代扁平化风格 - Twitter/YouTube/Google 风格 */

.items-view {
  max-width: var(--container-max-width);
  margin: 0 auto;
  padding: var(--spacing-6);
  background: var(--color-bg-page);
}

/* 页面头部 - 扁平简洁 */
.page-header {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-2);
  margin-bottom: var(--spacing-8);
}

.page-title {
  display: flex;
  align-items: center;
  gap: var(--spacing-3);
  font-size: var(--font-size-4xl);
  font-weight: var(--font-weight-bold);
  color: var(--color-text-primary);
  margin: 0;
}

.page-title .el-icon {
  color: var(--color-primary);
}

.page-meta {
  font-size: var(--font-size-base);
  color: var(--color-text-secondary);
  margin: 0;
}

/* 搜索栏 - 扁平 */
.search-section {
  margin-bottom: var(--spacing-6);
}

.search-input {
  max-width: 100%;
}

.search-input :deep(.el-input__wrapper) {
  box-shadow: var(--shadow-sm);
  border: 1px solid var(--color-border-base);
}

.search-input :deep(.el-input__wrapper:hover) {
  border-color: var(--color-primary-light);
}

/* 筛选栏 - 扁平 */
.filter-bar {
  display: flex;
  align-items: center;
  gap: var(--spacing-6);
  padding: var(--spacing-4);
  background: var(--color-bg-section);
  border: 1px solid var(--color-border-base);
  border-radius: var(--radius-lg);
  margin-bottom: var(--spacing-6);
  flex-wrap: wrap;
}

.filter-item {
  display: flex;
  align-items: center;
  gap: var(--spacing-3);
}

.filter-label {
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
  font-weight: var(--font-weight-medium);
  white-space: nowrap;
}

.filter-divider {
  color: var(--color-text-placeholder);
  margin: 0 var(--spacing-1);
}

.filter-apply-btn {
  margin-left: auto;
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
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: var(--spacing-4);
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

  .page-title {
    font-size: var(--font-size-3xl);
  }

  .filter-bar {
    flex-direction: column;
    align-items: stretch;
    gap: var(--spacing-4);
  }

  .filter-item {
    justify-content: space-between;
  }

  .filter-apply-btn {
    margin-left: 0;
    width: 100%;
  }

  .items-grid {
    grid-template-columns: 1fr;
    gap: var(--spacing-3);
  }
}
</style>