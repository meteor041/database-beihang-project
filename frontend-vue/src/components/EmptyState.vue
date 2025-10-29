<template>
  <div class="empty-state">
    <v-container>
      <v-row justify="center">
        <v-col cols="12" class="text-center">
          <v-img
            v-if="image"
            :src="image"
            :max-width="imageSize"
            class="mx-auto mb-4"
            alt="Empty state"
          ></v-img>
          <v-icon v-else :size="imageSize" color="grey-lighten-1" class="mb-4">
            mdi-inbox-outline
          </v-icon>

          <p class="text-h6 text-grey-darken-1 mb-4">{{ description }}</p>

          <v-btn
            v-if="actionText"
            :color="getColor(actionType)"
            size="large"
            @click="handleAction"
          >
            {{ actionText }}
          </v-btn>
        </v-col>
      </v-row>
    </v-container>
  </div>
</template>

<script setup lang="ts">
interface Props {
  image?: string
  imageSize?: number
  description?: string
  actionText?: string
  actionType?: 'primary' | 'success' | 'warning' | 'error' | 'info'
}

const props = withDefaults(defineProps<Props>(), {
  image: '',
  imageSize: 200,
  description: '暂无数据',
  actionText: '',
  actionType: 'primary'
})

const emit = defineEmits<{
  action: []
}>()

const getColor = (type: string) => {
  const colorMap: Record<string, string> = {
    primary: 'primary',
    success: 'success',
    warning: 'warning',
    error: 'error',
    info: 'info'
  }
  return colorMap[type] || 'primary'
}

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
