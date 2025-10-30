<template>
  <div class="profile-container">
    <!-- 顶部用户卡片 -->
    <div class="profile-header">
      <div class="user-banner">
        <div class="user-avatar-section">
          <UserAvatar
            :avatar="currentUser?.avatar || undefined"
            :username="currentUser?.username"
            :size="80"
          />
          <div class="user-info">
            <h1>{{ currentUser?.username }}</h1>
            <p class="real-name">{{ currentUser?.real_name }}</p>
            <div class="credit-badge">
              <el-icon><Medal /></el-icon>
              <span>信用分: {{ currentUser?.credit_score || 100 }}</span>
            </div>
          </div>
        </div>
        <div class="stats-overview">
          <div class="stat-item">
            <div class="stat-value">{{ stats.seller_stats?.total_sales || 0 }}</div>
            <div class="stat-label">出售</div>
          </div>
          <div class="stat-item">
            <div class="stat-value">{{ stats.buyer_stats?.total_orders || 0 }}</div>
            <div class="stat-label">购买</div>
          </div>
          <div class="stat-item">
            <div class="stat-value">{{ wishlistCount }}</div>
            <div class="stat-label">收藏</div>
          </div>
        </div>
      </div>
    </div>

    <!-- Tab导航 -->
    <el-tabs v-model="activeTab" class="profile-tabs" @tab-change="handleTabChange">
      <!-- 基本信息 -->
      <el-tab-pane label="基本信息" name="info">
        <div class="tab-content">
          <el-card>
            <template #header>
              <div class="card-header">
                <span>个人资料</span>
              </div>
            </template>
            <el-form :model="userForm" label-width="100px" class="profile-form">
              <el-form-item label="学号">
                <el-input v-model="userForm.student_id" disabled />
              </el-form-item>
              <el-form-item label="用户名">
                <el-input v-model="userForm.username" />
              </el-form-item>
              <el-form-item label="真实姓名">
                <el-input v-model="userForm.real_name" />
              </el-form-item>
              <el-form-item label="手机号">
                <el-input v-model="userForm.phone" />
              </el-form-item>
              <el-form-item label="邮箱">
                <el-input v-model="userForm.email" />
              </el-form-item>
              <el-form-item>
                <el-button type="primary" @click="updateUserInfo" :loading="updating">
                  保存修改
                </el-button>
              </el-form-item>
            </el-form>
          </el-card>
        </div>
      </el-tab-pane>

      <!-- 我的商品 -->
      <el-tab-pane label="我的商品" name="items">
        <div class="tab-content">
          <div class="section-header">
            <el-radio-group v-model="itemStatus" @change="loadMyItems">
              <el-radio-button value="available">在售</el-radio-button>
              <el-radio-button value="sold">已售出</el-radio-button>
              <el-radio-button value="removed">已下架</el-radio-button>
            </el-radio-group>
            <el-button type="primary" :icon="Plus" @click="router.push('/publish')">
              发布商品
            </el-button>
          </div>

          <el-skeleton :loading="itemsLoading" :rows="3" animated>
            <el-empty v-if="myItems.length === 0" description="暂无商品" />
            <div v-else class="items-grid">
              <ItemCard
                v-for="item in myItems"
                :key="item.item_id"
                :item="item"
                @click="viewItem(item.item_id)"
              >
                <template #actions>
                  <el-button
                    v-if="item.status === 'available'"
                    size="small"
                    @click.stop="editItem(item.item_id)"
                  >
                    编辑
                  </el-button>
                </template>
              </ItemCard>
            </div>
          </el-skeleton>
        </div>
      </el-tab-pane>

      <!-- 我的订单 -->
      <el-tab-pane label="我的订单" name="orders">
        <div class="tab-content">
          <el-tabs v-model="orderRole" class="order-tabs">
            <el-tab-pane label="我买到的" name="buyer">
              <el-skeleton :loading="ordersLoading" :rows="3" animated>
                <el-empty v-if="buyerOrders.length === 0" description="暂无订单" />
                <div v-else class="orders-list">
                  <el-card
                    v-for="order in buyerOrders"
                    :key="order.order_id"
                    class="order-card"
                    shadow="hover"
                    @click="viewOrder(order.order_id)"
                  >
                    <div class="order-header">
                      <span class="order-number">订单号: {{ order.order_number }}</span>
                      <OrderStatus :status="order.order_status" />
                    </div>
                    <div class="order-body">
                      <el-image
                        :src="order.item_images?.[0] || '/placeholder.png'"
                        class="order-image"
                        fit="cover"
                      />
                      <div class="order-info">
                        <div class="order-title">{{ order.item_title }}</div>
                        <div class="order-price">¥{{ order.total_amount }}</div>
                        <div class="order-time">{{ formatDate(order.create_time) }}</div>
                      </div>
                    </div>
                  </el-card>
                </div>
              </el-skeleton>
            </el-tab-pane>

            <el-tab-pane label="我卖出的" name="seller">
              <el-skeleton :loading="ordersLoading" :rows="3" animated>
                <el-empty v-if="sellerOrders.length === 0" description="暂无订单" />
                <div v-else class="orders-list">
                  <el-card
                    v-for="order in sellerOrders"
                    :key="order.order_id"
                    class="order-card"
                    shadow="hover"
                    @click="viewOrder(order.order_id)"
                  >
                    <div class="order-header">
                      <span class="order-number">订单号: {{ order.order_number }}</span>
                      <OrderStatus :status="order.order_status" />
                    </div>
                    <div class="order-body">
                      <el-image
                        :src="order.item_images?.[0] || '/placeholder.png'"
                        class="order-image"
                        fit="cover"
                      />
                      <div class="order-info">
                        <div class="order-title">{{ order.item_title }}</div>
                        <div class="order-price">¥{{ order.total_amount }}</div>
                        <div class="order-time">{{ formatDate(order.create_time) }}</div>
                      </div>
                    </div>
                  </el-card>
                </div>
              </el-skeleton>
            </el-tab-pane>
          </el-tabs>
        </div>
      </el-tab-pane>

      <!-- 我的收藏 -->
      <el-tab-pane label="我的收藏" name="wishlist">
        <div class="tab-content">
          <el-skeleton :loading="wishlistLoading" :rows="3" animated>
            <el-empty v-if="wishlistItems.length === 0" description="暂无收藏" />
            <div v-else class="items-grid">
              <ItemCard
                v-for="wishlist in wishlistItems"
                :key="wishlist.item_id"
                :item="{
                  item_id: wishlist.item_id,
                  title: wishlist.title || '未知商品',
                  price: wishlist.price || 0,
                  images: wishlist.images || [],
                  status: wishlist.status || 'available',
                  view_count: wishlist.view_count || 0,
                  condition_level: wishlist.condition_level || 'acceptable',
                  location: wishlist.location || '未知地点',
                  username: wishlist.seller_name,
                  credit_score: wishlist.credit_score,
                  category_name: wishlist.category_name
                }"
                @click="viewItem(wishlist.item_id)"
              >
                <template #actions>
                  <el-button
                    size="small"
                    type="danger"
                    :icon="Delete"
                    @click.stop="removeFromWishlist(wishlist.item_id)"
                  >
                    移除
                  </el-button>
                </template>
              </ItemCard>
            </div>
          </el-skeleton>
        </div>
      </el-tab-pane>

      <!-- 地址管理 -->
      <el-tab-pane label="地址管理" name="addresses">
        <div class="tab-content">
          <div class="section-header">
            <span></span>
            <el-button type="primary" :icon="Plus" @click="openCreateAddress">
              添加地址
            </el-button>
          </div>

          <el-skeleton :loading="addressesLoading" :rows="3" animated>
            <el-empty v-if="addresses.length === 0" description="暂无地址" />
            <div v-else class="addresses-list">
              <el-card
                v-for="address in addresses"
                :key="address.address_id"
                class="address-card"
                shadow="hover"
              >
                <div class="address-header">
                  <span class="recipient">{{ address.recipient_name }}</span>
                  <span class="phone">{{ address.phone }}</span>
                  <el-tag v-if="address.is_default" type="success" size="small">
                    默认地址
                  </el-tag>
                </div>
                <div class="address-detail">
                  {{ address.province }} {{ address.city }} {{ address.district }}
                  {{ address.detailed_address }}
                </div>
                <div class="address-actions">
                  <el-button size="small" @click="openEditAddress(address)">编辑</el-button>
                  <el-button
                    v-if="!address.is_default"
                    size="small"
                    @click="setDefaultAddress(address.address_id)"
                  >
                    设为默认
                  </el-button>
                  <el-button
                    size="small"
                    type="danger"
                    @click="deleteAddress(address.address_id)"
                  >
                    删除
                  </el-button>
                </div>
              </el-card>
            </div>
          </el-skeleton>
        </div>
      </el-tab-pane>
    </el-tabs>

    <!-- 地址编辑对话框 -->
    <el-dialog
      v-model="showAddressModal"
      :title="addressModalMode === 'edit' ? '编辑地址' : '添加地址'"
      width="600px"
    >
      <AddressForm
        :address="addressInitialValue || undefined"
        :loading="addressModalLoading"
        :submit-text="addressModalMode === 'edit' ? '保存修改' : '添加地址'"
        @save="handleAddressSave"
        @cancel="closeAddressModal"
      />
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { itemAPI, addressAPI, orderAPI, wishlistAPI } from '@/api'
import type { Item, Address, AddressParams, Wishlist, Order } from '@/types'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Delete, Medal } from '@element-plus/icons-vue'
import UserAvatar from '@/components/UserAvatar.vue'
import ItemCard from '@/components/ItemCard.vue'
import OrderStatus from '@/components/OrderStatus.vue'
import AddressForm from '@/components/AddressForm.vue'

const router = useRouter()
const userStore = useUserStore()

const activeTab = ref('info')
const orderRole = ref('buyer')
const updating = ref(false)

const userForm = ref({
  student_id: '',
  username: '',
  real_name: '',
  phone: '',
  email: ''
})

// 商品相关
const myItems = ref<Item[]>([])
const itemsLoading = ref(false)
const itemStatus = ref('available')

// 订单相关
const buyerOrders = ref<Order[]>([])
const sellerOrders = ref<Order[]>([])
const ordersLoading = ref(false)

// 收藏相关
const wishlistItems = ref<Wishlist[]>([])
const wishlistLoading = ref(false)
const wishlistCount = ref(0)

// 地址相关
const addresses = ref<Address[]>([])
const addressesLoading = ref(false)
const showAddressModal = ref(false)
const editingAddress = ref<Address | null>(null)
const addressModalMode = ref<'create' | 'edit'>('create')
const addressModalLoading = ref(false)

// 统计数据
const stats = ref<any>({})

const currentUser = computed(() => userStore.currentUser)

const addressInitialValue = computed<Omit<AddressParams, 'user_id'> | null>(() => {
  if (!editingAddress.value) return null
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

// 格式化日期
const formatDate = (dateString: string) => {
  const date = new Date(dateString)
  return date.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit'
  })
}

// 初始化用户表单
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

// Tab切换
const handleTabChange = (tabName: string) => {
  switch (tabName) {
    case 'items':
      loadMyItems()
      break
    case 'orders':
      loadOrders()
      break
    case 'wishlist':
      loadWishlist()
      break
    case 'addresses':
      loadAddresses()
      break
  }
}

// 更新用户信息
const updateUserInfo = async () => {
  updating.value = true
  try {
    const result = await userStore.updateUserInfo(userForm.value)
    if (result.success) {
      ElMessage.success('信息更新成功')
    } else {
      ElMessage.error(result.message)
    }
  } catch (error) {
    ElMessage.error('更新失败，请重试')
  } finally {
    updating.value = false
  }
}

// 加载我的商品
const loadMyItems = async (forceReload = false) => {
  if (!currentUser.value) return

  // 商品需要根据状态筛选，所以每次都要加载
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
    ElMessage.error('加载商品失败')
  } finally {
    itemsLoading.value = false
  }
}

// 加载订单
const loadOrders = async (forceReload = false) => {
  if (!currentUser.value) return

  // 如果已经有数据且不是强制刷新，则跳过
  if (!forceReload && (buyerOrders.value.length > 0 || sellerOrders.value.length > 0)) {
    return
  }

  ordersLoading.value = true
  try {
    // 修复：正确传递 userId 作为第一个参数
    const response = await orderAPI.getUserOrders(currentUser.value.user_id, {})
    const orders = response.orders || []

    // 分离买家和卖家订单
    buyerOrders.value = orders.filter(
      (order: Order) => order.buyer_id === currentUser.value?.user_id
    )
    sellerOrders.value = orders.filter(
      (order: Order) => order.seller_id === currentUser.value?.user_id
    )
  } catch (error) {
    console.error('Failed to load orders:', error)
    ElMessage.error('加载订单失败')
  } finally {
    ordersLoading.value = false
  }
}

// 加载收藏
const loadWishlist = async (forceReload = false) => {
  if (!currentUser.value) return

  // 如果已经有数据且不是强制刷新，则跳过
  if (!forceReload && wishlistItems.value.length > 0) {
    return
  }

  wishlistLoading.value = true
  try {
    const response = await wishlistAPI.getWishlist(currentUser.value.user_id, {
      page: 1,
      limit: 20
    })
    wishlistItems.value = response.wishlist || []
    wishlistCount.value = wishlistItems.value.length
  } catch (error) {
    console.error('Failed to load wishlist:', error)
    ElMessage.error('加载收藏失败')
  } finally {
    wishlistLoading.value = false
  }
}

// 加载地址
const loadAddresses = async (forceReload = false) => {
  if (!currentUser.value) return

  // 如果已经有数据且不是强制刷新，则跳过
  if (!forceReload && addresses.value.length > 0) {
    return
  }

  addressesLoading.value = true
  try {
    const response = await addressAPI.getUserAddresses(currentUser.value.user_id)
    addresses.value = response.addresses || []
  } catch (error) {
    console.error('Failed to load addresses:', error)
    ElMessage.error('加载地址失败')
  } finally {
    addressesLoading.value = false
  }
}

// 加载统计数据
const loadStats = async () => {
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

// 查看商品
const viewItem = (itemId: number) => {
  router.push(`/items/${itemId}`)
}

// 编辑商品
const editItem = (itemId: number) => {
  router.push(`/items/${itemId}/edit`)
}

// 查看订单
const viewOrder = (orderId: number) => {
  router.push(`/orders/${orderId}`)
}

// 从收藏中移除
const removeFromWishlist = async (itemId: number) => {
  if (!currentUser.value) return
  try {
    await wishlistAPI.removeFromWishlist({
      user_id: currentUser.value.user_id,
      item_id: itemId
    })
    ElMessage.success('已移除收藏')
    // 强制刷新收藏列表
    loadWishlist(true)
  } catch (error) {
    console.error('Failed to remove from wishlist:', error)
    ElMessage.error('移除失败')
  }
}

// 地址管理
const openCreateAddress = () => {
  editingAddress.value = null
  addressModalMode.value = 'create'
  showAddressModal.value = true
}

const openEditAddress = (address: Address) => {
  editingAddress.value = address
  addressModalMode.value = 'edit'
  showAddressModal.value = true
}

const closeAddressModal = () => {
  showAddressModal.value = false
  addressModalLoading.value = false
  editingAddress.value = null
  addressModalMode.value = 'create'
}

const handleAddressSave = async (value: Omit<AddressParams, 'user_id'>) => {
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
    // 强制刷新地址列表
    loadAddresses(true)
  } catch (error: any) {
    console.error('Failed to save address:', error)
    const backendMessage = error?.response?.data?.error
    ElMessage.error(backendMessage || '保存地址失败，请重试')
  } finally {
    addressModalLoading.value = false
  }
}

const setDefaultAddress = async (addressId: number) => {
  if (!currentUser.value) return
  try {
    await addressAPI.setDefaultAddress(addressId, {
      user_id: currentUser.value.user_id
    })
    ElMessage.success('已设为默认地址')
    // 强制刷新地址列表
    loadAddresses(true)
  } catch (error) {
    console.error('Failed to set default address:', error)
    ElMessage.error('设置失败')
  }
}

const deleteAddress = async (addressId: number) => {
  if (!currentUser.value) return
  try {
    await ElMessageBox.confirm('确定要删除这个地址吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })

    await addressAPI.deleteAddress(addressId, {
      user_id: currentUser.value.user_id
    })

    ElMessage.success('地址已删除')
    // 强制刷新地址列表
    loadAddresses(true)
  } catch (error: any) {
    if (error !== 'cancel') {
      console.error('Failed to delete address:', error)

      // 显示详细错误信息
      let errorMessage = '删除失败'
      if (error?.response?.data?.error) {
        const backendError = error.response.data.error
        // 翻译后端错误信息
        if (backendError.includes('pending orders')) {
          errorMessage = '该地址有未完成的订单，无法删除'
        } else if (backendError.includes('not found')) {
          errorMessage = '地址不存在'
        } else if (backendError.includes('Permission denied')) {
          errorMessage = '无权删除该地址'
        } else {
          errorMessage = `删除失败：${backendError}`
        }
      }

      ElMessage.error(errorMessage)
    }
  }
}

onMounted(() => {
  if (!userStore.isLoggedIn) {
    router.push('/login')
    return
  }
  initUserForm()
  loadStats()
  loadWishlist() // 加载收藏以获取数量
})
</script>

<style scoped>
.profile-container {
  width: 100%;
  padding: var(--spacing-6) var(--spacing-8);
  min-height: 100vh;
}

/* 用户头部 */
.profile-header {
  margin-bottom: var(--spacing-6);
}

.user-banner {
  background: linear-gradient(135deg, var(--color-primary) 0%, var(--color-primary-dark) 100%);
  border-radius: var(--radius-xl);
  padding: var(--spacing-8);
  color: white;
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: var(--shadow-lg);
}

.user-avatar-section {
  display: flex;
  align-items: center;
  gap: var(--spacing-5);
}

.user-info h1 {
  margin: 0 0 var(--spacing-2) 0;
  font-size: var(--font-size-3xl);
  font-weight: var(--font-weight-bold);
}

.real-name {
  margin: 0 0 var(--spacing-3) 0;
  opacity: 0.9;
  font-size: var(--font-size-base);
}

.credit-badge {
  display: inline-flex;
  align-items: center;
  gap: var(--spacing-2);
  background: rgba(255, 255, 255, 0.2);
  padding: var(--spacing-2) var(--spacing-3);
  border-radius: var(--radius-full);
  font-weight: var(--font-weight-medium);
  font-size: var(--font-size-sm);
}

.stats-overview {
  display: flex;
  gap: var(--spacing-6);
}

.stat-item {
  text-align: center;
}

.stat-value {
  font-size: var(--font-size-3xl);
  font-weight: var(--font-weight-bold);
  margin-bottom: var(--spacing-1);
}

.stat-label {
  font-size: var(--font-size-sm);
  opacity: 0.9;
}

/* Tabs */
.profile-tabs {
  background: var(--color-bg-card);
  border-radius: var(--radius-lg);
  padding: var(--spacing-4);
  box-shadow: var(--shadow-sm);
}

.tab-content {
  padding: var(--spacing-4) 0;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--spacing-4);
}

/* 表单 */
.profile-form {
  max-width: 600px;
}

.card-header {
  font-size: var(--font-size-lg);
  font-weight: var(--font-weight-semibold);
}

/* 商品和收藏网格 */
.items-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
  gap: var(--spacing-4);
}

/* 订单列表 */
.order-tabs {
  margin-top: var(--spacing-4);
}

.orders-list {
  display: grid;
  gap: var(--spacing-4);
}

.order-card {
  cursor: pointer;
  transition: all 0.3s ease;
}

.order-card:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-md);
}

.order-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--spacing-3);
  padding-bottom: var(--spacing-3);
  border-bottom: 1px solid var(--color-border-light);
}

.order-number {
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
}

.order-body {
  display: flex;
  gap: var(--spacing-4);
}

.order-image {
  width: 100px;
  height: 100px;
  border-radius: var(--radius-base);
  flex-shrink: 0;
}

.order-info {
  flex: 1;
}

.order-title {
  font-size: var(--font-size-base);
  font-weight: var(--font-weight-medium);
  margin-bottom: var(--spacing-2);
}

.order-price {
  color: var(--color-price);
  font-size: var(--font-size-lg);
  font-weight: var(--font-weight-bold);
  margin-bottom: var(--spacing-2);
}

.order-time {
  font-size: var(--font-size-xs);
  color: var(--color-text-secondary);
}

/* 地址列表 */
.addresses-list {
  display: grid;
  gap: var(--spacing-4);
}

.address-card {
  transition: all 0.3s ease;
}

.address-card:hover {
  box-shadow: var(--shadow-md);
}

.address-header {
  display: flex;
  gap: var(--spacing-3);
  align-items: center;
  margin-bottom: var(--spacing-3);
}

.recipient {
  font-weight: var(--font-weight-semibold);
  font-size: var(--font-size-base);
}

.phone {
  color: var(--color-text-secondary);
  font-size: var(--font-size-sm);
}

.address-detail {
  color: var(--color-text-secondary);
  line-height: var(--line-height-relaxed);
  margin-bottom: var(--spacing-3);
}

.address-actions {
  display: flex;
  gap: var(--spacing-2);
}

/* 响应式 */
@media (max-width: 768px) {
  .profile-container {
    padding: var(--spacing-4);
  }

  .user-banner {
    flex-direction: column;
    gap: var(--spacing-4);
    text-align: center;
  }

  .user-avatar-section {
    flex-direction: column;
    text-align: center;
  }

  .stats-overview {
    width: 100%;
    justify-content: space-around;
  }

  .items-grid {
    grid-template-columns: 1fr;
  }

  .order-body {
    flex-direction: column;
  }

  .order-image {
    width: 100%;
    height: 200px;
  }
}
</style>
