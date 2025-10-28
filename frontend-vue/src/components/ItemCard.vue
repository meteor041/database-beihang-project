<template>
  <el-card
    :body-style="{ padding: '0px' }"
    shadow="hover"
    class="item-card"
    @click="handleClick"
  >
    <!-- 商品图片 -->
    <div class="item-image">
      <el-image
        :src="item.images && item.images[0] ? item.images[0] : '/placeholder.png'"
        :alt="item.title"
        fit="cover"
        lazy
      >
        <template #error>
          <div class="image-slot">
            <el-icon><Picture /></el-icon>
          </div>
        </template>
      </el-image>

      <!-- 商品状态标签 -->
      <el-tag
        v-if="item.status === 'sold'"
        class="status-tag"
        type="info"
        size="small"
      >
        已售出
      </el-tag>
    </div>

    <!-- 商品信息 -->
    <div class="item-info">
      <h3 class="item-title">{{ item.title }}</h3>

      <p v-if="showDescription" class="item-description">
        {{ truncatedDescription }}
      </p>

      <!-- 价格和成色 -->
      <div class="item-details">
        <div class="price-section">
          <span class="current-price">¥{{ item.price }}</span>
          <span v-if="item.original_price" class="original-price">
            ¥{{ item.original_price }}
          </span>
        </div>
        <el-tag size="small" :type="getConditionType(item.condition_level)">
          {{ getConditionText(item.condition_level) }}
        </el-tag>
      </div>

      <!-- 元信息 -->
      <div class="item-meta">
        <div class="seller-info">
          <el-avatar
            v-if="item.username"
            :size="20"
            :src="item.avatar"
          >
            {{ item.username?.charAt(0) }}
          </el-avatar>
          <span class="seller-name">{{ item.username }}</span>
        </div>

        <div class="stats">
          <span class="stat-item">
            <el-icon><View /></el-icon>
            {{ item.view_count || 0 }}
          </span>
          <span v-if="showWishlistCount && wishlistCount > 0" class="stat-item">
            <el-icon><Star /></el-icon>
            {{ wishlistCount }}
          </span>
        </div>
      </div>
    </div>
  </el-card>
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

// 获取成色对应的标签类型
const getConditionType = (level: ConditionLevel): 'success' | 'warning' | 'info' | '' => {
  const typeMap: Record<ConditionLevel, 'success' | 'warning' | 'info' | ''> = {
    brand_new: 'success',
    like_new: 'success',
    very_good: '',
    good: 'warning',
    acceptable: 'info'
  }
  return typeMap[level] || ''
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
  transition: all 0.3s ease;
  height: 100%;
  display: flex;
  flex-direction: column;
}

.item-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.12);
}

.item-image {
  position: relative;
  width: 100%;
  height: 200px;
  overflow: hidden;
  background-color: #f5f7fa;
}

.item-image .el-image {
  width: 100%;
  height: 100%;
}

.image-slot {
  display: flex;
  justify-content: center;
  align-items: center;
  width: 100%;
  height: 100%;
  background-color: #f5f7fa;
  color: #909399;
}

.image-slot .el-icon {
  font-size: 40px;
}

.status-tag {
  position: absolute;
  top: 10px;
  right: 10px;
}

.item-info {
  padding: 15px;
  flex: 1;
  display: flex;
  flex-direction: column;
}

.item-title {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
  margin: 0 0 8px 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.item-description {
  font-size: 13px;
  color: #606266;
  margin: 0 0 12px 0;
  line-height: 1.5;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.item-details {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.price-section {
  display: flex;
  align-items: baseline;
  gap: 8px;
}

.current-price {
  font-size: 20px;
  font-weight: 700;
  color: #f56c6c;
}

.original-price {
  font-size: 14px;
  color: #909399;
  text-decoration: line-through;
}

.item-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: auto;
  padding-top: 12px;
  border-top: 1px solid #f0f0f0;
}

.seller-info {
  display: flex;
  align-items: center;
  gap: 6px;
}

.seller-name {
  font-size: 13px;
  color: #606266;
}

.stats {
  display: flex;
  gap: 12px;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 13px;
  color: #909399;
}

.stat-item .el-icon {
  font-size: 14px;
}

@media (max-width: 768px) {
  .item-image {
    height: 150px;
  }

  .item-title {
    font-size: 14px;
  }

  .current-price {
    font-size: 18px;
  }
}
</style>
