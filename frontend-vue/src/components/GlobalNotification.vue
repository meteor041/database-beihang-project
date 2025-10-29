<template>
  <v-snackbar
    v-for="notification in notifications"
    :key="notification.id"
    v-model="notification.visible"
    :timeout="notification.timeout"
    :color="getColor(notification.type)"
    location="top"
    :multi-line="notification.message.length > 50"
    @update:model-value="(val) => !val && removeNotification(notification.id)"
  >
    <div class="d-flex align-center">
      <v-icon :icon="getIcon(notification.type)" class="mr-2"></v-icon>
      <span>{{ notification.message }}</span>
    </div>

    <template v-slot:actions>
      <v-btn
        icon="mdi-close"
        variant="text"
        size="small"
        @click="removeNotification(notification.id)"
      ></v-btn>
    </template>
  </v-snackbar>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import { useNotification, type Notification } from '@/composables/useNotification'

const { notifications: notificationList } = useNotification()

interface VisibleNotification extends Notification {
  visible: boolean
}

const notifications = ref<VisibleNotification[]>([])

watch(notificationList, (newList) => {
  // 找出新增的通知
  newList.forEach(notification => {
    if (!notifications.value.find(n => n.id === notification.id)) {
      notifications.value.push({
        ...notification,
        visible: true
      })
    }
  })

  // 移除已经不在列表中的通知
  notifications.value = notifications.value.filter(n =>
    notificationList.value.find(nl => nl.id === n.id)
  )
}, { deep: true })

const removeNotification = (id: number) => {
  const notification = notifications.value.find(n => n.id === id)
  if (notification) {
    notification.visible = false
  }
  setTimeout(() => {
    notifications.value = notifications.value.filter(n => n.id !== id)
  }, 300)
}

const getColor = (type: string) => {
  switch (type) {
    case 'success': return 'success'
    case 'error': return 'error'
    case 'warning': return 'warning'
    case 'info': return 'info'
    default: return 'info'
  }
}

const getIcon = (type: string) => {
  switch (type) {
    case 'success': return 'mdi-check-circle'
    case 'error': return 'mdi-alert-circle'
    case 'warning': return 'mdi-alert'
    case 'info': return 'mdi-information'
    default: return 'mdi-information'
  }
}
</script>
