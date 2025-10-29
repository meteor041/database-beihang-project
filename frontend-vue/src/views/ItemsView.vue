<template>
  <v-container class="items-view">
    <!-- 搜索栏 -->
    <div class="items-header mb-8">
      <h1 class="text-h3 font-weight-bold">商品列表</h1>
      <div class="search-bar">
        <v-text-field
          v-model="searchKeyword"
          placeholder="搜索商品..."
          prepend-inner-icon="mdi-magnify"
          variant="outlined"
          density="comfortable"
          hide-details
          clearable
          @keyup.enter="handleSearch"
          class="search-input"
        ></v-text-field>
        <v-btn
          color="primary"
          size="large"
          @click="handleSearch"
        >
          搜索
        </v-btn>
      </div>
    </div>

    <!-- 筛选区域 -->
    <v-card class="filters-card mb-8" elevation="2">
      <v-card-text>
        <v-row align="center">
          <v-col cols="12" sm="6" md="3">
            <v-select
              v-model="selectedCategory"
              :items="categoryOptions"
              item-title="text"
              item-value="value"
              label="分类"
              prepend-inner-icon="mdi-shape"
              variant="outlined"
              density="comfortable"
              hide-details
              @update:model-value="loadItems"
            ></v-select>
          </v-col>

          <v-col cols="12" sm="6" md="4">
            <div class="d-flex align-center ga-2">
              <v-text-field
                v-model="minPrice"
                type="number"
                label="最低价"
                prepend-inner-icon="mdi-currency-cny"
                variant="outlined"
                density="comfortable"
                hide-details
              ></v-text-field>
              <span class="text-grey">-</span>
              <v-text-field
                v-model="maxPrice"
                type="number"
                label="最高价"
                prepend-inner-icon="mdi-currency-cny"
                variant="outlined"
                density="comfortable"
                hide-details
              ></v-text-field>
            </div>
          </v-col>

          <v-col cols="6" sm="3" md="2">
            <v-select
              v-model="sortBy"
              :items="sortByOptions"
              label="排序方式"
              variant="outlined"
              density="comfortable"
              hide-details
              @update:model-value="loadItems"
            ></v-select>
          </v-col>

          <v-col cols="6" sm="3" md="2">
            <v-select
              v-model="sortOrder"
              :items="sortOrderOptions"
              label="排序"
              variant="outlined"
              density="comfortable"
              hide-details
              @update:model-value="loadItems"
            ></v-select>
          </v-col>

          <v-col cols="12" md="1">
            <v-btn
              color="success"
              block
              @click="applyFilters"
            >
              应用
            </v-btn>
          </v-col>
        </v-row>
      </v-card-text>
    </v-card>

    <!-- 加载状态 -->
    <v-progress-linear v-if="loading" indeterminate color="primary" class="mb-4"></v-progress-linear>

    <!-- 空状态 -->
    <EmptyState
      v-else-if="items.length === 0"
      description="暂无商品"
      action-text="浏览其他分类"
      @action="selectedCategory = ''; loadItems()"
    />

    <!-- 商品列表 -->
    <v-row v-else>
      <v-col
        v-for="item in items"
        :key="item.item_id"
        cols="12"
        sm="6"
        md="4"
        lg="3"
      >
        <ItemCard :item="item" @click="goToItem(item.item_id)" />
      </v-col>
    </v-row>

    <!-- 分页 -->
    <div v-if="pagination.pages > 1" class="d-flex justify-center mt-8">
      <v-pagination
        v-model="page"
        :length="pagination.pages"
        :total-visible="7"
        @update:model-value="changePage"
        rounded="circle"
      ></v-pagination>
    </div>
  </v-container>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useNotification } from '@/composables/useNotification'
import { itemAPI } from '@/api'
import ItemCard from '@/components/ItemCard.vue'
import EmptyState from '@/components/EmptyState.vue'
import type { Item, Category } from '@/types'

interface Pagination {
  page: number
  limit: number
  total: number
  pages: number
}

const router = useRouter()
const route = useRoute()
const notification = useNotification()

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

// 分类选项
const categoryOptions = computed(() => {
  return [
    { text: '全部分类', value: '' },
    ...categories.value.map(cat => ({
      text: cat.category_name,
      value: cat.category_id.toString()
    }))
  ]
})

// 排序方式选项
const sortByOptions = [
  { title: '发布时间', value: 'publish_date' },
  { title: '价格', value: 'price' },
  { title: '浏览量', value: 'view_count' }
]

// 排序顺序选项
const sortOrderOptions = [
  { title: '降序', value: 'DESC' },
  { title: '升序', value: 'ASC' }
]

const loadCategories = async () => {
  try {
    const response = await itemAPI.getCategories()
    categories.value = response.categories || []
  } catch (error) {
    console.error('Failed to load categories:', error)
    notification.error('加载分类失败')
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
    notification.error('加载商品失败')
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
    notification.error('搜索失败')
  } finally {
    loading.value = false
  }
}

const applyFilters = (): void => {
  page.value = 1
  handleSearch()
}

const changePage = (newPage: number): void => {
  page.value = newPage
  loadItems()
  // 滚动到顶部
  window.scrollTo({ top: 0, behavior: 'smooth' })
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
  max-width: 1400px;
}

.items-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 20px;
}

.search-bar {
  display: flex;
  gap: 12px;
  min-width: 400px;
}

.search-input {
  flex: 1;
}

@media (max-width: 768px) {
  .items-header {
    flex-direction: column;
    align-items: stretch;
  }

  .search-bar {
    min-width: auto;
    width: 100%;
  }
}
</style>
