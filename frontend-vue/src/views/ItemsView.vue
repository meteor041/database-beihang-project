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
            :src="item.images && item.images[0] ? item.images[0] : '/placeholder.jpg'" 
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

const router = useRouter()
const route = useRoute()

const items = ref([])
const categories = ref([])
const loading = ref(false)
const pagination = ref({
  page: 1,
  limit: 20,
  total: 0,
  pages: 0
})

// 搜索和筛选参数
const searchKeyword = ref('')
const selectedCategory = ref('')
const minPrice = ref('')
const maxPrice = ref('')
const sortBy = ref('publish_date')
const sortOrder = ref('DESC')
const page = ref(1)

const conditionMap = {
  'brand_new': '全新',
  'like_new': '几乎全新',
  'very_good': '非常好',
  'good': '良好',
  'acceptable': '可接受'
}

const getConditionText = (condition: string) => {
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

const handleSearch = async () => {
  if (!searchKeyword.value.trim()) {
    loadItems()
    return
  }

  loading.value = true
  try {
    const params: Record<string, string | number> = {
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

const applyFilters = () => {
  page.value = 1
  handleSearch()
}

const changePage = (newPage: number) => {
  if (newPage >= 1 && newPage <= pagination.value.pages) {
    page.value = newPage
    loadItems()
  }
}

const goToItem = (itemId: number) => {
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
  max-width: 1800px;
  margin: 0 auto;
  padding: 30px 40px;
}

.items-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 40px;
}

.items-header h1 {
  color: #2c3e50;
  margin: 0;
  font-size: 2.5rem;
}

.search-bar {
  display: flex;
  gap: 15px;
}

.search-input {
  padding: 12px 16px;
  border: 1px solid #ddd;
  border-radius: 6px;
  width: 400px;
  font-size: 16px;
}

.search-btn {
  padding: 12px 24px;
  background-color: #007bff;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 16px;
}

.search-btn:hover {
  background-color: #0056b3;
}

.items-filters {
  display: flex;
  gap: 30px;
  align-items: center;
  margin-bottom: 40px;
  padding: 25px 30px;
  background: #f8f9fa;
  border-radius: 10px;
  flex-wrap: wrap;
}

.filter-group {
  display: flex;
  align-items: center;
  gap: 12px;
}

.filter-group label {
  font-weight: 500;
  color: #2c3e50;
  font-size: 16px;
}

.filter-group select,
.price-input {
  padding: 10px 12px;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 15px;
  min-width: 120px;
}

.price-input {
  width: 100px;
}

.filter-btn {
  padding: 10px 20px;
  background-color: #28a745;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 15px;
}

.filter-btn:hover {
  background-color: #218838;
}

.loading {
  text-align: center;
  padding: 40px;
  color: #6c757d;
  font-size: 18px;
}

.no-items {
  text-align: center;
  padding: 40px;
  color: #6c757d;
  font-size: 18px;
}

.items-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 30px;
  margin-bottom: 40px;
}

.item-card {
  background: white;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 4px 12px rgba(0,0,0,0.08);
  cursor: pointer;
  transition: all 0.3s;
}

.item-card:hover {
  transform: translateY(-6px);
  box-shadow: 0 8px 25px rgba(0,0,0,0.15);
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
  padding: 20px;
}

.item-info h3 {
  color: #2c3e50;
  margin: 0 0 10px 0;
  font-size: 1.2rem;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.item-description {
  color: #6c757d;
  font-size: 0.95rem;
  margin: 0 0 12px 0;
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
  margin-bottom: 12px;
}

.item-price {
  color: #e74c3c;
  font-weight: 600;
  font-size: 1.3rem;
}

.item-condition {
  background-color: #f8f9fa;
  color: #6c757d;
  padding: 4px 10px;
  border-radius: 15px;
  font-size: 0.85rem;
}

.item-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.95rem;
  color: #6c757d;
}

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 20px;
  margin-top: 40px;
}

.page-btn {
  padding: 8px 16px;
  background-color: #007bff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.page-btn:hover:not(:disabled) {
  background-color: #0056b3;
}

.page-btn:disabled {
  background-color: #6c757d;
  cursor: not-allowed;
}

.page-info {
  color: #6c757d;
  font-weight: 500;
}

@media (max-width: 768px) {
  .items-header {
    flex-direction: column;
    gap: 20px;
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