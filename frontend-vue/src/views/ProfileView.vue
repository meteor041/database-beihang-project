<template>
  <v-container class="profile-view">
    <h1 class="text-h3 font-weight-bold mb-6">个人中心</h1>

    <v-row>
      <!-- 侧边栏 -->
      <v-col cols="12" md="3">
        <v-card elevation="2" class="mb-4">
          <v-card-text class="text-center">
            <UserAvatar
              :src="currentUser?.avatar"
              :username="currentUser?.username"
              :size="100"
              class="mb-4"
            />
            <h2 class="text-h5 mb-2">{{ currentUser?.username }}</h2>
            <p class="text-body-2 text-grey mb-2">{{ currentUser?.real_name }}</p>
            <v-chip color="warning" prepend-icon="mdi-star">
              信用分：{{ currentUser?.credit_score }}
            </v-chip>
          </v-card-text>
        </v-card>

        <v-list density="compact" nav>
          <v-list-item
            v-for="tab in tabs"
            :key="tab.key"
            :value="tab.key"
            :active="activeTab === tab.key"
            :prepend-icon="tab.icon"
            @click="switchTab(tab.key)"
          >
            <v-list-item-title>{{ tab.label }}</v-list-item-title>
          </v-list-item>
        </v-list>
      </v-col>

      <!-- 主内容区 -->
      <v-col cols="12" md="9">
        <!-- 基本信息 -->
        <v-card v-if="activeTab === 'info'" elevation="2">
          <v-card-title>基本信息</v-card-title>
          <v-card-text>
            <v-form @submit.prevent="updateUserInfo">
              <v-text-field
                v-model="userForm.student_id"
                label="学号"
                variant="outlined"
                disabled
                class="mb-4"
              ></v-text-field>

              <v-text-field
                v-model="userForm.username"
                label="用户名"
                variant="outlined"
                required
                class="mb-4"
              ></v-text-field>

              <v-text-field
                v-model="userForm.real_name"
                label="真实姓名"
                variant="outlined"
                required
                class="mb-4"
              ></v-text-field>

              <v-text-field
                v-model="userForm.phone"
                label="手机号"
                variant="outlined"
                required
                class="mb-4"
              ></v-text-field>

              <v-text-field
                v-model="userForm.email"
                label="邮箱"
                type="email"
                variant="outlined"
                required
                class="mb-4"
              ></v-text-field>

              <v-btn
                type="submit"
                color="primary"
                size="large"
                :loading="updating"
                block
              >
                更新信息
              </v-btn>
            </v-form>
          </v-card-text>
        </v-card>

        <!-- 我的商品 -->
        <v-card v-if="activeTab === 'items'" elevation="2">
          <v-card-title class="d-flex justify-space-between">
            <span>我的商品</span>
            <v-btn color="primary" to="/publish" prepend-icon="mdi-plus">
              发布新商品
            </v-btn>
          </v-card-title>

          <v-card-text>
            <v-select
              v-model="itemStatus"
              :items="itemStatusOptions"
              label="状态筛选"
              variant="outlined"
              density="comfortable"
              @update:model-value="loadMyItems"
              class="mb-4"
            ></v-select>

            <v-progress-linear v-if="itemsLoading" indeterminate color="primary"></v-progress-linear>

            <EmptyState
              v-else-if="myItems.length === 0"
              description="暂无商品"
              action-text="发布商品"
              @action="router.push('/publish')"
            />

            <v-row v-else>
              <v-col
                v-for="item in myItems"
                :key="item.item_id"
                cols="12"
                sm="6"
                md="4"
              >
                <v-card>
                  <v-img
                    :src="item.images && item.images[0] ? item.images[0] : '/placeholder.png'"
                    :alt="item.title"
                    height="200"
                    cover
                  ></v-img>
                  <v-card-text>
                    <h3 class="text-h6 mb-2">{{ item.title }}</h3>
                    <div class="text-h6 text-error mb-2">¥{{ item.price }}</div>
                    <v-chip size="small" :color="getStatusColor(item.status)" class="mb-2">
                      {{ getStatusText(item.status) }}
                    </v-chip>
                    <div class="text-caption text-grey">{{ item.view_count }} 次浏览</div>
                  </v-card-text>
                  <v-card-actions>
                    <v-btn variant="text" @click="viewItem(item.item_id)">查看</v-btn>
                    <v-btn
                      v-if="item.status === 'available'"
                      variant="text"
                      color="primary"
                      @click="editItem(item.item_id)"
                    >
                      编辑
                    </v-btn>
                  </v-card-actions>
                </v-card>
              </v-col>
            </v-row>
          </v-card-text>
        </v-card>

        <!-- 统计数据 -->
        <v-card v-if="activeTab === 'stats'" elevation="2">
          <v-card-title>数据统计</v-card-title>
          <v-card-text>
            <v-progress-linear v-if="statsLoading" indeterminate color="primary"></v-progress-linear>
            <v-row v-else>
              <v-col cols="6" md="3" v-for="stat in stats" :key="stat.label">
                <v-card variant="tonal" :color="stat.color">
                  <v-card-text class="text-center">
                    <v-icon :icon="stat.icon" size="48" class="mb-2"></v-icon>
                    <div class="text-h4 font-weight-bold">{{ stat.value }}</div>
                    <div class="text-caption">{{ stat.label }}</div>
                  </v-card-text>
                </v-card>
              </v-col>
            </v-row>
          </v-card-text>
        </v-card>

        <!-- 修改密码 -->
        <v-card v-if="activeTab === 'password'" elevation="2">
          <v-card-title>修改密码</v-card-title>
          <v-card-text>
            <v-form @submit.prevent="updatePassword">
              <v-text-field
                v-model="passwordForm.oldPassword"
                label="当前密码"
                type="password"
                variant="outlined"
                required
                class="mb-4"
              ></v-text-field>

              <v-text-field
                v-model="passwordForm.newPassword"
                label="新密码"
                type="password"
                variant="outlined"
                required
                class="mb-4"
              ></v-text-field>

              <v-text-field
                v-model="passwordForm.confirmPassword"
                label="确认新密码"
                type="password"
                variant="outlined"
                required
                class="mb-4"
              ></v-text-field>

              <v-btn
                type="submit"
                color="primary"
                size="large"
                :loading="passwordUpdating"
                block
              >
                修改密码
              </v-btn>
            </v-form>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { useNotification } from '@/composables/useNotification'
import { userAPI, itemAPI } from '@/api'
import UserAvatar from '@/components/UserAvatar.vue'
import EmptyState from '@/components/EmptyState.vue'
import type { Item } from '@/types'

const router = useRouter()
const userStore = useUserStore()
const notification = useNotification()

const currentUser = computed(() => userStore.currentUser)
const activeTab = ref('info')

const tabs = [
  { key: 'info', label: '基本信息', icon: 'mdi-account' },
  { key: 'items', label: '我的商品', icon: 'mdi-package-variant' },
  { key: 'stats', label: '数据统计', icon: 'mdi-chart-box' },
  { key: 'password', label: '修改密码', icon: 'mdi-lock' }
]

// 基本信息
const userForm = ref({
  student_id: '',
  username: '',
  real_name: '',
  phone: '',
  email: ''
})
const updating = ref(false)

// 我的商品
const myItems = ref<Item[]>([])
const itemsLoading = ref(false)
const itemStatus = ref('available')
const itemStatusOptions = [
  { title: '在售', value: 'available' },
  { title: '已售出', value: 'sold' },
  { title: '已下架', value: 'removed' }
]

// 统计数据
const stats = ref([
  { label: '发布商品', value: 0, icon: 'mdi-package-variant', color: 'primary' },
  { label: '售出商品', value: 0, icon: 'mdi-sale', color: 'success' },
  { label: '购买商品', value: 0, icon: 'mdi-cart', color: 'info' },
  { label: '收藏商品', value: 0, icon: 'mdi-heart', color: 'error' }
])
const statsLoading = ref(false)

// 修改密码
const passwordForm = ref({
  oldPassword: '',
  newPassword: '',
  confirmPassword: ''
})
const passwordUpdating = ref(false)

const getStatusText = (status: string): string => {
  const map: Record<string, string> = {
    available: '在售',
    sold: '已售出',
    removed: '已下架'
  }
  return map[status] || status
}

const getStatusColor = (status: string): string => {
  const map: Record<string, string> = {
    available: 'success',
    sold: 'error',
    removed: 'grey'
  }
  return map[status] || 'grey'
}

const switchTab = (tab: string): void => {
  activeTab.value = tab
  if (tab === 'items') loadMyItems()
  if (tab === 'stats') loadStats()
}

const updateUserInfo = async (): Promise<void> => {
  if (!currentUser.value) return

  updating.value = true
  try {
    await userAPI.updateUserProfile({
      user_id: currentUser.value.user_id,
      ...userForm.value
    })

    await userStore.fetchCurrentUser()
    notification.success('信息更新成功')
  } catch (error) {
    console.error('Failed to update user info:', error)
    notification.error('更新失败')
  } finally {
    updating.value = false
  }
}

const loadMyItems = async (): Promise<void> => {
  if (!currentUser.value) return

  itemsLoading.value = true
  try {
    const response = await itemAPI.getUserItems(currentUser.value.user_id, {
      status: itemStatus.value
    })
    myItems.value = response.items || []
  } catch (error) {
    console.error('Failed to load items:', error)
    notification.error('加载商品失败')
  } finally {
    itemsLoading.value = false
  }
}

const loadStats = async (): Promise<void> => {
  if (!currentUser.value) return

  statsLoading.value = true
  try {
    // 这里应该调用统计API，暂时使用模拟数据
    stats.value[0].value = myItems.value.length
    // 可以从API获取更多统计数据
  } catch (error) {
    console.error('Failed to load stats:', error)
  } finally {
    statsLoading.value = false
  }
}

const viewItem = (itemId: number): void => {
  router.push(`/items/${itemId}`)
}

const editItem = (itemId: number): void => {
  router.push(`/items/${itemId}/edit`)
}

const updatePassword = async (): Promise<void> => {
  if (!currentUser.value) return

  if (passwordForm.value.newPassword !== passwordForm.value.confirmPassword) {
    notification.error('两次输入的密码不一致')
    return
  }

  if (passwordForm.value.newPassword.length < 6) {
    notification.error('密码长度不能少于6位')
    return
  }

  passwordUpdating.value = true
  try {
    await userAPI.changePassword({
      user_id: currentUser.value.user_id,
      old_password: passwordForm.value.oldPassword,
      new_password: passwordForm.value.newPassword
    })

    notification.success('密码修改成功，请重新登录')
    setTimeout(() => {
      userStore.logout()
      router.push('/login')
    }, 2000)
  } catch (error) {
    console.error('Failed to update password:', error)
    notification.error('密码修改失败')
  } finally {
    passwordUpdating.value = false
  }
}

onMounted(() => {
  if (!currentUser.value) {
    router.push('/login')
    return
  }

  // 初始化表单
  userForm.value = {
    student_id: currentUser.value.student_id || '',
    username: currentUser.value.username || '',
    real_name: currentUser.value.real_name || '',
    phone: currentUser.value.phone || '',
    email: currentUser.value.email || ''
  }

  loadMyItems()
})
</script>

<style scoped>
.profile-view {
  max-width: 1400px;
}
</style>
