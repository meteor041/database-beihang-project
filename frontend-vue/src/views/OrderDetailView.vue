<template>
  <div class="order-detail-view">
    <div class="detail-container">
      <h1>订单详情</h1>

      <div v-if="loading" class="loading">
        加载中...
      </div>

      <div v-else-if="!order" class="error">
        订单不存在
      </div>

      <div v-else class="detail-content">
        <!-- 订单状态 -->
        <div class="section status-section">
          <div class="status-card">
            <div :class="['status-icon', getStatusClass(order.order_status)]">
              {{ getStatusIcon(order.order_status) }}
            </div>
            <div class="status-info">
              <h2>{{ getStatusText(order.order_status) }}</h2>
              <p class="status-time">{{ formatDate(order.order_date) }}</p>
            </div>
          </div>
        </div>

        <!-- 订单进度 -->
        <div class="section timeline-section">
          <h3>订单进度</h3>
          <div class="timeline">
            <div :class="['timeline-item', { active: isStatusActive('pending') }]">
              <div class="timeline-dot"></div>
              <div class="timeline-content">
                <div class="timeline-title">订单创建</div>
                <div class="timeline-time">{{ formatDate(order.order_date) }}</div>
              </div>
            </div>
            <div :class="['timeline-item', { active: isStatusActive('paid') }]">
              <div class="timeline-dot"></div>
              <div class="timeline-content">
                <div class="timeline-title">买家付款</div>
                <div v-if="order.payment_time" class="timeline-time">
                  {{ formatDate(order.payment_time) }}
                </div>
              </div>
            </div>
            <div :class="['timeline-item', { active: isStatusActive('shipped') }]">
              <div class="timeline-dot"></div>
              <div class="timeline-content">
                <div class="timeline-title">卖家发货</div>
                <div v-if="order.ship_time" class="timeline-time">
                  {{ formatDate(order.ship_time) }}
                </div>
              </div>
            </div>
            <div :class="['timeline-item', { active: isStatusActive('completed') }]">
              <div class="timeline-dot"></div>
              <div class="timeline-content">
                <div class="timeline-title">交易完成</div>
                <div v-if="order.complete_time" class="timeline-time">
                  {{ formatDate(order.complete_time) }}
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 商品信息 -->
        <div class="section">
          <h3>商品信息</h3>
          <div class="item-card">
            <img
              :src="order.item_images?.[0] || '/placeholder.jpg'"
              :alt="order.item_title"
              class="item-image"
            />
            <div class="item-info">
              <h4>{{ order.item_title }}</h4>
              <p class="item-price">¥{{ order.item_price }}</p>
            </div>
          </div>
        </div>

        <!-- 订单信息 -->
        <div class="section">
          <h3>订单信息</h3>
          <div class="info-list">
            <div class="info-item">
              <span class="label">订单编号：</span>
              <span class="value">{{ order.order_number }}</span>
            </div>
            <div class="info-item">
              <span class="label">创建时间：</span>
              <span class="value">{{ formatDate(order.order_date) }}</span>
            </div>
            <div class="info-item">
              <span class="label">支付方式：</span>
              <span class="value">{{ getPaymentMethodText(order.payment_method) }}</span>
            </div>
            <div class="info-item">
              <span class="label">配送方式：</span>
              <span class="value">{{ getDeliveryMethodText(order.delivery_method) }}</span>
            </div>
            <div v-if="order.remarks" class="info-item">
              <span class="label">订单备注：</span>
              <span class="value">{{ order.remarks }}</span>
            </div>
          </div>
        </div>

        <!-- 收货地址 -->
        <div v-if="order.address" class="section">
          <h3>收货地址</h3>
          <div class="address-card">
            <div class="address-header">
              <span class="recipient">{{ order.address.receiver_name }}</span>
              <span class="phone">{{ order.address.receiver_phone }}</span>
            </div>
            <div class="address-detail">
              {{ order.address.province }} {{ order.address.city }}
              {{ order.address.district }} {{ order.address.detailed_address }}
            </div>
          </div>
        </div>

        <!-- 交易双方 -->
        <div class="section">
          <h3>交易信息</h3>
          <div class="info-list">
            <div class="info-item">
              <span class="label">卖家：</span>
              <span class="value">{{ order.seller_username }}</span>
            </div>
            <div class="info-item">
              <span class="label">买家：</span>
              <span class="value">{{ order.buyer_username }}</span>
            </div>
          </div>
        </div>

        <!-- 费用明细 -->
        <div class="section summary-section">
          <h3>费用明细</h3>
          <div class="summary-list">
            <div class="summary-item">
              <span>商品金额：</span>
              <span>¥{{ order.item_price }}</span>
            </div>
            <div class="summary-item total">
              <span>实付金额：</span>
              <span class="amount">¥{{ order.total_amount }}</span>
            </div>
          </div>
        </div>

        <!-- 操作按钮 -->
        <div class="actions">
          <button @click="router.back()" class="btn-secondary">
            返回
          </button>
          <button
            v-if="canCancel"
            @click="handleCancel"
            class="btn-danger"
          >
            取消订单
          </button>
          <button
            v-if="canPay"
            @click="handlePay"
            class="btn-primary"
          >
            立即支付
          </button>
          <button
            v-if="canConfirm"
            @click="handleConfirm"
            class="btn-success"
          >
            确认收货
          </button>
          <button
            v-if="canContact"
            @click="handleContact"
            class="btn-secondary"
          >
            联系{{ isBuyer ? '卖家' : '买家' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { orderAPI } from '@/api'
import { ElMessage, ElMessageBox } from 'element-plus'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()

interface OrderDetail {
  order_id: number
  order_number: string
  order_status: string
  order_date: string
  payment_time?: string
  ship_time?: string
  complete_time?: string
  item_id: number
  item_title: string
  item_price: number
  item_images?: string[]
  total_amount: number
  payment_method: string
  delivery_method: string
  remarks?: string
  buyer_id: number
  buyer_username: string
  seller_id: number
  seller_username: string
  address?: {
    receiver_name: string
    receiver_phone: string
    province: string
    city: string
    district: string
    detailed_address: string
  }
}

const order = ref<OrderDetail | null>(null)
const loading = ref(false)

const isBuyer = computed(() => {
  return order.value && userStore.currentUser && order.value.buyer_id === userStore.currentUser.user_id
})

const canCancel = computed(() => {
  return order.value?.order_status === 'pending'
})

const canPay = computed(() => {
  return isBuyer.value && order.value?.order_status === 'pending'
})

const canConfirm = computed(() => {
  return isBuyer.value && order.value?.order_status === 'shipped'
})

const canContact = computed(() => {
  return order.value && ['pending', 'paid', 'shipped'].includes(order.value.order_status)
})

const statusMap: Record<string, string> = {
  'pending': '待支付',
  'paid': '已支付',
  'shipped': '已发货',
  'completed': '已完成',
  'cancelled': '已取消'
}

const paymentMethodMap: Record<string, string> = {
  'alipay': '支付宝',
  'wechat': '微信支付',
  'cash': '线下支付'
}

const deliveryMethodMap: Record<string, string> = {
  'pickup': '自取',
  'express': '快递配送'
}

const getStatusText = (status: string): string => {
  return statusMap[status] || status
}

const getPaymentMethodText = (method: string): string => {
  return paymentMethodMap[method] || method
}

const getDeliveryMethodText = (method: string): string => {
  return deliveryMethodMap[method] || method
}

const getStatusClass = (status: string): string => {
  const classMap: Record<string, string> = {
    'pending': 'pending',
    'paid': 'paid',
    'shipped': 'shipped',
    'completed': 'completed',
    'cancelled': 'cancelled'
  }
  return classMap[status] || 'default'
}

const getStatusIcon = (status: string): string => {
  const iconMap: Record<string, string> = {
    'pending': '⏰',
    'paid': '💰',
    'shipped': '🚚',
    'completed': '✅',
    'cancelled': '❌'
  }
  return iconMap[status] || '📦'
}

const isStatusActive = (status: string): boolean => {
  if (!order.value) return false

  const statusOrder = ['pending', 'paid', 'shipped', 'completed']
  const currentIndex = statusOrder.indexOf(order.value.order_status)
  const targetIndex = statusOrder.indexOf(status)

  return currentIndex >= targetIndex
}

const formatDate = (dateString: string): string => {
  return new Date(dateString).toLocaleString('zh-CN')
}

const loadOrder = async (): Promise<void> => {
  const orderId = route.params.id
  if (!orderId) {
    ElMessage.error('缺少订单ID')
    router.back()
    return
  }

  loading.value = true
  try {
    const response = await orderAPI.getOrder(Number(orderId))
    order.value = response.data?.order as any || null

    if (!order.value) {
      ElMessage.error('订单不存在')
      setTimeout(() => router.back(), 1500)
    }
  } catch (error) {
    console.error('Failed to load order:', error)
    ElMessage.error('加载订单失败')
  } finally {
    loading.value = false
  }
}

const handleCancel = async (): Promise<void> => {
  if (!order.value || !userStore.currentUser) return

  try {
    await ElMessageBox.confirm('确定要取消这个订单吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })

    await orderAPI.cancelOrder(order.value.order_id, {
      user_id: userStore.currentUser.user_id
    })

    ElMessage.success('订单已取消')
    loadOrder()
  } catch (error: any) {
    if (error !== 'cancel') {
      console.error('Failed to cancel order:', error)
      ElMessage.error('取消订单失败')
    }
  }
}

const handlePay = async (): Promise<void> => {
  if (!order.value || !userStore.currentUser) return

  try {
    await orderAPI.updatePaymentStatus(order.value.order_id, {
      user_id: userStore.currentUser.user_id,
      payment_status: 'paid'
    })

    ElMessage.success('支付成功！')
    loadOrder()
  } catch (error) {
    console.error('Failed to pay order:', error)
    ElMessage.error('支付失败，请重试')
  }
}

const handleConfirm = async (): Promise<void> => {
  if (!order.value || !userStore.currentUser) return

  try {
    await ElMessageBox.confirm('确认已收到货物？', '提示', {
      confirmButtonText: '确认收货',
      cancelButtonText: '取消',
      type: 'info'
    })

    await orderAPI.updateOrderStatus(order.value.order_id, {
      user_id: userStore.currentUser.user_id,
      status: 'completed'
    })

    ElMessage.success('确认收货成功！')
    loadOrder()
  } catch (error: any) {
    if (error !== 'cancel') {
      console.error('Failed to confirm order:', error)
      ElMessage.error('确认收货失败')
    }
  }
}

const handleContact = (): void => {
  if (!order.value) return

  const targetUserId = isBuyer.value ? order.value.seller_id : order.value.buyer_id
  router.push(`/messages?user_id=${targetUserId}&item_id=${order.value.item_id}`)
}

onMounted(() => {
  if (!userStore.isLoggedIn) {
    router.push('/login')
    return
  }

  loadOrder()
})
</script>

<style scoped>
.order-detail-view {
  min-height: calc(100vh - 200px);
  background-color: #f5f5f5;
  padding: 20px;
}

.detail-container {
  max-width: 900px;
  margin: 0 auto;
}

.detail-container h1 {
  color: #303133;
  margin-bottom: 30px;
  text-align: center;
}

.loading,
.error {
  text-align: center;
  padding: 40px;
  background: white;
  border-radius: 8px;
}

.detail-content {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.section {
  background: white;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.section h3 {
  color: #303133;
  font-size: 16px;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid #f0f0f0;
}

/* 状态卡片 */
.status-section {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.status-card {
  display: flex;
  align-items: center;
  gap: 20px;
}

.status-icon {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 32px;
  background: rgba(255, 255, 255, 0.2);
}

.status-info h2 {
  color: white;
  margin-bottom: 8px;
}

.status-time {
  color: rgba(255, 255, 255, 0.9);
  font-size: 14px;
}

/* 时间线 */
.timeline-section {
  padding: 24px 40px;
}

.timeline {
  position: relative;
  padding-left: 30px;
}

.timeline::before {
  content: '';
  position: absolute;
  left: 8px;
  top: 0;
  bottom: 0;
  width: 2px;
  background: #e4e7ed;
}

.timeline-item {
  position: relative;
  padding-bottom: 30px;
}

.timeline-item:last-child {
  padding-bottom: 0;
}

.timeline-dot {
  position: absolute;
  left: -26px;
  top: 4px;
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background: #e4e7ed;
  border: 2px solid white;
  box-shadow: 0 0 0 2px #e4e7ed;
}

.timeline-item.active .timeline-dot {
  background: #409eff;
  box-shadow: 0 0 0 2px #409eff;
}

.timeline-title {
  color: #606266;
  font-size: 14px;
  margin-bottom: 4px;
}

.timeline-item.active .timeline-title {
  color: #303133;
  font-weight: 500;
}

.timeline-time {
  color: #909399;
  font-size: 12px;
}

/* 商品卡片 */
.item-card {
  display: flex;
  gap: 16px;
  padding: 16px;
  background: #fafafa;
  border-radius: 8px;
}

.item-image {
  width: 80px;
  height: 80px;
  object-fit: cover;
  border-radius: 8px;
}

.item-info h4 {
  color: #303133;
  margin-bottom: 8px;
}

.item-price {
  color: #f56c6c;
  font-size: 18px;
  font-weight: bold;
}

/* 信息列表 */
.info-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.info-item {
  display: flex;
  color: #606266;
  font-size: 14px;
}

.info-item .label {
  width: 100px;
  color: #909399;
}

.info-item .value {
  flex: 1;
  color: #303133;
}

/* 地址卡片 */
.address-card {
  padding: 16px;
  background: #fafafa;
  border-radius: 8px;
}

.address-header {
  display: flex;
  gap: 16px;
  margin-bottom: 8px;
  font-weight: 500;
}

.address-detail {
  color: #606266;
  font-size: 14px;
}

/* 费用明细 */
.summary-section {
  background: #fff9e6;
}

.summary-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.summary-item {
  display: flex;
  justify-content: space-between;
  font-size: 14px;
}

.summary-item.total {
  border-top: 2px solid #e6a23c;
  padding-top: 12px;
  margin-top: 8px;
  font-size: 18px;
  font-weight: bold;
  color: #f56c6c;
}

/* 操作按钮 */
.actions {
  display: flex;
  gap: 12px;
  justify-content: center;
  flex-wrap: wrap;
  padding: 20px 0;
}

.btn-primary,
.btn-secondary,
.btn-success,
.btn-danger {
  padding: 10px 24px;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.3s;
}

.btn-primary {
  background: #409eff;
  color: white;
}

.btn-primary:hover {
  background: #66b1ff;
}

.btn-secondary {
  background: #f5f5f5;
  color: #606266;
}

.btn-secondary:hover {
  background: #e0e0e0;
}

.btn-success {
  background: #67c23a;
  color: white;
}

.btn-success:hover {
  background: #85ce61;
}

.btn-danger {
  background: #f56c6c;
  color: white;
}

.btn-danger:hover {
  background: #f78989;
}

@media (max-width: 768px) {
  .detail-container {
    padding: 10px;
  }

  .section {
    padding: 16px;
  }

  .timeline-section {
    padding: 16px 24px;
  }

  .actions {
    flex-direction: column;
  }

  .actions button {
    width: 100%;
  }

  .item-card {
    flex-direction: column;
  }
}
</style>
