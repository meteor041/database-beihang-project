<template>
  <v-container class="item-edit-view">
    <v-card elevation="4" class="mx-auto" max-width="1000">
      <v-card-title class="text-h4 font-weight-bold text-center pa-6 bg-primary">
        <v-icon class="mr-2" size="large">mdi-pencil</v-icon>
        编辑商品
      </v-card-title>

      <v-progress-linear v-if="loading" indeterminate></v-progress-linear>

      <EmptyState
        v-else-if="!item"
        icon="mdi-alert-circle"
        description="商品不存在"
        action-text="返回"
        @action="router.back()"
      />

      <v-card-text v-else class="pa-8">
        <v-form @submit.prevent="handleSubmit">
          <v-text-field
            v-model="form.title"
            label="商品标题"
            variant="outlined"
            required
            counter="100"
            maxlength="100"
            class="mb-4"
          ></v-text-field>

          <v-select
            v-model="form.category_id"
            :items="categoryOptions"
            item-title="text"
            item-value="value"
            label="商品分类"
            variant="outlined"
            required
            class="mb-4"
          ></v-select>

          <v-row>
            <v-col cols="12" sm="6">
              <v-text-field
                v-model="form.price"
                type="number"
                label="售价"
                variant="outlined"
                step="0.01"
                min="0"
                required
              ></v-text-field>
            </v-col>
            <v-col cols="12" sm="6">
              <v-text-field
                v-model="form.original_price"
                type="number"
                label="原价（选填）"
                variant="outlined"
                step="0.01"
                min="0"
              ></v-text-field>
            </v-col>
          </v-row>

          <v-select
            v-model="form.condition_level"
            :items="conditionOptions"
            label="商品成色"
            variant="outlined"
            required
            class="mb-4"
          ></v-select>

          <v-text-field
            v-model="form.location"
            label="交易地点"
            variant="outlined"
            required
            class="mb-4"
          ></v-text-field>

          <v-textarea
            v-model="form.description"
            label="商品描述"
            variant="outlined"
            rows="6"
            counter="2000"
            maxlength="2000"
            required
            class="mb-4"
          ></v-textarea>

          <div class="d-flex justify-center ga-4">
            <v-btn variant="outlined" size="large" @click="router.back()">
              取消
            </v-btn>
            <v-btn type="submit" color="primary" size="large" :loading="updating">
              保存修改
            </v-btn>
          </div>
        </v-form>
      </v-card-text>
    </v-card>
  </v-container>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { useNotification } from '@/composables/useNotification'
import { itemAPI } from '@/api'
import EmptyState from '@/components/EmptyState.vue'
import type { Item, Category } from '@/types'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()
const notification = useNotification()

const item = ref<Item | null>(null)
const categories = ref<Category[]>([])
const loading = ref(false)
const updating = ref(false)

const form = ref({
  title: '',
  category_id: '',
  price: '',
  original_price: '',
  condition_level: '',
  location: '',
  description: ''
})

const categoryOptions = computed(() => {
  return categories.value.map(cat => ({
    text: cat.category_name,
    value: cat.category_id.toString()
  }))
})

const conditionOptions = [
  { title: '全新', value: 'brand_new' },
  { title: '几乎全新', value: 'like_new' },
  { title: '轻微使用', value: 'very_good' },
  { title: '明显使用', value: 'good' },
  { title: '磨损较重', value: 'acceptable' }
]

const loadItem = async (): Promise<void> => {
  const itemId = route.params.id
  if (!itemId) return

  loading.value = true
  try {
    const response = await itemAPI.getItem(Number(itemId))
    item.value = response.item

    if (item.value) {
      form.value = {
        title: item.value.title,
        category_id: item.value.category_id?.toString() || '',
        price: item.value.price?.toString() || '',
        original_price: item.value.original_price?.toString() || '',
        condition_level: item.value.condition_level || '',
        location: item.value.location || '',
        description: item.value.description || ''
      }
    }
  } catch (error) {
    console.error('Failed to load item:', error)
    notification.error('加载商品失败')
  } finally {
    loading.value = false
  }
}

const loadCategories = async (): Promise<void> => {
  try {
    const response = await itemAPI.getCategories()
    categories.value = response.categories || []
  } catch (error) {
    console.error('Failed to load categories:', error)
  }
}

const handleSubmit = async (): Promise<void> => {
  if (!item.value || !userStore.currentUser) return

  updating.value = true
  try {
    await itemAPI.updateItem(item.value.item_id, {
      user_id: userStore.currentUser.user_id,
      ...form.value,
      category_id: parseInt(form.value.category_id),
      price: parseFloat(form.value.price),
      original_price: form.value.original_price ? parseFloat(form.value.original_price) : undefined
    })

    notification.success('商品更新成功！')
    router.push(`/items/${item.value.item_id}`)
  } catch (error) {
    console.error('Failed to update item:', error)
    notification.error('更新失败')
  } finally {
    updating.value = false
  }
}

onMounted(() => {
  loadCategories()
  loadItem()
})
</script>

<style scoped>
.item-edit-view {
  max-width: 1000px;
  padding: 40px 20px;
}
</style>
