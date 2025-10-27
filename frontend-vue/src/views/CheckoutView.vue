<template>
  <div class="checkout-view">
    <div class="checkout-container">
      <h1>确认订单</h1>

      <div v-if="loading" class="loading">
        加载中...
      </div>

      <div v-else-if="!item" class="error">
        商品不存在或已下架
      </div>

      <div v-else class="checkout-content">
        <!-- 商品信息 -->
        <div class="section">
          <h2>商品信息</h2>
          <div class="item-card">
            <img
              :src="item.images && item.images[0] ? item.images[0] : '/placeholder.jpg'"
              :alt="item.title"
              class="item-image"
            />
            <div class="item-info">
              <h3>{{ item.title }}</h3>
              <p class="item-price">¥{{ item.price }}</p>
              <p class="item-seller">卖家：{{ item.username }}</p>
            </div>
          </div>
        </div>

        <!-- 收货地址 -->
        <div class="section">
          <div class="section-header">
            <h2>收货地址</h2>
            <button @click="showAddressModal = true" class="btn-link">
              {{ selectedAddress ? '更换地址' : '选择地址' }}
            </button>
          </div>

          <div v-if="selectedAddress" class="address-card">
            <div class="address-info">
              <span class="recipient">{{ selectedAddress.recipient_name }}</span>
              <span class="phone">{{ selectedAddress.phone }}</span>
            </div>
            <div class="address-detail">
              {{ selectedAddress.province }} {{ selectedAddress.city }} {{ selectedAddress.district }} {{ selectedAddress.detailed_address }}
            </div>
          </div>

          <div v-else class="no-address">
            <p>暂无收货地址，请先添加地址</p>
            <button @click="openAddressModal" class="btn-primary">
              添加地址
            </button>
          </div>
        </div>

        <!-- 支付方式 -->
        <div class="section">
          <h2>支付方式</h2>
          <div class="payment-methods">
            <label class="payment-option">
              <input
                type="radio"
                v-model="paymentMethod"
                value="alipay"
              />
              <span class="payment-name">支付宝</span>
            </label>
            <label class="payment-option">
              <input
                type="radio"
                v-model="paymentMethod"
                value="wechat"
              />
              <span class="payment-name">微信支付</span>
            </label>
            <label class="payment-option">
              <input
                type="radio"
                v-model="paymentMethod"
                value="cash"
              />
              <span class="payment-name">线下支付</span>
            </label>
          </div>
        </div>

        <!-- 配送方式 -->
        <div class="section">
          <h2>配送方式</h2>
          <div class="delivery-methods">
            <label class="delivery-option">
              <input
                type="radio"
                v-model="deliveryMethod"
                value="meet"
              />
              <span class="delivery-name">自取（{{ item.location }}）</span>
            </label>
            <label class="delivery-option">
              <input
                type="radio"
                v-model="deliveryMethod"
                value="express"
              />
              <span class="delivery-name">快递配送</span>
            </label>
          </div>
        </div>

        <!-- 备注 -->
        <div class="section">
          <h2>订单备注</h2>
          <textarea
            v-model="remarks"
            placeholder="选填，可以告诉卖家您的特殊需求"
            maxlength="200"
            rows="3"
          ></textarea>
        </div>

        <!-- 订单总价 -->
        <div class="section summary">
          <div class="summary-row">
            <span>商品价格：</span>
            <span class="amount">¥{{ item.price }}</span>
          </div>
          <div class="summary-row total">
            <span>应付总额：</span>
            <span class="amount">¥{{ item.price }}</span>
          </div>
        </div>

        <!-- 提交按钮 -->
        <div class="actions">
          <button @click="router.back()" class="btn-cancel">
            取消
          </button>
          <button
            @click="submitOrder"
            :disabled="submitting || !canSubmit"
            class="btn-submit"
          >
            {{ submitting ? '提交中...' : '提交订单' }}
          </button>
        </div>
      </div>
    </div>

    <!-- 地址选择弹窗 -->
    <div v-if="showAddressModal" class="modal-overlay" @click="closeAddressModal">
      <div class="modal-content" @click.stop>
        <h3>选择收货地址</h3>

        <div class="modal-toolbar">
          <button @click.stop="toggleAddAddress" class="btn-primary">
            {{ addingAddress ? '返回地址列表' : '新增地址' }}
          </button>
        </div>

        <AddressForm
          v-if="addingAddress"
          :show-cancel="true"
          :loading="addressSaving"
          submit-text="保存地址"
          @cancel="cancelAddAddress"
          @save="handleAddressSave"
        />

        <div v-else-if="addresses.length === 0" class="no-data">
          <p>暂无收货地址</p>
        </div>

        <div v-else class="address-list">
          <div
            v-for="address in addresses"
            :key="address.address_id"
            @click="selectAddress(address)"
            :class="['address-item', { active: selectedAddress?.address_id === address.address_id }]"
          >
            <div class="address-info">
              <span class="recipient">{{ address.recipient_name }}</span>
              <span class="phone">{{ address.phone }}</span>
              <span v-if="address.is_default" class="default-badge">默认</span>
            </div>
            <div class="address-detail">
              {{ address.province }} {{ address.city }} {{ address.district }} {{ address.detailed_address }}
            </div>
          </div>
        </div>

        <div class="modal-actions">
          <button @click="closeAddressModal" class="btn-cancel">
            关闭
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
import { itemAPI, addressAPI, orderAPI } from '@/api'
import type { Item, Address, PaymentMethod, DeliveryMethod, CreateOrderParams, AddressParams } from '@/types'
import { ElMessage } from 'element-plus'
import AddressForm from '@/components/AddressForm.vue'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()

const item = ref<Item | null>(null)
const addresses = ref<Address[]>([])
const selectedAddress = ref<Address | null>(null)
const paymentMethod = ref<PaymentMethod>('alipay')
const deliveryMethod = ref<DeliveryMethod>('meet')
const remarks = ref('')

const loading = ref(false)
const submitting = ref(false)
const showAddressModal = ref(false)
const addingAddress = ref(false)
const addressSaving = ref(false)

type AddressFormValue = Omit<AddressParams, 'user_id'>

const canSubmit = computed(() => {
  return selectedAddress.value !== null && paymentMethod.value && deliveryMethod.value
})

const loadItem = async (): Promise<void> => {
  const itemId = route.query.item_id
  if (!itemId) {
    ElMessage.error('缺少商品ID')
    router.back()
    return
  }

  loading.value = true
  try {
    const response = await itemAPI.getItem(Number(itemId))
    item.value = response.item

    if (!item.value || item.value.status !== 'available') {
      ElMessage.error('商品不可购买')
      setTimeout(() => router.back(), 1500)
    }
  } catch (error) {
    console.error('Failed to load item:', error)
    ElMessage.error('加载商品失败')
  } finally {
    loading.value = false
  }
}

const loadAddresses = async (): Promise<void> => {
  if (!userStore.currentUser) return

  try {
    const response = await addressAPI.getUserAddresses(userStore.currentUser.user_id)
    addresses.value = response.addresses || []

    // 自动选择默认地址
    const defaultAddress = addresses.value.find(addr => addr.is_default)
    if (defaultAddress) {
      selectedAddress.value = defaultAddress
    } else if (addresses.value.length > 0) {
      selectedAddress.value = addresses.value[0] || null
    }
  } catch (error) {
    console.error('Failed to load addresses:', error)
  }
}

const selectAddress = (address: Address): void => {
  selectedAddress.value = address
  closeAddressModal()
}

const openAddressModal = () => {
  showAddressModal.value = true
  addingAddress.value = false
}

const closeAddressModal = () => {
  showAddressModal.value = false
  addingAddress.value = false
}

const toggleAddAddress = () => {
  addingAddress.value = !addingAddress.value
}

const cancelAddAddress = () => {
  addingAddress.value = false
}

const handleAddressSave = async (value: AddressFormValue): Promise<void> => {
  if (!userStore.currentUser) {
    router.push('/login')
    return
  }

  try {
    addressSaving.value = true
    const payload: AddressParams = {
      ...value,
      user_id: userStore.currentUser.user_id
    }
    await addressAPI.addAddress(payload)
    ElMessage.success('地址添加成功')
    addingAddress.value = false
    await loadAddresses()
  } catch (error: any) {
    console.error('Failed to save address:', error)
    const backendMessage = error?.response?.data?.error
    ElMessage.error(backendMessage || '保存地址失败，请重试')
  } finally {
    addressSaving.value = false
  }
}

const submitOrder = async (): Promise<void> => {
  if (!canSubmit.value || !item.value || !selectedAddress.value || !userStore.currentUser) {
    ElMessage.warning('请完善订单信息')
    return
  }

  submitting.value = true
  try {
    const orderData: CreateOrderParams = {
      buyer_id: userStore.currentUser.user_id,
      item_id: item.value.item_id,
      address_id: selectedAddress.value.address_id,
      payment_method: paymentMethod.value,
      delivery_method: deliveryMethod.value,
      notes: remarks.value.trim() || undefined
    }

    const response = await orderAPI.createOrder(orderData)

    if (response.order_id) {
      ElMessage.success('订单创建成功！')
      setTimeout(() => {
        router.push('/orders')
      }, 1500)
    }
  } catch (error) {
    console.error('Failed to create order:', error)
    ElMessage.error('创建订单失败，请重试')
  } finally {
    submitting.value = false
  }
}

onMounted(() => {
  if (!userStore.isLoggedIn) {
    router.push('/login')
    return
  }

  loadItem()
  loadAddresses()
})
</script>

<style scoped>
.checkout-view {
  min-height: calc(100vh - 200px);
  background-color: #f5f5f5;
  padding: 20px;
}

.checkout-container {
  max-width: 1000px;
  margin: 0 auto;
}

.checkout-container h1 {
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

.checkout-content {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.section {
  background: white;
  border-radius: 8px;
  padding: 20px;
}

.section h2 {
  color: #303133;
  font-size: 18px;
  margin-bottom: 15px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.btn-link {
  background: none;
  border: none;
  color: #409eff;
  cursor: pointer;
  font-size: 14px;
}

.btn-link:hover {
  text-decoration: underline;
}

/* 商品卡片 */
.item-card {
  display: flex;
  gap: 15px;
  padding: 15px;
  background: #f9f9f9;
  border-radius: 8px;
}

.item-image {
  width: 100px;
  height: 100px;
  object-fit: cover;
  border-radius: 8px;
}

.item-info h3 {
  color: #303133;
  margin-bottom: 8px;
}

.item-price {
  color: #f56c6c;
  font-size: 20px;
  font-weight: bold;
  margin-bottom: 5px;
}

.item-seller {
  color: #909399;
  font-size: 14px;
}

/* 地址卡片 */
.address-card {
  padding: 15px;
  background: #f9f9f9;
  border-radius: 8px;
}

.address-info {
  display: flex;
  gap: 15px;
  margin-bottom: 8px;
}

.recipient {
  font-weight: 500;
  color: #303133;
}

.phone {
  color: #606266;
}

.address-detail {
  color: #606266;
  font-size: 14px;
}

.no-address {
  text-align: center;
  padding: 30px;
}

.no-address p {
  color: #909399;
  margin-bottom: 15px;
}

/* 支付和配送方式 */
.payment-methods,
.delivery-methods {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.payment-option,
.delivery-option {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px;
  border: 1px solid #dcdfe6;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s;
}

.payment-option:hover,
.delivery-option:hover {
  border-color: #409eff;
  background: #ecf5ff;
}

.payment-option input,
.delivery-option input {
  cursor: pointer;
}

/* 备注 */
textarea {
  width: 100%;
  padding: 12px;
  border: 1px solid #dcdfe6;
  border-radius: 8px;
  font-size: 14px;
  resize: vertical;
  font-family: inherit;
}

textarea:focus {
  outline: none;
  border-color: #409eff;
}

/* 订单总价 */
.summary {
  background: #fff9e6;
}

.summary-row {
  display: flex;
  justify-content: space-between;
  padding: 8px 0;
}

.summary-row.total {
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
  gap: 15px;
  justify-content: center;
  padding: 20px 0;
}

.btn-cancel,
.btn-submit,
.btn-primary {
  padding: 12px 40px;
  border: none;
  border-radius: 8px;
  font-size: 16px;
  cursor: pointer;
  transition: all 0.3s;
}

.btn-cancel {
  background: #f5f5f5;
  color: #606266;
}

.btn-cancel:hover {
  background: #e0e0e0;
}

.btn-submit,
.btn-primary {
  background: #67c23a;
  color: white;
}

.btn-submit:hover:not(:disabled),
.btn-primary:hover {
  background: #5daf34;
}

.btn-submit:disabled {
  background: #c0c4cc;
  cursor: not-allowed;
}

/* 弹窗 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  border-radius: 12px;
  padding: 24px;
  max-width: 600px;
  width: 90%;
  max-height: 80vh;
  overflow-y: auto;
}

.modal-content h3 {
  color: #303133;
  margin-bottom: 20px;
}

.no-data {
  text-align: center;
  padding: 40px;
  color: #909399;
}

.address-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin-bottom: 20px;
}

.address-item {
  padding: 15px;
  border: 2px solid #dcdfe6;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s;
}

.address-item:hover {
  border-color: #409eff;
  background: #ecf5ff;
}

.address-item.active {
  border-color: #409eff;
  background: #ecf5ff;
}

.default-badge {
  padding: 2px 8px;
  background: #67c23a;
  color: white;
  font-size: 12px;
  border-radius: 4px;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
}

@media (max-width: 768px) {
  .checkout-view {
    padding: 10px;
  }

  .item-card {
    flex-direction: column;
  }

  .actions {
    flex-direction: column;
  }

  .btn-cancel,
  .btn-submit {
    width: 100%;
  }
}
</style>
