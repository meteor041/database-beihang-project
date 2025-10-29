<template>
  <div class="orders-view">
    <h1>我的订单</h1>
    
    <div class="order-tabs">
      <button 
        v-for="tab in tabs"
        :key="tab.key"
        :class="['tab-btn', { active: activeTab === tab.key }]"
        @click="switchTab(tab.key)"
      >
        {{ tab.label }}
      </button>
    </div>

    <div v-if="loading" class="loading">
      加载中...
    </div>

    <div v-else-if="orders.length === 0" class="no-orders">
      暂无订单
    </div>

    <div v-else class="orders-list">
      <div 
        v-for="order in orders"
        :key="order.order_id"
        class="order-card"
      >
        <div class="order-header">
          <div class="order-info">
            <span class="order-number">订单号：{{ order.order_number }}</span>
            <span class="order-date">{{ formatDate(order.create_time) }}</span>
          </div>
          <div class="order-status">
            <span :class="['status-badge', getStatusClass(order.order_status)]">
              {{ getStatusText(order.order_status) }}
            </span>
          </div>
        </div>

        <div class="order-content">
          <div class="item-info">
            <img 
              :src="order.item_images && order.item_images[0] ? order.item_images[0] : '/placeholder.png'"
              :alt="order.item_title"
              class="item-image"
            />
            <div class="item-details">
              <h3>{{ order.item_title }}</h3>
              <p class="item-price">¥{{ order.total_amount }}</p>
              <p class="payment-method">{{ getPaymentMethodText(order.payment_method) }}</p>
            </div>
          </div>

          <div class="order-actions">
            <button 
              v-if="canCancel(order)"
              @click="cancelOrder(order.order_id)"
              class="action-btn cancel-btn"
            >
              取消订单
            </button>
            
            <button 
              v-if="canPay(order)"
              @click="payOrder(order.order_id)"
              class="action-btn pay-btn"
            >
              立即支付
            </button>
            
            <button 
              v-if="canConfirm(order)"
              @click="confirmOrder(order.order_id)"
              class="action-btn confirm-btn"
            >
              确认收货
            </button>
            
            <button 
              @click="viewOrderDetail(order.order_id)"
              class="action-btn detail-btn"
            >
              查看详情
            </button>
          </div>
        </div>
      </div>
    </div>

    <div v-if="orders.length > 0" class="pagination">
      <button 
        @click="loadOrders(page - 1)"
        :disabled="page <= 1"
        class="page-btn"
      >
        上一页
      </button>
      
      <span class="page-info">第 {{ page }} 页</span>
      
      <button 
        @click="loadOrders(page + 1)"
        :disabled="orders.length < limit"
        class="page-btn"
      >
        下一页
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { orderAPI } from '@/api'
import type { Order } from '@/types'

const router = useRouter()
const userStore = useUserStore()

const orders = ref<Order[]>([])
const loading = ref(false)
const activeTab = ref<'buyer' | 'seller'>('buyer')
const page = ref(1)
const limit = ref(10)

const tabs = [
  { key: 'buyer' as const, label: '我买到的' },
  { key: 'seller' as const, label: '我卖出的' }
]

const statusMap: Record<string, string> = {
  'pending_payment': '待支付',
  'paid': '已支付',
  'shipped': '已发货',
  'completed': '已完成',
  'cancelled': '已取消'
}

const paymentMethodMap: Record<string, string> = {
  'alipay': '支付宝',
  'wechat': '微信支付',
  'cash': '现金支付'
}

const getStatusText = (status: string): string => {
  return statusMap[status] || status
}

const getStatusClass = (status: string): string => {
  const classMap: Record<string, string> = {
    'pending_payment': 'pending',
    'paid': 'paid',
    'shipped': 'shipped',
    'completed': 'completed',
    'cancelled': 'cancelled'
  }
  return classMap[status] || 'default'
}

const getPaymentMethodText = (method: string): string => {
  return paymentMethodMap[method] || method
}

const formatDate = (dateString?: string | null): string => {
  if (!dateString) return '-'
  return new Date(dateString).toLocaleString('zh-CN')
}

const canCancel = (order: Order): boolean => {
  return order.order_status === 'pending_payment'
}

const canPay = (order: Order): boolean => {
  return order.order_status === 'pending_payment' && activeTab.value === 'buyer'
}

const canConfirm = (order: Order): boolean => {
  return order.order_status === 'shipped' && activeTab.value === 'buyer'
}

const loadOrders = async (newPage = 1): Promise<void> => {
  if (!userStore.isLoggedIn || !userStore.currentUser) {
    router.push('/login')
    return
  }

  loading.value = true
  page.value = newPage

  try {
    const response = await orderAPI.getUserOrders(userStore.currentUser.user_id, {
      role: activeTab.value,
      page: page.value,
      limit: limit.value
    })

    orders.value = (response.orders || []).map((order) => ({
      ...order,
      item_images: Array.isArray(order.item_images)
        ? order.item_images
        : order.item_images
          ? (() => {
              try {
                return JSON.parse(order.item_images as unknown as string)
              } catch {
                return []
              }
            })()
          : []
    }))
  } catch (error) {
    console.error('Failed to load orders:', error)
  } finally {
    loading.value = false
  }
}

const switchTab = (tab: 'buyer' | 'seller'): void => {
  activeTab.value = tab
  page.value = 1
  loadOrders()
}

const cancelOrder = async (orderId: number): Promise<void> => {
  if (!confirm('确定要取消这个订单吗?') || !userStore.currentUser) {
    return
  }

  try {
    await orderAPI.cancelOrder(orderId, {
      user_id: userStore.currentUser.user_id
    })

    loadOrders(page.value)
  } catch (error) {
    console.error('Failed to cancel order:', error)
    alert('取消订单失败，请重试')
  }
}

const payOrder = async (orderId: number): Promise<void> => {
  if (!userStore.currentUser) return

  try {
    await orderAPI.updatePaymentStatus(orderId, {
      user_id: userStore.currentUser.user_id,
      payment_status: 'paid'
    })

    loadOrders(page.value)
    alert('支付成功！')
  } catch (error) {
    console.error('Failed to pay order:', error)
    alert('支付失败，请重试')
  }
}

const confirmOrder = async (orderId: number) => {
  if (!confirm('确定已收到商品吗？') || !userStore.currentUser) {
    return
  }

  try {
    await orderAPI.updateOrderStatus(orderId, {
      user_id: userStore.currentUser.user_id,
      status: 'completed'
    })
    
    // 重新加载订单列表
    loadOrders(page.value)
    alert('确认收货成功！')
  } catch (error) {
    console.error('Failed to confirm order:', error)
    alert('确认收货失败，请重试')
  }
}

const viewOrderDetail = (orderId: number) => {
  router.push(`/orders/${orderId}`)
}

onMounted(() => {
  loadOrders()
})
</script>

<style scoped>
/* 使用设计系统变量 */
.orders-view {
  max-width: 1600px;
  margin: 0 auto;
  padding: var(--spacing-2xl) var(--spacing-3xl);
}

.orders-view h1 {
  color: var(--color-text-primary);
  margin-bottom: var(--spacing-2xl);
  text-align: center;
}

.order-tabs {
  display: flex;
  gap: var(--spacing-sm);
  margin-bottom: var(--spacing-2xl);
  justify-content: center;
}

.tab-btn {
  padding: var(--spacing-sm) var(--spacing-lg);
  border: 1px solid var(--color-border-base);
  background: var(--color-bg-card);
  color: var(--color-text-secondary);
  border-radius: var(--radius-base);
  cursor: pointer;
  transition: all var(--transition-base);
}

.tab-btn:hover {
  background: var(--color-bg-page);
}

.tab-btn.active {
  background: var(--color-primary);
  color: white;
  border-color: var(--color-primary);
}

.loading {
  text-align: center;
  padding: var(--spacing-3xl);
  color: var(--color-text-secondary);
  font-size: var(--font-size-xl);
}

.no-orders {
  text-align: center;
  padding: var(--spacing-3xl);
  color: var(--color-text-secondary);
  font-size: var(--font-size-xl);
}

.orders-list {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-lg);
}

.order-card {
  background: var(--color-bg-card);
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-base);
  overflow: hidden;
}

.order-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--spacing-lg) var(--spacing-lg);
  background: var(--color-bg-page);
  border-bottom: 1px solid var(--color-border-lighter);
}

.order-info {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-xs);
}

.order-number {
  font-weight: var(--font-weight-medium);
  color: var(--color-text-primary);
}

.order-date {
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
}

.status-badge {
  padding: var(--spacing-xs) var(--spacing-md);
  border-radius: var(--radius-lg);
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-medium);
}

.status-badge.pending {
  background: var(--color-warning-light);
  color: #856404;
}

.status-badge.paid {
  background: var(--color-info-light);
  color: #0c5460;
}

.status-badge.shipped {
  background: var(--color-success-light);
  color: #155724;
}

.status-badge.completed {
  background: var(--color-info-light);
  color: #0c5460;
}

.status-badge.cancelled {
  background: var(--color-danger-light);
  color: #721c24;
}

.order-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--spacing-lg);
}

.item-info {
  display: flex;
  gap: var(--spacing-lg);
  flex: 1;
}

.item-image {
  width: 80px;
  height: 80px;
  object-fit: cover;
  border-radius: var(--radius-base);
}

.item-details h3 {
  color: var(--color-text-primary);
  margin: 0 0 var(--spacing-sm) 0;
  font-size: var(--font-size-xl);
}

.item-price {
  color: var(--color-price);
  font-weight: var(--font-weight-semibold);
  font-size: var(--font-size-2xl);
  margin: 0 0 var(--spacing-xs) 0;
}

.payment-method {
  color: var(--color-text-secondary);
  font-size: var(--font-size-sm);
  margin: 0;
}

.order-actions {
  display: flex;
  gap: var(--spacing-sm);
  flex-wrap: wrap;
}

.action-btn {
  padding: var(--spacing-sm) var(--spacing-base);
  border: none;
  border-radius: var(--radius-sm);
  font-size: var(--font-size-base);
  cursor: pointer;
  transition: all var(--transition-base);
}

.cancel-btn {
  background: var(--color-info);
  color: white;
}

.cancel-btn:hover {
  background: #5a6268;
}

.pay-btn {
  background: var(--color-price);
  color: white;
}

.pay-btn:hover {
  background: #c82333;
}

.confirm-btn {
  background: var(--color-success);
  color: white;
}

.confirm-btn:hover {
  background: #218838;
}

.detail-btn {
  background: var(--color-primary);
  color: white;
}

.detail-btn:hover {
  background: var(--color-primary-dark);
}

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: var(--spacing-lg);
  margin-top: var(--spacing-3xl);
}

.page-btn {
  padding: var(--spacing-sm) var(--spacing-base);
  background-color: var(--color-primary);
  color: white;
  border: none;
  border-radius: var(--radius-sm);
  cursor: pointer;
  transition: background-color var(--transition-fast);
}

.page-btn:hover:not(:disabled) {
  background-color: var(--color-primary-dark);
}

.page-btn:disabled {
  background-color: var(--color-info);
  cursor: not-allowed;
}

.page-info {
  color: var(--color-text-secondary);
  font-weight: var(--font-weight-medium);
}

@media (max-width: 768px) {
  .order-header {
    flex-direction: column;
    gap: var(--spacing-sm);
    align-items: flex-start;
  }

  .order-content {
    flex-direction: column;
    gap: var(--spacing-lg);
    align-items: stretch;
  }

  .item-info {
    flex-direction: column;
    text-align: center;
  }

  .order-actions {
    justify-content: center;
  }

  .action-btn {
    flex: 1;
    min-width: 80px;
  }
}
</style>
