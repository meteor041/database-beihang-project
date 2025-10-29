<template>
  <div class="profile-view">
    <h1>个人中心</h1>
    
    <div class="profile-container">
      <div class="profile-sidebar">
        <div class="user-card">
          <img 
            :src="currentUser?.avatar || '/default-avatar.png'"
            :alt="currentUser?.username"
            class="user-avatar"
          />
          <div class="user-info">
            <h2>{{ currentUser?.username }}</h2>
            <p>{{ currentUser?.real_name }}</p>
            <div class="credit-score">
              信用分：{{ currentUser?.credit_score }}
            </div>
          </div>
        </div>

        <nav class="profile-nav">
          <button 
            v-for="tab in tabs"
            :key="tab.key"
            :class="['nav-btn', { active: activeTab === tab.key }]"
            @click="switchTab(tab.key)"
          >
            {{ tab.label }}
          </button>
        </nav>
      </div>

      <div class="profile-content">
        <!-- 基本信息 -->
        <div v-if="activeTab === 'info'" class="tab-content">
          <h2>基本信息</h2>
          <form @submit.prevent="updateUserInfo" class="info-form">
            <div class="form-group">
              <label>学号</label>
              <input 
                v-model="userForm.student_id" 
                type="text" 
                disabled
                class="disabled-input"
              />
            </div>

            <div class="form-group">
              <label>用户名</label>
              <input 
                v-model="userForm.username" 
                type="text" 
                required
              />
            </div>

            <div class="form-group">
              <label>真实姓名</label>
              <input 
                v-model="userForm.real_name" 
                type="text" 
                required
              />
            </div>

            <div class="form-group">
              <label>手机号</label>
              <input 
                v-model="userForm.phone" 
                type="tel" 
                required
              />
            </div>

            <div class="form-group">
              <label>邮箱</label>
              <input 
                v-model="userForm.email" 
                type="email" 
                required
              />
            </div>

            <div v-if="updateMessage" class="message">
              {{ updateMessage }}
            </div>

            <button type="submit" :disabled="updating" class="update-btn">
              {{ updating ? '更新中...' : '更新信息' }}
            </button>
          </form>
        </div>

        <!-- 我的商品 -->
        <div v-if="activeTab === 'items'" class="tab-content">
          <div class="section-header">
            <h2>我的商品</h2>
            <router-link to="/publish" class="publish-btn">发布新商品</router-link>
          </div>

          <div class="item-filters">
            <select v-model="itemStatus" @change="loadMyItems">
              <option value="available">在售</option>
              <option value="sold">已售出</option>
              <option value="removed">已下架</option>
            </select>
          </div>

          <div v-if="itemsLoading" class="loading">
            加载中...
          </div>

          <div v-else-if="myItems.length === 0" class="no-items">
            暂无商品
          </div>

          <div v-else class="items-grid">
            <div 
              v-for="item in myItems"
              :key="item.item_id"
              class="item-card"
            >
              <img 
                :src="item.images && item.images[0] ? item.images[0] : '/placeholder.png'"
                :alt="item.title"
                class="item-image"
              />
              <div class="item-info">
                <h3>{{ item.title }}</h3>
                <p class="item-price">¥{{ item.price }}</p>
                <p class="item-status">{{ getStatusText(item.status) }}</p>
                <p class="item-views">{{ item.view_count }} 次浏览</p>
              </div>
              <div class="item-actions">
                <button @click="viewItem(item.item_id)" class="view-btn">
                  查看
                </button>
                <button 
                  v-if="item.status === 'available'"
                  @click="editItem(item.item_id)" 
                  class="edit-btn"
                >
                  编辑
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- 地址管理 -->
        <div v-if="activeTab === 'addresses'" class="tab-content">
          <div class="section-header">
            <h2>收货地址</h2>
            <button @click="openCreateAddress" class="add-btn">
              添加地址
            </button>
          </div>

          <div v-if="addressesLoading" class="loading">
            加载中...
          </div>

          <div v-else-if="addresses.length === 0" class="no-items">
            暂无地址
          </div>

          <div v-else class="addresses-list">
            <div 
              v-for="address in addresses"
              :key="address.address_id"
              class="address-card"
            >
              <div class="address-info">
                <div class="address-header">
                  <span class="recipient">{{ address.recipient_name }}</span>
                  <span class="phone">{{ address.phone }}</span>
                  <span v-if="address.is_default" class="default-badge">默认</span>
                </div>
                <div class="address-detail">
                  {{ address.province }} {{ address.city }} {{ address.district }} {{ address.detailed_address }}
                </div>
              </div>
              <div class="address-actions">
                <button @click="openEditAddress(address)" class="edit-btn">
                  编辑
                </button>
                <button 
                  v-if="!address.is_default"
                  @click="setDefaultAddress(address.address_id)"
                  class="default-btn"
                >
                  设为默认
                </button>
                <button 
                  @click="deleteAddress(address.address_id)"
                  class="delete-btn"
                >
                  删除
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- 统计信息 -->
        <div v-if="activeTab === 'stats'" class="tab-content">
          <h2>统计信息</h2>
          
          <div class="stats-grid">
            <div class="stat-card">
              <div class="stat-number">{{ stats.buyer_stats?.total_orders || 0 }}</div>
              <div class="stat-label">购买订单</div>
            </div>
            <div class="stat-card">
              <div class="stat-number">{{ stats.seller_stats?.total_sales || 0 }}</div>
              <div class="stat-label">销售订单</div>
            </div>
            <div class="stat-card">
              <div class="stat-number">¥{{ stats.buyer_stats?.total_spent || 0 }}</div>
              <div class="stat-label">总消费</div>
            </div>
            <div class="stat-card">
              <div class="stat-number">¥{{ stats.seller_stats?.total_earned || 0 }}</div>
              <div class="stat-label">总收入</div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 地址编辑弹窗 -->
    <div v-if="showAddressModal" class="modal-overlay" @click="closeAddressModal">
      <div class="modal-content" @click.stop>
        <h3>{{ addressModalMode === 'edit' ? '编辑地址' : '添加地址' }}</h3>
        <AddressForm
          :address="addressInitialValue || undefined"
          :loading="addressModalLoading"
          :submit-text="addressModalMode === 'edit' ? '保存修改' : '添加地址'"
          @save="handleAddressSave"
          @cancel="closeAddressModal"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { itemAPI, addressAPI, orderAPI } from '@/api'
import type { Item, Address, AddressParams, OrderStatistics } from '@/types'
import AddressForm from '@/components/AddressForm.vue'
import { ElMessage } from 'element-plus'

const router = useRouter()
const userStore = useUserStore()

const activeTab = ref('info')
const updating = ref(false)
const updateMessage = ref('')

const userForm = ref({
  student_id: '',
  username: '',
  real_name: '',
  phone: '',
  email: ''
})

const myItems = ref<Item[]>([])
const itemsLoading = ref(false)
const itemStatus = ref('available')

const addresses = ref<Address[]>([])
const addressesLoading = ref(false)
const showAddressModal = ref(false)
const editingAddress = ref<Address | null>(null)
const addressModalMode = ref<'create' | 'edit'>('create')
const addressModalLoading = ref(false)

interface Stats {
  buyer_stats?: {
    total_orders?: number
    total_spent?: number
  }
  seller_stats?: {
    total_sales?: number
    total_earned?: number
  }
}

const stats = ref<any>({})

const currentUser = computed(() => userStore.currentUser)

const tabs = [
  { key: 'info', label: '基本信息' },
  { key: 'items', label: '我的商品' },
  { key: 'addresses', label: '地址管理' },
  { key: 'stats', label: '统计信息' }
]

const statusMap: Record<string, string> = {
  'available': '在售',
  'sold': '已售出',
  'removed': '已下架'
}

const getStatusText = (status?: string): string => {
  if (!status) return '未知状态'
  return statusMap[status] || status
}

const initUserForm = (): void => {
  if (currentUser.value) {
    userForm.value = {
      student_id: currentUser.value.student_id || '',
      username: currentUser.value.username || '',
      real_name: currentUser.value.real_name || '',
      phone: currentUser.value.phone || '',
      email: currentUser.value.email || ''
    }
  }
}

const switchTab = (tab: string): void => {
  activeTab.value = tab

  switch (tab) {
    case 'items':
      loadMyItems()
      break
    case 'addresses':
      loadAddresses()
      break
    case 'stats':
      loadStats()
      break
  }
}

const updateUserInfo = async (): Promise<void> => {
  updating.value = true
  updateMessage.value = ''

  try {
    const result = await userStore.updateUserInfo(userForm.value)

    if (result.success) {
      updateMessage.value = '信息更新成功'
    } else {
      updateMessage.value = result.message
    }
  } catch {
    updateMessage.value = '更新失败，请重试'
  } finally {
    updating.value = false
  }
}

const loadMyItems = async (): Promise<void> => {
  if (!currentUser.value) return

  itemsLoading.value = true
  try {
    const response = await itemAPI.getUserItems(currentUser.value.user_id, {
      status: itemStatus.value,
      page: 1,
      limit: 20
    })
    myItems.value = response.items || []
  } catch (error) {
    console.error('Failed to load my items:', error)
  } finally {
    itemsLoading.value = false
  }
}

const viewItem = (itemId: number): void => {
  router.push(`/items/${itemId}`)
}

const editItem = (itemId: number): void => {
  router.push(`/items/${itemId}/edit`)
}

const loadAddresses = async (): Promise<void> => {
  if (!currentUser.value) return

  addressesLoading.value = true
  try {
    const response = await addressAPI.getUserAddresses(currentUser.value.user_id)
    addresses.value = response.addresses || []
  } catch (error) {
    console.error('Failed to load addresses:', error)
  } finally {
    addressesLoading.value = false
  }
}

type AddressFormValue = Omit<AddressParams, 'user_id'>

const addressInitialValue = computed<AddressFormValue | null>(() => {
  if (!editingAddress.value) {
    return null
  }
  const address = editingAddress.value
  return {
    recipient_name: address.recipient_name,
    phone: address.phone,
    province: address.province,
    city: address.city,
    district: address.district,
    detailed_address: address.detailed_address,
    postal_code: address.postal_code ?? '',
    address_type: address.address_type,
    is_default: address.is_default
  }
})

const openCreateAddress = (): void => {
  editingAddress.value = null
  addressModalMode.value = 'create'
  showAddressModal.value = true
}

const openEditAddress = (address: Address): void => {
  editingAddress.value = address
  addressModalMode.value = 'edit'
  showAddressModal.value = true
}

const closeAddressModal = (): void => {
  showAddressModal.value = false
  addressModalLoading.value = false
  editingAddress.value = null
  addressModalMode.value = 'create'
}

const handleAddressSave = async (value: AddressFormValue): Promise<void> => {
  if (!currentUser.value) return

  const payload: AddressParams = {
    ...value,
    user_id: currentUser.value.user_id
  }

  try {
    addressModalLoading.value = true
    if (addressModalMode.value === 'edit' && editingAddress.value) {
      await addressAPI.updateAddress(editingAddress.value.address_id, payload)
      ElMessage.success('地址更新成功')
    } else {
      await addressAPI.addAddress(payload)
      ElMessage.success('地址添加成功')
    }
    closeAddressModal()
    loadAddresses()
  } catch (error: any) {
    console.error('Failed to save address:', error)
    const backendMessage = error?.response?.data?.error
    ElMessage.error(backendMessage || '保存地址失败，请重试')
  } finally {
    addressModalLoading.value = false
  }
}

const setDefaultAddress = async (addressId: number): Promise<void> => {
  if (!currentUser.value) return

  try {
    await addressAPI.setDefaultAddress(addressId, {
      user_id: currentUser.value.user_id
    })
    loadAddresses()
  } catch (error) {
    console.error('Failed to set default address:', error)
    alert('设置默认地址失败，请重试')
  }
}

const deleteAddress = async (addressId: number): Promise<void> => {
  if (!confirm('确定要删除这个地址吗?') || !currentUser.value) {
    return
  }

  try {
    await addressAPI.deleteAddress(addressId, {
      user_id: currentUser.value.user_id
    })
    loadAddresses()
  } catch (error) {
    console.error('Failed to delete address:', error)
    alert('删除地址失败，请重试')
  }
}

const loadStats = async (): Promise<void> => {
  if (!currentUser.value) return

  try {
    const response = await orderAPI.getOrderStatistics({
      user_id: currentUser.value.user_id
    })
    stats.value = response || {}
  } catch (error) {
    console.error('Failed to load stats:', error)
  }
}

onMounted(() => {
  if (!userStore.isLoggedIn) {
    router.push('/login')
    return
  }
  
  initUserForm()
})
</script>

<style scoped>
/* 现代扁平化风格 - Twitter/YouTube/Google 风格 */

.profile-view {
  max-width: var(--container-max-width);
  margin: 0 auto;
  padding: var(--spacing-6);
  background: var(--color-bg-page);
}

.profile-view h1 {
  color: var(--color-text-primary);
  margin-bottom: var(--spacing-8);
  font-size: var(--font-size-4xl);
  font-weight: var(--font-weight-bold);
}

.profile-container {
  display: grid;
  grid-template-columns: 300px 1fr;
  gap: var(--spacing-6);
}

/* 侧边栏 */
.profile-sidebar {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-4);
}

/* 用户卡片 - 扁平带边框 */
.user-card {
  background: var(--color-bg-card);
  padding: var(--spacing-6);
  border: 1px solid var(--color-border-base);
  border-radius: var(--radius-lg);
  text-align: center;
}

.user-avatar {
  width: 80px;
  height: 80px;
  border-radius: var(--radius-round);
  object-fit: cover;
  margin-bottom: var(--spacing-4);
  border: 3px solid var(--color-border-light);
}

.user-info h2 {
  color: var(--color-text-primary);
  margin: 0 0 var(--spacing-2) 0;
  font-size: var(--font-size-xl);
  font-weight: var(--font-weight-semibold);
}

.user-info p {
  color: var(--color-text-secondary);
  margin: 0 0 var(--spacing-3) 0;
  font-size: var(--font-size-sm);
}

.credit-score {
  background: var(--color-primary-lighter);
  color: var(--color-primary-dark);
  padding: var(--spacing-2) var(--spacing-3);
  border-radius: var(--radius-full);
  font-weight: var(--font-weight-medium);
  font-size: var(--font-size-sm);
  display: inline-block;
}

/* 导航 - 扁平 */
.profile-nav {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-1);
}

.nav-btn {
  padding: var(--spacing-3) var(--spacing-4);
  background: var(--color-bg-card);
  border: 1px solid var(--color-border-base);
  border-radius: var(--radius-base);
  text-align: left;
  cursor: pointer;
  transition: all var(--transition-base);
  font-size: var(--font-size-base);
  color: var(--color-text-primary);
  font-weight: var(--font-weight-medium);
}

.nav-btn:hover {
  border-color: var(--color-primary-light);
  background: var(--color-bg-section);
}

.nav-btn.active {
  background: var(--color-primary);
  color: white;
  border-color: var(--color-primary);
}

/* 内容区域 - 扁平带边框 */
.profile-content {
  background: var(--color-bg-card);
  padding: var(--spacing-6);
  border: 1px solid var(--color-border-base);
  border-radius: var(--radius-lg);
  min-height: 500px;
}

.tab-content h2 {
  color: var(--color-text-primary);
  margin-bottom: var(--spacing-6);
  font-size: var(--font-size-2xl);
  font-weight: var(--font-weight-bold);
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--spacing-6);
}

.section-header h2 {
  margin: 0;
}

.publish-btn,
.add-btn {
  background: var(--color-primary);
  color: white;
  padding: var(--spacing-2) var(--spacing-4);
  border: none;
  border-radius: var(--radius-base);
  text-decoration: none;
  cursor: pointer;
  transition: all var(--transition-base);
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-medium);
}

.publish-btn:hover,
.add-btn:hover {
  background: var(--color-primary-dark);
}

/* 表单样式 - 扁平 */
.info-form {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-4);
  max-width: 500px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-2);
}

.form-group label {
  font-weight: var(--font-weight-medium);
  color: var(--color-text-primary);
  font-size: var(--font-size-sm);
}

.form-group input {
  padding: var(--spacing-3);
  border: 1px solid var(--color-border-base);
  border-radius: var(--radius-base);
  font-size: var(--font-size-base);
  transition: border-color var(--transition-fast);
}

.form-group input:focus {
  outline: none;
  border-color: var(--color-primary);
}

.disabled-input {
  background: var(--color-bg-section);
  color: var(--color-text-secondary);
  cursor: not-allowed;
}

.update-btn {
  background: var(--color-success);
  color: white;
  padding: var(--spacing-3) var(--spacing-5);
  border: none;
  border-radius: var(--radius-base);
  cursor: pointer;
  font-size: var(--font-size-base);
  font-weight: var(--font-weight-medium);
  transition: all var(--transition-base);
}

.update-btn:hover:not(:disabled) {
  background: #218838;
}

.update-btn:disabled {
  background: var(--color-neutral-400);
  cursor: not-allowed;
}

.message {
  padding: var(--spacing-3);
  border-radius: var(--radius-base);
  background: var(--color-success-light);
  color: #155724;
  border: 1px solid #c3e6cb;
  font-size: var(--font-size-sm);
}

/* 筛选器 */
.item-filters {
  margin-bottom: var(--spacing-4);
}

.item-filters select {
  padding: var(--spacing-2) var(--spacing-3);
  border: 1px solid var(--color-border-base);
  border-radius: var(--radius-base);
  font-size: var(--font-size-sm);
  background: var(--color-bg-card);
  cursor: pointer;
}

/* 加载和空状态 */
.loading,
.no-items {
  text-align: center;
  padding: var(--spacing-8);
  color: var(--color-text-secondary);
  font-size: var(--font-size-base);
}

/* 商品网格 */
.items-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
  gap: var(--spacing-4);
}

.item-card {
  border: 1px solid var(--color-border-base);
  border-radius: var(--radius-lg);
  overflow: hidden;
  transition: all var(--transition-base);
  background: var(--color-bg-card);
}

.item-card:hover {
  border-color: var(--color-border-light);
  box-shadow: var(--shadow-md);
  transform: translateY(-2px);
}

.item-image {
  width: 100%;
  height: 160px;
  object-fit: cover;
  background: var(--color-neutral-100);
}

.item-info {
  padding: var(--spacing-3);
}

.item-info h3 {
  color: var(--color-text-primary);
  margin: 0 0 var(--spacing-2) 0;
  font-size: var(--font-size-base);
  font-weight: var(--font-weight-medium);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.item-price {
  color: var(--color-price);
  font-weight: var(--font-weight-bold);
  margin: 0 0 var(--spacing-1) 0;
  font-size: var(--font-size-lg);
}

.item-status,
.item-views {
  color: var(--color-text-secondary);
  font-size: var(--font-size-xs);
  margin: 0 0 var(--spacing-1) 0;
}

.item-actions {
  display: flex;
  gap: var(--spacing-2);
  padding: var(--spacing-3);
  border-top: 1px solid var(--color-border-light);
}

.view-btn,
.edit-btn {
  flex: 1;
  padding: var(--spacing-2) var(--spacing-3);
  border: none;
  border-radius: var(--radius-base);
  cursor: pointer;
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-medium);
  transition: all var(--transition-base);
}

.view-btn {
  background: var(--color-primary);
  color: white;
}

.view-btn:hover {
  background: var(--color-primary-dark);
}

.edit-btn {
  background: var(--color-success);
  color: white;
}

.edit-btn:hover {
  background: #218838;
}

/* 地址列表 */
.addresses-list {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-4);
}

.address-card {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--spacing-4);
  border: 1px solid var(--color-border-base);
  border-radius: var(--radius-lg);
  background: var(--color-bg-card);
  transition: all var(--transition-base);
}

.address-card:hover {
  border-color: var(--color-border-light);
  box-shadow: var(--shadow-sm);
}

.address-header {
  display: flex;
  gap: var(--spacing-3);
  align-items: center;
  margin-bottom: var(--spacing-2);
}

.recipient {
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
  font-size: var(--font-size-base);
}

.phone {
  color: var(--color-text-secondary);
  font-size: var(--font-size-sm);
}

.default-badge {
  background: var(--color-primary);
  color: white;
  padding: var(--spacing-1) var(--spacing-2);
  border-radius: var(--radius-full);
  font-size: var(--font-size-xs);
  font-weight: var(--font-weight-medium);
}

.address-detail {
  color: var(--color-text-secondary);
  font-size: var(--font-size-sm);
  line-height: var(--line-height-relaxed);
}

.address-actions {
  display: flex;
  gap: var(--spacing-2);
  flex-shrink: 0;
}

.address-actions button {
  padding: var(--spacing-2) var(--spacing-3);
  border: none;
  border-radius: var(--radius-base);
  cursor: pointer;
  font-size: var(--font-size-xs);
  font-weight: var(--font-weight-medium);
  transition: all var(--transition-base);
}

.default-btn {
  background: var(--color-primary);
  color: white;
}

.default-btn:hover {
  background: var(--color-primary-dark);
}

.delete-btn {
  background: var(--color-danger);
  color: white;
}

.delete-btn:hover {
  background: #c82333;
}

/* 统计卡片 - 扁平带边框 */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: var(--spacing-4);
}

.stat-card {
  text-align: center;
  padding: var(--spacing-6);
  border: 1px solid var(--color-border-base);
  border-radius: var(--radius-lg);
  background: var(--color-bg-card);
  transition: all var(--transition-base);
}

.stat-card:hover {
  border-color: var(--color-primary-light);
  box-shadow: var(--shadow-md);
}

.stat-number {
  font-size: var(--font-size-4xl);
  font-weight: var(--font-weight-bold);
  color: var(--color-primary);
  margin-bottom: var(--spacing-2);
}

.stat-label {
  color: var(--color-text-secondary);
  font-size: var(--font-size-sm);
}

/* 弹窗样式 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: var(--z-index-modal);
}

.modal-content {
  background: var(--color-bg-card);
  border: 1px solid var(--color-border-base);
  border-radius: var(--radius-lg);
  padding: var(--spacing-6);
  width: 90%;
  max-width: 600px;
  box-shadow: var(--shadow-2xl);
}

.modal-content h3 {
  color: var(--color-text-primary);
  margin: 0 0 var(--spacing-4) 0;
  font-size: var(--font-size-xl);
  font-weight: var(--font-weight-bold);
}

/* 响应式 */
@media (max-width: 1024px) {
  .profile-container {
    grid-template-columns: 250px 1fr;
  }
}

@media (max-width: 768px) {
  .profile-view {
    padding: var(--spacing-4);
  }

  .profile-view h1 {
    font-size: var(--font-size-3xl);
    margin-bottom: var(--spacing-6);
  }

  .profile-container {
    grid-template-columns: 1fr;
    gap: var(--spacing-4);
  }

  .profile-nav {
    flex-direction: row;
    overflow-x: auto;
    gap: var(--spacing-2);
  }

  .nav-btn {
    white-space: nowrap;
  }

  .section-header {
    flex-direction: column;
    gap: var(--spacing-3);
    align-items: stretch;
  }

  .items-grid {
    grid-template-columns: 1fr;
  }

  .address-card {
    flex-direction: column;
    gap: var(--spacing-3);
    align-items: stretch;
  }

  .address-actions {
    justify-content: center;
  }

  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style>
