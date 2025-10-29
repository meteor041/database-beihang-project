<template>
  <v-container fluid class="messages-view pa-0" style="height: calc(100vh - 64px);">
    <h1 class="text-h3 font-weight-bold pa-4">消息中心</h1>

    <v-row no-gutters style="height: calc(100% - 80px);">
      <!-- 会话列表 -->
      <v-col cols="12" md="4" lg="3" class="conversation-panel">
        <v-card flat class="h-100">
          <v-card-title class="bg-grey-lighten-4">会话列表</v-card-title>
          <v-divider></v-divider>

          <v-progress-linear v-if="conversationsLoading" indeterminate></v-progress-linear>

          <EmptyState
            v-else-if="conversations.length === 0"
            icon="mdi-message-outline"
            description="暂无会话"
            class="mt-8"
          />

          <v-list v-else density="compact" class="conversation-list">
            <v-list-item
              v-for="conversation in conversations"
              :key="`${conversation.other_user_id}-${conversation.item_id}`"
              :active="isActiveConversation(conversation)"
              @click="selectConversation(conversation)"
            >
              <template v-slot:prepend>
                <v-avatar>
                  <v-img
                    v-if="conversation.other_avatar"
                    :src="conversation.other_avatar"
                  ></v-img>
                  <span v-else>{{ conversation.other_username?.charAt(0) }}</span>
                </v-avatar>
              </template>

              <v-list-item-title>
                {{ conversation.other_username }}
                <v-chip
                  v-if="conversation.unread_count > 0"
                  color="error"
                  size="x-small"
                  class="ml-2"
                >
                  {{ conversation.unread_count }}
                </v-chip>
              </v-list-item-title>
              <v-list-item-subtitle>{{ conversation.item_title }}</v-list-item-subtitle>
              <v-list-item-subtitle class="text-caption">
                {{ conversation.last_message }}
              </v-list-item-subtitle>

              <template v-slot:append>
                <span class="text-caption text-grey">
                  {{ formatTime(conversation.last_message_time) }}
                </span>
              </template>
            </v-list-item>
          </v-list>
        </v-card>
      </v-col>

      <!-- 聊天区域 -->
      <v-col cols="12" md="8" lg="9" class="chat-panel">
        <v-card flat class="h-100 d-flex flex-column">
          <div v-if="!selectedConversation" class="flex-grow-1 d-flex align-center justify-center">
            <EmptyState
              icon="mdi-message-text-outline"
              description="请选择一个会话开始聊天"
            />
          </div>

          <template v-else>
            <!-- 聊天头部 -->
            <v-card-title class="bg-grey-lighten-4 d-flex align-center">
              <v-avatar size="40" class="mr-3">
                <v-img
                  v-if="selectedConversation.other_avatar"
                  :src="selectedConversation.other_avatar"
                ></v-img>
                <span v-else>{{ selectedConversation.other_username?.charAt(0) }}</span>
              </v-avatar>
              <div>
                <div class="text-body-1">{{ selectedConversation.other_username }}</div>
                <div class="text-caption text-grey">{{ selectedConversation.item_title }}</div>
              </div>
            </v-card-title>
            <v-divider></v-divider>

            <!-- 消息列表 -->
            <v-card-text
              ref="messagesArea"
              class="flex-grow-1 overflow-y-auto messages-area pa-4"
              style="max-height: calc(100vh - 340px);"
            >
              <v-progress-circular
                v-if="messagesLoading"
                indeterminate
                class="d-block mx-auto"
              ></v-progress-circular>

              <div v-else>
                <div
                  v-for="message in messages"
                  :key="message.message_id"
                  :class="[
                    'd-flex mb-4',
                    message.sender_id === currentUser?.user_id ? 'justify-end' : 'justify-start'
                  ]"
                >
                  <v-card
                    :color="message.sender_id === currentUser?.user_id ? 'primary' : 'grey-lighten-3'"
                    :class="message.sender_id === currentUser?.user_id ? 'text-white' : ''"
                    max-width="70%"
                    elevation="1"
                  >
                    <v-card-text class="pa-3">
                      <div style="white-space: pre-wrap; word-break: break-word;">
                        {{ message.content }}
                      </div>
                      <div class="text-caption mt-1" :class="message.sender_id === currentUser?.user_id ? 'text-white' : 'text-grey'">
                        {{ formatTime(message.send_time) }}
                      </div>
                    </v-card-text>
                  </v-card>
                </div>
              </div>
            </v-card-text>

            <!-- 消息输入 -->
            <v-divider></v-divider>
            <v-card-actions class="pa-4">
              <v-row no-gutters>
                <v-col cols="12">
                  <v-textarea
                    v-model="newMessage"
                    placeholder="输入消息... (Enter发送, Shift+Enter换行)"
                    variant="outlined"
                    rows="3"
                    hide-details
                    @keydown.enter.exact.prevent="sendMessage"
                  ></v-textarea>
                </v-col>
                <v-col cols="12" class="d-flex justify-end mt-2">
                  <v-btn
                    color="primary"
                    :disabled="!newMessage.trim() || sendingMessage"
                    :loading="sendingMessage"
                    @click="sendMessage"
                  >
                    发送
                  </v-btn>
                </v-col>
              </v-row>
            </v-card-actions>
          </template>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup lang="ts">
import { ref, onMounted, computed, nextTick } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { useNotification } from '@/composables/useNotification'
import { messageAPI } from '@/api'
import EmptyState from '@/components/EmptyState.vue'
import type { Conversation, Message } from '@/types'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()
const notification = useNotification()

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
    notification.error('加载会话列表失败')
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
    notification.error('加载消息失败')
  } finally {
    messagesLoading.value = false
  }
}

const selectConversation = (conversation: Conversation): void => {
  selectedConversation.value = conversation
  loadMessages()
}

const scrollToBottom = (): void => {
  if (messagesArea.value) {
    messagesArea.value.scrollTop = messagesArea.value.scrollHeight
  }
}

const sendMessage = async (): Promise<void> => {
  if (!newMessage.value.trim() || !selectedConversation.value || !currentUser.value) {
    return
  }

  sendingMessage.value = true
  try {
    await messageAPI.sendMessage({
      sender_id: currentUser.value.user_id,
      receiver_id: selectedConversation.value.other_user_id,
      item_id: selectedConversation.value.item_id,
      content: newMessage.value.trim()
    })

    newMessage.value = ''
    await loadMessages()
    await loadConversations()
  } catch (error) {
    console.error('Failed to send message:', error)
    notification.error('发送失败')
  } finally {
    sendingMessage.value = false
  }
}

onMounted(async () => {
  await loadConversations()

  // 从路由参数获取要打开的会话
  if (route.query.user_id && route.query.item_id) {
    const userId = parseInt(route.query.user_id as string)
    const itemId = parseInt(route.query.item_id as string)

    const conversation = conversations.value.find(
      c => c.other_user_id === userId && c.item_id === itemId
    )

    if (conversation) {
      selectConversation(conversation)
    }
  }
})
</script>

<style scoped>
.messages-view {
  background-color: #f5f5f5;
}

.conversation-panel {
  border-right: 1px solid #e0e0e0;
}

.conversation-list {
  overflow-y: auto;
  max-height: calc(100vh - 200px);
}

.messages-area {
  background-color: #fafafa;
}
</style>
