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
              <p class="status-time">{{ formatDate(order.create_time) }}</p>
            </div>
          </div>
        </div>

        <!-- 订单进度 -->
        <div class="section timeline-section">
          <h3>订单进度</h3>
          <div class="timeline">
            <div :class="['timeline-item', { active: isStatusActive('pending_payment') }]">
              <div class="timeline-dot"></div>
              <div class="timeline-content">
                <div class="timeline-title">订单创建</div>
                <div class="timeline-time">{{ formatDate(order.create_time) }}</div>
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
              :src="order.item_images?.[0] || '/placeholder.png'"
              :alt="order.item_title"
              class="item-image"
            />
            <div class="item-info">
              <h4>{{ order.item_title }}</h4>
              <p class="item-price">¥{{ order.total_amount }}</p>
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
              <span class="value">{{ formatDate(order.create_time) }}</span>
            </div>
            <div class="info-item">
              <span class="label">支付方式：</span>
              <span class="value">{{ getPaymentMethodText(order.payment_method) }}</span>
            </div>
            <div class="info-item">
              <span class="label">配送方式：</span>
              <span class="value">{{ getDeliveryMethodText(order.delivery_method) }}</span>
            </div>
            <div v-if="order.notes" class="info-item">
              <span class="label">订单备注：</span>
              <span class="value">{{ order.notes }}</span>
            </div>
          </div>
        </div>

        <!-- 收货地址 -->
        <div v-if="order.address" class="section">
          <h3>收货地址</h3>
          <div class="address-card">
            <div class="address-header">
              <span class="recipient">{{ order.address.recipient_name }}</span>
              <span class="phone">{{ order.address.phone }}</span>
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
              <span class="value">{{ order.seller_name }}</span>
            </div>
            <div class="info-item">
              <span class="label">买家：</span>
              <span class="value">{{ order.buyer_name }}</span>
            </div>
          </div>
        </div>

        <!-- 费用明细 -->
        <div class="section summary-section">
          <h3>费用明细</h3>
          <div class="summary-list">
            <div class="summary-item">
              <span>商品金额：</span>
              <span>¥{{ order.total_amount }}</span>
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
import type { Order, OrderStatus } from '@/types'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()

type OrderDetail = Order & {
  address?: {
    recipient_name: string
    phone: string
    province: string
    city: string
    district: string
    detailed_address: string
    postal_code?: string | null
  }
}

const order = ref<OrderDetail | null>(null)
const loading = ref(false)

const isBuyer = computed(() => {
  return Boolean(order.value && userStore.currentUser && order.value.buyer_id === userStore.currentUser.user_id)
})

const canCancel = computed(() => order.value?.order_status === 'pending_payment')

const canPay = computed(() => isBuyer.value && order.value?.order_status === 'pending_payment')

const canConfirm = computed(() => isBuyer.value && order.value?.order_status === 'shipped')

const canContact = computed(() => {
  if (!order.value) return false
  return ['pending_payment', 'paid', 'shipped'].includes(order.value.order_status)
})

const statusMap: Record<OrderStatus, string> = {
  pending_payment: '待支付',
  paid: '已支付',
  shipped: '已发货',
  completed: '已完成',
  cancelled: '已取消'
}

const paymentMethodMap: Record<string, string> = {
  alipay: '支付宝',
  wechat: '微信支付',
  cash: '线下支付'
}

const deliveryMethodMap: Record<string, string> = {
  meet: '当面交易',
  express: '快递配送'
}

const getStatusText = (status: OrderStatus): string => statusMap[status] || status

const getPaymentMethodText = (method: string): string => paymentMethodMap[method] || method

const getDeliveryMethodText = (method: string): string => deliveryMethodMap[method] || method

const getStatusClass = (status: OrderStatus): string => {
  const classMap: Record<OrderStatus, string> = {
    pending_payment: 'pending',
    paid: 'paid',
    shipped: 'shipped',
    completed: 'completed',
    cancelled: 'cancelled'
  }
  return classMap[status] || 'default'
}

const getStatusIcon = (status: OrderStatus): string => {
  const iconMap: Record<OrderStatus, string> = {
    pending_payment: '⏰',
    paid: '💰',
    shipped: '🚚',
    completed: '✅',
    cancelled: '❌'
  }
  return iconMap[status] || '📦'
}

const isStatusActive = (status: OrderStatus): boolean => {
  if (!order.value) return false
  const statusOrder: OrderStatus[] = ['pending_payment', 'paid', 'shipped', 'completed']
  const currentIndex = statusOrder.indexOf(order.value.order_status)
  const targetIndex = statusOrder.indexOf(status)
  if (currentIndex === -1 || targetIndex === -1) return false
  return currentIndex >= targetIndex
}

const formatDate = (dateString?: string | null): string => {
  if (!dateString) return '-'
  return new Date(dateString).toLocaleString('zh-CN')
}

const normaliseImages = (images: unknown): string[] => {
  if (Array.isArray(images)) return images as string[]
  if (typeof images === 'string') {
    try {
      const parsed = JSON.parse(images)
      return Array.isArray(parsed) ? parsed : []
    } catch {
      return []
    }
  }
  return []
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
    const raw = response.order as any

    if (!raw) {
      ElMessage.error('订单不存在')
      setTimeout(() => router.back(), 1500)
      return
    }

    const detail: OrderDetail = {
      ...raw,
      item_images: normaliseImages(raw.item_images),
      buyer_name: raw.buyer_name ?? raw.buyer_username ?? raw.buyer_name,
      seller_name: raw.seller_name ?? raw.seller_username ?? raw.seller_name,
      address: raw.recipient_name
        ? {
            recipient_name: raw.recipient_name,
            phone: raw.address_phone ?? raw.phone,
            province: raw.province,
            city: raw.city,
            district: raw.district,
            detailed_address: raw.detailed_address,
            postal_code: raw.postal_code ?? null
          }
        : undefined
    }

    order.value = detail
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
/* 现代扁平化风格 - Twitter/YouTube/Google 风格 */

.order-detail-view {
  min-height: calc(100vh - 200px);
  background-color: var(--color-bg-page);
  padding: var(--spacing-6) var(--spacing-8);
}

.detail-container {
  max-width: 1400px;
  margin: 0 auto;
}

.detail-container h1 {
  color: var(--color-text-primary);
  margin-bottom: var(--spacing-8);
  text-align: center;
  font-size: var(--font-size-3xl);
  font-weight: var(--font-weight-bold);
}

.loading,
.error {
  text-align: center;
  padding: var(--spacing-5xl);
  background: var(--color-bg-card);
  border: 1px solid var(--color-border-base);
  border-radius: var(--radius-lg);
  color: var(--color-text-secondary);
}

.detail-content {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-5);
}

/* 卡片 - 扁平带边框 */
.section {
  background: var(--color-bg-card);
  border: 1px solid var(--color-border-base);
  border-radius: var(--radius-lg);
  padding: var(--spacing-6);
  box-shadow: var(--shadow-sm);
}

.section h3 {
  color: var(--color-text-primary);
  font-size: var(--font-size-xl);
  font-weight: var(--font-weight-semibold);
  margin-bottom: var(--spacing-4);
  padding-bottom: var(--spacing-3);
  border-bottom: 1px solid var(--color-border-light);
}

/* 状态卡片 - 扁平带边框 */
.status-section {
  background: var(--color-bg-card);
  border: 1px solid var(--color-border-base);
  border-radius: var(--radius-lg);
  padding: var(--spacing-6);
  box-shadow: var(--shadow-sm);
}

.status-card {
  display: flex;
  align-items: center;
  gap: var(--spacing-5);
}

.status-icon {
  width: 64px;
  height: 64px;
  border-radius: var(--radius-round);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: var(--font-size-4xl);
  background: var(--color-bg-section);
  border: 2px solid var(--color-border-base);
  flex-shrink: 0;
}

.status-icon.pending {
  background: var(--color-warning-lighter);
  border-color: var(--color-warning-light);
}

.status-icon.paid {
  background: var(--color-primary-lighter);
  border-color: var(--color-primary-light);
}

.status-icon.shipped {
  background: var(--color-info-light);
  border-color: var(--color-info);
}

.status-icon.completed {
  background: var(--color-success-light);
  border-color: var(--color-success);
}

.status-icon.cancelled {
  background: var(--color-danger-light);
  border-color: var(--color-danger);
}

.status-info h2 {
  color: var(--color-text-primary);
  margin-bottom: var(--spacing-2);
  font-size: var(--font-size-2xl);
  font-weight: var(--font-weight-bold);
}

.status-time {
  color: var(--color-text-secondary);
  font-size: var(--font-size-sm);
}

/* 时间线 - 扁平 */
.timeline-section {
  padding: var(--spacing-6);
}

.timeline {
  position: relative;
  padding-left: var(--spacing-8);
}

.timeline::before {
  content: '';
  position: absolute;
  left: 8px;
  top: 0;
  bottom: 0;
  width: 2px;
  background: var(--color-border-base);
}

.timeline-item {
  position: relative;
  padding-bottom: var(--spacing-8);
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
  border-radius: var(--radius-round);
  background: var(--color-border-base);
  border: 2px solid var(--color-bg-card);
  box-shadow: 0 0 0 2px var(--color-border-base);
}

.timeline-item.active .timeline-dot {
  background: var(--color-primary);
  box-shadow: 0 0 0 2px var(--color-primary);
}

.timeline-title {
  color: var(--color-text-regular);
  font-size: var(--font-size-sm);
  margin-bottom: var(--spacing-1);
}

.timeline-item.active .timeline-title {
  color: var(--color-text-primary);
  font-weight: var(--font-weight-medium);
}

.timeline-time {
  color: var(--color-text-secondary);
  font-size: var(--font-size-xs);
}

/* 商品卡片 - 扁平带边框 */
.item-card {
  display: flex;
  gap: var(--spacing-4);
  padding: var(--spacing-4);
  background: var(--color-bg-section);
  border: 1px solid var(--color-border-light);
  border-radius: var(--radius-lg);
}

.item-image {
  width: 80px;
  height: 80px;
  object-fit: cover;
  border-radius: var(--radius-base);
  border: 1px solid var(--color-border-light);
  flex-shrink: 0;
}

.item-info h4 {
  color: var(--color-text-primary);
  margin-bottom: var(--spacing-2);
  font-size: var(--font-size-base);
  font-weight: var(--font-weight-medium);
}

.item-price {
  color: var(--color-price);
  font-size: var(--font-size-xl);
  font-weight: var(--font-weight-bold);
}

/* 信息列表 */
.info-list {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-3);
}

.info-item {
  display: flex;
  color: var(--color-text-regular);
  font-size: var(--font-size-sm);
}

.info-item .label {
  width: 100px;
  color: var(--color-text-secondary);
  flex-shrink: 0;
}

.info-item .value {
  flex: 1;
  color: var(--color-text-primary);
}

/* 地址卡片 - 扁平带边框 */
.address-card {
  padding: var(--spacing-4);
  background: var(--color-bg-section);
  border: 1px solid var(--color-border-light);
  border-radius: var(--radius-lg);
}

.address-header {
  display: flex;
  gap: var(--spacing-4);
  margin-bottom: var(--spacing-2);
  font-weight: var(--font-weight-medium);
  color: var(--color-text-primary);
}

.address-detail {
  color: var(--color-text-regular);
  font-size: var(--font-size-sm);
}

/* 费用明细 - 扁平带边框 */
.summary-section {
  background: var(--color-warning-lighter);
  border-color: var(--color-warning-light);
}

.summary-list {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-3);
}

.summary-item {
  display: flex;
  justify-content: space-between;
  font-size: var(--font-size-sm);
  color: var(--color-text-regular);
}

.summary-item.total {
  border-top: 2px solid var(--color-warning);
  padding-top: var(--spacing-3);
  margin-top: var(--spacing-2);
  font-size: var(--font-size-xl);
  font-weight: var(--font-weight-bold);
  color: var(--color-price);
}

/* 操作按钮 - 扁平 */
.actions {
  display: flex;
  gap: var(--spacing-3);
  justify-content: center;
  flex-wrap: wrap;
  padding: var(--spacing-5) 0;
}

.btn-primary,
.btn-secondary,
.btn-success,
.btn-danger {
  padding: var(--spacing-3) var(--spacing-6);
  border: 1px solid;
  border-radius: var(--radius-base);
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-medium);
  cursor: pointer;
  transition: all var(--transition-base);
}

.btn-primary {
  background: var(--color-primary);
  border-color: var(--color-primary);
  color: white;
}

.btn-primary:hover {
  background: var(--color-primary-dark);
  border-color: var(--color-primary-dark);
}

.btn-secondary {
  background: var(--color-bg-section);
  border-color: var(--color-border-base);
  color: var(--color-text-regular);
}

.btn-secondary:hover {
  background: var(--color-bg-hover);
  border-color: var(--color-border-light);
}

.btn-success {
  background: var(--color-success);
  border-color: var(--color-success);
  color: white;
}

.btn-success:hover {
  background: #5daf34;
  border-color: #5daf34;
}

.btn-danger {
  background: var(--color-danger);
  border-color: var(--color-danger);
  color: white;
}

.btn-danger:hover {
  background: #f35151;
  border-color: #f35151;
}

/* 响应式 */
@media (max-width: 768px) {
  .order-detail-view {
    padding: var(--spacing-4);
  }

  .detail-container {
    padding: 0;
  }

  .section {
    padding: var(--spacing-4);
  }

  .timeline-section {
    padding: var(--spacing-4);
  }

  .actions {
    flex-direction: column;
    padding: var(--spacing-4) 0;
  }

  .actions button {
    width: 100%;
  }

  .item-card {
    flex-direction: column;
  }

  .item-image {
    width: 100%;
    height: 200px;
  }
}
</style>
