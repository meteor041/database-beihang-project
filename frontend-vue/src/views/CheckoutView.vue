<template>
  <v-container class="checkout-view">
    <v-card elevation="4" class="mx-auto" max-width="1000">
      <v-card-title class="text-h4 font-weight-bold text-center pa-6 bg-primary">
        <v-icon class="mr-2">mdi-cart-check</v-icon>
        确认订单
      </v-card-title>

      <v-card-text class="pa-8">
        <v-stepper v-model="step" alt-labels>
          <v-stepper-header>
            <v-stepper-item title="商品信息" value="1"></v-stepper-item>
            <v-divider></v-divider>
            <v-stepper-item title="收货地址" value="2"></v-stepper-item>
            <v-divider></v-divider>
            <v-stepper-item title="支付方式" value="3"></v-stepper-item>
            <v-divider></v-divider>
            <v-stepper-item title="确认下单" value="4"></v-stepper-item>
          </v-stepper-header>

          <v-stepper-window>
            <!-- 步骤1: 商品信息 -->
            <v-stepper-window-item value="1">
              <v-card v-if="item" variant="tonal" class="my-4">
                <v-card-text class="d-flex ga-4">
                  <v-img :src="item.images?.[0] || '/placeholder.png'" width="120" height="120" cover></v-img>
                  <div class="flex-grow-1">
                    <h3 class="text-h6 mb-2">{{ item.title }}</h3>
                    <div class="text-h5 text-error font-weight-bold">¥{{ item.price }}</div>
                    <div class="text-body-2 text-grey">卖家：{{ item.username }}</div>
                  </div>
                </v-card-text>
              </v-card>
              <v-btn color="primary" @click="step = '2'">下一步</v-btn>
            </v-stepper-window-item>

            <!-- 步骤2: 收货地址 -->
            <v-stepper-window-item value="2">
              <v-text-field v-model="form.address" label="收货地址" variant="outlined" required class="my-4"></v-text-field>
              <v-text-field v-model="form.phone" label="联系电话" variant="outlined" required class="mb-4"></v-text-field>
              <div class="d-flex ga-2">
                <v-btn variant="outlined" @click="step = '1'">上一步</v-btn>
                <v-btn color="primary" @click="step = '3'">下一步</v-btn>
              </div>
            </v-stepper-window-item>

            <!-- 步骤3: 支付方式 -->
            <v-stepper-window-item value="3">
              <v-radio-group v-model="form.payment_method" class="my-4">
                <v-radio label="支付宝" value="alipay"></v-radio>
                <v-radio label="微信支付" value="wechat"></v-radio>
                <v-radio label="现金支付" value="cash"></v-radio>
              </v-radio-group>
              <div class="d-flex ga-2">
                <v-btn variant="outlined" @click="step = '2'">上一步</v-btn>
                <v-btn color="primary" @click="step = '4'">下一步</v-btn>
              </div>
            </v-stepper-window-item>

            <!-- 步骤4: 确认下单 -->
            <v-stepper-window-item value="4">
              <v-card variant="tonal" class="my-4">
                <v-card-text>
                  <div class="mb-2"><strong>商品：</strong>{{ item?.title }}</div>
                  <div class="mb-2"><strong>价格：</strong>¥{{ item?.price }}</div>
                  <div class="mb-2"><strong>地址：</strong>{{ form.address }}</div>
                  <div class="mb-2"><strong>电话：</strong>{{ form.phone }}</div>
                  <div class="mb-2"><strong>支付：</strong>{{ getPaymentText(form.payment_method) }}</div>
                </v-card-text>
              </v-card>
              <div class="d-flex ga-2">
                <v-btn variant="outlined" @click="step = '3'">上一步</v-btn>
                <v-btn color="success" :loading="submitting" @click="submitOrder">确认下单</v-btn>
              </div>
            </v-stepper-window-item>
          </v-stepper-window>
        </v-stepper>
      </v-card-text>
    </v-card>
  </v-container>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { useNotification } from '@/composables/useNotification'
import { itemAPI, orderAPI } from '@/api'
import type { Item } from '@/types'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()
const notification = useNotification()

const step = ref('1')
const item = ref<Item | null>(null)
const submitting = ref(false)

const form = ref({
  address: '',
  phone: '',
  payment_method: 'alipay'
})

const getPaymentText = (method: string): string => {
  const map: Record<string, string> = {
    alipay: '支付宝',
    wechat: '微信支付',
    cash: '现金支付'
  }
  return map[method] || method
}

const loadItem = async (): Promise<void> => {
  const itemId = route.query.item_id
  if (!itemId) return

  try {
    const response = await itemAPI.getItem(Number(itemId))
    item.value = response.item
  } catch (error) {
    console.error('Failed to load item:', error)
    notification.error('加载商品失败')
  }
}

const submitOrder = async (): Promise<void> => {
  if (!item.value || !userStore.currentUser) return

  submitting.value = true
  try {
    const response = await orderAPI.createOrder({
      buyer_id: userStore.currentUser.user_id,
      item_id: item.value.item_id,
      total_amount: item.value.price,
      shipping_address: form.value.address,
      receiver_phone: form.value.phone,
      payment_method: form.value.payment_method
    })

    notification.success('订单创建成功！')
    router.push(`/orders/${response.order_id}`)
  } catch (error) {
    console.error('Failed to create order:', error)
    notification.error('创建订单失败')
  } finally {
    submitting.value = false
  }
}

onMounted(() => {
  if (!userStore.isLoggedIn) {
    notification.warning('请先登录')
    router.push('/login')
    return
  }
  loadItem()
})
</script>

<style scoped>
.checkout-view {
  max-width: 1000px;
  padding: 40px 20px;
}
</style>
