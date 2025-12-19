<template>
  <div class="wishlist-view">
    <!-- 简洁的页面头部 - 无渐变 -->
    <div class="page-header">
      <div class="header-left">
        <h1 class="page-title">
          <el-icon><Star /></el-icon>
          我的收藏
        </h1>
        <p class="page-meta">{{ total }} 件商品</p>
      </div>

      <!-- 批量操作 -->
      <div class="header-actions" v-if="wishlistItems.length > 0">
        <el-button
          :type="isAllSelected ? 'default' : 'primary'"
          @click="toggleSelectAll"
        >
          {{ isAllSelected ? '取消全选' : '全选' }}
        </el-button>
        <el-button
          type="danger"
          plain
          @click="batchRemove"
          :disabled="selectedItems.length === 0"
        >
          删除 ({{ selectedItems.length }})
        </el-button>
      </div>
    </div>

    <!-- 筛选栏 - 扁平设计 -->
    <div class="filter-bar" v-if="wishlistItems.length > 0">
      <div class="filter-item">
        <span class="filter-label">分类</span>
        <el-select
          v-model="selectedCategory"
          placeholder="全部"
          @change="loadWishlist"
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
        <span class="filter-label">排序</span>
        <el-select
          v-model="sortBy"
          @change="loadWishlist"
          size="default"
          style="width: 120px"
        >
          <el-option value="add_time" label="收藏时间" />
          <el-option value="price" label="价格" />
        </el-select>
        <el-select
          v-model="sortOrder"
          @change="loadWishlist"
          size="default"
          style="width: 90px"
        >
          <el-option value="DESC" label="降序" />
          <el-option value="ASC" label="升序" />
        </el-select>
      </div>
    </div>

    <!-- 加载状态 -->
    <div v-if="loading" class="loading-container" v-loading="loading" element-loading-text="加载中...">
      <div style="height: 400px"></div>
    </div>

    <!-- 空状态 -->
    <el-empty
      v-else-if="wishlistItems.length === 0"
      description="还没有收藏商品"
      :image-size="100"
    >
      <el-button type="primary" @click="router.push('/items')">
        去逛逛
      </el-button>
    </el-empty>

    <!-- 商品网格 - 简洁卡片 -->
    <div v-else class="items-grid">
      <div
        v-for="item in wishlistItems"
        :key="item.wishlist_id"
        class="item-card"
      >
        <!-- 卡片头部 - 选择框和删除 -->
        <div class="card-tools">
          <el-checkbox
            :model-value="selectedItems.includes(item.wishlist_id)"
            @change="toggleSelection(item.wishlist_id)"
          />
          <el-button
            text
            type="danger"
            size="small"
            @click="removeFromWishlist(item.wishlist_id)"
          >
            删除
          </el-button>
        </div>

        <!-- 商品图片 -->
        <div class="item-image" @click="goToItem(item.item_id)">
          <el-image
            :src="item.images && item.images[0] ? item.images[0] : '/placeholder.png'"
            :alt="item.title"
            fit="cover"
            lazy
          >
            <template #error>
              <div class="image-slot">
                <el-icon><Picture /></el-icon>
              </div>
            </template>
          </el-image>

          <!-- 状态标签 -->
          <el-tag
            v-if="item.status && item.status !== 'available'"
            class="status-badge"
            :type="item.status === 'sold' ? 'danger' : 'info'"
            size="small"
          >
            {{ getStatusText(item.status) }}
          </el-tag>
        </div>

        <!-- 商品信息 -->
        <div class="item-content">
          <h3 @click="goToItem(item.item_id)" class="item-title">
            {{ item.title }}
          </h3>

          <div class="item-price-row">
            <span class="price">¥{{ item.price }}</span>
            <el-tag
              size="small"
              :type="getConditionType(item.condition_level)"
            >
              {{ getConditionText(item.condition_level) }}
            </el-tag>
          </div>

          <div class="item-meta-row">
            <span class="meta-text">{{ item.seller_name }}</span>
            <span class="meta-divider">·</span>
            <span class="meta-text">{{ item.category_name }}</span>
          </div>

          <div class="item-footer">
            <span class="time-text">{{ formatDate(item.add_time) }}</span>
            <el-button
              v-if="item.status === 'available'"
              type="primary"
              size="small"
              text
              @click="contactSeller(item)"
            >
              联系
            </el-button>
          </div>

          <div v-if="item.notes" class="item-notes">
            <el-icon size="12"><Document /></el-icon>
            <span>{{ item.notes }}</span>
            <el-button
              text
              size="small"
              @click="editNotes(item)"
              style="margin-left: auto"
            >
              编辑
            </el-button>
          </div>
          <el-button
            v-else
            text
            size="small"
            @click="editNotes(item)"
            style="width: 100%"
          >
            添加备注
          </el-button>
        </div>
      </div>
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

    <!-- 编辑备注对话框 -->
    <el-dialog
      v-model="showNotesModal"
      title="编辑备注"
      width="480px"
    >
      <el-input
        v-model="editingNotes"
        type="textarea"
        :rows="4"
        placeholder="添加备注..."
        maxlength="200"
        show-word-limit
      />

      <template #footer>
        <el-button @click="closeNotesModal">取消</el-button>
        <el-button type="primary" @click="saveNotes">
          保存
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { wishlistAPI, itemAPI } from '@/api'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Star, Delete, Picture, Document } from '@element-plus/icons-vue'
import type { Wishlist, Category } from '@/types'

const router = useRouter()
const userStore = useUserStore()

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

const total = computed(() => pagination.value.total)

const isAllSelected = computed(() => {
  return wishlistItems.value.length > 0 && selectedItems.value.length === wishlistItems.value.length
})

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

const getConditionText = (condition?: string): string => {
  if (!condition) return '-'
  return conditionMap[condition] || condition
}

const getConditionType = (condition?: string): string => {
  if (!condition) return 'info'
  const typeMap: Record<string, string> = {
    'brand_new': 'success',
    'like_new': 'success',
    'very_good': '',
    'good': 'warning',
    'acceptable': 'info'
  }
  return typeMap[condition] || 'info'
}

const getStatusText = (status: string): string => {
  return statusMap[status] || status
}

const formatDate = (dateString?: string): string => {
  if (!dateString) return '-'

  // 处理服务器返回的时间格式 "YYYY-MM-DD HH:MM:SS"
  const normalized = dateString.replace(' ', 'T')
  const date = new Date(normalized)

  if (isNaN(date.getTime())) return '-'

  const now = new Date()
  const diff = now.getTime() - date.getTime()
  const days = Math.floor(diff / (1000 * 60 * 60 * 24))

  // 处理负数天数（时区问题）
  if (days < 0) return date.toLocaleDateString('zh-CN')
  if (days === 0) return '今天'
  if (days === 1) return '昨天'
  if (days < 7) return `${days}天前`
  if (days < 30) return `${Math.floor(days / 7)}周前`
  if (days < 365) return `${Math.floor(days / 30)}个月前`
  return date.toLocaleDateString('zh-CN')
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
    ElMessage.error('加载收藏失败')
  } finally {
    loading.value = false
  }
}

const changePage = (newPage: number): void => {
  page.value = newPage
  loadWishlist()
}

const toggleSelection = (wishlistId: number) => {
  const index = selectedItems.value.indexOf(wishlistId)
  if (index > -1) {
    selectedItems.value.splice(index, 1)
  } else {
    selectedItems.value.push(wishlistId)
  }
}

const toggleSelectAll = () => {
  if (isAllSelected.value) {
    selectedItems.value = []
  } else {
    selectedItems.value = wishlistItems.value.map(item => item.wishlist_id)
  }
}

const removeFromWishlist = async (wishlistId: number) => {
  if (!userStore.currentUser) {
    router.push('/login')
    return
  }

  try {
    await ElMessageBox.confirm('确定要取消收藏吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })

    const item = wishlistItems.value.find(item => item.wishlist_id === wishlistId)
    if (!item) return

    await wishlistAPI.removeFromWishlist({
      user_id: userStore.currentUser.user_id,
      item_id: item.item_id
    })

    ElMessage.success('已取消收藏')
    loadWishlist()
  } catch (error: any) {
    if (error !== 'cancel') {
      console.error('Failed to remove from wishlist:', error)
      ElMessage.error('操作失败')
    }
  }
}

const batchRemove = async () => {
  if (selectedItems.value.length === 0) return

  if (!userStore.currentUser) {
    router.push('/login')
    return
  }

  try {
    await ElMessageBox.confirm(
      `确定要删除 ${selectedItems.value.length} 件商品吗？`,
      '批量删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

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

    ElMessage.success('删除成功')
    loadWishlist()
  } catch (error: any) {
    if (error !== 'cancel') {
      console.error('Failed to batch remove from wishlist:', error)
      ElMessage.error('操作失败')
    }
  }
}

const goToItem = (itemId: number) => {
  router.push(`/items/${itemId}`)
}

const contactSeller = async (item: Wishlist): Promise<void> => {
  if (!userStore.isLoggedIn) {
    router.push('/login')
    return
  }

  try {
    const response = await itemAPI.getItem(item.item_id)
    const detail = response.item
    if (detail?.user_id) {
      router.push(`/messages?user_id=${detail.user_id}&item_id=${detail.item_id}`)
    } else {
      router.push(`/items/${item.item_id}`)
    }
  } catch (error) {
    console.error('Failed to load item for messaging:', error)
    router.push(`/items/${item.item_id}`)
  }
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
    await wishlistAPI.updateWishlistNotes(editingItem.value.wishlist_id, {
      user_id: userStore.currentUser.user_id,
      notes: editingNotes.value
    })

    const index = wishlistItems.value.findIndex(item => item.wishlist_id === editingItem.value?.wishlist_id)
    if (index !== -1 && editingItem.value && wishlistItems.value[index]) {
      wishlistItems.value[index].notes = editingNotes.value
    }

    ElMessage.success('保存成功')
    closeNotesModal()
  } catch (error) {
    console.error('Failed to update notes:', error)
    ElMessage.error('保存失败')
  }
}

onMounted(() => {
  if (!userStore.isLoggedIn) {
    router.push('/login')
    return
  }

  loadCategories()
  loadWishlist()
})
</script>

<style scoped>
/* 现代扁平化风格 - Twitter/YouTube/Google 风格 */

.wishlist-view {
  max-width: var(--container-max-width);
  margin: 0 auto;
  padding: var(--spacing-6);
  background: var(--color-bg-page);
}

/* 页面头部 - 扁平简洁 */
.page-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  margin-bottom: var(--spacing-8);
  gap: var(--spacing-4);
  flex-wrap: wrap;
}

.header-left {
  flex: 1;
  min-width: 200px;
}

.page-title {
  display: flex;
  align-items: center;
  gap: var(--spacing-3);
  font-size: var(--font-size-4xl);
  font-weight: var(--font-weight-bold);
  color: var(--color-text-primary);
  margin: 0 0 var(--spacing-2) 0;
}

.page-title .el-icon {
  color: var(--color-primary);
}

.page-meta {
  font-size: var(--font-size-base);
  color: var(--color-text-secondary);
  margin: 0;
}

.header-actions {
  display: flex;
  gap: var(--spacing-2);
  align-items: center;
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

/* 商品卡片 - 扁平带边框 */
.item-card {
  background: var(--color-bg-card);
  border: 1px solid var(--color-border-base);
  border-radius: var(--radius-lg);
  overflow: hidden;
  transition: all var(--transition-base);
}

.item-card:hover {
  border-color: var(--color-border-light);
  box-shadow: var(--shadow-md);
  transform: translateY(-2px);
}

/* 卡片工具栏 */
.card-tools {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--spacing-3);
  border-bottom: 1px solid var(--color-border-light);
}

/* 商品图片 */
.item-image {
  height: 220px;
  cursor: pointer;
  overflow: hidden;
  position: relative;
  background: var(--color-neutral-50);
}

.item-image :deep(.el-image) {
  width: 100%;
  height: 100%;
  transition: transform var(--transition-slow);
}

.item-image:hover :deep(.el-image) {
  transform: scale(1.03);
}

.image-slot {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
  font-size: var(--font-size-6xl);
  color: var(--color-text-placeholder);
}

.status-badge {
  position: absolute;
  top: var(--spacing-2);
  right: var(--spacing-2);
}

/* 商品内容 */
.item-content {
  padding: var(--spacing-4);
}

.item-title {
  margin: 0 0 var(--spacing-3) 0;
  font-size: var(--font-size-base);
  font-weight: var(--font-weight-medium);
  color: var(--color-text-primary);
  cursor: pointer;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  line-height: var(--line-height-snug);
  transition: color var(--transition-fast);
}

.item-title:hover {
  color: var(--color-primary);
}

.item-price-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--spacing-3);
}

.price {
  font-size: var(--font-size-2xl);
  font-weight: var(--font-weight-bold);
  color: var(--color-price);
}

.item-meta-row {
  display: flex;
  align-items: center;
  gap: var(--spacing-2);
  margin-bottom: var(--spacing-3);
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
}

.meta-text {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.meta-divider {
  color: var(--color-text-placeholder);
}

.item-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: var(--spacing-3);
  border-top: 1px solid var(--color-border-light);
}

.time-text {
  font-size: var(--font-size-xs);
  color: var(--color-text-secondary);
}

.item-notes {
  display: flex;
  align-items: center;
  gap: var(--spacing-2);
  margin-top: var(--spacing-3);
  padding: var(--spacing-2);
  background: var(--color-neutral-50);
  border-radius: var(--radius-base);
  font-size: var(--font-size-xs);
  color: var(--color-text-secondary);
}

.item-notes span {
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

/* 分页 */
.pagination-wrapper {
  display: flex;
  justify-content: center;
  padding: var(--spacing-6) 0;
}

/* 响应式 */
@media (max-width: 768px) {
  .wishlist-view {
    padding: var(--spacing-4);
  }

  .page-header {
    flex-direction: column;
    align-items: stretch;
  }

  .header-actions {
    width: 100%;
  }

  .filter-bar {
    flex-direction: column;
    align-items: stretch;
  }

  .filter-item {
    justify-content: space-between;
  }

  .items-grid {
    grid-template-columns: 1fr;
    gap: var(--spacing-3);
  }
}
</style>
