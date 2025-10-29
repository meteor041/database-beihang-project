<template>
  <v-container class="wishlist-view">
    <h1 class="text-h3 font-weight-bold mb-6">我的收藏</h1>

    <!-- 筛选和批量操作 -->
    <v-card elevation="2" class="mb-6">
      <v-card-text>
        <v-row align="center">
          <v-col cols="12" sm="4" md="3">
            <v-select
              v-model="selectedCategory"
              :items="categoryOptions"
              item-title="text"
              item-value="value"
              label="分类"
              variant="outlined"
              density="comfortable"
              hide-details
              @update:model-value="loadWishlist"
            ></v-select>
          </v-col>

          <v-col cols="6" sm="4" md="2">
            <v-select
              v-model="sortBy"
              :items="sortByOptions"
              label="排序"
              variant="outlined"
              density="comfortable"
              hide-details
              @update:model-value="loadWishlist"
            ></v-select>
          </v-col>

          <v-col cols="6" sm="4" md="2">
            <v-select
              v-model="sortOrder"
              :items="sortOrderOptions"
              label="顺序"
              variant="outlined"
              density="comfortable"
              hide-details
              @update:model-value="loadWishlist"
            ></v-select>
          </v-col>

          <v-col cols="12" md="5" class="d-flex ga-2 justify-end">
            <v-btn
              variant="outlined"
              @click="toggleSelectAll"
            >
              {{ isAllSelected ? '取消全选' : '全选' }}
            </v-btn>
            <v-btn
              color="error"
              :disabled="selectedItems.length === 0"
              @click="batchRemove"
            >
              批量删除 ({{ selectedItems.length }})
            </v-btn>
          </v-col>
        </v-row>
      </v-card-text>
    </v-card>

    <!-- 加载状态 -->
    <v-progress-linear v-if="loading" indeterminate color="primary" class="mb-4"></v-progress-linear>

    <!-- 空状态 -->
    <EmptyState
      v-else-if="wishlistItems.length === 0"
      icon="mdi-heart-outline"
      description="暂无收藏商品"
      action-text="去逛逛"
      @action="router.push('/items')"
    />

    <!-- 收藏列表 -->
    <v-row v-else>
      <v-col
        v-for="item in wishlistItems"
        :key="item.wishlist_id"
        cols="12"
        sm="6"
        md="4"
        lg="3"
      >
        <v-card elevation="2" class="wishlist-card h-100">
          <!-- 卡片头部 -->
          <div class="card-header pa-2 d-flex justify-space-between">
            <v-checkbox
              :model-value="selectedItems.includes(item.wishlist_id)"
              @update:model-value="toggleItem(item.wishlist_id)"
              hide-details
              density="compact"
            ></v-checkbox>
            <v-btn
              icon="mdi-heart"
              size="small"
              color="error"
              variant="text"
              @click="removeFromWishlist(item.wishlist_id)"
            ></v-btn>
          </div>

          <!-- 商品图片 -->
          <v-img
            :src="item.images && item.images[0] ? item.images[0] : '/placeholder.png'"
            :alt="item.title"
            height="200"
            cover
            class="cursor-pointer"
            @click="goToItem(item.item_id)"
          >
            <v-chip
              v-if="item.status && item.status !== 'available'"
              class="ma-2"
              :color="item.status === 'sold' ? 'error' : 'grey'"
              size="small"
            >
              {{ getStatusText(item.status) }}
            </v-chip>
          </v-img>

          <v-card-text>
            <h3
              class="text-h6 mb-2 cursor-pointer text-truncate"
              @click="goToItem(item.item_id)"
            >
              {{ item.title }}
            </h3>

            <div class="d-flex justify-space-between align-center mb-2">
              <span class="text-h6 text-error font-weight-bold">¥{{ item.price }}</span>
              <v-chip size="small" color="primary" variant="tonal">
                {{ item.condition_level && getConditionText(item.condition_level) }}
              </v-chip>
            </div>

            <div class="d-flex justify-space-between text-body-2 text-grey mb-2">
              <span>{{ item.seller_name }}</span>
              <span>{{ item.category_name }}</span>
            </div>

            <div class="text-caption text-grey mb-2">
              收藏于 {{ formatDate(item.add_time) }}
            </div>

            <v-alert
              v-if="item.notes"
              density="compact"
              type="info"
              variant="tonal"
              class="text-caption"
            >
              备注：{{ item.notes }}
            </v-alert>
          </v-card-text>

          <v-card-actions>
            <v-btn
              v-if="item.status === 'available'"
              variant="outlined"
              size="small"
              block
              @click="contactSeller(item)"
            >
              联系卖家
            </v-btn>
            <v-btn
              variant="outlined"
              size="small"
              block
              @click="editNotes(item)"
            >
              编辑备注
            </v-btn>
          </v-card-actions>
        </v-card>
      </v-col>
    </v-row>

    <!-- 分页 -->
    <div v-if="pagination.pages > 1" class="d-flex justify-center mt-6">
      <v-pagination
        v-model="page"
        :length="pagination.pages"
        @update:model-value="changePage"
        rounded="circle"
      ></v-pagination>
    </div>

    <!-- 编辑备注对话框 -->
    <v-dialog v-model="showNotesModal" max-width="500">
      <v-card>
        <v-card-title>编辑收藏备注</v-card-title>
        <v-card-text>
          <v-textarea
            v-model="editingNotes"
            label="备注"
            placeholder="添加备注..."
            counter="200"
            maxlength="200"
            rows="4"
            variant="outlined"
          ></v-textarea>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn variant="text" @click="closeNotesModal">取消</v-btn>
          <v-btn color="primary" @click="saveNotes">保存</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-container>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { useNotification } from '@/composables/useNotification'
import { wishlistAPI, itemAPI } from '@/api'
import EmptyState from '@/components/EmptyState.vue'
import type { Wishlist, Category } from '@/types'

const router = useRouter()
const userStore = useUserStore()
const notification = useNotification()

const wishlistItems = ref<Wishlist[]>([])
const categories = ref<Category[]>([])
const loading = ref(false)
const selectedItems = ref<number[]>([])
const pagination = ref({
  page: 1,
  limit: 20,
  total: 0,
  pages: 0
})

const selectedCategory = ref('')
const sortBy = ref('add_time')
const sortOrder = ref('DESC')
const page = ref(1)

const showNotesModal = ref(false)
const editingItem = ref<Wishlist | null>(null)
const editingNotes = ref('')

const isAllSelected = computed(() => {
  return wishlistItems.value.length > 0 && selectedItems.value.length === wishlistItems.value.length
})

const categoryOptions = computed(() => {
  return [
    { text: '全部分类', value: '' },
    ...categories.value.map(cat => ({
      text: cat.category_name,
      value: cat.category_id.toString()
    }))
  ]
})

const sortByOptions = [
  { title: '收藏时间', value: 'add_time' },
  { title: '价格', value: 'price' }
]

const sortOrderOptions = [
  { title: '降序', value: 'DESC' },
  { title: '升序', value: 'ASC' }
]

const conditionMap: Record<string, string> = {
  'brand_new': '全新',
  'like_new': '几乎全新',
  'very_good': '非常好',
  'good': '良好',
  'acceptable': '可接受'
}

const statusMap: Record<string, string> = {
  'available': '在售',
  'sold': '已售出',
  'removed': '已下架'
}

const getConditionText = (condition: string): string => {
  return conditionMap[condition] || condition
}

const getStatusText = (status: string): string => {
  return statusMap[status] || status
}

const formatDate = (dateString?: string): string => {
  if (!dateString) return '-'
  return new Date(dateString).toLocaleDateString('zh-CN')
}

const loadCategories = async (): Promise<void> => {
  try {
    const response = await itemAPI.getCategories()
    categories.value = response.categories || []
  } catch (error) {
    console.error('Failed to load categories:', error)
  }
}

const loadWishlist = async (): Promise<void> => {
  if (!userStore.isLoggedIn || !userStore.currentUser) {
    router.push('/login')
    return
  }

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

    const response = await wishlistAPI.getWishlist(userStore.currentUser.user_id, params)
    wishlistItems.value = (response.wishlist || []).map((entry) => ({
      ...entry,
      images: Array.isArray(entry.images) ? entry.images : []
    }))

    if (response.pagination) {
      page.value = response.pagination.page
      pagination.value = {
        page: response.pagination.page,
        limit: response.pagination.limit,
        total: response.pagination.total,
        pages: response.pagination.pages
      }
    }

    selectedItems.value = []
  } catch (error) {
    console.error('Failed to load wishlist:', error)
    notification.error('加载收藏列表失败')
  } finally {
    loading.value = false
  }
}

const changePage = (newPage: number): void => {
  page.value = newPage
  loadWishlist()
}

const toggleItem = (wishlistId: number): void => {
  const index = selectedItems.value.indexOf(wishlistId)
  if (index > -1) {
    selectedItems.value.splice(index, 1)
  } else {
    selectedItems.value.push(wishlistId)
  }
}

const toggleSelectAll = (): void => {
  if (isAllSelected.value) {
    selectedItems.value = []
  } else {
    selectedItems.value = wishlistItems.value.map(item => item.wishlist_id)
  }
}

const removeFromWishlist = async (wishlistId: number): Promise<void> => {
  if (!userStore.currentUser) {
    router.push('/login')
    return
  }

  try {
    const item = wishlistItems.value.find(item => item.wishlist_id === wishlistId)
    if (!item) return

    await wishlistAPI.removeFromWishlist({
      user_id: userStore.currentUser.user_id,
      item_id: item.item_id
    })

    notification.success('已取消收藏')
    loadWishlist()
  } catch (error) {
    console.error('Failed to remove from wishlist:', error)
    notification.error('取消收藏失败')
  }
}

const batchRemove = async (): Promise<void> => {
  if (selectedItems.value.length === 0 || !userStore.currentUser) return

  try {
    const itemIds = selectedItems.value
      .map((wishlistId) => wishlistItems.value.find(item => item.wishlist_id === wishlistId)?.item_id)
      .filter((id): id is number => typeof id === 'number')

    if (itemIds.length === 0) {
      loadWishlist()
      return
    }

    await wishlistAPI.batchRemoveFromWishlist({
      user_id: userStore.currentUser.user_id,
      item_ids: itemIds
    })

    notification.success(`已取消 ${itemIds.length} 个商品的收藏`)
    loadWishlist()
  } catch (error) {
    console.error('Failed to batch remove:', error)
    notification.error('批量删除失败')
  }
}

const goToItem = (itemId: number): void => {
  router.push(`/items/${itemId}`)
}

const contactSeller = (item: Wishlist): void => {
  router.push(`/messages?user_id=${item.seller_id}&item_id=${item.item_id}`)
}

const editNotes = (item: Wishlist): void => {
  editingItem.value = item
  editingNotes.value = item.notes || ''
  showNotesModal.value = true
}

const closeNotesModal = (): void => {
  showNotesModal.value = false
  editingItem.value = null
  editingNotes.value = ''
}

const saveNotes = async (): Promise<void> => {
  if (!editingItem.value || !userStore.currentUser) return

  try {
    await wishlistAPI.updateWishlistNotes({
      user_id: userStore.currentUser.user_id,
      item_id: editingItem.value.item_id,
      notes: editingNotes.value
    })

    notification.success('备注已保存')
    closeNotesModal()
    loadWishlist()
  } catch (error) {
    console.error('Failed to update notes:', error)
    notification.error('保存备注失败')
  }
}

onMounted(() => {
  loadCategories()
  loadWishlist()
})
</script>

<style scoped>
.wishlist-view {
  max-width: 1400px;
}

.wishlist-card {
  transition: all 0.3s;
}

.wishlist-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.15) !important;
}

.card-header {
  position: relative;
}

.cursor-pointer {
  cursor: pointer;
}
</style>
