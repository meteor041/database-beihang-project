<template>
  <v-container class="order-detail-view">
    <h1 class="text-h3 font-weight-bold mb-6">订单详情</h1>

    <v-progress-linear v-if="loading" indeterminate></v-progress-linear>

    <EmptyState
      v-else-if="!order"
      icon="mdi-package-variant-closed"
      description="订单不存在"
      action-text="返回订单列表"
      @action="router.push('/orders')"
    />

    <div v-else>
      <v-row>
        <v-col cols="12" md="8">
          <!-- 订单状态 -->
          <v-card class="mb-4">
            <v-card-title class="bg-grey-lighten-4">
              <v-icon class="mr-2">mdi-timeline</v-icon>
              订单状态
            </v-card-title>
            <v-card-text>
              <OrderStatus :status="order.order_status" />
            </v-card-text>
          </v-card>

          <!-- 商品信息 -->
          <v-card class="mb-4">
            <v-card-title class="bg-grey-lighten-4">商品信息</v-card-title>
            <v-card-text class="d-flex ga-4">
              <v-img
                :src="order.item_images?.[0] || '/placeholder.png'"
                width="120"
                height="120"
                cover
              ></v-img>
              <div class="flex-grow-1">
                <h3 class="text-h6 mb-2">{{ order.item_title }}</h3>
                <div class="text-h5 text-error font-weight-bold">¥{{ order.total_amount }}</div>
                <v-chip size="small" color="primary" class="mt-2">
                  {{ order.payment_method }}
                </v-chip>
              </div>
            </v-card-text>
          </v-card>

          <!-- 收货信息 -->
          <v-card>
            <v-card-title class="bg-grey-lighten-4">收货信息</v-card-title>
            <v-list>
              <v-list-item>
                <template v-slot:prepend>
                  <v-icon>mdi-map-marker</v-icon>
                </template>
                <v-list-item-title>地址</v-list-item-title>
                <v-list-item-subtitle>{{ order.shipping_address }}</v-list-item-subtitle>
              </v-list-item>
              <v-list-item>
                <template v-slot:prepend>
                  <v-icon>mdi-phone</v-icon>
                </template>
                <v-list-item-title>电话</v-list-item-title>
                <v-list-item-subtitle>{{ order.receiver_phone }}</v-list-item-subtitle>
              </v-list-item>
            </v-list>
          </v-card>
        </v-col>

        <v-col cols="12" md="4">
          <v-card>
            <v-card-title class="bg-grey-lighten-4">订单信息</v-card-title>
            <v-list density="compact">
              <v-list-item>
                <v-list-item-title>订单号</v-list-item-title>
                <v-list-item-subtitle>{{ order.order_number }}</v-list-item-subtitle>
              </v-list-item>
              <v-list-item>
                <v-list-item-title>创建时间</v-list-item-title>
                <v-list-item-subtitle>{{ formatDate(order.create_time) }}</v-list-item-subtitle>
              </v-list-item>
              <v-list-item>
                <v-list-item-title>订单状态</v-list-item-title>
                <template v-slot:append>
                  <v-chip :color="getStatusColor(order.order_status)" size="small">
                    {{ getStatusText(order.order_status) }}
                  </v-chip>
                </template>
              </v-list-item>
            </v-list>
          </v-card>

          <div class="d-flex flex-column ga-2 mt-4">
            <v-btn
              v-if="order.order_status === 'pending_payment'"
              color="success"
              block
              @click="payOrder"
            >
              立即支付
            </v-btn>
            <v-btn
              v-if="order.order_status === 'shipped'"
              color="primary"
              block
              @click="confirmOrder"
            >
              确认收货
            </v-btn>
            <v-btn variant="outlined" block @click="router.push('/orders')">
              返回订单列表
            </v-btn>
          </div>
        </v-col>
      </v-row>
    </div>
  </v-container>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { useNotification } from '@/composables/useNotification'
import { orderAPI } from '@/api'
import OrderStatus from '@/components/OrderStatus.vue'
import EmptyState from '@/components/EmptyState.vue'
import type { Order } from '@/types'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()
const notification = useNotification()

const order = ref<Order | null>(null)
const loading = ref(false)

const statusMap: Record<string, string> = {
  'pending_payment': '待支付',
  'paid': '已支付',
  'shipped': '已发货',
  'completed': '已完成',
  'cancelled': '已取消'
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

const formatDate = (dateString?: string): string => {
  if (!dateString) return '-'
  return new Date(dateString).toLocaleString('zh-CN')
}

const loadOrder = async (): Promise<void> => {
  const orderId = route.params.id
  if (!orderId || !userStore.currentUser) return

  loading.value = true
  try {
    const response = await orderAPI.getOrderDetail(Number(orderId), userStore.currentUser.user_id)
    order.value = response.order
  } catch (error) {
    console.error('Failed to load order:', error)
    notification.error('加载订单失败')
  } finally {
    loading.value = false
  }
}

const payOrder = async (): Promise<void> => {
  if (!order.value || !userStore.currentUser) return

  try {
    await orderAPI.updatePaymentStatus(order.value.order_id, {
      user_id: userStore.currentUser.user_id,
      payment_status: 'paid'
    })

    notification.success('支付成功！')
    await loadOrder()
  } catch (error) {
    console.error('Failed to pay order:', error)
    notification.error('支付失败')
  }
}

const confirmOrder = async (): Promise<void> => {
  if (!order.value || !userStore.currentUser) return

  try {
    await orderAPI.updateOrderStatus(order.value.order_id, {
      user_id: userStore.currentUser.user_id,
      status: 'completed'
    })

    notification.success('确认收货成功！')
    await loadOrder()
  } catch (error) {
    console.error('Failed to confirm order:', error)
    notification.error('确认收货失败')
  }
}

onMounted(() => {
  loadOrder()
})
</script>

<style scoped>
.order-detail-view {
  max-width: 1400px;
}
</style>
