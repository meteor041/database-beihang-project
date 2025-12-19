<template>
  <div class="messages-view">
    <div class="messages-container">
      <!-- 左侧会话列表 -->
      <div class="conversations-sidebar">
        <div class="sidebar-header">
          <h2>消息</h2>
          <div class="header-actions">
            <el-tooltip content="刷新" placement="bottom">
              <el-button
                :icon="Refresh"
                circle
                size="small"
                @click="loadConversations"
                :loading="conversationsLoading"
              />
            </el-tooltip>
          </div>
        </div>

        <div v-if="conversationsLoading && conversations.length === 0" class="loading">
          <el-icon class="is-loading"><Loading /></el-icon>
          <span>加载中...</span>
        </div>

        <div v-else-if="conversations.length === 0" class="no-conversations">
          <el-empty description="暂无会话" :image-size="80" />
        </div>

        <div v-else class="conversation-items">
          <div
            v-for="conversation in conversations"
            :key="`${conversation.other_user_id}-${conversation.item_id}`"
            :class="['conversation-item', { active: isActiveConversation(conversation) }]"
            @click="selectConversation(conversation)"
          >
            <el-avatar
              :src="conversation.other_avatar || undefined"
              :size="48"
              class="user-avatar"
            >
              {{ conversation.other_username?.charAt(0) }}
            </el-avatar>
            <div class="conversation-info">
              <div class="conversation-header">
                <span class="username">{{ conversation.other_username }}</span>
                <span class="time">{{ formatTime(conversation.last_message_time) }}</span>
              </div>
              <div class="item-title">关于: {{ conversation.item_title }}</div>
              <div class="last-message">{{ conversation.last_message }}</div>
            </div>
            <el-badge
              v-if="conversation.unread_count > 0"
              :value="conversation.unread_count > 99 ? '99+' : conversation.unread_count"
              class="unread-badge"
            />
          </div>
        </div>
      </div>

      <!-- 右侧聊天区域 -->
      <div class="chat-area">
        <div v-if="!selectedConversation" class="no-selection">
          <div class="no-selection-content">
            <el-icon :size="80" color="var(--color-primary)"><ChatDotRound /></el-icon>
            <p>选择一个会话开始聊天</p>
          </div>
        </div>

        <div v-else class="chat-container">
          <!-- 聊天头部 -->
          <div class="chat-header">
            <div class="chat-info">
              <el-button
                class="back-button"
                :icon="ArrowLeft"
                circle
                size="small"
                @click="selectedConversation = null"
              />
              <el-avatar
                :src="selectedConversation.other_avatar || undefined"
                :size="40"
              >
                {{ selectedConversation.other_username?.charAt(0) }}
              </el-avatar>
              <div class="chat-user-info">
                <div class="username">
                  {{ selectedConversation.other_username }}
                </div>
                <div class="item-title" @click="goToItem">
                  <el-icon><Goods /></el-icon>
                  {{ selectedConversation.item_title }}
                </div>
              </div>
            </div>
            <div class="header-actions">
              <el-tooltip content="刷新消息" placement="bottom">
                <el-button
                  :icon="Refresh"
                  circle
                  size="small"
                  @click="loadMessages"
                  :loading="messagesLoading"
                />
              </el-tooltip>
            </div>
          </div>

          <!-- 消息列表区域 -->
          <div class="messages-area" ref="messagesArea">
            <div v-if="messagesLoading && messages.length === 0" class="loading">
              <el-icon class="is-loading"><Loading /></el-icon>
              <span>加载消息中...</span>
            </div>

            <div v-else class="message-list">
              <!-- 时间分割线 -->
              <template v-for="(message, index) in messages" :key="message.message_id">
                <div
                  v-if="shouldShowDateDivider(index)"
                  class="date-divider"
                >
                  <span>{{ formatDateDivider(message.send_time) }}</span>
                </div>

                <div
                  :class="[
                    'message-wrapper',
                    {
                      'own-message': message.sender_id === currentUser?.user_id,
                      'withdrawn': message.is_withdrawn
                    }
                  ]"
                  @contextmenu.prevent="showContextMenu($event, message)"
                >
                  <!-- 对方头像（非自己的消息显示） -->
                  <el-avatar
                    v-if="message.sender_id !== currentUser?.user_id"
                    :src="selectedConversation.other_avatar || undefined"
                    :size="32"
                    class="message-avatar"
                  >
                    {{ selectedConversation.other_username?.charAt(0) }}
                  </el-avatar>

                  <div class="message-content">
                    <!-- 已撤回的消息 -->
                    <div v-if="message.is_withdrawn" class="message-withdrawn">
                      <el-icon><InfoFilled /></el-icon>
                      {{ message.sender_id === currentUser?.user_id ? '你撤回了一条消息' : '对方撤回了一条消息' }}
                    </div>

                    <!-- 正常消息 -->
                    <div v-else class="message-bubble">
                      <div class="message-text">{{ message.content }}</div>

                      <!-- 消息底部：时间 + 状态 -->
                      <div class="message-footer">
                        <span class="message-time">{{ formatMessageTime(message.send_time) }}</span>
                        <!-- 自己发送的消息显示状态 -->
                        <span v-if="message.sender_id === currentUser?.user_id" class="message-status">
                          <!-- 发送中 -->
                          <el-icon v-if="message.sending" class="is-loading status-sending"><Loading /></el-icon>
                          <!-- 发送失败 -->
                          <el-icon v-else-if="message.failed" class="status-failed" @click="retrySend(message)">
                            <WarningFilled />
                          </el-icon>
                          <!-- 已读 -->
                          <span v-else-if="message.is_read" class="status-read">
                            <el-icon><Check /></el-icon>
                            <el-icon><Check /></el-icon>
                          </span>
                          <!-- 已送达 -->
                          <span v-else class="status-sent">
                            <el-icon><Check /></el-icon>
                          </span>
                        </span>
                      </div>
                    </div>
                  </div>
                </div>
              </template>
            </div>
          </div>

          <!-- 消息输入框 -->
          <div class="message-input">
            <div class="input-wrapper">
              <el-input
                v-model="newMessage"
                type="textarea"
                :rows="3"
                placeholder="输入消息... (Enter 发送, Shift+Enter 换行)"
                @keydown.enter.exact.prevent="sendMessage"
                resize="none"
                class="message-textarea"
                :maxlength="500"
                show-word-limit
              />
              <el-button
                type="primary"
                @click="sendMessage"
                :disabled="!newMessage.trim() || sendingMessage"
                :loading="sendingMessage"
                size="large"
                class="send-button"
              >
                <el-icon v-if="!sendingMessage"><Promotion /></el-icon>
                发送
              </el-button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 右键菜单 -->
    <div
      v-if="contextMenu.visible"
      class="context-menu"
      :style="{ top: contextMenu.y + 'px', left: contextMenu.x + 'px' }"
      @click.stop
    >
      <div
        v-if="contextMenu.message?.sender_id === currentUser?.user_id && canWithdraw(contextMenu.message)"
        class="context-menu-item"
        @click="withdrawMessage"
      >
        <el-icon><RefreshLeft /></el-icon>
        撤回
      </div>
      <div class="context-menu-item" @click="copyMessage">
        <el-icon><DocumentCopy /></el-icon>
        复制
      </div>
    </div>

    <!-- 点击其他区域关闭右键菜单 -->
    <div
      v-if="contextMenu.visible"
      class="context-menu-overlay"
      @click="closeContextMenu"
    ></div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, computed, nextTick, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { messageAPI, userAPI, itemAPI } from '@/api'
import { ElMessage, ElMessageBox } from 'element-plus'
import type { Conversation, Message } from '@/types'
import {
  Loading, ChatDotRound, Promotion, Refresh, ArrowLeft, Goods,
  Check, WarningFilled, RefreshLeft, DocumentCopy, InfoFilled
} from '@element-plus/icons-vue'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()

// 扩展 Message 类型
interface ExtendedMessage extends Message {
  sending?: boolean
  failed?: boolean
  is_withdrawn?: boolean
  tempId?: string
}

const conversations = ref<Conversation[]>([])
const messages = ref<ExtendedMessage[]>([])
const selectedConversation = ref<Conversation | null>(null)
const newMessage = ref('')

const conversationsLoading = ref(false)
const messagesLoading = ref(false)
const sendingMessage = ref(false)

const messagesArea = ref<HTMLElement | null>(null)

// 轮询相关
let pollingTimer: ReturnType<typeof setInterval> | null = null
const POLLING_INTERVAL = 5000 // 5秒轮询一次

// 右键菜单
const contextMenu = ref({
  visible: false,
  x: 0,
  y: 0,
  message: null as ExtendedMessage | null
})

const currentUser = computed(() => userStore.currentUser)

// 格式化本地时间为服务器格式 (YYYY-MM-DD HH:MM:SS)
const formatLocalTime = (date: Date): string => {
  const pad = (n: number) => n.toString().padStart(2, '0')
  return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())} ${pad(date.getHours())}:${pad(date.getMinutes())}:${pad(date.getSeconds())}`
}

// 解析时间字符串（处理多种格式）
const parseTime = (timeString: string): Date => {
  if (!timeString) return new Date()

  // 如果是 ISO 格式带 Z（UTC时间），直接解析
  if (timeString.endsWith('Z')) {
    return new Date(timeString)
  }

  // 处理 "YYYY-MM-DD HH:MM:SS" 格式（服务器返回的本地时间）
  // 替换空格为T，但不加Z，这样会被解析为本地时间
  const normalized = timeString.replace(' ', 'T')
  const date = new Date(normalized)

  if (isNaN(date.getTime())) {
    console.warn('Failed to parse time:', timeString)
    return new Date()
  }

  return date
}

// 格式化时间（会话列表）
const formatTime = (timeString: string): string => {
  const date = parseTime(timeString)
  const now = new Date()
  const diff = now.getTime() - date.getTime()

  // 处理时间差为负数的情况（时区问题或时钟不同步）
  if (diff < -60000) {
    // 超过1分钟的未来时间，显示具体时间
    return date.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
  } else if (diff < 60000) {
    return '刚刚'
  } else if (diff < 3600000) {
    return `${Math.floor(diff / 60000)}分钟前`
  } else if (diff < 86400000) {
    return `${Math.floor(diff / 3600000)}小时前`
  } else if (diff < 172800000) {
    return '昨天'
  } else {
    return date.toLocaleDateString('zh-CN', { month: 'numeric', day: 'numeric' })
  }
}

// 格式化消息时间（聊天气泡）
const formatMessageTime = (timeString: string): string => {
  const date = parseTime(timeString)
  return date.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
}

// 格式化日期分割线
const formatDateDivider = (timeString: string): string => {
  const date = parseTime(timeString)
  const now = new Date()
  const today = new Date(now.getFullYear(), now.getMonth(), now.getDate())
  const messageDate = new Date(date.getFullYear(), date.getMonth(), date.getDate())
  const diff = today.getTime() - messageDate.getTime()
  const days = Math.floor(diff / 86400000)

  // 处理负数天数（未来日期，可能是时区问题）
  if (days < 0) {
    return date.toLocaleDateString('zh-CN', { year: 'numeric', month: 'long', day: 'numeric' })
  }
  if (days === 0) return '今天'
  if (days === 1) return '昨天'
  if (days < 7) return `${days}天前`
  return date.toLocaleDateString('zh-CN', { year: 'numeric', month: 'long', day: 'numeric' })
}

// 是否显示日期分割线
const shouldShowDateDivider = (index: number): boolean => {
  if (index === 0) return true
  const currentMsg = messages.value[index]
  const previousMsg = messages.value[index - 1]
  if (!currentMsg || !previousMsg) return false
  const current = parseTime(currentMsg.send_time)
  const previous = parseTime(previousMsg.send_time)
  // 如果日期不同，显示分割线
  return current.toDateString() !== previous.toDateString()
}

// 判断是否可以撤回（2分钟内）
const canWithdraw = (message: ExtendedMessage | null): boolean => {
  if (!message) return false
  const sendTime = parseTime(message.send_time).getTime()
  const now = Date.now()
  return now - sendTime < 2 * 60 * 1000 // 2分钟
}

const isActiveConversation = (conversation: Conversation): boolean => {
  return selectedConversation.value !== null &&
    selectedConversation.value.other_user_id === conversation.other_user_id &&
    selectedConversation.value.item_id === conversation.item_id
}

const loadConversations = async (): Promise<void> => {
  if (!userStore.isLoggedIn || !currentUser.value) {
    router.push('/login')
    return
  }

  conversationsLoading.value = true
  try {
    const response = await messageAPI.getConversations(currentUser.value.user_id)
    conversations.value = response.conversations || []
  } catch (error) {
    console.error('Failed to load conversations:', error)
  } finally {
    conversationsLoading.value = false
  }
}

const loadMessages = async (silent = false): Promise<void> => {
  if (!selectedConversation.value || !currentUser.value) return

  if (!silent) {
    messagesLoading.value = true
  }

  try {
    const response = await messageAPI.getConversationMessages({
      user_id: currentUser.value.user_id,
      other_user_id: selectedConversation.value.other_user_id,
      item_id: selectedConversation.value.item_id,
      page: 1,
      limit: 50
    })

    const newMessages = (response.messages || []).reverse()

    // 保留正在发送的消息
    const sendingMessages = messages.value.filter(m => m.sending)

    // 合并消息，避免重复
    const existingIds = new Set(newMessages.map(m => m.message_id))
    const filteredSending = sendingMessages.filter(m => !existingIds.has(m.message_id))

    messages.value = [...newMessages, ...filteredSending]

    if (!silent) {
      nextTick(() => {
        scrollToBottom()
      })
    }

    // 更新会话的未读数
    if (selectedConversation.value) {
      const conv = conversations.value.find(c =>
        c.other_user_id === selectedConversation.value!.other_user_id &&
        c.item_id === selectedConversation.value!.item_id
      )
      if (conv) {
        conv.unread_count = 0
      }
    }
  } catch (error) {
    console.error('Failed to load messages:', error)
  } finally {
    messagesLoading.value = false
  }
}

const selectConversation = (conversation: Conversation): void => {
  selectedConversation.value = conversation
  loadMessages()
  startPolling()
}

// 生成临时ID
const generateTempId = (): string => {
  return `temp_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
}

const sendMessage = async (): Promise<void> => {
  if (!newMessage.value.trim() || !selectedConversation.value || sendingMessage.value || !currentUser.value) {
    return
  }

  const messageContent = newMessage.value.trim()
  const tempId = generateTempId()

  // 乐观更新：立即显示消息
  const optimisticMessage: ExtendedMessage = {
    message_id: -1, // 临时ID
    tempId,
    sender_id: currentUser.value.user_id,
    receiver_id: selectedConversation.value.other_user_id,
    item_id: selectedConversation.value.item_id,
    content: messageContent,
    message_type: 'text',
    send_time: formatLocalTime(new Date()),
    is_read: false,
    sending: true
  }

  messages.value.push(optimisticMessage)
  newMessage.value = ''

  nextTick(() => {
    scrollToBottom()
  })

  sendingMessage.value = true

  try {
    const response = await messageAPI.sendMessage({
      sender_id: currentUser.value.user_id,
      receiver_id: selectedConversation.value.other_user_id,
      item_id: selectedConversation.value.item_id,
      content: messageContent,
      message_type: 'text'
    })

    // 更新乐观消息为真实消息
    const index = messages.value.findIndex(m => m.tempId === tempId)
    if (index !== -1 && messages.value[index]) {
      const msg = messages.value[index]
      msg.message_id = response.message_id
      msg.sending = false
      msg.failed = false
    }

    // 刷新会话列表以更新最后消息
    loadConversations()
  } catch (error) {
    console.error('Failed to send message:', error)
    // 标记发送失败
    const index = messages.value.findIndex(m => m.tempId === tempId)
    if (index !== -1 && messages.value[index]) {
      const msg = messages.value[index]
      msg.sending = false
      msg.failed = true
    }
    ElMessage.error('发送失败，点击重试')
  } finally {
    sendingMessage.value = false
  }
}

// 重新发送失败的消息
const retrySend = async (message: ExtendedMessage): Promise<void> => {
  if (!selectedConversation.value || !currentUser.value) return

  message.sending = true
  message.failed = false

  try {
    const response = await messageAPI.sendMessage({
      sender_id: currentUser.value.user_id,
      receiver_id: selectedConversation.value.other_user_id,
      item_id: selectedConversation.value.item_id,
      content: message.content,
      message_type: message.message_type
    })

    message.message_id = response.message_id
    message.sending = false
    loadConversations()
  } catch (error) {
    console.error('Failed to resend message:', error)
    message.sending = false
    message.failed = true
    ElMessage.error('发送失败')
  }
}

// 右键菜单
const showContextMenu = (event: MouseEvent, message: ExtendedMessage): void => {
  if (message.is_withdrawn || message.sending) return

  contextMenu.value = {
    visible: true,
    x: event.clientX,
    y: event.clientY,
    message
  }
}

const closeContextMenu = (): void => {
  contextMenu.value.visible = false
  contextMenu.value.message = null
}

// 撤回消息
const withdrawMessage = async (): Promise<void> => {
  const message = contextMenu.value.message
  if (!message || !currentUser.value) return

  try {
    await messageAPI.deleteMessage(message.message_id, {
      user_id: currentUser.value.user_id
    })

    // 标记为已撤回
    message.is_withdrawn = true
    ElMessage.success('消息已撤回')
    loadConversations()
  } catch (error: any) {
    console.error('Failed to withdraw message:', error)
    if (error.response?.data?.error?.includes('2 minutes')) {
      ElMessage.error('超过2分钟的消息无法撤回')
    } else {
      ElMessage.error('撤回失败')
    }
  } finally {
    closeContextMenu()
  }
}

// 复制消息
const copyMessage = async (): Promise<void> => {
  const message = contextMenu.value.message
  if (!message || message.message_type !== 'text') {
    ElMessage.warning('只能复制文本消息')
    closeContextMenu()
    return
  }

  try {
    await navigator.clipboard.writeText(message.content)
    ElMessage.success('已复制到剪贴板')
  } catch (error) {
    console.error('Failed to copy:', error)
    ElMessage.error('复制失败')
  }
  closeContextMenu()
}

// 跳转到商品详情
const goToItem = (): void => {
  if (selectedConversation.value) {
    router.push(`/items/${selectedConversation.value.item_id}`)
  }
}

const scrollToBottom = (): void => {
  if (messagesArea.value) {
    messagesArea.value.scrollTop = messagesArea.value.scrollHeight
  }
}

// 轮询
const startPolling = (): void => {
  stopPolling()
  pollingTimer = setInterval(() => {
    if (selectedConversation.value) {
      loadMessages(true) // 静默刷新
    }
    loadConversations() // 刷新会话列表
  }, POLLING_INTERVAL)
}

const stopPolling = (): void => {
  if (pollingTimer) {
    clearInterval(pollingTimer)
    pollingTimer = null
  }
}

// 处理从商品详情页跳转过来的情况（联系卖家）
const parseQueryNumber = (value: unknown): number | null => {
  const raw = Array.isArray(value) ? value[0] : value
  if (raw === undefined || raw === null) return null
  const num = Number(raw)
  return Number.isNaN(num) ? null : num
}

const handleQueryParams = async () => {
  const userIdNum = parseQueryNumber(route.query.user_id)
  const itemIdNum = parseQueryNumber(route.query.item_id)

  if (userIdNum === null || itemIdNum === null || !currentUser.value) return

  // 先在现有会话列表中查找
  const existingConversation = conversations.value.find(conv =>
    conv.other_user_id === userIdNum && conv.item_id === itemIdNum
  )

  if (existingConversation) {
    selectConversation(existingConversation)
  } else {
    // 没找到会话，创建临时会话
    try {
      const [userResponse, itemResponse] = await Promise.all([
        userAPI.getUser(userIdNum),
        itemAPI.getItem(itemIdNum)
      ])

      const tempConversation: Conversation = {
        other_user_id: userIdNum,
        other_username: userResponse.user.username,
        other_avatar: userResponse.user.avatar,
        item_id: itemIdNum,
        item_title: itemResponse.item.title,
        item_images: itemResponse.item.images || [],
        last_message_time: formatLocalTime(new Date()),
        last_message: '',
        unread_count: 0
      }

      selectedConversation.value = tempConversation
      messages.value = []
      startPolling()
    } catch (error) {
      console.error('Failed to create temporary conversation:', error)
      ElMessage.error('无法加载会话信息')
    }
  }
}

watch(() => route.query, () => {
  if (conversations.value.length > 0) {
    handleQueryParams()
  }
}, { immediate: false })

watch(conversations, () => {
  if (route.query.user_id && route.query.item_id) {
    handleQueryParams()
  }
}, { once: true })

onMounted(async () => {
  if (!userStore.isLoggedIn) {
    router.push('/login')
    return
  }

  await loadConversations()

  if (route.query.user_id && route.query.item_id) {
    await handleQueryParams()
  }

  // 开始轮询会话列表
  startPolling()
})

onUnmounted(() => {
  stopPolling()
})
</script>

<style scoped>
/* 现代化消息页面 - 全屏布局 */

.messages-view {
  width: 100%;
  padding: var(--spacing-4) var(--spacing-6);
  height: calc(100vh - var(--spacing-4) * 2);
  box-sizing: border-box;
}

/* 消息容器 - 全屏高度 */
.messages-container {
  display: grid;
  grid-template-columns: 380px 1fr;
  gap: 0;
  height: 100%;
  background: var(--color-bg-card);
  border: 1px solid var(--color-border-base);
  border-radius: var(--radius-xl);
  overflow: hidden;
  box-shadow: var(--shadow-lg);
}

/* 左侧会话列表 */
.conversations-sidebar {
  border-right: 1px solid var(--color-border-base);
  display: flex;
  flex-direction: column;
  background: var(--color-bg-section);
  height: 100%;
  min-height: 0;
}

.sidebar-header {
  padding: var(--spacing-4) var(--spacing-5);
  border-bottom: 1px solid var(--color-border-light);
  background: var(--color-bg-card);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.sidebar-header h2 {
  margin: 0;
  font-size: var(--font-size-xl);
  font-weight: var(--font-weight-bold);
  color: var(--color-text-primary);
}

.header-actions {
  display: flex;
  gap: var(--spacing-2);
}

/* 加载和空状态 */
.loading,
.no-conversations {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: var(--spacing-8);
  color: var(--color-text-secondary);
  gap: var(--spacing-2);
}

.conversation-items {
  flex: 1;
  overflow-y: auto;
  min-height: 0;
}

/* 会话项 */
.conversation-item {
  display: flex;
  align-items: flex-start;
  gap: var(--spacing-3);
  padding: var(--spacing-4);
  cursor: pointer;
  transition: all 0.2s ease;
  border-bottom: 1px solid var(--color-border-lighter);
  position: relative;
  background: var(--color-bg-card);
}

.conversation-item:hover {
  background: var(--color-bg-hover);
}

.conversation-item.active {
  background: var(--color-primary-lighter);
  border-left: 3px solid var(--color-primary);
}

.conversation-info {
  flex: 1;
  min-width: 0;
}

.conversation-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--spacing-1);
}

.username {
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
  font-size: var(--font-size-base);
}

.time {
  font-size: var(--font-size-xs);
  color: var(--color-text-placeholder);
  flex-shrink: 0;
  margin-left: var(--spacing-2);
}

.item-title {
  font-size: var(--font-size-xs);
  color: var(--color-text-secondary);
  margin-bottom: var(--spacing-1);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  display: flex;
  align-items: center;
  gap: var(--spacing-1);
  cursor: pointer;
}

.item-title:hover {
  color: var(--color-primary);
}

.last-message {
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.withdrawn-hint {
  color: var(--color-text-placeholder);
  font-style: italic;
}

.unread-badge {
  position: absolute;
  top: var(--spacing-3);
  right: var(--spacing-3);
}

/* 右侧聊天区域 */
.chat-area {
  display: flex;
  flex-direction: column;
  background: #f5f7fa;
  height: 100%;
  min-height: 0;
}

.no-selection {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
}

.no-selection-content {
  text-align: center;
  color: var(--color-text-secondary);
}

.no-selection-content p {
  margin-top: var(--spacing-4);
  font-size: var(--font-size-lg);
}

.chat-container {
  display: flex;
  flex-direction: column;
  height: 100%;
  min-height: 0;
}

/* 聊天头部 */
.chat-header {
  padding: var(--spacing-3) var(--spacing-5);
  border-bottom: 1px solid var(--color-border-light);
  background: var(--color-bg-card);
  flex-shrink: 0;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.chat-info {
  display: flex;
  align-items: center;
  gap: var(--spacing-3);
}

.back-button {
  display: none;
}

.chat-user-info {
  flex: 1;
}

.chat-user-info .username {
  font-size: var(--font-size-base);
  font-weight: var(--font-weight-semibold);
  margin-bottom: 2px;
}

.chat-user-info .item-title {
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
}

/* 消息列表区域 */
.messages-area {
  flex: 1;
  overflow-y: auto;
  padding: var(--spacing-5);
  background: #f5f7fa;
  min-height: 0;
}

.message-list {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-3);
  min-height: min-content;
}

/* 日期分割线 */
.date-divider {
  display: flex;
  align-items: center;
  justify-content: center;
  margin: var(--spacing-4) 0;
}

.date-divider span {
  background: var(--color-bg-section);
  padding: var(--spacing-1) var(--spacing-3);
  border-radius: var(--radius-full);
  font-size: var(--font-size-xs);
  color: var(--color-text-placeholder);
}

/* 消息气泡 */
.message-wrapper {
  display: flex;
  justify-content: flex-start;
  align-items: flex-end;
  gap: var(--spacing-2);
  animation: messageSlideIn 0.3s ease;
}

.message-wrapper.own-message {
  justify-content: flex-end;
}

.message-avatar {
  flex-shrink: 0;
}

.message-content {
  max-width: 70%;
}

.message-bubble {
  padding: var(--spacing-3) var(--spacing-4);
  border-radius: var(--radius-lg);
  background: white;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
  position: relative;
}

.own-message .message-bubble {
  background: var(--color-primary);
  color: white;
}

/* 已撤回消息 */
.message-withdrawn {
  display: flex;
  align-items: center;
  gap: var(--spacing-1);
  padding: var(--spacing-2) var(--spacing-3);
  color: var(--color-text-placeholder);
  font-size: var(--font-size-sm);
  font-style: italic;
}

.message-text {
  font-size: var(--font-size-base);
  line-height: var(--line-height-relaxed);
  word-wrap: break-word;
  white-space: pre-wrap;
}

.message-footer {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: var(--spacing-2);
  margin-top: var(--spacing-1);
}

.message-time {
  font-size: 10px;
  color: var(--color-text-placeholder);
}

.own-message .message-time {
  color: rgba(255, 255, 255, 0.7);
}

/* 消息状态 */
.message-status {
  display: flex;
  align-items: center;
  font-size: 12px;
}

.status-sending {
  color: rgba(255, 255, 255, 0.7);
}

.status-failed {
  color: #ff4d4f;
  cursor: pointer;
}

.status-sent {
  color: rgba(255, 255, 255, 0.7);
}

.status-read {
  color: #52c41a;
  display: flex;
}

.status-read .el-icon:last-child {
  margin-left: -6px;
}

@keyframes messageSlideIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* 消息输入框 */
.message-input {
  padding: var(--spacing-3) var(--spacing-5);
  border-top: 1px solid var(--color-border-light);
  background: var(--color-bg-card);
  flex-shrink: 0;
}

.input-wrapper {
  display: flex;
  gap: var(--spacing-3);
  align-items: flex-end;
}

.message-textarea {
  flex: 1;
}

.message-textarea :deep(.el-textarea__inner) {
  border-radius: var(--radius-lg);
  font-size: var(--font-size-base);
  line-height: var(--line-height-relaxed);
}

.send-button {
  border-radius: var(--radius-lg);
  padding: var(--spacing-3) var(--spacing-5);
}

/* 右键菜单 */
.context-menu-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 999;
}

.context-menu {
  position: fixed;
  background: white;
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-lg);
  padding: var(--spacing-2) 0;
  min-width: 120px;
  z-index: 1000;
}

.context-menu-item {
  display: flex;
  align-items: center;
  gap: var(--spacing-2);
  padding: var(--spacing-2) var(--spacing-4);
  cursor: pointer;
  font-size: var(--font-size-sm);
  transition: background 0.2s;
}

.context-menu-item:hover {
  background: var(--color-bg-hover);
}

/* 滚动条美化 */
.conversation-items::-webkit-scrollbar,
.messages-area::-webkit-scrollbar {
  width: 6px;
}

.conversation-items::-webkit-scrollbar-track,
.messages-area::-webkit-scrollbar-track {
  background: transparent;
}

.conversation-items::-webkit-scrollbar-thumb,
.messages-area::-webkit-scrollbar-thumb {
  background: var(--color-border-base);
  border-radius: var(--radius-full);
}

.conversation-items::-webkit-scrollbar-thumb:hover,
.messages-area::-webkit-scrollbar-thumb:hover {
  background: var(--color-border-dark);
}

/* 响应式 */
@media (max-width: 1024px) {
  .messages-container {
    grid-template-columns: 320px 1fr;
  }
}

@media (max-width: 768px) {
  .messages-view {
    padding: 0;
    height: calc(100vh - 72px);
  }

  .messages-container {
    grid-template-columns: 1fr;
    border-radius: 0;
  }

  .conversations-sidebar {
    display: none;
  }

  .conversations-sidebar.show-mobile {
    display: flex;
  }

  .chat-area {
    display: flex;
  }

  .back-button {
    display: flex;
  }

  .message-content {
    max-width: 85%;
  }
}
</style>
