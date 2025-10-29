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
/* 现代扁平化风格 - Twitter/YouTube/Google 风格 */

.orders-view {
  max-width: var(--container-max-width);
  margin: 0 auto;
  padding: var(--spacing-6);
  background: var(--color-bg-page);
}

.orders-view h1 {
  color: var(--color-text-primary);
  margin-bottom: var(--spacing-8);
  font-size: var(--font-size-4xl);
  font-weight: var(--font-weight-bold);
}

/* 标签切换 - 扁平 */
.order-tabs {
  display: flex;
  gap: var(--spacing-2);
  margin-bottom: var(--spacing-8);
  justify-content: center;
}

.tab-btn {
  padding: var(--spacing-3) var(--spacing-5);
  border: 1px solid var(--color-border-base);
  background: var(--color-bg-card);
  color: var(--color-text-primary);
  border-radius: var(--radius-base);
  cursor: pointer;
  transition: all var(--transition-base);
  font-size: var(--font-size-base);
  font-weight: var(--font-weight-medium);
}

.tab-btn:hover {
  border-color: var(--color-primary-light);
  background: var(--color-bg-section);
}

.tab-btn.active {
  background: var(--color-primary);
  color: white;
  border-color: var(--color-primary);
}

/* 加载和空状态 */
.loading,
.no-orders {
  text-align: center;
  padding: var(--spacing-10);
  color: var(--color-text-secondary);
  font-size: var(--font-size-base);
}

/* 订单列表 */
.orders-list {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-4);
}

/* 订单卡片 - 扁平带边框 */
.order-card {
  background: var(--color-bg-card);
  border: 1px solid var(--color-border-base);
  border-radius: var(--radius-lg);
  overflow: hidden;
  transition: all var(--transition-base);
}

.order-card:hover {
  border-color: var(--color-border-light);
  box-shadow: var(--shadow-md);
}

/* 订单头部 */
.order-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--spacing-4) var(--spacing-4);
  background: var(--color-bg-section);
  border-bottom: 1px solid var(--color-border-light);
}

.order-info {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-1);
}

.order-number {
  font-weight: var(--font-weight-medium);
  color: var(--color-text-primary);
  font-size: var(--font-size-sm);
}

.order-date {
  font-size: var(--font-size-xs);
  color: var(--color-text-secondary);
}

/* 状态标签 - 扁平 */
.status-badge {
  padding: var(--spacing-1) var(--spacing-3);
  border-radius: var(--radius-full);
  font-size: var(--font-size-xs);
  font-weight: var(--font-weight-medium);
  border: 1px solid;
}

.status-badge.pending {
  background: var(--color-warning-light);
  color: #856404;
  border-color: #ffeaa7;
}

.status-badge.paid {
  background: var(--color-info-light);
  color: #0c5460;
  border-color: #bee5eb;
}

.status-badge.shipped {
  background: var(--color-success-light);
  color: #155724;
  border-color: #c3e6cb;
}

.status-badge.completed {
  background: var(--color-primary-lighter);
  color: var(--color-primary-dark);
  border-color: var(--color-primary-light);
}

.status-badge.cancelled {
  background: var(--color-danger-light);
  color: #721c24;
  border-color: #f5c6cb;
}

/* 订单内容 */
.order-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--spacing-4);
  gap: var(--spacing-4);
}

.item-info {
  display: flex;
  gap: var(--spacing-4);
  flex: 1;
  align-items: center;
}

.item-image {
  width: 80px;
  height: 80px;
  object-fit: cover;
  border-radius: var(--radius-base);
  border: 1px solid var(--color-border-base);
  background: var(--color-neutral-100);
  flex-shrink: 0;
}

.item-details {
  flex: 1;
  min-width: 0;
}

.item-details h3 {
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
  font-size: var(--font-size-xl);
  margin: 0 0 var(--spacing-1) 0;
}

.payment-method {
  color: var(--color-text-secondary);
  font-size: var(--font-size-xs);
  margin: 0;
}

/* 操作按钮 - 扁平 */
.order-actions {
  display: flex;
  gap: var(--spacing-2);
  flex-wrap: wrap;
  flex-shrink: 0;
}

.action-btn {
  padding: var(--spacing-2) var(--spacing-3);
  border: none;
  border-radius: var(--radius-base);
  font-size: var(--font-size-xs);
  font-weight: var(--font-weight-medium);
  cursor: pointer;
  transition: all var(--transition-base);
  white-space: nowrap;
}

.cancel-btn {
  background: var(--color-neutral-500);
  color: white;
}

.cancel-btn:hover {
  background: var(--color-neutral-600);
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

/* 分页 */
.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: var(--spacing-4);
  margin-top: var(--spacing-8);
}

.page-btn {
  padding: var(--spacing-2) var(--spacing-4);
  background-color: var(--color-primary);
  color: white;
  border: none;
  border-radius: var(--radius-base);
  cursor: pointer;
  transition: all var(--transition-base);
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-medium);
}

.page-btn:hover:not(:disabled) {
  background-color: var(--color-primary-dark);
}

.page-btn:disabled {
  background-color: var(--color-neutral-400);
  cursor: not-allowed;
}

.page-info {
  color: var(--color-text-secondary);
  font-weight: var(--font-weight-medium);
  font-size: var(--font-size-sm);
}

/* 响应式 */
@media (max-width: 768px) {
  .orders-view {
    padding: var(--spacing-4);
  }

  .orders-view h1 {
    font-size: var(--font-size-3xl);
    margin-bottom: var(--spacing-6);
  }

  .order-header {
    flex-direction: column;
    gap: var(--spacing-2);
    align-items: flex-start;
  }

  .order-content {
    flex-direction: column;
    gap: var(--spacing-4);
    align-items: stretch;
  }

  .item-info {
    flex-direction: row;
    align-items: center;
  }

  .order-actions {
    width: 100%;
    justify-content: stretch;
  }

  .action-btn {
    flex: 1;
  }
}
</style>
