<template>
  <v-container class="item-detail">
    <!-- 加载状态 -->
    <div v-if="loading" class="d-flex justify-center align-center" style="min-height: 400px;">
      <v-progress-circular indeterminate color="primary" size="64"></v-progress-circular>
    </div>

    <!-- 未找到商品 -->
    <EmptyState
      v-else-if="!item"
      icon="mdi-package-variant-closed"
      description="商品不存在"
      action-text="浏览其他商品"
      @action="router.push('/items')"
    />

    <!-- 商品详情 -->
    <div v-else>
      <v-row>
        <!-- 左侧：图片区域 -->
        <v-col cols="12" md="6">
          <v-card elevation="2">
            <v-carousel
              v-if="item.images && item.images.length > 0"
              v-model="currentImageIndex"
              height="500"
              hide-delimiter-background
              show-arrows="hover"
            >
              <v-carousel-item
                v-for="(image, index) in item.images"
                :key="index"
                :src="image"
                cover
              >
                <template v-slot:placeholder>
                  <div class="d-flex align-center justify-center fill-height">
                    <v-progress-circular indeterminate color="grey-lighten-5"></v-progress-circular>
                  </div>
                </template>
              </v-carousel-item>
            </v-carousel>
            <v-img
              v-else
              src="/placeholder.png"
              height="500"
              cover
            ></v-img>

            <!-- 缩略图 -->
            <v-card-text v-if="item.images && item.images.length > 1" class="pa-2">
              <div class="d-flex ga-2" style="overflow-x: auto;">
                <v-img
                  v-for="(image, index) in item.images"
                  :key="index"
                  :src="image"
                  width="80"
                  height="80"
                  cover
                  class="thumbnail"
                  :class="{ 'thumbnail-active': currentImageIndex === index }"
                  @click="currentImageIndex = index"
                ></v-img>
              </div>
            </v-card-text>
          </v-card>
        </v-col>

        <!-- 右侧：商品信息 -->
        <v-col cols="12" md="6">
          <v-card elevation="2" class="pa-6">
            <!-- 商品标题 -->
            <h1 class="text-h4 font-weight-bold mb-4">{{ item.title }}</h1>

            <!-- 价格 -->
            <div class="mb-6">
              <span class="text-h4 font-weight-bold text-error">¥{{ item.price }}</span>
              <span v-if="item.original_price" class="text-body-1 text-grey text-decoration-line-through ml-4">
                原价：¥{{ item.original_price }}
              </span>
            </div>

            <!-- 商品元数据 -->
            <v-card variant="tonal" class="mb-6">
              <v-list density="comfortable">
                <v-list-item>
                  <template v-slot:prepend>
                    <v-icon color="primary">mdi-star-circle</v-icon>
                  </template>
                  <v-list-item-title>成色</v-list-item-title>
                  <template v-slot:append>
                    <v-chip
                      :color="getConditionColor(item.condition_level)"
                      size="small"
                    >
                      {{ getConditionText(item.condition_level) }}
                    </v-chip>
                  </template>
                </v-list-item>

                <v-list-item>
                  <template v-slot:prepend>
                    <v-icon color="primary">mdi-shape</v-icon>
                  </template>
                  <v-list-item-title>分类</v-list-item-title>
                  <template v-slot:append>
                    <span>{{ item.category_name }}</span>
                  </template>
                </v-list-item>

                <v-list-item>
                  <template v-slot:prepend>
                    <v-icon color="primary">mdi-map-marker</v-icon>
                  </template>
                  <v-list-item-title>交易地点</v-list-item-title>
                  <template v-slot:append>
                    <span>{{ item.location }}</span>
                  </template>
                </v-list-item>

                <v-list-item>
                  <template v-slot:prepend>
                    <v-icon color="primary">mdi-eye</v-icon>
                  </template>
                  <v-list-item-title>浏览次数</v-list-item-title>
                  <template v-slot:append>
                    <span>{{ item.view_count }}</span>
                  </template>
                </v-list-item>
              </v-list>
            </v-card>

            <!-- 卖家信息 -->
            <div class="mb-6">
              <h3 class="text-h6 font-weight-bold mb-3">卖家信息</h3>
              <v-card variant="tonal">
                <v-card-text class="d-flex align-center ga-4">
                  <v-avatar size="60" color="primary">
                    <v-img v-if="item.avatar" :src="item.avatar"></v-img>
                    <span v-else class="text-h6">{{ item.username?.charAt(0) }}</span>
                  </v-avatar>
                  <div>
                    <div class="text-h6 font-weight-medium">{{ item.username }}</div>
                    <div class="text-body-2 text-grey">
                      <v-icon size="small" color="warning">mdi-star</v-icon>
                      信用分：{{ item.credit_score }}
                    </div>
                  </div>
                </v-card-text>
              </v-card>
            </div>

            <!-- 操作按钮 -->
            <div v-if="isLoggedIn && currentUser?.user_id !== item.user_id" class="d-flex flex-column ga-3">
              <v-btn
                :color="isWishlisted ? 'error' : 'grey'"
                :variant="isWishlisted ? 'flat' : 'outlined'"
                size="large"
                :prepend-icon="isWishlisted ? 'mdi-heart' : 'mdi-heart-outline'"
                :loading="wishlistLoading"
                @click="toggleWishlist"
              >
                {{ isWishlisted ? '已收藏' : '收藏' }}
              </v-btn>

              <v-btn
                color="success"
                size="large"
                prepend-icon="mdi-message-text"
                @click="contactSeller"
              >
                联系卖家
              </v-btn>

              <v-btn
                color="primary"
                size="large"
                prepend-icon="mdi-cart"
                @click="buyNow"
              >
                立即购买
              </v-btn>
            </div>

            <!-- 未登录提示 -->
            <v-alert
              v-else-if="!isLoggedIn"
              type="info"
              variant="tonal"
              class="mb-0"
            >
              <template v-slot:title>
                需要登录
              </template>
              <template v-slot:text>
                <router-link to="/login" class="text-primary text-decoration-none font-weight-medium">
                  登录后可收藏、联系卖家和购买
                </router-link>
              </template>
            </v-alert>
          </v-card>
        </v-col>
      </v-row>

      <!-- 商品描述 -->
      <v-row class="mt-6">
        <v-col cols="12">
          <v-card elevation="2">
            <v-card-title class="text-h5 font-weight-bold">
              <v-icon class="mr-2">mdi-text-box</v-icon>
              商品描述
            </v-card-title>
            <v-divider></v-divider>
            <v-card-text class="text-body-1" style="white-space: pre-wrap; line-height: 1.8;">
              {{ item.description }}
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>
    </div>
  </v-container>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { useNotification } from '@/composables/useNotification'
import { itemAPI, wishlistAPI } from '@/api'
import EmptyState from '@/components/EmptyState.vue'
import type { Item, ConditionLevel } from '@/types'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()
const notification = useNotification()

const item = ref<Item | null>(null)
const loading = ref(false)
const currentImageIndex = ref(0)
const isWishlisted = ref(false)
const wishlistLoading = ref(false)

const isLoggedIn = computed(() => userStore.isLoggedIn)
const currentUser = computed(() => userStore.currentUser)

const conditionMap: Record<string, string> = {
  'brand_new': '全新',
  'like_new': '几乎全新',
  'very_good': '轻微使用',
  'good': '明显使用',
  'acceptable': '磨损较重'
}

const getConditionText = (condition: string): string => {
  return conditionMap[condition] || condition
}

const getConditionColor = (level: ConditionLevel): string => {
  const colorMap: Record<ConditionLevel, string> = {
    brand_new: 'success',
    like_new: 'success',
    very_good: 'info',
    good: 'warning',
    acceptable: 'grey'
  }
  return colorMap[level] || 'grey'
}

const loadItem = async (): Promise<void> => {
  const itemId = route.params.id
  if (!itemId) return

  loading.value = true
  try {
    const response = await itemAPI.getItem(Number(itemId))
    item.value = response.item

    if (isLoggedIn.value && item.value) {
      checkWishlistStatus()
    }
  } catch (error) {
    console.error('Failed to load item:', error)
    notification.error('加载商品失败')
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
      notification.success('已取消收藏')
    } else {
      await wishlistAPI.addToWishlist({
        user_id: currentUser.value.user_id,
        item_id: item.value.item_id
      })
      isWishlisted.value = true
      notification.success('收藏成功')
    }
  } catch (error) {
    console.error('Failed to toggle wishlist:', error)
    notification.error('操作失败')
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
  max-width: 1400px;
}

.thumbnail {
  cursor: pointer;
  opacity: 0.6;
  transition: all 0.3s;
  border-radius: 4px;
  flex-shrink: 0;
}

.thumbnail:hover {
  opacity: 0.9;
}

.thumbnail-active {
  opacity: 1;
  border: 2px solid rgb(var(--v-theme-primary));
}
</style>
