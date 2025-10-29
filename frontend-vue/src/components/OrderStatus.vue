<template>
  <div class="order-status-timeline">
    <v-timeline side="end" density="compact">
      <v-timeline-item
        v-for="step in statusSteps"
        :key="step.status"
        :dot-color="step.color"
        size="small"
      >
        <template v-slot:icon>
          <v-icon :color="step.iconColor">{{ step.icon }}</v-icon>
        </template>

        <template v-slot:opposite>
          <span class="text-caption">{{ step.timestamp }}</span>
        </template>

        <div class="step-content">
          <h4 class="text-subtitle-1 font-weight-bold">{{ step.title }}</h4>
          <p v-if="step.description" class="text-body-2 text-grey">{{ step.description }}</p>
        </div>
      </v-timeline-item>
    </v-timeline>

    <!-- 状态徽章展示 -->
    <div v-if="showBadge" class="status-badge mt-4 text-center">
      <v-chip
        :color="getChipColor(status)"
        size="large"
        label
      >
        {{ getStatusText(status) }}
      </v-chip>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { OrderStatus } from '@/types'

interface Props {
  status: OrderStatus
  orderDate?: string
  paymentDate?: string
  deliveryDate?: string
  completionDate?: string
  cancellationDate?: string
  showBadge?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  orderDate: '',
  paymentDate: '',
  deliveryDate: '',
  completionDate: '',
  cancellationDate: '',
  showBadge: true
})

// 状态步骤配置
const statusSteps = computed(() => {
  const steps = []

  // 订单已创建
  steps.push({
    status: 'pending_payment',
    title: '订单已创建',
    description: '等待买家支付',
    timestamp: props.orderDate,
    color: props.status === 'pending_payment' ? 'warning' : 'success',
    icon: 'mdi-clock-outline',
    iconColor: 'white'
  })

  // 已取消的订单
  if (props.status === 'cancelled') {
    steps.push({
      status: 'cancelled',
      title: '订单已取消',
      description: '订单已被取消',
      timestamp: props.cancellationDate,
      color: 'error',
      icon: 'mdi-close',
      iconColor: 'white'
    })
    return steps
  }

  // 已支付
  if (['paid', 'shipped', 'completed'].includes(props.status)) {
    steps.push({
      status: 'paid',
      title: '支付成功',
      description: '等待卖家发货',
      timestamp: props.paymentDate,
      color: props.status === 'paid' ? 'info' : 'success',
      icon: 'mdi-check',
      iconColor: 'white'
    })
  }

  // 已发货
  if (['shipped', 'completed'].includes(props.status)) {
    steps.push({
      status: 'shipped',
      title: '已发货',
      description: '商品正在配送中',
      timestamp: props.deliveryDate,
      color: props.status === 'shipped' ? 'info' : 'success',
      icon: 'mdi-truck-delivery',
      iconColor: 'white'
    })
  }

  // 已完成
  if (props.status === 'completed') {
    steps.push({
      status: 'completed',
      title: '交易完成',
      description: '订单已完成，感谢您的购买',
      timestamp: props.completionDate,
      color: 'success',
      icon: 'mdi-check-circle',
      iconColor: 'white'
    })
  }

  return steps
})

// 获取状态芯片颜色
const getChipColor = (status: OrderStatus) => {
  const colorMap: Record<OrderStatus, string> = {
    pending_payment: 'warning',
    paid: 'info',
    shipped: 'primary',
    completed: 'success',
    cancelled: 'error'
  }
  return colorMap[status] || 'info'
}

// 获取状态文本
const getStatusText = (status: OrderStatus): string => {
  const textMap: Record<OrderStatus, string> = {
    pending_payment: '待支付',
    paid: '已支付',
    shipped: '已发货',
    completed: '已完成',
    cancelled: '已取消'
  }
  return textMap[status] || status
}
</script>

<style scoped>
.order-status-timeline {
  padding: 20px 0;
}

.step-content h4 {
  margin-bottom: 4px;
}

.step-content p {
  margin: 0;
}

@media (max-width: 768px) {
  .step-content h4 {
    font-size: 14px;
  }

  .step-content p {
    font-size: 12px;
  }
}
</style>
