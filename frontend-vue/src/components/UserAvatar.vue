<template>
  <div class="user-avatar-wrapper">
    <v-avatar
      :size="avatarSize"
      :color="avatar ? undefined : 'primary'"
      :class="{ clickable: clickable }"
      @click="handleClick"
    >
      <v-img v-if="avatar" :src="avatar" alt="Avatar" cover></v-img>
      <span v-else class="text-h6">{{ fallbackText }}</span>
    </v-avatar>

    <!-- 信用分星级显示 -->
    <div v-if="showCreditScore && creditScore !== undefined" class="credit-score">
      <v-rating
        :model-value="creditStars"
        readonly
        density="compact"
        color="amber"
        half-increments
        size="small"
      ></v-rating>
      <span class="credit-text">{{ creditScore }}分</span>
    </div>

    <!-- 在线状态指示器 -->
    <div v-if="showOnlineStatus" :class="['online-indicator', { online: isOnline }]" />
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  avatar?: string
  username?: string
  creditScore?: number
  showCreditScore?: boolean
  showOnlineStatus?: boolean
  isOnline?: boolean
  size?: number
  clickable?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  avatar: '',
  username: '',
  creditScore: undefined,
  showCreditScore: false,
  showOnlineStatus: false,
  isOnline: false,
  size: 40,
  clickable: false
})

const emit = defineEmits<{
  click: []
}>()

// 计算头像尺寸
const avatarSize = computed(() => props.size)

// 头像备用文字（用户名首字母）
const fallbackText = computed(() => {
  if (!props.username) return '?'
  return props.username.charAt(0).toUpperCase()
})

// 信用分转换为星级（满分100分，5星）
const creditStars = computed(() => {
  if (props.creditScore === undefined) return 0
  return (props.creditScore / 100) * 5
})

const handleClick = () => {
  if (props.clickable) {
    emit('click')
  }
}
</script>

<style scoped>
.user-avatar-wrapper {
  position: relative;
  display: inline-flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
}

.clickable {
  cursor: pointer;
  transition: transform 0.2s;
}

.clickable:hover {
  transform: scale(1.1);
}

.credit-score {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  font-size: 12px;
}

.credit-text {
  font-size: 12px;
  color: #666;
}

.online-indicator {
  position: absolute;
  bottom: 0;
  right: 0;
  width: 12px;
  height: 12px;
  border-radius: 50%;
  border: 2px solid #fff;
  background-color: #c0c4cc;
}

.online-indicator.online {
  background-color: #67c23a;
  box-shadow: 0 0 4px rgba(103, 194, 58, 0.5);
}
</style>
