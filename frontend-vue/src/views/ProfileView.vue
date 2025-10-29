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
/* 使用设计系统变量 */
.profile-view {
  max-width: 1800px;
  margin: 0 auto;
  padding: var(--spacing-2xl) var(--spacing-3xl);
}

.profile-view h1 {
  color: var(--color-text-primary);
  margin-bottom: var(--spacing-2xl);
  text-align: center;
}

.profile-container {
  display: grid;
  grid-template-columns: 350px 1fr;
  gap: var(--spacing-3xl);
}

.profile-sidebar {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-lg);
}

.user-card {
  background: var(--color-bg-card);
  padding: var(--spacing-2xl);
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-base);
  text-align: center;
}

.user-avatar {
  width: 100px;
  height: 100px;
  border-radius: var(--radius-round);
  object-fit: cover;
  margin-bottom: var(--spacing-lg);
}

.user-info h2 {
  color: var(--color-text-primary);
  margin: 0 0 var(--spacing-xs) 0;
}

.user-info p {
  color: var(--color-text-secondary);
  margin: 0 0 var(--spacing-sm) 0;
}

.credit-score {
  background: #e3f2fd;
  color: #1976d2;
  padding: var(--spacing-sm) var(--spacing-base);
  border-radius: var(--radius-lg);
  font-weight: var(--font-weight-medium);
  display: inline-block;
}

.profile-nav {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-xs);
}

.nav-btn {
  padding: var(--spacing-lg) var(--spacing-lg);
  background: var(--color-bg-card);
  border: none;
  border-radius: var(--radius-md);
  text-align: left;
  cursor: pointer;
  transition: all var(--transition-base);
  box-shadow: var(--shadow-sm);
}

.nav-btn:hover {
  background: var(--color-bg-page);
}

.nav-btn.active {
  background: var(--color-primary);
  color: white;
}

.profile-content {
  background: var(--color-bg-card);
  padding: var(--spacing-2xl);
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-base);
}

.tab-content h2 {
  color: var(--color-text-primary);
  margin-bottom: var(--spacing-2xl);
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--spacing-2xl);
}

.publish-btn,
.add-btn {
  background: var(--color-primary);
  color: white;
  padding: var(--spacing-sm) var(--spacing-lg);
  border: none;
  border-radius: var(--radius-base);
  text-decoration: none;
  cursor: pointer;
  transition: background-color var(--transition-base);
}

.publish-btn:hover,
.add-btn:hover {
  background: var(--color-primary-dark);
}

.info-form {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-lg);
  max-width: 500px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-sm);
}

.form-group label {
  font-weight: var(--font-weight-medium);
  color: var(--color-text-primary);
}

.form-group input {
  padding: var(--spacing-md);
  border: 1px solid var(--color-border-base);
  border-radius: var(--radius-sm);
  font-size: var(--font-size-lg);
}

.disabled-input {
  background: var(--color-bg-page);
  color: var(--color-text-secondary);
}

.form-row {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: var(--spacing-lg);
}

.update-btn {
  background: var(--color-success);
  color: white;
  padding: var(--spacing-md) var(--spacing-xl);
  border: none;
  border-radius: var(--radius-base);
  cursor: pointer;
  font-size: var(--font-size-lg);
  transition: background-color var(--transition-base);
}

.update-btn:hover:not(:disabled) {
  background: #218838;
}

.update-btn:disabled {
  background: var(--color-info);
  cursor: not-allowed;
}

.message {
  padding: var(--spacing-sm);
  border-radius: var(--radius-sm);
  background: var(--color-success-light);
  color: #155724;
  border: 1px solid #c3e6cb;
}

.item-filters {
  margin-bottom: var(--spacing-lg);
}

.item-filters select {
  padding: var(--spacing-sm) var(--spacing-md);
  border: 1px solid var(--color-border-base);
  border-radius: var(--radius-sm);
}

.loading {
  text-align: center;
  padding: var(--spacing-3xl);
  color: var(--color-text-secondary);
}

.no-items {
  text-align: center;
  padding: var(--spacing-3xl);
  color: var(--color-text-secondary);
}

.items-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: var(--spacing-lg);
}

.item-card {
  border: 1px solid var(--color-border-lighter);
  border-radius: var(--radius-md);
  overflow: hidden;
  transition: all var(--transition-base);
}

.item-card:hover {
  box-shadow: var(--shadow-md);
}

.item-image {
  width: 100%;
  height: 150px;
  object-fit: cover;
}

.item-info {
  padding: var(--spacing-lg);
}

.item-info h3 {
  color: var(--color-text-primary);
  margin: 0 0 var(--spacing-sm) 0;
  font-size: var(--font-size-base);
}

.item-price {
  color: var(--color-price);
  font-weight: var(--font-weight-semibold);
  margin: 0 0 var(--spacing-xs) 0;
}

.item-status,
.item-views {
  color: var(--color-text-secondary);
  font-size: var(--font-size-sm);
  margin: 0 0 var(--spacing-xs) 0;
}

.item-actions {
  display: flex;
  gap: var(--spacing-sm);
  padding: var(--spacing-lg);
  border-top: 1px solid var(--color-bg-page);
}

.view-btn,
.edit-btn {
  flex: 1;
  padding: var(--spacing-sm) var(--spacing-md);
  border: none;
  border-radius: var(--radius-sm);
  cursor: pointer;
  font-size: var(--font-size-base);
}

.view-btn {
  background: var(--color-primary);
  color: white;
}

.edit-btn {
  background: var(--color-success);
  color: white;
}

.addresses-list {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-lg);
}

.address-card {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--spacing-lg);
  border: 1px solid var(--color-border-lighter);
  border-radius: var(--radius-md);
}

.address-header {
  display: flex;
  gap: var(--spacing-lg);
  align-items: center;
  margin-bottom: var(--spacing-sm);
}

.recipient {
  font-weight: var(--font-weight-medium);
  color: var(--color-text-primary);
}

.phone {
  color: var(--color-text-secondary);
}

.default-badge {
  background: var(--color-primary);
  color: white;
  padding: var(--spacing-xs) var(--spacing-sm);
  border-radius: var(--radius-lg);
  font-size: var(--font-size-xs);
}

.address-detail {
  color: var(--color-text-secondary);
}

.address-actions {
  display: flex;
  gap: var(--spacing-sm);
}

.address-actions button {
  padding: var(--spacing-xs) var(--spacing-md);
  border: none;
  border-radius: var(--radius-sm);
  cursor: pointer;
  font-size: var(--font-size-xs);
}

.default-btn {
  background: var(--color-primary);
  color: white;
}

.delete-btn {
  background: var(--color-danger);
  color: white;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: var(--spacing-lg);
}

.stat-card {
  text-align: center;
  padding: var(--spacing-2xl);
  border: 1px solid var(--color-border-lighter);
  border-radius: var(--radius-md);
}

.stat-number {
  font-size: var(--font-size-4xl);
  font-weight: var(--font-weight-semibold);
  color: var(--color-primary);
  margin-bottom: var(--spacing-sm);
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
  background: var(--color-bg-overlay);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: var(--z-index-modal);
}

.modal-content {
  background: var(--color-bg-card);
  border-radius: var(--radius-md);
  padding: var(--spacing-2xl);
  width: 90%;
  max-width: 600px;
}

.modal-content h3 {
  color: var(--color-text-primary);
  margin-bottom: var(--spacing-lg);
}

@media (max-width: 768px) {
  .profile-container {
    grid-template-columns: 1fr;
  }

  .profile-nav {
    flex-direction: row;
    overflow-x: auto;
  }

  .nav-btn {
    white-space: nowrap;
  }

  .section-header {
    flex-direction: column;
    gap: var(--spacing-lg);
    align-items: stretch;
  }

  .form-row {
    grid-template-columns: 1fr;
  }

  .address-card {
    flex-direction: column;
    gap: var(--spacing-lg);
    align-items: stretch;
  }

  .address-actions {
    justify-content: center;
  }
}
</style>
