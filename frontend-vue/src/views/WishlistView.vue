<template>
  <div class="wishlist-view">
    <h1>我的收藏</h1>
    
    <div class="wishlist-filters">
      <div class="filter-group">
        <label>分类：</label>
        <select v-model="selectedCategory" @change="loadWishlist">
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
        <label>排序：</label>
        <select v-model="sortBy" @change="loadWishlist">
          <option value="add_time">收藏时间</option>
          <option value="price">价格</option>
        </select>
        <select v-model="sortOrder" @change="loadWishlist">
          <option value="DESC">降序</option>
          <option value="ASC">升序</option>
        </select>
      </div>

      <div class="filter-actions">
        <button @click="toggleSelectAll" class="select-all-btn">
          {{ isAllSelected ? '取消全选' : '全选' }}
        </button>
        <button 
          @click="batchRemove"
          :disabled="selectedItems.length === 0"
          class="batch-remove-btn"
        >
          批量删除 ({{ selectedItems.length }})
        </button>
      </div>
    </div>

    <div v-if="loading" class="loading">
      加载中...
    </div>

    <div v-else-if="wishlistItems.length === 0" class="no-items">
      暂无收藏商品
    </div>

    <div v-else class="wishlist-grid">
      <div 
        v-for="item in wishlistItems" 
        :key="item.wishlist_id"
        class="wishlist-card"
      >
        <div class="card-header">
          <input
            type="checkbox"
            :value="item.wishlist_id"
            v-model="selectedItems"
            class="item-checkbox"
          />
          <button 
            @click="removeFromWishlist(item.wishlist_id)"
            class="remove-btn"
            title="取消收藏"
          >
            ❤️
          </button>
        </div>

        <div class="item-image" @click="item.item && goToItem(item.item.item_id)">
          <img
            :src="item.item?.images && item.item.images[0] ? item.item.images[0] : '/placeholder.jpg'"
            :alt="item.item?.title"
          />
          <div v-if="item.item && item.item.status !== 'available'" class="status-overlay">
            {{ getStatusText(item.item.status) }}
          </div>
        </div>

        <div class="item-info">
          <h3 @click="item.item && goToItem(item.item.item_id)">{{ item.item?.title }}</h3>
          <div class="item-details">
            <span class="item-price">¥{{ item.item?.price }}</span>
            <span class="item-condition">{{ item.item && getConditionText(item.item.condition_level) }}</span>
          </div>
          <div class="item-meta">
            <span class="item-seller">{{ item.item?.username }}</span>
            <span class="item-category">{{ item.item?.category_name }}</span>
          </div>
          <div class="wishlist-info">
            <span class="add-time">收藏于 {{ formatDate(item.wishlist_date) }}</span>
            <div v-if="item.notes" class="notes">
              备注：{{ item.notes }}
            </div>
          </div>
        </div>

        <div class="item-actions">
          <button
            v-if="item.item && item.item.status === 'available'"
            @click="contactSeller(item)"
            class="contact-btn"
          >
            联系卖家
          </button>
          <button 
            @click="editNotes(item)"
            class="edit-notes-btn"
          >
            编辑备注
          </button>
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

    <!-- 编辑备注弹窗 -->
    <div v-if="showNotesModal" class="modal-overlay" @click="closeNotesModal">
      <div class="modal-content" @click.stop>
        <h3>编辑收藏备注</h3>
        <textarea
          v-model="editingNotes"
          placeholder="添加备注..."
          maxlength="200"
          rows="4"
        ></textarea>
        <div class="char-count">{{ editingNotes.length }}/200</div>
        <div class="modal-actions">
          <button @click="closeNotesModal" class="cancel-btn">取消</button>
          <button @click="saveNotes" class="save-btn">保存</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { wishlistAPI, itemAPI } from '@/api'
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

const getConditionText = (condition: string): string => {
  return conditionMap[condition] || condition
}

const getStatusText = (status: string): string => {
  return statusMap[status] || status
}

const formatDate = (dateString: string): string => {
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
    wishlistItems.value = response.wishlist || []

    selectedItems.value = []
  } catch (error) {
    console.error('Failed to load wishlist:', error)
  } finally {
    loading.value = false
  }
}

const changePage = (newPage: number): void => {
  if (newPage >= 1 && newPage <= pagination.value.pages) {
    page.value = newPage
    loadWishlist()
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
  if (!confirm('确定要取消收藏这个商品吗？')) {
    return
  }

  try {
    // 找到对应的商品
    const item = wishlistItems.value.find(item => item.wishlist_id === wishlistId)
    if (!item) return

    await wishlistAPI.removeFromWishlist({
      user_id: userStore.currentUser.user_id,
      item_id: item.item_id
    })

    // 重新加载收藏列表
    loadWishlist()
  } catch (error) {
    console.error('Failed to remove from wishlist:', error)
    alert('取消收藏失败，请重试')
  }
}

const batchRemove = async () => {
  if (selectedItems.value.length === 0) return

  if (!confirm(`确定要取消收藏这 ${selectedItems.value.length} 个商品吗？`)) {
    return
  }

  try {
    // 获取对应的商品ID
    const itemIds = selectedItems.value.map(wishlistId => {
      const item = wishlistItems.value.find(item => item.wishlist_id === wishlistId)
      return item?.item_id
    }).filter(Boolean)

    await wishlistAPI.batchRemoveFromWishlist({
      user_id: userStore.currentUser.user_id,
      item_ids: itemIds
    })

    // 重新加载收藏列表
    loadWishlist()
  } catch (error) {
    console.error('Failed to batch remove from wishlist:', error)
    alert('批量取消收藏失败，请重试')
  }
}

const goToItem = (itemId: number) => {
  router.push(`/items/${itemId}`)
}

const contactSeller = (item: Wishlist): void => {
  if (!item.item) return
  router.push(`/messages?user_id=${item.item.user_id}&item_id=${item.item_id}`)
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
  if (!editingItem.value) return

  try {
    await wishlistAPI.updateWishlistNotes(editingItem.value.wishlist_id, {
      notes: editingNotes.value
    })

    const index = wishlistItems.value.findIndex(item => item.wishlist_id === editingItem.value?.wishlist_id)
    if (index !== -1 && editingItem.value && wishlistItems.value[index]) {
      wishlistItems.value[index].notes = editingNotes.value
    }

    closeNotesModal()
  } catch (error) {
    console.error('Failed to update notes:', error)
    alert('保存备注失败，请重试')
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
.wishlist-view {
  max-width: 1800px;
  margin: 0 auto;
  padding: 30px 40px;
}

.wishlist-view h1 {
  color: #2c3e50;
  margin-bottom: 30px;
  text-align: center;
}

.wishlist-filters {
  display: flex;
  gap: 20px;
  align-items: center;
  margin-bottom: 30px;
  padding: 20px;
  background: #f8f9fa;
  border-radius: 8px;
  flex-wrap: wrap;
}

.filter-group {
  display: flex;
  align-items: center;
  gap: 10px;
}

.filter-group label {
  font-weight: 500;
  color: #2c3e50;
}

.filter-group select {
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
}

.filter-actions {
  display: flex;
  gap: 10px;
  margin-left: auto;
}

.select-all-btn,
.batch-remove-btn {
  padding: 8px 16px;
  border: none;
  border-radius: 4px;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.3s;
}

.select-all-btn {
  background: #007bff;
  color: white;
}

.select-all-btn:hover {
  background: #0056b3;
}

.batch-remove-btn {
  background: #dc3545;
  color: white;
}

.batch-remove-btn:hover:not(:disabled) {
  background: #c82333;
}

.batch-remove-btn:disabled {
  background: #6c757d;
  cursor: not-allowed;
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

.wishlist-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 30px;
  margin-bottom: 40px;
}

.wishlist-card {
  background: white;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  transition: all 0.3s;
}

.wishlist-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 16px rgba(0,0,0,0.15);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 15px;
  background: #f8f9fa;
}

.item-checkbox {
  width: 18px;
  height: 18px;
}

.remove-btn {
  background: none;
  border: none;
  font-size: 1.2rem;
  cursor: pointer;
  transition: transform 0.3s;
}

.remove-btn:hover {
  transform: scale(1.1);
}

.item-image {
  height: 200px;
  overflow: hidden;
  cursor: pointer;
  position: relative;
}

.item-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.3s;
}

.item-image:hover img {
  transform: scale(1.05);
}

.status-overlay {
  position: absolute;
  top: 10px;
  right: 10px;
  background: rgba(0,0,0,0.7);
  color: white;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 0.8rem;
}

.item-info {
  padding: 15px;
}

.item-info h3 {
  color: #2c3e50;
  margin: 0 0 10px 0;
  font-size: 1.1rem;
  cursor: pointer;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.item-info h3:hover {
  color: #007bff;
}

.item-details {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.item-price {
  color: #e74c3c;
  font-weight: 600;
  font-size: 1.2rem;
}

.item-condition {
  background-color: #f8f9fa;
  color: #6c757d;
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 0.8rem;
}

.item-meta {
  display: flex;
  justify-content: space-between;
  margin-bottom: 10px;
  font-size: 0.9rem;
  color: #6c757d;
}

.wishlist-info {
  font-size: 0.8rem;
  color: #6c757d;
}

.add-time {
  display: block;
  margin-bottom: 5px;
}

.notes {
  background: #f8f9fa;
  padding: 8px;
  border-radius: 4px;
  font-style: italic;
}

.item-actions {
  display: flex;
  gap: 10px;
  padding: 15px;
  border-top: 1px solid #f8f9fa;
}

.contact-btn,
.edit-notes-btn {
  flex: 1;
  padding: 8px 12px;
  border: none;
  border-radius: 4px;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.3s;
}

.contact-btn {
  background: #28a745;
  color: white;
}

.contact-btn:hover {
  background: #218838;
}

.edit-notes-btn {
  background: #6c757d;
  color: white;
}

.edit-notes-btn:hover {
  background: #5a6268;
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

/* 弹窗样式 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0,0,0,0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  border-radius: 8px;
  padding: 30px;
  width: 90%;
  max-width: 500px;
  position: relative;
}

.modal-content h3 {
  color: #2c3e50;
  margin-bottom: 20px;
}

.modal-content textarea {
  width: 100%;
  padding: 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  resize: vertical;
  font-family: inherit;
  font-size: 14px;
}

.char-count {
  text-align: right;
  font-size: 12px;
  color: #6c757d;
  margin: 5px 0 20px 0;
}

.modal-actions {
  display: flex;
  gap: 15px;
  justify-content: flex-end;
}

.cancel-btn,
.save-btn {
  padding: 10px 20px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
}

.cancel-btn {
  background: #6c757d;
  color: white;
}

.save-btn {
  background: #007bff;
  color: white;
}

.cancel-btn:hover {
  background: #5a6268;
}

.save-btn:hover {
  background: #0056b3;
}

@media (max-width: 768px) {
  .wishlist-filters {
    flex-direction: column;
    align-items: stretch;
  }

  .filter-group {
    justify-content: space-between;
  }

  .filter-actions {
    margin-left: 0;
    justify-content: center;
  }

  .wishlist-grid {
    grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  }
}
</style>