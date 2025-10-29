<template>
  <div class="messages-view">
    <h1>消息中心</h1>
    
    <div class="messages-container">
      <div class="conversations-list">
        <h2>会话列表</h2>
        
        <div v-if="conversationsLoading" class="loading">
          加载中...
        </div>
        
        <div v-else-if="conversations.length === 0" class="no-conversations">
          暂无会话
        </div>
        
        <div v-else class="conversation-items">
          <div 
            v-for="conversation in conversations"
            :key="`${conversation.other_user_id}-${conversation.item_id}`"
            :class="['conversation-item', { active: isActiveConversation(conversation) }]"
            @click="selectConversation(conversation)"
          >
            <img 
              :src="conversation.other_avatar || '/default-avatar.png'"
              :alt="conversation.other_username"
              class="user-avatar"
            />
            <div class="conversation-info">
              <div class="conversation-header">
                <span class="username">{{ conversation.other_username }}</span>
                <span class="time">{{ formatTime(conversation.last_message_time) }}</span>
              </div>
              <div class="item-title">{{ conversation.item_title }}</div>
              <div class="last-message">{{ conversation.last_message }}</div>
            </div>
            <div v-if="conversation.unread_count > 0" class="unread-badge">
              {{ conversation.unread_count }}
            </div>
          </div>
        </div>
      </div>

      <div class="chat-area">
        <div v-if="!selectedConversation" class="no-selection">
          请选择一个会话开始聊天
        </div>
        
        <div v-else class="chat-container">
          <div class="chat-header">
            <div class="chat-info">
              <img 
                :src="selectedConversation.other_avatar || '/default-avatar.png'"
                :alt="selectedConversation.other_username"
                class="user-avatar"
              />
              <div>
                <div class="username">{{ selectedConversation.other_username }}</div>
                <div class="item-title">{{ selectedConversation.item_title }}</div>
              </div>
            </div>
          </div>

          <div class="messages-area" ref="messagesArea">
            <div v-if="messagesLoading" class="loading">
              加载消息中...
            </div>
            
            <div v-else class="message-list">
              <div 
                v-for="message in messages"
                :key="message.message_id"
                :class="['message-item', { 'own-message': message.sender_id === currentUser?.user_id }]"
              >
                <div class="message-content">
                  <div class="message-text">{{ message.content }}</div>
                  <div class="message-time">{{ formatTime(message.send_time) }}</div>
                </div>
              </div>
            </div>
          </div>

          <div class="message-input">
            <div class="input-container">
              <textarea
                v-model="newMessage"
                placeholder="输入消息..."
                @keydown.enter.exact.prevent="sendMessage"
                @keydown.shift.enter="newMessage += '\n'"
                rows="3"
              ></textarea>
              <button 
                @click="sendMessage"
                :disabled="!newMessage.trim() || sendingMessage"
                class="send-btn"
              >
                {{ sendingMessage ? '发送中...' : '发送' }}
              </button>
            </div>
            <div class="input-hint">
              按 Enter 发送，Shift + Enter 换行
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
/* 使用设计系统变量 */
.messages-view {
  max-width: 1800px;
  margin: 0 auto;
  padding: var(--spacing-2xl) var(--spacing-3xl);
}

.messages-view h1 {
  color: var(--color-text-primary);
  margin-bottom: var(--spacing-2xl);
  text-align: center;
}

.messages-container {
  display: grid;
  grid-template-columns: 400px 1fr;
  gap: var(--spacing-2xl);
  height: 700px;
  background: var(--color-bg-card);
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-base);
  overflow: hidden;
}

.conversations-list {
  border-right: 1px solid var(--color-border-lighter);
  display: flex;
  flex-direction: column;
}

.conversations-list h2 {
  color: var(--color-text-primary);
  padding: var(--spacing-lg);
  margin: 0;
  border-bottom: 1px solid var(--color-border-lighter);
  font-size: var(--font-size-2xl);
}

.loading {
  text-align: center;
  padding: var(--spacing-3xl) var(--spacing-lg);
  color: var(--color-text-secondary);
}

.no-conversations {
  text-align: center;
  padding: var(--spacing-3xl) var(--spacing-lg);
  color: var(--color-text-secondary);
}

.conversation-items {
  flex: 1;
  overflow-y: auto;
}

.conversation-item {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
  padding: var(--spacing-lg) var(--spacing-lg);
  cursor: pointer;
  transition: background-color var(--transition-base);
  border-bottom: 1px solid var(--color-bg-page);
  position: relative;
}

.conversation-item:hover {
  background-color: var(--color-bg-page);
}

.conversation-item.active {
  background-color: #e3f2fd;
}

.user-avatar {
  width: 50px;
  height: 50px;
  border-radius: var(--radius-round);
  object-fit: cover;
}

.conversation-info {
  flex: 1;
  min-width: 0;
}

.conversation-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--spacing-xs);
}

.username {
  font-weight: var(--font-weight-medium);
  color: var(--color-text-primary);
}

.time {
  font-size: var(--font-size-xs);
  color: var(--color-text-secondary);
}

.item-title {
  font-size: var(--font-size-sm);
  color: var(--color-primary);
  margin-bottom: var(--spacing-xs);
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
  background: var(--color-price);
  color: white;
  border-radius: var(--radius-round);
  width: 20px;
  height: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: var(--font-size-xs);
  font-weight: var(--font-weight-medium);
}

.chat-area {
  display: flex;
  flex-direction: column;
}

.no-selection {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: var(--color-text-secondary);
  font-size: var(--font-size-xl);
}

.chat-container {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.chat-header {
  padding: var(--spacing-lg);
  border-bottom: 1px solid var(--color-border-lighter);
}

.chat-info {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
}

.chat-info .username {
  font-weight: var(--font-weight-medium);
  color: var(--color-text-primary);
  margin-bottom: var(--spacing-xs);
}

.chat-info .item-title {
  font-size: var(--font-size-sm);
  color: var(--color-primary);
}

.messages-area {
  flex: 1;
  overflow-y: auto;
  padding: var(--spacing-lg);
}

.message-list {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-lg);
}

.message-item {
  display: flex;
}

.message-item.own-message {
  justify-content: flex-end;
}

.message-content {
  max-width: 70%;
  background: var(--color-bg-page);
  padding: var(--spacing-md) var(--spacing-base);
  border-radius: var(--radius-xl);
  position: relative;
}

.own-message .message-content {
  background: var(--color-primary);
  color: white;
}

.message-text {
  word-wrap: break-word;
  white-space: pre-wrap;
}

.message-time {
  font-size: var(--font-size-xs);
  opacity: 0.7;
  margin-top: var(--spacing-xs);
}

.message-input {
  padding: var(--spacing-lg);
  border-top: 1px solid var(--color-border-lighter);
}

.input-container {
  display: flex;
  gap: var(--spacing-sm);
  align-items: flex-end;
}

.input-container textarea {
  flex: 1;
  padding: var(--spacing-md);
  border: 1px solid var(--color-border-base);
  border-radius: var(--radius-lg);
  resize: none;
  font-family: inherit;
  font-size: var(--font-size-base);
  outline: none;
}

.input-container textarea:focus {
  border-color: var(--color-primary);
}

.send-btn {
  padding: var(--spacing-md) var(--spacing-lg);
  background: var(--color-primary);
  color: white;
  border: none;
  border-radius: var(--radius-lg);
  cursor: pointer;
  font-size: var(--font-size-base);
  transition: background-color var(--transition-base);
}

.send-btn:hover:not(:disabled) {
  background: var(--color-primary-dark);
}

.send-btn:disabled {
  background: var(--color-info);
  cursor: not-allowed;
}

.input-hint {
  font-size: var(--font-size-xs);
  color: var(--color-text-secondary);
  margin-top: var(--spacing-sm);
  text-align: center;
}

@media (max-width: 768px) {
  .messages-container {
    grid-template-columns: 1fr;
    height: auto;
  }

  .conversations-list {
    border-right: none;
    border-bottom: 1px solid var(--color-border-lighter);
    max-height: 300px;
  }

  .chat-area {
    min-height: 400px;
  }

  .message-content {
    max-width: 85%;
  }
}
</style>
