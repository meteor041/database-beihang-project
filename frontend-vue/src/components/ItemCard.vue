<template>
  <el-card
    :body-style="{ padding: '0px' }"
    shadow="hover"
    class="item-card"
    @click="handleClick"
  >
    <!-- 商品图片 -->
    <div class="item-image">
      <!-- 有图片时显示图片 -->
      <el-image
        v-if="item.images && item.images[0]"
        :src="item.images[0]"
        :alt="item.title"
        fit="cover"
        lazy
      >
        <template #error>
          <div class="image-slot">
            <div class="placeholder-icon">
              <el-icon><ShoppingBag /></el-icon>
            </div>
          </div>
        </template>
      </el-image>

      <!-- 无图片时显示占位图 -->
      <div v-else class="image-slot">
        <div class="placeholder-icon">
          <el-icon><ShoppingBag /></el-icon>
        </div>
      </div>

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
import { ShoppingBag } from '@element-plus/icons-vue'
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
/* 现代扁平化商品卡片 - Twitter/YouTube/Google 风格 */

.item-card {
  cursor: pointer;
  transition: all var(--transition-base);
  height: 100%;
  display: flex;
  flex-direction: column;
  background: var(--color-bg-card);
  border: 1px solid var(--color-border-base);
  border-radius: var(--radius-lg);
  overflow: hidden;
}

.item-card :deep(.el-card__body) {
  padding: 0;
  height: 100%;
  display: flex;
  flex-direction: column;
}

.item-card:hover {
  border-color: var(--color-border-light);
  box-shadow: var(--shadow-md);
  transform: translateY(-2px);
}

/* 商品图片 */
.item-image {
  position: relative;
  width: 100%;
  height: 200px;
  overflow: hidden;
  background-color: var(--color-neutral-100);
}

.item-image .el-image {
  width: 100%;
  height: 100%;
  transition: transform var(--transition-slow);
}

.item-card:hover .item-image .el-image {
  transform: scale(1.03);
}

.image-slot {
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
.image-slot::before,
.image-slot::after {
  content: '';
  position: absolute;
  border-radius: 50%;
  opacity: 0.1;
}

.image-slot::before {
  width: 200px;
  height: 200px;
  background: var(--el-color-primary);
  top: -80px;
  right: -80px;
}

.image-slot::after {
  width: 150px;
  height: 150px;
  background: var(--el-color-primary);
  bottom: -60px;
  left: -60px;
}

.placeholder-icon {
  position: relative;
  z-index: 1;
  width: 90px;
  height: 90px;
  background: white;
  border-radius: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  transition: transform var(--transition-base);
}

.item-card:hover .placeholder-icon {
  transform: scale(1.05);
}

.placeholder-icon .el-icon {
  font-size: 48px;
  color: var(--el-color-primary);
}

.status-tag {
  position: absolute;
  top: var(--spacing-2);
  right: var(--spacing-2);
}

/* 商品信息 */
.item-info {
  padding: var(--spacing-4);
  flex: 1;
  display: flex;
  flex-direction: column;
}

.item-title {
  font-size: var(--font-size-base);
  font-weight: var(--font-weight-medium);
  color: var(--color-text-primary);
  margin: 0 0 var(--spacing-2) 0;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  line-height: var(--line-height-snug);
  transition: color var(--transition-fast);
}

.item-card:hover .item-title {
  color: var(--color-primary);
}

.item-description {
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
  margin: 0 0 var(--spacing-3) 0;
  line-height: var(--line-height-relaxed);
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

/* 价格和成色 */
.item-details {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--spacing-3);
}

.price-section {
  display: flex;
  align-items: baseline;
  gap: var(--spacing-2);
}

.current-price {
  font-size: var(--font-size-2xl);
  font-weight: var(--font-weight-bold);
  color: var(--color-price);
}

.original-price {
  font-size: var(--font-size-sm);
  color: var(--color-text-placeholder);
  text-decoration: line-through;
}

/* 元信息 */
.item-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: auto;
  padding-top: var(--spacing-3);
  border-top: 1px solid var(--color-border-light);
}

.seller-info {
  display: flex;
  align-items: center;
  gap: var(--spacing-2);
}

.seller-name {
  font-size: var(--font-size-xs);
  color: var(--color-text-secondary);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  max-width: 100px;
}

.stats {
  display: flex;
  gap: var(--spacing-3);
}

.stat-item {
  display: flex;
  align-items: center;
  gap: var(--spacing-1);
  font-size: var(--font-size-xs);
  color: var(--color-text-secondary);
}

.stat-item .el-icon {
  font-size: 14px;
}

/* 响应式 */
@media (max-width: 768px) {
  .item-image {
    height: 180px;
  }

  .item-info {
    padding: var(--spacing-3);
  }

  .item-title {
    font-size: var(--font-size-sm);
  }

  .current-price {
    font-size: var(--font-size-xl);
  }

  .seller-name {
    max-width: 80px;
  }
}
</style>
