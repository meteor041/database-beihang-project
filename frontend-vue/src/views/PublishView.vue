<template>
  <v-container class="publish-view">
    <v-card elevation="4" class="mx-auto" max-width="1000">
      <v-card-title class="text-h4 font-weight-bold text-center pa-6 bg-primary">
        <v-icon class="mr-2" size="large">mdi-package-variant-plus</v-icon>
        发布商品
      </v-card-title>

      <v-card-text class="pa-8">
        <v-form ref="formRef" @submit.prevent="handlePublish">
          <!-- 基本信息 -->
          <div class="mb-8">
            <h2 class="text-h5 font-weight-bold mb-4 d-flex align-center">
              <v-icon class="mr-2" color="primary">mdi-information</v-icon>
              基本信息
            </h2>

            <v-text-field
              v-model="form.title"
              label="商品标题"
              placeholder="请输入商品标题"
              prepend-inner-icon="mdi-tag"
              variant="outlined"
              counter="100"
              maxlength="100"
              :rules="[rules.required]"
              required
              class="mb-4"
            ></v-text-field>

            <v-select
              v-model="form.category_id"
              :items="categoryOptions"
              item-title="text"
              item-value="value"
              label="商品分类"
              prepend-inner-icon="mdi-shape"
              variant="outlined"
              :rules="[rules.required]"
              required
              class="mb-4"
            ></v-select>

            <v-row>
              <v-col cols="12" sm="6">
                <v-text-field
                  v-model="form.price"
                  type="number"
                  label="售价"
                  prepend-inner-icon="mdi-currency-cny"
                  variant="outlined"
                  step="0.01"
                  min="0"
                  :rules="[rules.required, rules.positiveNumber]"
                  required
                ></v-text-field>
              </v-col>

              <v-col cols="12" sm="6">
                <v-text-field
                  v-model="form.original_price"
                  type="number"
                  label="原价（选填）"
                  prepend-inner-icon="mdi-currency-cny"
                  variant="outlined"
                  step="0.01"
                  min="0"
                  :rules="[rules.originalPriceValid]"
                ></v-text-field>
              </v-col>
            </v-row>

            <v-select
              v-model="form.condition_level"
              :items="conditionOptions"
              item-title="text"
              item-value="value"
              label="成色"
              prepend-inner-icon="mdi-star-circle"
              variant="outlined"
              :rules="[rules.required]"
              required
              class="mb-4"
            ></v-select>

            <v-text-field
              v-model="form.location"
              label="交易地点"
              placeholder="请输入交易地点"
              prepend-inner-icon="mdi-map-marker"
              variant="outlined"
              :rules="[rules.required]"
              required
            ></v-text-field>
          </div>

          <v-divider class="my-8"></v-divider>

          <!-- 商品描述 -->
          <div class="mb-8">
            <h2 class="text-h5 font-weight-bold mb-4 d-flex align-center">
              <v-icon class="mr-2" color="primary">mdi-text-box</v-icon>
              商品描述
            </h2>

            <v-textarea
              v-model="form.description"
              label="详细描述"
              placeholder="请详细描述商品的特点、使用情况等"
              prepend-inner-icon="mdi-text"
              variant="outlined"
              counter="1000"
              maxlength="1000"
              rows="6"
              :rules="[rules.required]"
              required
            ></v-textarea>
          </div>

          <v-divider class="my-8"></v-divider>

          <!-- 商品图片 -->
          <div class="mb-8">
            <h2 class="text-h5 font-weight-bold mb-4 d-flex align-center">
              <v-icon class="mr-2" color="primary">mdi-image-multiple</v-icon>
              商品图片
            </h2>

            <v-card
              variant="outlined"
              class="upload-area mb-4"
              :class="{ 'upload-area-hover': form.images.length < 9 }"
              @click="form.images.length < 9 && triggerFileInput()"
            >
              <v-card-text class="text-center pa-8">
                <input
                  ref="fileInput"
                  type="file"
                  multiple
                  accept="image/*"
                  @change="handleImageUpload"
                  style="display: none"
                />
                <v-icon size="80" color="grey-lighten-1" class="mb-4">mdi-camera-plus</v-icon>
                <div class="text-h6 mb-2">点击上传图片</div>
                <div class="text-body-2 text-grey">最多9张，每张不超过5MB</div>
                <div class="text-caption text-grey mt-2">已上传 {{ form.images.length }}/9</div>
              </v-card-text>
            </v-card>

            <!-- 图片预览 -->
            <v-row v-if="form.images.length > 0">
              <v-col
                v-for="(image, index) in form.images"
                :key="index"
                cols="6"
                sm="4"
                md="3"
              >
                <v-card class="image-item">
                  <v-img
                    :src="image"
                    aspect-ratio="1"
                    cover
                  ></v-img>
                  <v-btn
                    icon="mdi-close"
                    size="small"
                    color="error"
                    class="remove-btn"
                    @click="removeImage(index)"
                  ></v-btn>
                </v-card>
              </v-col>
            </v-row>
          </div>

          <!-- 错误和成功消息 -->
          <v-alert
            v-if="errorMessage"
            type="error"
            variant="tonal"
            class="mb-4"
            closable
            @click:close="errorMessage = ''"
          >
            {{ errorMessage }}
          </v-alert>

          <v-alert
            v-if="successMessage"
            type="success"
            variant="tonal"
            class="mb-4"
          >
            {{ successMessage }}
          </v-alert>

          <!-- 操作按钮 -->
          <div class="d-flex justify-center ga-4">
            <v-btn
              variant="outlined"
              size="large"
              prepend-icon="mdi-refresh"
              @click="resetForm"
              :disabled="loading"
            >
              重置
            </v-btn>

            <v-btn
              type="submit"
              color="primary"
              size="large"
              prepend-icon="mdi-upload"
              :loading="loading"
            >
              发布商品
            </v-btn>
          </div>
        </v-form>
      </v-card-text>
    </v-card>
  </v-container>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { useNotification } from '@/composables/useNotification'
import { itemAPI } from '@/api'
import type { ConditionLevel } from '@/types'

interface Category {
  category_id: number
  category_name: string
}

interface PublishForm {
  title: string
  category_id: string
  price: string
  original_price: string
  condition_level: string
  location: string
  description: string
  images: string[]
}

const router = useRouter()
const userStore = useUserStore()
const notification = useNotification()

const formRef = ref()
const fileInput = ref<HTMLInputElement | null>(null)

const form = ref<PublishForm>({
  title: '',
  category_id: '',
  price: '',
  original_price: '',
  condition_level: '',
  location: '',
  description: '',
  images: []
})

const categories = ref<Category[]>([])
const loading = ref(false)
const errorMessage = ref('')
const successMessage = ref('')

// 分类选项
const categoryOptions = computed(() => {
  return categories.value.map(cat => ({
    text: cat.category_name,
    value: cat.category_id.toString()
  }))
})

// 成色选项
const conditionOptions = [
  { text: '全新', value: 'brand_new' },
  { text: '几乎全新', value: 'like_new' },
  { text: '轻微使用', value: 'very_good' },
  { text: '明显使用', value: 'good' },
  { text: '磨损较重', value: 'acceptable' }
]

// 验证规则
const rules = {
  required: (value: string) => !!value || '此字段为必填项',
  positiveNumber: (value: string) => {
    const num = parseFloat(value)
    return (num > 0) || '请输入有效的价格'
  },
  originalPriceValid: (value: string) => {
    if (!value) return true
    const originalPrice = parseFloat(value)
    const price = parseFloat(form.value.price)
    return originalPrice >= price || '原价不能低于售价'
  }
}

const loadCategories = async (): Promise<void> => {
  try {
    const response = await itemAPI.getCategories()
    categories.value = response.categories || []
  } catch (error) {
    console.error('Failed to load categories:', error)
    notification.error('加载分类失败')
  }
}

const triggerFileInput = (): void => {
  fileInput.value?.click()
}

const handleImageUpload = (event: Event): void => {
  const target = event.target as HTMLInputElement
  const files = Array.from(target.files || [])

  if (form.value.images.length + files.length > 9) {
    errorMessage.value = '最多只能上传9张图片'
    setTimeout(() => errorMessage.value = '', 3000)
    return
  }

  files.forEach(file => {
    if (file.size > 5 * 1024 * 1024) {
      errorMessage.value = '图片大小不能超过5MB'
      setTimeout(() => errorMessage.value = '', 3000)
      return
    }

    const reader = new FileReader()
    reader.onload = (e) => {
      if (e.target?.result) {
        form.value.images.push(e.target.result as string)
      }
    }
    reader.readAsDataURL(file)
  })

  target.value = ''
}

const removeImage = (index: number): void => {
  form.value.images.splice(index, 1)
}

const validateForm = (): string | null => {
  if (!form.value.title.trim()) {
    return '请输入商品标题'
  }

  if (!form.value.category_id) {
    return '请选择商品分类'
  }

  if (!form.value.price || parseFloat(form.value.price) <= 0) {
    return '请输入有效的售价'
  }

  if (form.value.original_price && parseFloat(form.value.original_price) < parseFloat(form.value.price)) {
    return '原价不能低于售价'
  }

  if (!form.value.condition_level) {
    return '请选择商品成色'
  }

  if (!form.value.location.trim()) {
    return '请输入交易地点'
  }

  if (!form.value.description.trim()) {
    return '请输入商品描述'
  }

  return null
}

const handlePublish = async (): Promise<void> => {
  const validationError = validateForm()
  if (validationError) {
    errorMessage.value = validationError
    return
  }

  if (!userStore.isLoggedIn || !userStore.currentUser) {
    router.push('/login')
    return
  }

  loading.value = true
  errorMessage.value = ''
  successMessage.value = ''

  try {
    const publishData = {
      user_id: userStore.currentUser.user_id,
      title: form.value.title.trim(),
      category_id: parseInt(form.value.category_id, 10),
      price: parseFloat(form.value.price),
      original_price: form.value.original_price ? parseFloat(form.value.original_price) : null,
      condition_level: form.value.condition_level as ConditionLevel,
      location: form.value.location.trim(),
      description: form.value.description.trim(),
      images: form.value.images
    }

    const response = await itemAPI.createItem(publishData)

    if (response.item_id) {
      successMessage.value = '商品发布成功！即将跳转到商品详情页...'
      notification.success('商品发布成功！')
      setTimeout(() => {
        router.push(`/items/${response.item_id}`)
      }, 2000)
    }
  } catch (error: unknown) {
    console.error('Failed to publish item:', error)
    const err = error as { response?: { data?: { error?: string } } }
    const message = err.response?.data?.error || '发布失败，请重试'
    errorMessage.value = message
    notification.error(message)
  } finally {
    loading.value = false
  }
}

const resetForm = (): void => {
  form.value = {
    title: '',
    category_id: '',
    price: '',
    original_price: '',
    condition_level: '',
    location: '',
    description: '',
    images: []
  }
  errorMessage.value = ''
  successMessage.value = ''
  formRef.value?.resetValidation()
}

onMounted(() => {
  if (!userStore.isLoggedIn) {
    notification.warning('请先登录')
    router.push('/login')
    return
  }

  loadCategories()
})
</script>

<style scoped>
.publish-view {
  max-width: 1000px;
  padding: 40px 20px;
}

.upload-area {
  cursor: pointer;
  transition: all 0.3s;
  border: 2px dashed rgba(var(--v-border-color), var(--v-border-opacity));
}

.upload-area-hover:hover {
  border-color: rgb(var(--v-theme-primary));
  background-color: rgba(var(--v-theme-primary), 0.05);
}

.image-item {
  position: relative;
}

.remove-btn {
  position: absolute;
  top: 8px;
  right: 8px;
  z-index: 1;
}
</style>
