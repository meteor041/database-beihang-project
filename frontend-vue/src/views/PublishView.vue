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

const router = useRouter()
const userStore = useUserStore()

const form = ref({
  title: '',
  category_id: '',
  price: '',
  original_price: '',
  condition_level: '',
  location: '',
  description: '',
  images: []
})

const categories = ref([])
const loading = ref(false)
const errorMessage = ref('')
const successMessage = ref('')
const fileInput = ref(null)

const loadCategories = async () => {
  try {
    const response = await itemAPI.getCategories()
    categories.value = response.categories || []
  } catch (error) {
    console.error('Failed to load categories:', error)
  }
}

const triggerFileInput = () => {
  fileInput.value?.click()
}

const handleImageUpload = (event) => {
  const files = Array.from(event.target.files)
  
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
      form.value.images.push(e.target.result)
    }
    reader.readAsDataURL(file)
  })

  // 清空文件输入
  event.target.value = ''
}

const removeImage = (index) => {
  form.value.images.splice(index, 1)
}

const validateForm = () => {
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

const handlePublish = async () => {
  const validationError = validateForm()
  if (validationError) {
    errorMessage.value = validationError
    return
  }

  if (!userStore.isLoggedIn) {
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
      category_id: parseInt(form.value.category_id),
      price: parseFloat(form.value.price),
      original_price: form.value.original_price ? parseFloat(form.value.original_price) : null,
      condition_level: form.value.condition_level,
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
  } catch (error) {
    console.error('Failed to publish item:', error)
    errorMessage.value = error.response?.data?.error || '发布失败，请重试'
  } finally {
    loading.value = false
  }
}

const resetForm = () => {
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
.publish-view {
  max-width: 1000px;
  margin: 0 auto;
  padding: 30px 40px;
}

.publish-container {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  padding: 30px;
}

.publish-container h1 {
  color: #2c3e50;
  margin-bottom: 30px;
  text-align: center;
}

.publish-form {
  display: flex;
  flex-direction: column;
  gap: 30px;
}

.form-section {
  border-bottom: 1px solid #eee;
  padding-bottom: 30px;
}

.form-section:last-of-type {
  border-bottom: none;
  padding-bottom: 0;
}

.form-section h2 {
  color: #2c3e50;
  margin-bottom: 20px;
  font-size: 1.3rem;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
  position: relative;
}

.form-group label {
  font-weight: 500;
  color: #2c3e50;
}

.form-group input,
.form-group select,
.form-group textarea {
  padding: 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 16px;
  transition: border-color 0.3s;
}

.form-group input:focus,
.form-group select:focus,
.form-group textarea:focus {
  outline: none;
  border-color: #007bff;
}

.char-count {
  position: absolute;
  bottom: 8px;
  right: 12px;
  font-size: 12px;
  color: #6c757d;
  background: white;
  padding: 2px 4px;
}

.image-upload {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.upload-area {
  border: 2px dashed #ddd;
  border-radius: 8px;
  padding: 40px;
  text-align: center;
  cursor: pointer;
  transition: border-color 0.3s;
}

.upload-area:hover {
  border-color: #007bff;
}

.upload-icon {
  font-size: 3rem;
  margin-bottom: 10px;
}

.upload-text {
  font-size: 1.1rem;
  color: #2c3e50;
  margin-bottom: 5px;
}

.upload-hint {
  font-size: 0.9rem;
  color: #6c757d;
}

.image-preview {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
  gap: 15px;
}

.image-item {
  position: relative;
  aspect-ratio: 1;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.image-item img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.remove-btn {
  position: absolute;
  top: 5px;
  right: 5px;
  width: 24px;
  height: 24px;
  border: none;
  border-radius: 50%;
  background: rgba(0,0,0,0.7);
  color: white;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
  line-height: 1;
}

.remove-btn:hover {
  background: rgba(0,0,0,0.9);
}

.error-message {
  color: #dc3545;
  font-size: 14px;
  text-align: center;
  padding: 10px;
  background-color: #f8d7da;
  border: 1px solid #f5c6cb;
  border-radius: 4px;
}

.success-message {
  color: #155724;
  font-size: 14px;
  text-align: center;
  padding: 10px;
  background-color: #d4edda;
  border: 1px solid #c3e6cb;
  border-radius: 4px;
}

.form-actions {
  display: flex;
  gap: 20px;
  justify-content: center;
  padding-top: 20px;
}

.reset-btn,
.submit-btn {
  padding: 12px 30px;
  border: none;
  border-radius: 6px;
  font-size: 16px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s;
}

.reset-btn {
  background: #6c757d;
  color: white;
}

.reset-btn:hover {
  background: #5a6268;
}

.submit-btn {
  background: #007bff;
  color: white;
}

.submit-btn:hover:not(:disabled) {
  background: #0056b3;
}

.submit-btn:disabled {
  background: #6c757d;
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