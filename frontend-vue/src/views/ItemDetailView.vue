<template>
  <div class="item-detail">
    <!-- 加载状态 -->
    <div v-if="loading" class="loading-container" v-loading="loading" element-loading-text="加载中...">
      <div style="height: 600px"></div>
    </div>

    <!-- 未找到 -->
    <el-empty v-else-if="!item" description="商品不存在" :image-size="100">
      <el-button type="primary" @click="router.push('/items')">
        返回商品列表
      </el-button>
    </el-empty>

    <!-- 商品详情 -->
    <div v-else class="detail-container">
      <!-- 左侧：图片 -->
      <div class="item-images-section">
        <el-card class="images-card" :body-style="{ padding: '0' }">
          <div class="main-image">
            <!-- 有图片时显示 -->
            <el-image
              v-if="currentImage"
              :src="currentImage"
              :alt="item.title"
              fit="contain"
              :preview-src-list="item.images"
              :initial-index="item.images?.indexOf(currentImage)"
            >
              <template #error>
                <div class="image-placeholder">
                  <div class="placeholder-icon">
                    <el-icon><ShoppingBag /></el-icon>
                  </div>
                </div>
              </template>
            </el-image>

            <!-- 无图片时显示占位图 -->
            <div v-else class="image-placeholder">
              <div class="placeholder-icon">
                <el-icon><ShoppingBag /></el-icon>
              </div>
            </div>

            <!-- 状态标签 -->
            <el-tag v-if="item.status === 'sold'" class="status-badge" type="danger" size="large">
              已售出
            </el-tag>
          </div>

          <!-- 缩略图 -->
          <div v-if="item.images && item.images.length > 1" class="image-thumbnails">
            <div
              v-for="(image, index) in item.images"
              :key="index"
              :class="['thumbnail-item', { active: currentImage === image }]"
              @click="currentImage = image"
            >
              <el-image
                :src="image"
                :alt="`${item.title} ${index + 1}`"
                fit="cover"
              />
            </div>
          </div>
        </el-card>
      </div>

      <!-- 右侧：商品信息 -->
      <div class="item-info-section">
        <!-- 标题 -->
        <h1 class="item-title">{{ item.title }}</h1>

        <!-- 价格卡片 -->
        <el-card class="price-card">
          <div class="price-row">
            <span class="current-price">¥{{ item.price }}</span>
            <el-tag v-if="item.original_price" class="discount-tag" size="large" type="warning">
              原价 ¥{{ item.original_price }}
            </el-tag>
          </div>
        </el-card>

        <!-- 商品信息卡片 -->
        <el-card class="info-card">
          <template #header>
            <div class="card-header">
              <el-icon><InfoFilled /></el-icon>
              <span>商品信息</span>
            </div>
          </template>

          <el-descriptions :column="1" border>
            <el-descriptions-item label="成色">
              <el-tag :type="getConditionType(item.condition_level)" size="small">
                {{ getConditionText(item.condition_level) }}
              </el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="分类">
              <el-icon size="14"><Grid /></el-icon>
              {{ item.category_name }}
            </el-descriptions-item>
            <el-descriptions-item label="交易地点">
              <el-icon size="14"><Location /></el-icon>
              {{ item.location }}
            </el-descriptions-item>
            <el-descriptions-item label="浏览次数">
              <el-icon size="14"><View /></el-icon>
              {{ item.view_count }} 次
            </el-descriptions-item>
            <el-descriptions-item label="收藏数">
              <el-icon size="14"><Star /></el-icon>
              {{ item.wishlist_count || 0 }} 人收藏
            </el-descriptions-item>
            <el-descriptions-item label="发布时间">
              <el-icon size="14"><Clock /></el-icon>
              {{ formatDate(item.publish_date) }}
            </el-descriptions-item>
          </el-descriptions>
        </el-card>

        <!-- 卖家信息卡片 -->
        <el-card class="seller-card">
          <template #header>
            <div class="card-header">
              <el-icon><User /></el-icon>
              <span>卖家信息</span>
            </div>
          </template>

          <div class="seller-content">
            <UserAvatar
              :avatar="item.avatar"
              :username="item.username"
              :size="56"
            />
            <div class="seller-details">
              <div class="seller-name">{{ item.username }}</div>
              <div class="seller-credit">
                <el-icon><Medal /></el-icon>
                信用分：{{ item.credit_score }}
              </div>
            </div>
          </div>
        </el-card>

        <!-- 操作按钮 -->
        <div v-if="isLoggedIn && currentUser?.user_id !== item.user_id" class="actions">
          <el-button
            :type="isWishlisted ? 'warning' : 'default'"
            :icon="isWishlisted ? StarFilled : Star"
            @click="toggleWishlist"
            :loading="wishlistLoading"
            size="large"
          >
            {{ isWishlisted ? '已收藏' : '收藏' }}
          </el-button>

          <el-button
            type="success"
            :icon="ChatDotRound"
            @click="contactSeller"
            size="large"
          >
            联系卖家
          </el-button>

          <el-button
            type="primary"
            :icon="ShoppingCart"
            @click="buyNow"
            size="large"
          >
            立即购买
          </el-button>
        </div>

        <el-alert v-else-if="!isLoggedIn" type="info" :closable="false">
          <template #title>
            <router-link to="/login" class="login-link">
              登录后可收藏、联系卖家和购买
            </router-link>
          </template>
        </el-alert>
      </div>
    </div>

    <!-- 商品描述 -->
    <el-card v-if="item" class="description-card">
      <template #header>
        <div class="card-header">
          <el-icon><Document /></el-icon>
          <span>商品描述</span>
        </div>
      </template>

      <div class="description-content">
        {{ item.description }}
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { itemAPI, wishlistAPI } from '@/api'
import { ElMessage } from 'element-plus'
import {
  Picture, InfoFilled, Grid, Location, View, Clock, User, Medal,
  Star, StarFilled, ChatDotRound, ShoppingCart, Document, ShoppingBag
} from '@element-plus/icons-vue'
import UserAvatar from '@/components/UserAvatar.vue'
import type { Item, ConditionLevel } from '@/types'

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

const getConditionType = (condition: string): 'success' | 'warning' | 'info' | '' => {
  const typeMap: Record<string, 'success' | 'warning' | 'info' | ''> = {
    'brand_new': 'success',
    'like_new': 'success',
    'very_good': '',
    'good': 'warning',
    'acceptable': 'info'
  }
  return typeMap[condition] || ''
}

const formatDate = (dateString?: string): string => {
  if (!dateString) return '-'

  // 处理服务器返回的时间格式 "YYYY-MM-DD HH:MM:SS"
  const normalized = dateString.replace(' ', 'T')
  const date = new Date(normalized)

  if (isNaN(date.getTime())) return '-'

  const now = new Date()
  const diff = now.getTime() - date.getTime()
  const days = Math.floor(diff / (1000 * 60 * 60 * 24))

  // 处理负数天数（时区问题）
  if (days < 0) return date.toLocaleDateString('zh-CN')
  if (days === 0) return '今天'
  if (days === 1) return '昨天'
  if (days < 7) return `${days}天前`
  if (days < 30) return `${Math.floor(days / 7)}周前`
  if (days < 365) return `${Math.floor(days / 30)}个月前`
  return date.toLocaleDateString('zh-CN')
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
      ElMessage.success('已取消收藏')
    } else {
      await wishlistAPI.addToWishlist({
        user_id: currentUser.value.user_id,
        item_id: item.value.item_id
      })
      isWishlisted.value = true
      ElMessage.success('收藏成功')
    }
  } catch (error) {
    console.error('Failed to toggle wishlist:', error)
    ElMessage.error('操作失败，请重试')
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
/* 现代扁平化风格 - Twitter/YouTube/Google 风格 */

.item-detail {
  width: 100%;
  padding: var(--spacing-6) var(--spacing-8);
  background: var(--color-bg-page);
  min-height: 100vh;
}

/* 加载容器 */
.loading-container {
  min-height: 600px;
  display: flex;
  align-items: center;
  justify-content: center;
}

/* 详情容器 - 响应式 Grid */
.detail-container {
  display: grid;
  grid-template-columns: minmax(400px, 1fr) minmax(400px, 1fr);
  gap: var(--spacing-8);
  margin-bottom: var(--spacing-8);
  max-width: 1800px;
  margin-left: auto;
  margin-right: auto;
}

/* 图片区域 */
.item-images-section {
  position: sticky;
  top: var(--spacing-6);
  align-self: start;
}

.images-card {
  border: 1px solid var(--color-border-base);
  border-radius: var(--radius-lg);
  overflow: hidden;
}

.main-image {
  position: relative;
  width: 100%;
  height: 500px;
  background: var(--color-neutral-100);
  display: flex;
  align-items: center;
  justify-content: center;
}

.main-image .el-image {
  width: 100%;
  height: 100%;
}

/* 占位图样式 - 与 ItemCard 保持一致 */
.image-placeholder {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  width: 100%;
  height: 100%;
  background: linear-gradient(135deg, #f5f7fa 0%, #e8edf3 100%);
  position: relative;
  overflow: hidden;
}

/* 添加装饰性几何图形 */
.image-placeholder::before,
.image-placeholder::after {
  content: '';
  position: absolute;
  border-radius: 50%;
  opacity: 0.1;
}

.image-placeholder::before {
  width: 300px;
  height: 300px;
  background: var(--el-color-primary);
  top: -120px;
  right: -120px;
}

.image-placeholder::after {
  width: 250px;
  height: 250px;
  background: var(--el-color-primary);
  bottom: -100px;
  left: -100px;
}

.image-placeholder .placeholder-icon {
  position: relative;
  z-index: 1;
  width: 140px;
  height: 140px;
  background: white;
  border-radius: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1);
  transition: transform var(--transition-base);
}

.image-placeholder .placeholder-icon:hover {
  transform: scale(1.05);
}

.image-placeholder .placeholder-icon .el-icon {
  font-size: 72px;
  color: var(--el-color-primary);
}

.status-badge {
  position: absolute;
  top: var(--spacing-4);
  right: var(--spacing-4);
}

/* 缩略图 */
.image-thumbnails {
  display: flex;
  gap: var(--spacing-2);
  padding: var(--spacing-3);
  overflow-x: auto;
  background: var(--color-bg-section);
}

.thumbnail-item {
  flex-shrink: 0;
  width: 80px;
  height: 80px;
  border: 2px solid transparent;
  border-radius: var(--radius-base);
  overflow: hidden;
  cursor: pointer;
  transition: all var(--transition-base);
}

.thumbnail-item:hover {
  border-color: var(--color-primary-light);
}

.thumbnail-item.active {
  border-color: var(--color-primary);
}

.thumbnail-item .el-image {
  width: 100%;
  height: 100%;
}

/* 信息区域 */
.item-info-section {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-4);
}

.item-title {
  margin: 0;
  font-size: var(--font-size-3xl);
  font-weight: var(--font-weight-bold);
  color: var(--color-text-primary);
  line-height: var(--line-height-snug);
}

/* 价格卡片 */
.price-card {
  border: 1px solid var(--color-border-base);
  border-radius: var(--radius-lg);
}

.price-row {
  display: flex;
  align-items: baseline;
  gap: var(--spacing-3);
}

.current-price {
  font-size: var(--font-size-5xl);
  font-weight: var(--font-weight-bold);
  color: var(--color-price);
}

.discount-tag {
  text-decoration: line-through;
}

/* 信息卡片 */
.info-card,
.seller-card {
  border: 1px solid var(--color-border-base);
  border-radius: var(--radius-lg);
}

.info-card :deep(.el-card__header),
.seller-card :deep(.el-card__header) {
  background: var(--color-bg-section);
  border-bottom: 1px solid var(--color-border-light);
  padding: var(--spacing-3) var(--spacing-4);
}

.card-header {
  display: flex;
  align-items: center;
  gap: var(--spacing-2);
  font-size: var(--font-size-base);
  font-weight: var(--font-weight-medium);
  color: var(--color-text-primary);
}

.card-header .el-icon {
  color: var(--color-primary);
}

/* 卖家信息 */
.seller-content {
  display: flex;
  align-items: center;
  gap: var(--spacing-4);
}

.seller-details {
  flex: 1;
}

.seller-name {
  font-size: var(--font-size-lg);
  font-weight: var(--font-weight-medium);
  color: var(--color-text-primary);
  margin-bottom: var(--spacing-1);
}

.seller-credit {
  display: flex;
  align-items: center;
  gap: var(--spacing-1);
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
}

/* 操作按钮 */
.actions {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-3);
  padding-top: var(--spacing-2);
}

.actions :deep(.el-button) {
  width: 100%;
}

.actions :deep(.el-button + .el-button) {
  margin-left: 0;
}

.login-link {
  color: var(--color-primary);
  text-decoration: none;
  font-weight: var(--font-weight-medium);
  transition: color var(--transition-fast);
}

.login-link:hover {
  color: var(--color-primary-dark);
  text-decoration: underline;
}

/* 商品描述卡片 */
.description-card {
  border: 1px solid var(--color-border-base);
  border-radius: var(--radius-lg);
}

.description-card :deep(.el-card__header) {
  background: var(--color-bg-section);
  border-bottom: 1px solid var(--color-border-light);
  padding: var(--spacing-3) var(--spacing-4);
}

.description-content {
  font-size: var(--font-size-base);
  color: var(--color-text-secondary);
  line-height: var(--line-height-relaxed);
  white-space: pre-wrap;
}

/* 响应式 */
@media (max-width: 1024px) {
  .detail-container {
    grid-template-columns: 1fr;
  }

  .item-images-section {
    position: relative;
    top: 0;
  }

  .main-image {
    height: 400px;
  }
}

@media (max-width: 768px) {
  .item-detail {
    padding: var(--spacing-4);
  }

  .main-image {
    height: 300px;
  }

  .item-title {
    font-size: var(--font-size-2xl);
  }

  .current-price {
    font-size: var(--font-size-4xl);
  }
}
</style>
