<template>
  <div class="empty-state">
    <el-empty
      :image="image"
      :image-size="imageSize"
      :description="description"
    >
      <template v-if="actionText" #default>
        <el-button :type="actionType" @click="handleAction">
          {{ actionText }}
        </el-button>
      </template>
    </el-empty>
  </div>
</template>

<script setup lang="ts">
interface Props {
  image?: string
  imageSize?: number
  description?: string
  actionText?: string
  actionType?: 'primary' | 'success' | 'warning' | 'danger' | 'info'
}

withDefaults(defineProps<Props>(), {
  image: '',
  imageSize: 200,
  description: '暂无数据',
  actionText: '',
  actionType: 'primary'
})

const emit = defineEmits<{
  action: []
}>()

const handleAction = () => {
  emit('action')
}
</script>

<style scoped>
.empty-state {
  padding: 60px 20px;
  text-align: center;
}
</style>
