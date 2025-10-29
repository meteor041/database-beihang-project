import { ref } from 'vue'

export type NotificationType = 'success' | 'error' | 'warning' | 'info'

export interface Notification {
  id: number
  message: string
  type: NotificationType
  timeout?: number
}

const notifications = ref<Notification[]>([])
let notificationId = 0

export function useNotification() {
  const show = (message: string, type: NotificationType = 'info', timeout: number = 3000) => {
    const id = ++notificationId
    notifications.value.push({
      id,
      message,
      type,
      timeout
    })

    if (timeout > 0) {
      setTimeout(() => {
        remove(id)
      }, timeout)
    }
  }

  const success = (message: string, timeout?: number) => {
    show(message, 'success', timeout)
  }

  const error = (message: string, timeout?: number) => {
    show(message, 'error', timeout)
  }

  const warning = (message: string, timeout?: number) => {
    show(message, 'warning', timeout)
  }

  const info = (message: string, timeout?: number) => {
    show(message, 'info', timeout)
  }

  const remove = (id: number) => {
    const index = notifications.value.findIndex(n => n.id === id)
    if (index !== -1) {
      notifications.value.splice(index, 1)
    }
  }

  return {
    notifications,
    show,
    success,
    error,
    warning,
    info,
    remove
  }
}
