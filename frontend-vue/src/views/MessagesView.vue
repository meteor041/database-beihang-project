<template>
  <div class="messages-view">
    <div class="messages-container">
      <!-- 左侧会话列表 -->
      <div class="conversations-sidebar">
        <div class="sidebar-header">
          <h2>消息</h2>
        </div>

        <div v-if="conversationsLoading" class="loading">
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
              :value="conversation.unread_count"
              class="unread-badge"
            />
          </div>
        </div>
      </div>

      <!-- 右侧聊天区域 -->
      <div class="chat-area">
        <div v-if="!selectedConversation" class="no-selection">
          <el-empty description="选择一个会话开始聊天" :image-size="200">
            <el-icon :size="80" color="var(--color-primary)"><ChatDotRound /></el-icon>
          </el-empty>
        </div>

        <div v-else class="chat-container">
          <!-- 聊天头部 -->
          <div class="chat-header">
            <div class="chat-info">
              <el-avatar
                :src="selectedConversation.other_avatar || undefined"
                :size="40"
              >
                {{ selectedConversation.other_username?.charAt(0) }}
              </el-avatar>
              <div class="chat-user-info">
                <div class="username">{{ selectedConversation.other_username }}</div>
                <div class="item-title">关于: {{ selectedConversation.item_title }}</div>
              </div>
            </div>
          </div>

          <!-- 消息列表区域 -->
          <div class="messages-area" ref="messagesArea">
            <div v-if="messagesLoading" class="loading">
              <el-icon class="is-loading"><Loading /></el-icon>
              <span>加载消息中...</span>
            </div>

            <div v-else class="message-list">
              <div
                v-for="message in messages"
                :key="message.message_id"
                :class="['message-wrapper', { 'own-message': message.sender_id === currentUser?.user_id }]"
              >
                <div class="message-bubble">
                  <div class="message-text">{{ message.content }}</div>
                  <div class="message-time">{{ formatTime(message.send_time) }}</div>
                </div>
              </div>
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
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed, nextTick, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { messageAPI, userAPI, itemAPI } from '@/api'
import type { Conversation, Message } from '@/types'
import { Loading, ChatDotRound, Promotion } from '@element-plus/icons-vue'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()

const conversations = ref<Conversation[]>([])
const messages = ref<Message[]>([])
const selectedConversation = ref<Conversation | null>(null)
const newMessage = ref('')

const conversationsLoading = ref(false)
const messagesLoading = ref(false)
const sendingMessage = ref(false)

const messagesArea = ref<HTMLElement | null>(null)

const currentUser = computed(() => userStore.currentUser)

const formatTime = (timeString: string): string => {
  const date = new Date(timeString)
  const now = new Date()
  const diff = now.getTime() - date.getTime()

  if (diff < 60000) {
    return '刚刚'
  } else if (diff < 3600000) {
    return `${Math.floor(diff / 60000)}分钟前`
  } else if (diff < 86400000) {
    return `${Math.floor(diff / 3600000)}小时前`
  } else {
    return date.toLocaleDateString('zh-CN')
  }
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

const loadMessages = async (): Promise<void> => {
  if (!selectedConversation.value || !currentUser.value) return

  messagesLoading.value = true
  try {
    const response = await messageAPI.getConversationMessages({
      user_id: currentUser.value.user_id,
      other_user_id: selectedConversation.value.other_user_id,
      item_id: selectedConversation.value.item_id,
      page: 1,
      limit: 50
    })
    
    messages.value = (response.messages || []).reverse()

    nextTick(() => {
      scrollToBottom()
    })
  } catch (error) {
    console.error('Failed to load messages:', error)
  } finally {
    messagesLoading.value = false
  }
}

const selectConversation = (conversation: Conversation): void => {
  selectedConversation.value = conversation
  loadMessages()
}

const sendMessage = async (): Promise<void> => {
  if (!newMessage.value.trim() || !selectedConversation.value || sendingMessage.value || !currentUser.value) {
    return
  }

  const messageContent = newMessage.value.trim()
  newMessage.value = ''
  sendingMessage.value = true

  try {
    await messageAPI.sendMessage({
      sender_id: currentUser.value.user_id,
      receiver_id: selectedConversation.value.other_user_id,
      item_id: selectedConversation.value.item_id,
      content: messageContent,
      message_type: 'text'
    })

    loadMessages()
    loadConversations()
  } catch (error) {
    console.error('Failed to send message:', error)
    alert('发送失败，请重试')
  } finally {
    sendingMessage.value = false
  }
}

const scrollToBottom = (): void => {
  if (messagesArea.value) {
    messagesArea.value.scrollTop = messagesArea.value.scrollHeight
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
    // 找到已存在的会话，直接选中
    selectConversation(existingConversation)
  } else {
    // 没找到会话，创建临时会话（第一次联系卖家的场景）
    try {
      // 并行获取用户信息和商品信息
      const [userResponse, itemResponse] = await Promise.all([
        userAPI.getUser(userIdNum),
        itemAPI.getItem(itemIdNum)
      ])

      // 创建临时会话对象
      const tempConversation: Conversation = {
        other_user_id: userIdNum,
        other_username: userResponse.user.username,
        other_avatar: userResponse.user.avatar,
        item_id: itemIdNum,
        item_title: itemResponse.item.title,
        item_images: itemResponse.item.images || [],
        last_message_time: new Date().toISOString(),
        last_message: '',
        unread_count: 0
      }

      // 自动选中这个临时会话
      selectedConversation.value = tempConversation
      messages.value = [] // 清空消息列表（因为是第一次联系）

      console.log('创建临时会话成功，可以开始发送消息')
    } catch (error) {
      console.error('Failed to create temporary conversation:', error)
      alert('无法加载会话信息，请稍后重试')
    }
  }
}

watch(() => route.query, () => {
  if (conversations.value.length > 0) {
    handleQueryParams()
  }
}, { immediate: false })

// 会话列表加载完成后，检查URL参数
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

  // 先加载会话列表
  await loadConversations()

  // 如果URL有参数（从商品详情页跳转过来），处理自动打开会话
  if (route.query.user_id && route.query.item_id) {
    await handleQueryParams()
  }
})
</script>

<style scoped>
/* 现代化消息页面 - 全屏布局 */

.messages-view {
  max-width: 1800px;
  margin: 0 auto;
  padding: var(--spacing-4);
  width: 100%;
  height: calc(100vh - 2rem); /* 只减去上下 padding，删除底部栏后无需预留额外空间 */
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
}

.sidebar-header {
  padding: var(--spacing-5);
  border-bottom: 1px solid var(--color-border-light);
  background: var(--color-bg-card);
}

.sidebar-header h2 {
  margin: 0;
  font-size: var(--font-size-2xl);
  font-weight: var(--font-weight-bold);
  color: var(--color-text-primary);
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

.user-avatar {
  flex-shrink: 0;
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
}

.last-message {
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.unread-badge {
  position: absolute;
  top: var(--spacing-4);
  right: var(--spacing-4);
}

/* 右侧聊天区域 */
.chat-area {
  display: flex;
  flex-direction: column;
  background: #f5f7fa;
  height: 100%;
}

.no-selection {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: var(--color-text-secondary);
}

.chat-container {
  display: flex;
  flex-direction: column;
  height: 100%;
}

/* 聊天头部 */
.chat-header {
  padding: var(--spacing-4) var(--spacing-5);
  border-bottom: 1px solid var(--color-border-light);
  background: var(--color-bg-card);
  flex-shrink: 0;
}

.chat-info {
  display: flex;
  align-items: center;
  gap: var(--spacing-3);
}

.chat-user-info {
  flex: 1;
}

.chat-user-info .username {
  font-size: var(--font-size-lg);
  font-weight: var(--font-weight-semibold);
  margin-bottom: var(--spacing-1);
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
}

.message-list {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-3);
}

/* 消息气泡 - 现代化设计 */
.message-wrapper {
  display: flex;
  justify-content: flex-start;
  animation: messageSlideIn 0.3s ease;
}

.message-wrapper.own-message {
  justify-content: flex-end;
}

.message-bubble {
  max-width: 70%;
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

.message-text {
  font-size: var(--font-size-base);
  line-height: var(--line-height-relaxed);
  word-wrap: break-word;
  white-space: pre-wrap;
  margin-bottom: var(--spacing-1);
}

.message-time {
  font-size: var(--font-size-xs);
  color: var(--color-text-placeholder);
  text-align: right;
}

.own-message .message-time {
  color: rgba(255, 255, 255, 0.8);
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
  padding: var(--spacing-4) var(--spacing-5);
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

  .chat-area {
    display: flex;
  }

  .message-bubble {
    max-width: 85%;
  }
}
</style>
