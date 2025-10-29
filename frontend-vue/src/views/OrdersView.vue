<template>
  <v-container class="orders-view">
    <h1 class="text-h3 font-weight-bold mb-6">我的订单</h1>

    <!-- Tab切换 -->
    <v-tabs v-model="activeTab" color="primary" class="mb-6">
      <v-tab value="buyer">
        <v-icon class="mr-2">mdi-cart</v-icon>
        我买到的
      </v-tab>
      <v-tab value="seller">
        <v-icon class="mr-2">mdi-store</v-icon>
        我卖出的
      </v-tab>
    </v-tabs>

    <!-- 加载状态 -->
    <v-progress-linear v-if="loading" indeterminate color="primary" class="mb-4"></v-progress-linear>

    <!-- 空状态 -->
    <EmptyState
      v-else-if="orders.length === 0"
      icon="mdi-package-variant"
      description="暂无订单"
      action-text="去逛逛"
      @action="router.push('/items')"
    />

    <!-- 订单列表 -->
    <v-row v-else>
      <v-col v-for="order in orders" :key="order.order_id" cols="12">
        <v-card elevation="2" class="order-card">
          <!-- 订单头部 -->
          <v-card-title class="d-flex justify-space-between align-center bg-grey-lighten-4">
            <div>
              <span class="text-body-2">订单号：{{ order.order_number }}</span>
              <span class="text-caption text-grey ml-4">{{ formatDate(order.create_time) }}</span>
            </div>
            <v-chip
              :color="getStatusColor(order.order_status)"
              size="small"
            >
              {{ getStatusText(order.order_status) }}
            </v-chip>
          </v-card-title>

          <v-divider></v-divider>

          <!-- 订单内容 -->
          <v-card-text>
            <v-row align="center">
              <v-col cols="12" md="6">
                <div class="d-flex ga-4">
                  <v-img
                    :src="order.item_images && order.item_images[0] ? order.item_images[0] : '/placeholder.png'"
                    :alt="order.item_title"
                    width="100"
                    height="100"
                    cover
                    class="rounded"
                  ></v-img>
                  <div>
                    <h3 class="text-h6 mb-2">{{ order.item_title }}</h3>
                    <div class="text-h6 text-error font-weight-bold">¥{{ order.total_amount }}</div>
                    <div class="text-body-2 text-grey">{{ getPaymentMethodText(order.payment_method) }}</div>
                  </div>
                </div>
              </v-col>

              <v-col cols="12" md="6" class="d-flex justify-end ga-2 flex-wrap">
                <v-btn
                  v-if="canCancel(order)"
                  variant="outlined"
                  color="error"
                  @click="cancelOrder(order.order_id)"
                >
                  取消订单
                </v-btn>

                <v-btn
                  v-if="canPay(order)"
                  color="success"
                  @click="payOrder(order.order_id)"
                >
                  立即支付
                </v-btn>

                <v-btn
                  v-if="canConfirm(order)"
                  color="primary"
                  @click="confirmOrder(order.order_id)"
                >
                  确认收货
                </v-btn>

                <v-btn
                  variant="outlined"
                  @click="viewOrderDetail(order.order_id)"
                >
                  查看详情
                </v-btn>
              </v-col>
            </v-row>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- 分页 -->
    <div v-if="orders.length > 0" class="d-flex justify-center mt-6">
      <v-pagination
        v-model="page"
        :length="totalPages"
        @update:model-value="loadOrders"
        rounded="circle"
      ></v-pagination>
    </div>
  </v-container>
</template>

<script setup lang="ts">
import { ref, watch, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { useNotification } from '@/composables/useNotification'
import { orderAPI } from '@/api'
import EmptyState from '@/components/EmptyState.vue'
import type { Order } from '@/types'

const router = useRouter()
const userStore = useUserStore()
const notification = useNotification()

const orders = ref<Order[]>([])
const loading = ref(false)
const activeTab = ref<'buyer' | 'seller'>('buyer')
const page = ref(1)
const limit = ref(10)
const totalPages = ref(1)

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

const getStatusColor = (status: string): string => {
  const colorMap: Record<string, string> = {
    'pending_payment': 'warning',
    'paid': 'info',
    'shipped': 'primary',
    'completed': 'success',
    'cancelled': 'error'
  }
  return colorMap[status] || 'grey'
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

    totalPages.value = response.pagination?.pages || 1
  } catch (error) {
    console.error('Failed to load orders:', error)
    notification.error('加载订单失败')
  } finally {
    loading.value = false
  }
}

const cancelOrder = async (orderId: number): Promise<void> => {
  if (!userStore.currentUser) return

  try {
    await orderAPI.cancelOrder(orderId, {
      user_id: userStore.currentUser.user_id
    })

    notification.success('订单已取消')
    loadOrders(page.value)
  } catch (error) {
    console.error('Failed to cancel order:', error)
    notification.error('取消订单失败')
  }
}

const payOrder = async (orderId: number): Promise<void> => {
  if (!userStore.currentUser) return

  try {
    await orderAPI.updatePaymentStatus(orderId, {
      user_id: userStore.currentUser.user_id,
      payment_status: 'paid'
    })

    notification.success('支付成功！')
    loadOrders(page.value)
  } catch (error) {
    console.error('Failed to pay order:', error)
    notification.error('支付失败')
  }
}

const confirmOrder = async (orderId: number): Promise<void> => {
  if (!userStore.currentUser) return

  try {
    await orderAPI.updateOrderStatus(orderId, {
      user_id: userStore.currentUser.user_id,
      status: 'completed'
    })

    notification.success('确认收货成功！')
    loadOrders(page.value)
  } catch (error) {
    console.error('Failed to confirm order:', error)
    notification.error('确认收货失败')
  }
}

const viewOrderDetail = (orderId: number): void => {
  router.push(`/orders/${orderId}`)
}

// 监听tab切换
watch(activeTab, () => {
  page.value = 1
  loadOrders()
})

onMounted(() => {
  loadOrders()
})
</script>

<style scoped>
.orders-view {
  max-width: 1400px;
}

.order-card {
  transition: all 0.3s;
}

.order-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15) !important;
}
</style>
