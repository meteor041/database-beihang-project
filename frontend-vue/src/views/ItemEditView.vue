<template>
  <div class="item-edit-view">
    <div class="edit-container">
      <h1>编辑商品</h1>

      <div v-if="loading" class="loading">
        加载中...
      </div>

      <div v-else-if="!item" class="error">
        商品不存在
      </div>

      <form v-else @submit.prevent="handleSubmit" class="edit-form">
        <!-- 商品标题 -->
        <div class="form-group">
          <label>商品标题 <span class="required">*</span></label>
          <input
            v-model="form.title"
            type="text"
            placeholder="请输入商品标题"
            maxlength="100"
            required
          />
        </div>

        <!-- 分类选择 -->
        <div class="form-group">
          <label>商品分类 <span class="required">*</span></label>
          <select v-model="form.category_id" required>
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

        <!-- 价格 -->
        <div class="form-row">
          <div class="form-group">
            <label>售价 <span class="required">*</span></label>
            <input
              v-model="form.price"
              type="number"
              step="0.01"
              min="0"
              placeholder="请输入售价"
              required
            />
          </div>
          <div class="form-group">
            <label>原价</label>
            <input
              v-model="form.original_price"
              type="number"
              step="0.01"
              min="0"
              placeholder="选填"
            />
          </div>
        </div>

        <!-- 成色 -->
        <div class="form-group">
          <label>商品成色 <span class="required">*</span></label>
          <select v-model="form.condition_level" required>
            <option value="">请选择成色</option>
            <option value="brand_new">全新</option>
            <option value="like_new">几乎全新</option>
            <option value="very_good">非常好</option>
            <option value="good">良好</option>
            <option value="acceptable">可接受</option>
          </select>
        </div>

        <!-- 交易地点 -->
        <div class="form-group">
          <label>交易地点 <span class="required">*</span></label>
          <input
            v-model="form.location"
            type="text"
            placeholder="如：北航学院路校区东门"
            required
          />
        </div>

        <!-- 商品描述 -->
        <div class="form-group">
          <label>商品描述 <span class="required">*</span></label>
          <textarea
            v-model="form.description"
            rows="6"
            placeholder="请详细描述商品信息、购买时间、使用情况等"
            maxlength="2000"
            required
          ></textarea>
          <div class="char-count">{{ form.description.length }}/2000</div>
        </div>

        <!-- 商品图片 -->
        <div class="form-group">
          <label>商品图片 <span class="tip">（最多9张）</span></label>
          <div class="image-upload">
            <div
              v-for="(image, index) in form.images"
              :key="index"
              class="image-item"
            >
              <img :src="image" :alt="`商品图片${index + 1}`" />
              <button
                type="button"
                @click="removeImage(index)"
                class="remove-btn"
              >
                ×
              </button>
            </div>
            <div
              v-if="form.images.length < 9"
              @click="triggerFileInput"
              class="upload-btn"
            >
              <span>+</span>
              <span>添加图片</span>
            </div>
            <input
              ref="fileInput"
              type="file"
              accept="image/*"
              multiple
              @change="handleImageUpload"
              style="display: none"
            />
          </div>
        </div>

        <!-- 错误和成功提示 -->
        <div v-if="errorMessage" class="message error">
          {{ errorMessage }}
        </div>
        <div v-if="successMessage" class="message success">
          {{ successMessage }}
        </div>

        <!-- 按钮组 -->
        <div class="form-actions">
          <button type="button" @click="router.back()" class="btn-cancel">
            取消
          </button>
          <button
            type="submit"
            :disabled="submitting"
            class="btn-submit"
          >
            {{ submitting ? '保存中...' : '保存修改' }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { itemAPI } from '@/api'
import type { Item, Category } from '@/types'
import { ElMessage } from 'element-plus'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()

const item = ref<Item | null>(null)
const categories = ref<Category[]>([])
const loading = ref(false)
const submitting = ref(false)
const errorMessage = ref('')
const successMessage = ref('')
const fileInput = ref<HTMLInputElement | null>(null)

interface EditForm {
  title: string
  category_id: number | ''
  price: string
  original_price: string
  condition_level: string
  location: string
  description: string
  images: string[]
}

const form = ref<EditForm>({
  title: '',
  category_id: '',
  price: '',
  original_price: '',
  condition_level: '',
  location: '',
  description: '',
  images: []
})

const loadItem = async (): Promise<void> => {
  const itemId = route.params.id
  if (!itemId) {
    ElMessage.error('缺少商品ID')
    router.back()
    return
  }

  loading.value = true
  try {
    const response = await itemAPI.getItem(Number(itemId))
    item.value = response.item

    if (!item.value) {
      ElMessage.error('商品不存在')
      setTimeout(() => router.back(), 1500)
      return
    }

    // 检查是否是商品所有者
    if (!userStore.currentUser || item.value.user_id !== userStore.currentUser.user_id) {
      ElMessage.error('您无权编辑此商品')
      setTimeout(() => router.back(), 1500)
      return
    }

    // 填充表单
    form.value = {
      title: item.value.title,
      category_id: item.value.category_id,
      price: item.value.price.toString(),
      original_price: item.value.original_price?.toString() || '',
      condition_level: item.value.condition_level,
      location: item.value.location,
      description: item.value.description,
      images: Array.isArray(item.value.images) ? item.value.images : []
    }
  } catch (error) {
    console.error('Failed to load item:', error)
    ElMessage.error('加载商品失败')
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

const handleSubmit = async (): Promise<void> => {
  const validationError = validateForm()
  if (validationError) {
    errorMessage.value = validationError
    return
  }

  if (!item.value) return

  submitting.value = true
  errorMessage.value = ''
  successMessage.value = ''

  try {
    const updateData: any = {
      title: form.value.title.trim(),
      category_id: Number(form.value.category_id),
      price: parseFloat(form.value.price),
      original_price: form.value.original_price ? parseFloat(form.value.original_price) : undefined,
      condition_level: form.value.condition_level,
      location: form.value.location.trim(),
      description: form.value.description.trim(),
      images: form.value.images
    }

    await itemAPI.updateItem(item.value.item_id, updateData)

    successMessage.value = '商品更新成功！'
    ElMessage.success('商品更新成功！')

    setTimeout(() => {
      router.push(`/items/${item.value?.item_id}`)
    }, 1500)
  } catch (error: any) {
    console.error('Failed to update item:', error)
    errorMessage.value = error.response?.data?.error || '更新失败，请重试'
    ElMessage.error(errorMessage.value)
  } finally {
    submitting.value = false
  }
}

onMounted(() => {
  if (!userStore.isLoggedIn) {
    router.push('/login')
    return
  }

  loadItem()
  loadCategories()
})
</script>

<style scoped>
.item-edit-view {
  min-height: calc(100vh - 200px);
  background-color: #f5f5f5;
  padding: 20px;
}

.edit-container {
  max-width: 800px;
  margin: 0 auto;
  background: white;
  border-radius: 12px;
  padding: 30px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

.edit-container h1 {
  color: #303133;
  margin-bottom: 30px;
  text-align: center;
}

.loading,
.error {
  text-align: center;
  padding: 40px;
  color: #909399;
}

.edit-form {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 15px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-group label {
  color: #303133;
  font-weight: 500;
}

.required {
  color: #f56c6c;
}

.tip {
  color: #909399;
  font-size: 12px;
  font-weight: normal;
}

.form-group input,
.form-group select,
.form-group textarea {
  padding: 12px;
  border: 1px solid #dcdfe6;
  border-radius: 8px;
  font-size: 14px;
  font-family: inherit;
  transition: border-color 0.3s;
}

.form-group input:focus,
.form-group select:focus,
.form-group textarea:focus {
  outline: none;
  border-color: #409eff;
}

.char-count {
  text-align: right;
  color: #909399;
  font-size: 12px;
}

/* 图片上传 */
.image-upload {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(100px, 1fr));
  gap: 10px;
}

.image-item {
  position: relative;
  width: 100%;
  padding-bottom: 100%;
  border-radius: 8px;
  overflow: hidden;
}

.image-item img {
  position: absolute;
  top: 0;
  left: 0;
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
  background: rgba(0, 0, 0, 0.6);
  color: white;
  border: none;
  border-radius: 50%;
  cursor: pointer;
  font-size: 18px;
  line-height: 1;
  display: flex;
  align-items: center;
  justify-content: center;
}

.remove-btn:hover {
  background: rgba(0, 0, 0, 0.8);
}

.upload-btn {
  width: 100%;
  padding-bottom: 100%;
  position: relative;
  border: 2px dashed #dcdfe6;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.upload-btn > * {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
}

.upload-btn span:first-child {
  font-size: 32px;
  color: #909399;
  margin-top: -15px;
}

.upload-btn span:last-child {
  font-size: 12px;
  color: #909399;
  margin-top: 20px;
}

.upload-btn:hover {
  border-color: #409eff;
  background: #ecf5ff;
}

/* 消息提示 */
.message {
  padding: 12px;
  border-radius: 8px;
  font-size: 14px;
}

.message.error {
  background: #fef0f0;
  color: #f56c6c;
  border: 1px solid #fde2e2;
}

.message.success {
  background: #f0f9ff;
  color: #67c23a;
  border: 1px solid #d9ecff;
}

/* 按钮 */
.form-actions {
  display: flex;
  gap: 15px;
  justify-content: center;
  margin-top: 20px;
}

.btn-cancel,
.btn-submit {
  padding: 12px 40px;
  border: none;
  border-radius: 8px;
  font-size: 16px;
  cursor: pointer;
  transition: all 0.3s;
}

.btn-cancel {
  background: #f5f5f5;
  color: #606266;
}

.btn-cancel:hover {
  background: #e0e0e0;
}

.btn-submit {
  background: #409eff;
  color: white;
}

.btn-submit:hover:not(:disabled) {
  background: #66b1ff;
}

.btn-submit:disabled {
  background: #c0c4cc;
  cursor: not-allowed;
}

@media (max-width: 768px) {
  .form-row {
    grid-template-columns: 1fr;
  }

  .edit-container {
    padding: 20px;
  }

  .form-actions {
    flex-direction: column;
  }

  .btn-cancel,
  .btn-submit {
    width: 100%;
  }
}
</style>
