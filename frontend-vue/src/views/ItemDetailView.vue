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
            :src="currentImage || '/placeholder.png'" 
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
              :src="item.avatar || '/default-avatar.png'" 
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
/* 使用设计系统变量 */
.item-detail {
  max-width: 1800px;
  margin: 0 auto;
  padding: var(--spacing-2xl) var(--spacing-3xl);
}

.loading {
  text-align: center;
  padding: var(--spacing-3xl);
  color: var(--color-text-secondary);
  font-size: var(--font-size-xl);
}

.not-found {
  text-align: center;
  padding: var(--spacing-3xl);
  color: var(--color-text-secondary);
  font-size: var(--font-size-xl);
}

.item-content {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--spacing-3xl);
  margin-bottom: var(--spacing-3xl);
}

.item-images {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-lg);
}

.main-image {
  width: 100%;
  height: 500px;
  border-radius: var(--radius-md);
  overflow: hidden;
  box-shadow: var(--shadow-md);
}

.main-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.image-thumbnails {
  display: flex;
  gap: var(--spacing-sm);
  overflow-x: auto;
}

.image-thumbnails img {
  width: 80px;
  height: 80px;
  object-fit: cover;
  border-radius: var(--radius-sm);
  cursor: pointer;
  opacity: 0.7;
  transition: opacity var(--transition-base);
}

.image-thumbnails img:hover,
.image-thumbnails img.active {
  opacity: 1;
}

.item-info h1 {
  color: var(--color-text-primary);
  margin: 0 0 var(--spacing-lg) 0;
  font-size: var(--font-size-4xl);
}

.item-price {
  margin-bottom: var(--spacing-lg);
}

.current-price {
  color: var(--color-price);
  font-size: var(--font-size-4xl);
  font-weight: var(--font-weight-semibold);
}

.original-price {
  color: var(--color-text-secondary);
  font-size: var(--font-size-base);
  text-decoration: line-through;
  margin-left: var(--spacing-lg);
}

.item-meta {
  background: var(--color-bg-page);
  padding: var(--spacing-lg);
  border-radius: var(--radius-md);
  margin-bottom: var(--spacing-2xl);
}

.meta-item {
  display: flex;
  margin-bottom: var(--spacing-sm);
}

.meta-item:last-child {
  margin-bottom: 0;
}

.meta-item .label {
  font-weight: var(--font-weight-medium);
  color: var(--color-text-primary);
  width: 100px;
}

.meta-item .value {
  color: var(--color-text-secondary);
}

.seller-info {
  margin-bottom: var(--spacing-2xl);
}

.seller-info h3 {
  color: var(--color-text-primary);
  margin-bottom: var(--spacing-lg);
}

.seller-card {
  display: flex;
  align-items: center;
  gap: var(--spacing-lg);
  padding: var(--spacing-lg);
  background: var(--color-bg-page);
  border-radius: var(--radius-md);
}

.seller-avatar {
  width: 60px;
  height: 60px;
  border-radius: var(--radius-round);
  object-fit: cover;
}

.seller-name {
  font-weight: var(--font-weight-medium);
  color: var(--color-text-primary);
  margin-bottom: var(--spacing-xs);
}

.seller-credit {
  color: var(--color-text-secondary);
  font-size: var(--font-size-sm);
}

.actions {
  display: flex;
  gap: var(--spacing-lg);
  flex-wrap: wrap;
}

.actions button {
  padding: var(--spacing-md) var(--spacing-xl);
  border: none;
  border-radius: var(--radius-base);
  font-size: var(--font-size-lg);
  font-weight: var(--font-weight-medium);
  cursor: pointer;
  transition: all var(--transition-base);
}

.wishlist-btn {
  background: var(--color-bg-page);
  color: var(--color-text-secondary);
  border: 1px solid var(--color-border-base);
}

.wishlist-btn.active {
  background: var(--color-price);
  color: white;
}

.wishlist-btn:hover {
  background: var(--color-bg-hover);
}

.wishlist-btn.active:hover {
  background: #c82333;
}

.contact-btn {
  background: var(--color-success);
  color: white;
}

.contact-btn:hover {
  background: #218838;
}

.buy-btn {
  background: var(--color-primary);
  color: white;
}

.buy-btn:hover {
  background: var(--color-primary-dark);
}

.login-prompt {
  text-align: center;
  padding: var(--spacing-lg);
  background: var(--color-bg-page);
  border-radius: var(--radius-md);
}

.login-link {
  color: var(--color-primary);
  text-decoration: none;
  font-weight: var(--font-weight-medium);
}

.login-link:hover {
  text-decoration: underline;
}

.item-description {
  background: var(--color-bg-card);
  padding: var(--spacing-2xl);
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-base);
}

.item-description h2 {
  color: var(--color-text-primary);
  margin-bottom: var(--spacing-lg);
}

.description-content {
  color: var(--color-text-secondary);
  line-height: var(--line-height-normal);
  white-space: pre-wrap;
}

@media (max-width: 768px) {
  .item-content {
    grid-template-columns: 1fr;
    gap: var(--spacing-lg);
  }

  .main-image {
    height: 300px;
  }

  .item-info h1 {
    font-size: var(--font-size-3xl);
  }

  .current-price {
    font-size: var(--font-size-3xl);
  }

  .actions {
    flex-direction: column;
  }

  .actions button {
    width: 100%;
  }
}
</style>