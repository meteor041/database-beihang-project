<template>
  <div class="order-status-timeline">
    <el-timeline>
      <el-timeline-item
        v-for="step in statusSteps"
        :key="step.status"
        :timestamp="step.timestamp"
        :type="step.type"
        :icon="step.icon"
        :color="step.color"
        placement="top"
      >
        <div class="step-content">
          <h4>{{ step.title }}</h4>
          <p v-if="step.description">{{ step.description }}</p>
        </div>
      </el-timeline-item>
    </el-timeline>

    <!-- 状态徽章展示 -->
    <div v-if="showBadge" class="status-badge">
      <el-tag :type="getBadgeType(status)" size="large">
        {{ getStatusText(status) }}
      </el-tag>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { OrderStatus } from '@/types'
import { Check, Clock, Van, CircleCheck, Close } from '@element-plus/icons-vue'

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
    status: 'pending',
    title: '订单已创建',
    description: '等待买家支付',
    timestamp: props.orderDate,
    type: props.status === 'pending' ? 'primary' : 'success',
    icon: Clock,
    color: props.status === 'pending' ? '#409eff' : '#67c23a'
  })

  // 已取消的订单
  if (props.status === 'cancelled') {
    steps.push({
      status: 'cancelled',
      title: '订单已取消',
      description: '订单已被取消',
      timestamp: props.cancellationDate,
      type: 'danger',
      icon: Close,
      color: '#f56c6c'
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
      type: props.status === 'paid' ? 'primary' : 'success',
      icon: Check,
      color: props.status === 'paid' ? '#409eff' : '#67c23a'
    })
  }

  // 已发货
  if (['shipped', 'completed'].includes(props.status)) {
    steps.push({
      status: 'shipped',
      title: '已发货',
      description: '商品正在配送中',
      timestamp: props.deliveryDate,
      type: props.status === 'shipped' ? 'primary' : 'success',
      icon: Van,
      color: props.status === 'shipped' ? '#409eff' : '#67c23a'
    })
  }

  // 已完成
  if (props.status === 'completed') {
    steps.push({
      status: 'completed',
      title: '交易完成',
      description: '订单已完成，感谢您的购买',
      timestamp: props.completionDate,
      type: 'success',
      icon: CircleCheck,
      color: '#67c23a'
    })
  }

  return steps
})

// 获取状态徽章类型
const getBadgeType = (status: OrderStatus) => {
  const typeMap: Record<OrderStatus, 'success' | 'info' | 'warning' | 'danger' | ''> = {
    pending: 'warning',
    paid: 'info',
    shipped: '',
    completed: 'success',
    cancelled: 'danger'
  }
  return typeMap[status] || 'info'
}

// 获取状态文本
const getStatusText = (status: OrderStatus): string => {
  const textMap: Record<OrderStatus, string> = {
    pending: '待支付',
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
  margin: 0 0 5px 0;
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.step-content p {
  margin: 0;
  font-size: 14px;
  color: #909399;
}

.status-badge {
  margin-top: 20px;
  text-align: center;
}

:deep(.el-timeline-item__timestamp) {
  font-size: 13px;
  color: #909399;
}

:deep(.el-timeline-item__node) {
  display: flex;
  align-items: center;
  justify-content: center;
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
