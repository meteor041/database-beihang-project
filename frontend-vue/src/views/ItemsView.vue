<template>
  <div class="items-view">
    <div class="items-header">
      <h1>商品列表</h1>
      <div class="search-bar">
        <input
          v-model="searchKeyword"
          type="text"
          placeholder="搜索商品..."
          @keyup.enter="handleSearch"
          class="search-input"
        />
        <button @click="handleSearch" class="search-btn">搜索</button>
      </div>
    </div>

    <div class="items-filters">
      <div class="filter-group">
        <label>分类：</label>
        <select v-model="selectedCategory" @change="loadItems">
          <option value="">全部分类</option>
          <option 
            v-for="category in categories" 
            :key="category.category_id"
            :value="category.category_id"
          >
            {{ category.category_name }}
          </option>
        </select>
      </div>

      <div class="filter-group">
        <label>价格：</label>
        <input
          v-model="minPrice"
          type="number"
          placeholder="最低价"
          class="price-input"
        />
        <span>-</span>
        <input
          v-model="maxPrice"
          type="number"
          placeholder="最高价"
          class="price-input"
        />
      </div>

      <div class="filter-group">
        <label>排序：</label>
        <select v-model="sortBy" @change="loadItems">
          <option value="publish_date">发布时间</option>
          <option value="price">价格</option>
          <option value="view_count">浏览量</option>
        </select>
        <select v-model="sortOrder" @change="loadItems">
          <option value="DESC">降序</option>
          <option value="ASC">升序</option>
        </select>
      </div>

      <button @click="applyFilters" class="filter-btn">应用筛选</button>
    </div>

    <div v-if="loading" class="loading">
      加载中...
    </div>

    <div v-else-if="items.length === 0" class="no-items">
      暂无商品
    </div>

    <div v-else class="items-grid">
      <div 
        v-for="item in items" 
        :key="item.item_id"
        class="item-card"
        @click="goToItem(item.item_id)"
      >
        <div class="item-image">
          <img 
            :src="item.images && item.images[0] ? item.images[0] : '/placeholder.png'" 
            :alt="item.title"
          />
        </div>
        <div class="item-info">
          <h3>{{ item.title }}</h3>
          <p class="item-description">{{ item.description }}</p>
          <div class="item-details">
            <span class="item-price">¥{{ item.price }}</span>
            <span class="item-condition">{{ getConditionText(item.condition_level) }}</span>
          </div>
          <div class="item-meta">
            <span class="item-seller">{{ item.username }}</span>
            <span class="item-views">{{ item.view_count }} 次浏览</span>
          </div>
        </div>
      </div>
    </div>

    <div v-if="pagination.pages > 1" class="pagination">
      <button 
        @click="changePage(page - 1)"
        :disabled="page <= 1"
        class="page-btn"
      >
        上一页
      </button>
      
      <span class="page-info">
        第 {{ page }} 页，共 {{ pagination.pages }} 页
      </span>
      
      <button 
        @click="changePage(page + 1)"
        :disabled="page >= pagination.pages"
        class="page-btn"
      >
        下一页
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { itemAPI } from '@/api'
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
/* 使用设计系统变量 */
.items-view {
  max-width: 1800px;
  margin: 0 auto;
  padding: var(--spacing-2xl) var(--spacing-3xl);
}

.items-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--spacing-3xl);
}

.items-header h1 {
  color: var(--color-text-primary);
  margin: 0;
  font-size: var(--font-size-5xl);
}

.search-bar {
  display: flex;
  gap: var(--spacing-lg);
}

.search-input {
  padding: var(--spacing-md) var(--spacing-base);
  border: 1px solid var(--color-border-base);
  border-radius: var(--radius-base);
  width: 400px;
  font-size: var(--font-size-lg);
}

.search-btn {
  padding: var(--spacing-md) var(--spacing-xl);
  background-color: var(--color-primary);
  color: white;
  border: none;
  border-radius: var(--radius-base);
  cursor: pointer;
  font-size: var(--font-size-lg);
  transition: background-color var(--transition-fast);
}

.search-btn:hover {
  background-color: var(--color-primary-dark);
}

.items-filters {
  display: flex;
  gap: var(--spacing-2xl);
  align-items: center;
  margin-bottom: var(--spacing-3xl);
  padding: var(--spacing-xl) var(--spacing-2xl);
  background: var(--color-bg-page);
  border-radius: var(--radius-lg);
  flex-wrap: wrap;
}

.filter-group {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
}

.filter-group label {
  font-weight: var(--font-weight-medium);
  color: var(--color-text-primary);
  font-size: var(--font-size-lg);
}

.filter-group select,
.price-input {
  padding: var(--spacing-sm) var(--spacing-md);
  border: 1px solid var(--color-border-base);
  border-radius: var(--radius-base);
  font-size: var(--font-size-md);
  min-width: 120px;
}

.price-input {
  width: 100px;
}

.filter-btn {
  padding: var(--spacing-sm) var(--spacing-lg);
  background-color: var(--color-success);
  color: white;
  border: none;
  border-radius: var(--radius-base);
  cursor: pointer;
  font-size: var(--font-size-md);
  transition: background-color var(--transition-fast);
}

.filter-btn:hover {
  background-color: #218838;
}

.loading {
  text-align: center;
  padding: var(--spacing-3xl);
  color: var(--color-text-secondary);
  font-size: var(--font-size-xl);
}

.no-items {
  text-align: center;
  padding: var(--spacing-3xl);
  color: var(--color-text-secondary);
  font-size: var(--font-size-xl);
}

.items-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: var(--spacing-2xl);
  margin-bottom: var(--spacing-3xl);
}

.item-card {
  background: var(--color-bg-card);
  border-radius: var(--radius-lg);
  overflow: hidden;
  box-shadow: var(--shadow-card);
  cursor: pointer;
  transition: all var(--transition-base);
}

.item-card:hover {
  transform: translateY(-6px);
  box-shadow: var(--shadow-card-hover);
}

.item-image {
  height: 220px;
  overflow: hidden;
}

.item-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.item-info {
  padding: var(--spacing-lg);
}

.item-info h3 {
  color: var(--color-text-primary);
  margin: 0 0 var(--spacing-sm) 0;
  font-size: var(--font-size-2xl);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.item-description {
  color: var(--color-text-secondary);
  font-size: var(--font-size-base);
  margin: 0 0 var(--spacing-md) 0;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

.item-details {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--spacing-md);
}

.item-price {
  color: var(--color-price);
  font-weight: var(--font-weight-semibold);
  font-size: var(--font-size-3xl);
}

.item-condition {
  background-color: var(--color-bg-page);
  color: var(--color-text-secondary);
  padding: var(--spacing-xs) var(--spacing-sm);
  border-radius: var(--radius-full);
  font-size: var(--font-size-xs);
}

.item-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: var(--font-size-base);
  color: var(--color-text-secondary);
}

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: var(--spacing-lg);
  margin-top: var(--spacing-3xl);
}

.page-btn {
  padding: var(--spacing-sm) var(--spacing-base);
  background-color: var(--color-primary);
  color: white;
  border: none;
  border-radius: var(--radius-sm);
  cursor: pointer;
  transition: background-color var(--transition-fast);
}

.page-btn:hover:not(:disabled) {
  background-color: var(--color-primary-dark);
}

.page-btn:disabled {
  background-color: var(--color-info);
  cursor: not-allowed;
}

.page-info {
  color: var(--color-text-secondary);
  font-weight: var(--font-weight-medium);
}

@media (max-width: 768px) {
  .items-header {
    flex-direction: column;
    gap: var(--spacing-lg);
    align-items: stretch;
  }

  .search-input {
    width: 100%;
  }

  .items-filters {
    flex-direction: column;
    align-items: stretch;
  }

  .filter-group {
    justify-content: space-between;
  }

  .items-grid {
    grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  }
}
</style>