<template>
  <v-card
    class="item-card"
    elevation="2"
    hover
    @click="handleClick"
  >
    <!-- 商品图片 -->
    <div class="item-image">
      <v-img
        :src="item.images && item.images[0] ? item.images[0] : '/placeholder.png'"
        :alt="item.title"
        cover
        height="200"
      >
        <template v-slot:error>
          <div class="d-flex align-center justify-center fill-height bg-grey-lighten-3">
            <v-icon size="40" color="grey">mdi-image-off</v-icon>
          </div>
        </template>
      </v-img>

      <!-- 商品状态标签 -->
      <v-chip
        v-if="item.status === 'sold'"
        class="status-tag"
        color="info"
        size="small"
      >
        已售出
      </v-chip>
    </div>

    <!-- 商品信息 -->
    <v-card-text class="item-info">
      <h3 class="item-title text-subtitle-1 font-weight-bold">{{ item.title }}</h3>

      <p v-if="showDescription" class="item-description text-body-2 text-grey-darken-1">
        {{ truncatedDescription }}
      </p>

      <!-- 价格和成色 -->
      <div class="item-details d-flex justify-space-between align-center my-3">
        <div class="price-section d-flex align-baseline">
          <span class="current-price text-h6 font-weight-bold text-error">¥{{ item.price }}</span>
          <span v-if="item.original_price" class="original-price text-body-2 text-grey ml-2">
            ¥{{ item.original_price }}
          </span>
        </div>
        <v-chip
          size="small"
          :color="getConditionColor(item.condition_level)"
          variant="flat"
        >
          {{ getConditionText(item.condition_level) }}
        </v-chip>
      </div>

      <!-- 元信息 -->
      <v-divider class="my-2"></v-divider>
      <div class="item-meta d-flex justify-space-between align-center">
        <div class="seller-info d-flex align-center">
          <v-avatar
            v-if="item.username"
            size="24"
            :color="item.avatar ? undefined : 'primary'"
          >
            <v-img v-if="item.avatar" :src="item.avatar"></v-img>
            <span v-else class="text-caption">{{ item.username?.charAt(0) }}</span>
          </v-avatar>
          <span class="seller-name text-caption text-grey-darken-1 ml-2">{{ item.username }}</span>
        </div>

        <div class="stats d-flex ga-3">
          <span class="stat-item text-caption text-grey d-flex align-center">
            <v-icon size="16" class="mr-1">mdi-eye</v-icon>
            {{ item.view_count || 0 }}
          </span>
          <span v-if="showWishlistCount && wishlistCount > 0" class="stat-item text-caption text-grey d-flex align-center">
            <v-icon size="16" class="mr-1">mdi-star</v-icon>
            {{ wishlistCount }}
          </span>
        </div>
      </div>
    </v-card-text>
  </v-card>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { Item, ConditionLevel } from '@/types'

interface Props {
  item: Item
  showDescription?: boolean
  showWishlistCount?: boolean
  wishlistCount?: number
}

const props = withDefaults(defineProps<Props>(), {
  showDescription: false,
  showWishlistCount: false,
  wishlistCount: 0
})

const emit = defineEmits<{
  click: [item: Item]
}>()

// 截断描述文本
const truncatedDescription = computed(() => {
  if (!props.item.description) return ''
  return props.item.description.length > 80
    ? props.item.description.slice(0, 80) + '...'
    : props.item.description
})

// 获取成色对应的颜色
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

// 获取成色文本
const getConditionText = (level: ConditionLevel): string => {
  const textMap: Record<ConditionLevel, string> = {
    brand_new: '全新',
    like_new: '几乎全新',
    very_good: '轻微使用',
    good: '明显使用',
    acceptable: '磨损较重'
  }
  return textMap[level] || level
}

const handleClick = () => {
  emit('click', props.item)
}
</script>

<style scoped>
.item-card {
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  height: 100%;
  display: flex;
  flex-direction: column;
}

.item-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.15) !important;
}

.item-image {
  position: relative;
  width: 100%;
  overflow: hidden;
}

.status-tag {
  position: absolute;
  top: 10px;
  right: 10px;
  z-index: 1;
}

.item-info {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.item-title {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  margin-bottom: 8px;
}

.item-description {
  margin-bottom: 12px;
  line-height: 1.5;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.current-price {
  color: #f56c6c;
}

.original-price {
  text-decoration: line-through;
}

@media (max-width: 768px) {
  .item-title {
    font-size: 14px;
  }

  .current-price {
    font-size: 18px;
  }
}
</style>
