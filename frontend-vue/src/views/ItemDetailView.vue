<template>
  <div class="item-detail">
    <div v-if="loading" class="loading">
      加载中...
    </div>

    <div v-else-if="!item" class="not-found">
      商品不存在
    </div>

    <div v-else class="item-content">
      <div class="item-images">
        <div class="main-image">
          <img 
            :src="currentImage || '/placeholder.jpg'" 
            :alt="item.title"
          />
        </div>
        <div v-if="item.images && item.images.length > 1" class="image-thumbnails">
          <img 
            v-for="(image, index) in item.images"
            :key="index"
            :src="image"
            :alt="`${item.title} ${index + 1}`"
            :class="{ active: currentImage === image }"
            @click="currentImage = image"
          />
        </div>
      </div>

      <div class="item-info">
        <h1>{{ item.title }}</h1>
        
        <div class="item-price">
          <span class="current-price">¥{{ item.price }}</span>
          <span v-if="item.original_price" class="original-price">
            原价：¥{{ item.original_price }}
          </span>
        </div>

        <div class="item-meta">
          <div class="meta-item">
            <span class="label">成色：</span>
            <span class="value">{{ getConditionText(item.condition_level) }}</span>
          </div>
          <div class="meta-item">
            <span class="label">分类：</span>
            <span class="value">{{ item.category_name }}</span>
          </div>
          <div class="meta-item">
            <span class="label">交易地点：</span>
            <span class="value">{{ item.location }}</span>
          </div>
          <div class="meta-item">
            <span class="label">浏览次数：</span>
            <span class="value">{{ item.view_count }}</span>
          </div>
        </div>

        <div class="seller-info">
          <h3>卖家信息</h3>
          <div class="seller-card">
            <img 
              :src="item.avatar || '/default-avatar.jpg'" 
              :alt="item.username"
              class="seller-avatar"
            />
            <div class="seller-details">
              <div class="seller-name">{{ item.username }}</div>
              <div class="seller-credit">
                信用分：{{ item.credit_score }}
              </div>
            </div>
          </div>
        </div>

        <div v-if="isLoggedIn && currentUser?.user_id !== item.user_id" class="actions">
          <button 
            @click="toggleWishlist"
            :class="['wishlist-btn', { active: isWishlisted }]"
            :disabled="wishlistLoading"
          >
            {{ isWishlisted ? '已收藏' : '收藏' }}
          </button>
          
          <button @click="contactSeller" class="contact-btn">
            联系卖家
          </button>
          
          <button @click="buyNow" class="buy-btn">
            立即购买
          </button>
        </div>

        <div v-else-if="!isLoggedIn" class="login-prompt">
          <router-link to="/login" class="login-link">
            登录后可收藏、联系卖家和购买
          </router-link>
        </div>
      </div>
    </div>

    <div v-if="item" class="item-description">
      <h2>商品描述</h2>
      <div class="description-content">
        {{ item.description }}
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { itemAPI, wishlistAPI } from '@/api'
import type { Item } from '@/types'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

const item = ref<Item | null>(null)
const loading = ref(false)
const currentImage = ref('')
const isWishlisted = ref(false)
const wishlistLoading = ref(false)

const isLoggedIn = computed(() => userStore.isLoggedIn)
const currentUser = computed(() => userStore.currentUser)

const conditionMap: Record<string, string> = {
  'brand_new': '全新',
  'like_new': '几乎全新',
  'very_good': '非常好',
  'good': '良好',
  'acceptable': '可接受'
}

const getConditionText = (condition: string): string => {
  return conditionMap[condition] || condition
}

const loadItem = async (): Promise<void> => {
  const itemId = route.params.id
  if (!itemId) return

  loading.value = true
  try {
    const response = await itemAPI.getItem(Number(itemId))
    item.value = response.item

    if (item.value?.images && item.value.images.length > 0) {
      currentImage.value = item.value.images[0] || ''
    }

    if (isLoggedIn.value && item.value) {
      checkWishlistStatus()
    }
  } catch (error) {
    console.error('Failed to load item:', error)
  } finally {
    loading.value = false
  }
}

const checkWishlistStatus = async (): Promise<void> => {
  if (!isLoggedIn.value || !item.value || !currentUser.value) return

  try {
    const response = await wishlistAPI.checkWishlistStatus({
      user_id: currentUser.value.user_id,
      item_id: item.value.item_id
    })
    isWishlisted.value = response.is_favorited || false
  } catch (error) {
    console.error('Failed to check wishlist status:', error)
  }
}

const toggleWishlist = async (): Promise<void> => {
  if (!isLoggedIn.value || !item.value || !currentUser.value) return

  wishlistLoading.value = true
  try {
    if (isWishlisted.value) {
      await wishlistAPI.removeFromWishlist({
        user_id: currentUser.value.user_id,
        item_id: item.value.item_id
      })
      isWishlisted.value = false
    } else {
      await wishlistAPI.addToWishlist({
        user_id: currentUser.value.user_id,
        item_id: item.value.item_id
      })
      isWishlisted.value = true
    }
  } catch (error) {
    console.error('Failed to toggle wishlist:', error)
  } finally {
    wishlistLoading.value = false
  }
}

const contactSeller = (): void => {
  if (!isLoggedIn.value) {
    router.push('/login')
    return
  }

  if (!item.value) return
  router.push(`/messages?user_id=${item.value.user_id}&item_id=${item.value.item_id}`)
}

const buyNow = (): void => {
  if (!isLoggedIn.value) {
    router.push('/login')
    return
  }

  if (!item.value) return
  router.push(`/order/create?item_id=${item.value.item_id}`)
}

onMounted(() => {
  loadItem()
})
</script>

<style scoped>
.item-detail {
  max-width: 1800px;
  margin: 0 auto;
  padding: 30px 40px;
}

.loading {
  text-align: center;
  padding: 40px;
  color: #6c757d;
  font-size: 18px;
}

.not-found {
  text-align: center;
  padding: 40px;
  color: #6c757d;
  font-size: 18px;
}

.item-content {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 40px;
  margin-bottom: 40px;
}

.item-images {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.main-image {
  width: 100%;
  height: 500px;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}

.main-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.image-thumbnails {
  display: flex;
  gap: 10px;
  overflow-x: auto;
}

.image-thumbnails img {
  width: 80px;
  height: 80px;
  object-fit: cover;
  border-radius: 4px;
  cursor: pointer;
  opacity: 0.7;
  transition: opacity 0.3s;
}

.image-thumbnails img:hover,
.image-thumbnails img.active {
  opacity: 1;
}

.item-info h1 {
  color: #2c3e50;
  margin: 0 0 20px 0;
  font-size: 2rem;
}

.item-price {
  margin-bottom: 20px;
}

.current-price {
  color: #e74c3c;
  font-size: 2rem;
  font-weight: 600;
}

.original-price {
  color: #6c757d;
  font-size: 1rem;
  text-decoration: line-through;
  margin-left: 15px;
}

.item-meta {
  background: #f8f9fa;
  padding: 20px;
  border-radius: 8px;
  margin-bottom: 30px;
}

.meta-item {
  display: flex;
  margin-bottom: 10px;
}

.meta-item:last-child {
  margin-bottom: 0;
}

.meta-item .label {
  font-weight: 500;
  color: #2c3e50;
  width: 100px;
}

.meta-item .value {
  color: #6c757d;
}

.seller-info {
  margin-bottom: 30px;
}

.seller-info h3 {
  color: #2c3e50;
  margin-bottom: 15px;
}

.seller-card {
  display: flex;
  align-items: center;
  gap: 15px;
  padding: 15px;
  background: #f8f9fa;
  border-radius: 8px;
}

.seller-avatar {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  object-fit: cover;
}

.seller-name {
  font-weight: 500;
  color: #2c3e50;
  margin-bottom: 5px;
}

.seller-credit {
  color: #6c757d;
  font-size: 0.9rem;
}

.actions {
  display: flex;
  gap: 15px;
  flex-wrap: wrap;
}

.actions button {
  padding: 12px 24px;
  border: none;
  border-radius: 6px;
  font-size: 16px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s;
}

.wishlist-btn {
  background: #f8f9fa;
  color: #6c757d;
  border: 1px solid #ddd;
}

.wishlist-btn.active {
  background: #e74c3c;
  color: white;
}

.wishlist-btn:hover {
  background: #e9ecef;
}

.wishlist-btn.active:hover {
  background: #c82333;
}

.contact-btn {
  background: #28a745;
  color: white;
}

.contact-btn:hover {
  background: #218838;
}

.buy-btn {
  background: #007bff;
  color: white;
}

.buy-btn:hover {
  background: #0056b3;
}

.login-prompt {
  text-align: center;
  padding: 20px;
  background: #f8f9fa;
  border-radius: 8px;
}

.login-link {
  color: #007bff;
  text-decoration: none;
  font-weight: 500;
}

.login-link:hover {
  text-decoration: underline;
}

.item-description {
  background: white;
  padding: 30px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.item-description h2 {
  color: #2c3e50;
  margin-bottom: 20px;
}

.description-content {
  color: #6c757d;
  line-height: 1.6;
  white-space: pre-wrap;
}

@media (max-width: 768px) {
  .item-content {
    grid-template-columns: 1fr;
    gap: 20px;
  }

  .main-image {
    height: 300px;
  }

  .item-info h1 {
    font-size: 1.5rem;
  }

  .current-price {
    font-size: 1.5rem;
  }

  .actions {
    flex-direction: column;
  }

  .actions button {
    width: 100%;
  }
}
</style>