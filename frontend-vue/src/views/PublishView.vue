<template>
  <div class="publish-view">
    <div class="publish-container">
      <h1>发布商品</h1>
      
      <form @submit.prevent="handlePublish" class="publish-form">
        <div class="form-section">
          <h2>基本信息</h2>
          
          <div class="form-group">
            <label for="title">商品标题 *</label>
            <input
              id="title"
              v-model="form.title"
              type="text"
              placeholder="请输入商品标题（最多100字符）"
              maxlength="100"
              required
            />
            <div class="char-count">{{ form.title.length }}/100</div>
          </div>

          <div class="form-group">
            <label for="category">商品分类 *</label>
            <select id="category" v-model="form.category_id" required>
              <option value="">请选择分类</option>
              <option 
                v-for="category in categories" 
                :key="category.category_id"
                :value="category.category_id"
              >
                {{ category.category_name }}
              </option>
            </select>
          </div>

          <div class="form-row">
            <div class="form-group">
              <label for="price">售价 *</label>
              <input
                id="price"
                v-model="form.price"
                type="number"
                step="0.01"
                min="0"
                placeholder="0.00"
                required
              />
            </div>

            <div class="form-group">
              <label for="originalPrice">原价</label>
              <input
                id="originalPrice"
                v-model="form.original_price"
                type="number"
                step="0.01"
                min="0"
                placeholder="0.00"
              />
            </div>
          </div>

          <div class="form-group">
            <label for="condition">成色 *</label>
            <select id="condition" v-model="form.condition_level" required>
              <option value="">请选择成色</option>
              <option value="brand_new">全新</option>
              <option value="like_new">几乎全新</option>
              <option value="very_good">非常好</option>
              <option value="good">良好</option>
              <option value="acceptable">可接受</option>
            </select>
          </div>

          <div class="form-group">
            <label for="location">交易地点 *</label>
            <input
              id="location"
              v-model="form.location"
              type="text"
              placeholder="请输入交易地点"
              required
            />
          </div>
        </div>

        <div class="form-section">
          <h2>商品描述</h2>
          
          <div class="form-group">
            <label for="description">详细描述 *</label>
            <textarea
              id="description"
              v-model="form.description"
              placeholder="请详细描述商品的特点、使用情况等（最多1000字符）"
              maxlength="1000"
              rows="6"
              required
            ></textarea>
            <div class="char-count">{{ form.description.length }}/1000</div>
          </div>
        </div>

        <div class="form-section">
          <h2>商品图片</h2>
          
          <div class="image-upload">
            <div class="upload-area" @click="triggerFileInput">
              <input
                ref="fileInput"
                type="file"
                multiple
                accept="image/*"
                @change="handleImageUpload"
                style="display: none"
              />
              <div class="upload-placeholder">
                <div class="upload-icon">📷</div>
                <div class="upload-text">点击上传图片</div>
                <div class="upload-hint">最多9张，每张不超过5MB</div>
              </div>
            </div>

            <div v-if="form.images.length > 0" class="image-preview">
              <div 
                v-for="(image, index) in form.images"
                :key="index"
                class="image-item"
              >
                <img :src="image" :alt="`商品图片 ${index + 1}`" />
                <button 
                  type="button"
                  @click="removeImage(index)"
                  class="remove-btn"
                >
                  ×
                </button>
              </div>
            </div>
          </div>
        </div>

        <div v-if="errorMessage" class="error-message">
          {{ errorMessage }}
        </div>

        <div v-if="successMessage" class="success-message">
          {{ successMessage }}
        </div>

        <div class="form-actions">
          <button type="button" @click="resetForm" class="reset-btn">
            重置
          </button>
          <button type="submit" :disabled="loading" class="submit-btn">
            {{ loading ? '发布中...' : '发布商品' }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
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
const fileInput = ref<HTMLInputElement | null>(null)

const loadCategories = async (): Promise<void> => {
  try {
    const response = await itemAPI.getCategories()
    categories.value = response.categories || []
  } catch (error) {
    console.error('Failed to load categories:', error)
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
    return
  }

  files.forEach(file => {
    if (file.size > 5 * 1024 * 1024) {
      errorMessage.value = '图片大小不能超过5MB'
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
      setTimeout(() => {
        router.push(`/items/${response.item_id}`)
      }, 2000)
    }
  } catch (error: unknown) {
    console.error('Failed to publish item:', error)
    const err = error as { response?: { data?: { error?: string } } }
    errorMessage.value = err.response?.data?.error || '发布失败，请重试'
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
}

onMounted(() => {
  if (!userStore.isLoggedIn) {
    router.push('/login')
    return
  }
  
  loadCategories()
})
</script>

<style scoped>
/* 使用设计系统变量 */
.publish-view {
  max-width: 1000px;
  margin: 0 auto;
  padding: var(--spacing-2xl) var(--spacing-3xl);
}

.publish-container {
  background: var(--color-bg-card);
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-card);
  padding: var(--spacing-2xl);
}

.publish-container h1 {
  color: var(--color-text-primary);
  margin-bottom: var(--spacing-2xl);
  text-align: center;
}

.publish-form {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-2xl);
}

.form-section {
  border-bottom: 1px solid var(--color-border-lighter);
  padding-bottom: var(--spacing-2xl);
}

.form-section:last-of-type {
  border-bottom: none;
  padding-bottom: 0;
}

.form-section h2 {
  color: var(--color-text-primary);
  margin-bottom: var(--spacing-lg);
  font-size: var(--font-size-3xl);
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--spacing-lg);
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-sm);
  position: relative;
}

.form-group label {
  font-weight: var(--font-weight-medium);
  color: var(--color-text-primary);
}

.form-group input,
.form-group select,
.form-group textarea {
  padding: var(--spacing-md);
  border: 1px solid var(--color-border-base);
  border-radius: var(--radius-sm);
  font-size: var(--font-size-lg);
  transition: border-color var(--transition-base);
}

.form-group input:focus,
.form-group select:focus,
.form-group textarea:focus {
  outline: none;
  border-color: var(--color-primary);
}

.char-count {
  position: absolute;
  bottom: var(--spacing-sm);
  right: var(--spacing-md);
  font-size: var(--font-size-xs);
  color: var(--color-text-secondary);
  background: var(--color-bg-card);
  padding: var(--spacing-xs) var(--spacing-xs);
}

.image-upload {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-lg);
}

.upload-area {
  border: 2px dashed var(--color-border-base);
  border-radius: var(--radius-md);
  padding: var(--spacing-3xl);
  text-align: center;
  cursor: pointer;
  transition: border-color var(--transition-base);
}

.upload-area:hover {
  border-color: var(--color-primary);
}

.upload-icon {
  font-size: var(--font-size-6xl);
  margin-bottom: var(--spacing-sm);
}

.upload-text {
  font-size: var(--font-size-lg);
  color: var(--color-text-primary);
  margin-bottom: var(--spacing-xs);
}

.upload-hint {
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
}

.image-preview {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
  gap: var(--spacing-md);
}

.image-item {
  position: relative;
  aspect-ratio: 1;
  border-radius: var(--radius-md);
  overflow: hidden;
  box-shadow: var(--shadow-card);
}

.image-item img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.remove-btn {
  position: absolute;
  top: var(--spacing-xs);
  right: var(--spacing-xs);
  width: 24px;
  height: 24px;
  border: none;
  border-radius: var(--radius-round);
  background: var(--color-bg-overlay);
  color: white;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: var(--font-size-lg);
  line-height: 1;
}

.remove-btn:hover {
  background: rgba(0,0,0,0.9);
}

.error-message {
  color: var(--color-danger);
  font-size: var(--font-size-base);
  text-align: center;
  padding: var(--spacing-sm);
  background-color: var(--color-danger-light);
  border: 1px solid #f5c6cb;
  border-radius: var(--radius-sm);
}

.success-message {
  color: #155724;
  font-size: var(--font-size-base);
  text-align: center;
  padding: var(--spacing-sm);
  background-color: var(--color-success-light);
  border: 1px solid #c3e6cb;
  border-radius: var(--radius-sm);
}

.form-actions {
  display: flex;
  gap: var(--spacing-lg);
  justify-content: center;
  padding-top: var(--spacing-lg);
}

.reset-btn,
.submit-btn {
  padding: var(--spacing-md) var(--spacing-2xl);
  border: none;
  border-radius: var(--radius-base);
  font-size: var(--font-size-lg);
  font-weight: var(--font-weight-medium);
  cursor: pointer;
  transition: all var(--transition-base);
}

.reset-btn {
  background: var(--color-info);
  color: white;
}

.reset-btn:hover {
  background: #5a6268;
}

.submit-btn {
  background: var(--color-primary);
  color: white;
}

.submit-btn:hover:not(:disabled) {
  background: var(--color-primary-dark);
}

.submit-btn:disabled {
  background: var(--color-info);
  cursor: not-allowed;
}

@media (max-width: 768px) {
  .form-row {
    grid-template-columns: 1fr;
  }

  .form-actions {
    flex-direction: column;
  }

  .reset-btn,
  .submit-btn {
    width: 100%;
  }
}
</style>
