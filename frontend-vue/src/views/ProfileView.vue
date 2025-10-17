<template>
  <div class="profile-view">
    <h1>个人中心</h1>
    
    <div class="profile-container">
      <div class="profile-sidebar">
        <div class="user-card">
          <img 
            :src="currentUser?.avatar || '/default-avatar.jpg'"
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
                :src="item.images && item.images[0] ? item.images[0] : '/placeholder.jpg'"
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
            <button @click="showAddressModal = true" class="add-btn">
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
                <button @click="editAddress(address)" class="edit-btn">
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
        <h3>{{ editingAddress ? '编辑地址' : '添加地址' }}</h3>
        <form @submit.prevent="saveAddress" class="address-form">
          <div class="form-row">
            <div class="form-group">
              <label>收件人</label>
              <input v-model="addressForm.recipient_name" type="text" required />
            </div>
            <div class="form-group">
              <label>手机号</label>
              <input v-model="addressForm.phone" type="tel" required />
            </div>
          </div>

          <div class="form-row">
            <div class="form-group">
              <label>省份</label>
              <input v-model="addressForm.province" type="text" required />
            </div>
            <div class="form-group">
              <label>城市</label>
              <input v-model="addressForm.city" type="text" required />
            </div>
            <div class="form-group">
              <label>区县</label>
              <input v-model="addressForm.district" type="text" required />
            </div>
          </div>

          <div class="form-group">
            <label>详细地址</label>
            <input v-model="addressForm.detailed_address" type="text" required />
          </div>

          <div class="form-group">
            <label>
              <input 
                v-model="addressForm.is_default" 
                type="checkbox"
              />
              设为默认地址
            </label>
          </div>

          <div class="modal-actions">
            <button type="button" @click="closeAddressModal" class="cancel-btn">
              取消
            </button>
            <button type="submit" class="save-btn">
              保存
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { itemAPI, addressAPI, orderAPI } from '@/api'

const router = useRouter()
const userStore = useUserStore()

const activeTab = ref('info')
const updating = ref(false)
const updateMessage = ref('')

// 用户信息表单
const userForm = ref({
  student_id: '',
  username: '',
  real_name: '',
  phone: '',
  email: ''
})

// 我的商品
const myItems = ref([])
const itemsLoading = ref(false)
const itemStatus = ref('available')

// 地址管理
const addresses = ref([])
const addressesLoading = ref(false)
const showAddressModal = ref(false)
const editingAddress = ref(null)
const addressForm = ref({
  recipient_name: '',
  phone: '',
  province: '',
  city: '',
  district: '',
  detailed_address: '',
  is_default: false
})

// 统计信息
const stats = ref({})

const currentUser = computed(() => userStore.currentUser)

const tabs = [
  { key: 'info', label: '基本信息' },
  { key: 'items', label: '我的商品' },
  { key: 'addresses', label: '地址管理' },
  { key: 'stats', label: '统计信息' }
]

const statusMap = {
  'available': '在售',
  'sold': '已售出',
  'removed': '已下架'
}

const getStatusText = (status: string) => {
  return statusMap[status] || status
}

const initUserForm = () => {
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

const switchTab = (tab: string) => {
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

const updateUserInfo = async () => {
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

const loadMyItems = async () => {
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

const viewItem = (itemId: number) => {
  router.push(`/items/${itemId}`)
}

const editItem = (itemId: number) => {
  router.push(`/items/${itemId}/edit`)
}

const loadAddresses = async () => {
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

interface Address {
  address_id: number
  recipient_name: string
  phone: string
  province: string
  city: string
  district: string
  detailed_address: string
  is_default: boolean
}

const editAddress = (address: Address) => {
  editingAddress.value = address
  addressForm.value = {
    recipient_name: address.recipient_name,
    phone: address.phone,
    province: address.province,
    city: address.city,
    district: address.district,
    detailed_address: address.detailed_address,
    is_default: address.is_default
  }
  showAddressModal.value = true
}

const closeAddressModal = () => {
  showAddressModal.value = false
  editingAddress.value = null
  addressForm.value = {
    recipient_name: '',
    phone: '',
    province: '',
    city: '',
    district: '',
    detailed_address: '',
    is_default: false
  }
}

const saveAddress = async () => {
  try {
    const addressData = {
      ...addressForm.value,
      user_id: currentUser.value.user_id
    }

    if (editingAddress.value) {
      await addressAPI.updateAddress(editingAddress.value.address_id, addressData)
    } else {
      await addressAPI.addAddress(addressData)
    }

    closeAddressModal()
    loadAddresses()
  } catch (error) {
    console.error('Failed to save address:', error)
    alert('保存地址失败，请重试')
  }
}

const setDefaultAddress = async (addressId: number) => {
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

const deleteAddress = async (addressId: number) => {
  if (!confirm('确定要删除这个地址吗？')) {
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

const loadStats = async () => {
  if (!currentUser.value) return

  try {
    const response = await orderAPI.getOrderStatistics({
      user_id: currentUser.value.user_id
    })
    stats.value = response
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
.profile-view {
  max-width: 1800px;
  margin: 0 auto;
  padding: 30px 40px;
}

.profile-view h1 {
  color: #2c3e50;
  margin-bottom: 30px;
  text-align: center;
}

.profile-container {
  display: grid;
  grid-template-columns: 350px 1fr;
  gap: 40px;
}

.profile-sidebar {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.user-card {
  background: white;
  padding: 30px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  text-align: center;
}

.user-avatar {
  width: 100px;
  height: 100px;
  border-radius: 50%;
  object-fit: cover;
  margin-bottom: 15px;
}

.user-info h2 {
  color: #2c3e50;
  margin: 0 0 5px 0;
}

.user-info p {
  color: #6c757d;
  margin: 0 0 10px 0;
}

.credit-score {
  background: #e3f2fd;
  color: #1976d2;
  padding: 8px 16px;
  border-radius: 20px;
  font-weight: 500;
  display: inline-block;
}

.profile-nav {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.nav-btn {
  padding: 15px 20px;
  background: white;
  border: none;
  border-radius: 8px;
  text-align: left;
  cursor: pointer;
  transition: all 0.3s;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.nav-btn:hover {
  background: #f8f9fa;
}

.nav-btn.active {
  background: #007bff;
  color: white;
}

.profile-content {
  background: white;
  padding: 30px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.tab-content h2 {
  color: #2c3e50;
  margin-bottom: 30px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
}

.publish-btn,
.add-btn {
  background: #007bff;
  color: white;
  padding: 10px 20px;
  border: none;
  border-radius: 6px;
  text-decoration: none;
  cursor: pointer;
  transition: background-color 0.3s;
}

.publish-btn:hover,
.add-btn:hover {
  background: #0056b3;
}

.info-form {
  display: flex;
  flex-direction: column;
  gap: 20px;
  max-width: 500px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-group label {
  font-weight: 500;
  color: #2c3e50;
}

.form-group input {
  padding: 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 16px;
}

.disabled-input {
  background: #f8f9fa;
  color: #6c757d;
}

.form-row {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
}

.update-btn {
  background: #28a745;
  color: white;
  padding: 12px 24px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 16px;
  transition: background-color 0.3s;
}

.update-btn:hover:not(:disabled) {
  background: #218838;
}

.update-btn:disabled {
  background: #6c757d;
  cursor: not-allowed;
}

.message {
  padding: 10px;
  border-radius: 4px;
  background: #d4edda;
  color: #155724;
  border: 1px solid #c3e6cb;
}

.item-filters {
  margin-bottom: 20px;
}

.item-filters select {
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.loading {
  text-align: center;
  padding: 40px;
  color: #6c757d;
}

.no-items {
  text-align: center;
  padding: 40px;
  color: #6c757d;
}

.items-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 20px;
}

.item-card {
  border: 1px solid #eee;
  border-radius: 8px;
  overflow: hidden;
  transition: all 0.3s;
}

.item-card:hover {
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}

.item-image {
  width: 100%;
  height: 150px;
  object-fit: cover;
}

.item-info {
  padding: 15px;
}

.item-info h3 {
  color: #2c3e50;
  margin: 0 0 8px 0;
  font-size: 1rem;
}

.item-price {
  color: #e74c3c;
  font-weight: 600;
  margin: 0 0 5px 0;
}

.item-status,
.item-views {
  color: #6c757d;
  font-size: 0.9rem;
  margin: 0 0 5px 0;
}

.item-actions {
  display: flex;
  gap: 10px;
  padding: 15px;
  border-top: 1px solid #f8f9fa;
}

.view-btn,
.edit-btn {
  flex: 1;
  padding: 8px 12px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
}

.view-btn {
  background: #007bff;
  color: white;
}

.edit-btn {
  background: #28a745;
  color: white;
}

.addresses-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.address-card {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  border: 1px solid #eee;
  border-radius: 8px;
}

.address-header {
  display: flex;
  gap: 15px;
  align-items: center;
  margin-bottom: 8px;
}

.recipient {
  font-weight: 500;
  color: #2c3e50;
}

.phone {
  color: #6c757d;
}

.default-badge {
  background: #007bff;
  color: white;
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 0.8rem;
}

.address-detail {
  color: #6c757d;
}

.address-actions {
  display: flex;
  gap: 10px;
}

.address-actions button {
  padding: 6px 12px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
}

.default-btn {
  background: #007bff;
  color: white;
}

.delete-btn {
  background: #dc3545;
  color: white;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
}

.stat-card {
  text-align: center;
  padding: 30px;
  border: 1px solid #eee;
  border-radius: 8px;
}

.stat-number {
  font-size: 2rem;
  font-weight: 600;
  color: #007bff;
  margin-bottom: 10px;
}

.stat-label {
  color: #6c757d;
  font-size: 0.9rem;
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
  max-width: 600px;
}

.modal-content h3 {
  color: #2c3e50;
  margin-bottom: 20px;
}

.address-form {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.modal-actions {
  display: flex;
  gap: 15px;
  justify-content: flex-end;
  margin-top: 20px;
}

.cancel-btn,
.save-btn {
  padding: 10px 20px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.cancel-btn {
  background: #6c757d;
  color: white;
}

.save-btn {
  background: #007bff;
  color: white;
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
    gap: 15px;
    align-items: stretch;
  }

  .form-row {
    grid-template-columns: 1fr;
  }

  .address-card {
    flex-direction: column;
    gap: 15px;
    align-items: stretch;
  }

  .address-actions {
    justify-content: center;
  }
}
</style>