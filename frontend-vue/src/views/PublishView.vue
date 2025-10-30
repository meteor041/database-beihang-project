<template>
  <div class="publish-view">
    <!-- 页面头部 -->
    <div class="page-header">
      <el-icon :size="32"><Plus /></el-icon>
      <div>
        <h1>发布商品</h1>
        <p class="subtitle">填写商品信息，让闲置物品找到新主人</p>
      </div>
    </div>

    <!-- 发布表单 -->
    <el-form
      ref="formRef"
      :model="form"
      :rules="rules"
      label-position="top"
      size="large"
      class="publish-form"
    >
      <!-- 基本信息卡片 -->
      <el-card shadow="hover" class="form-card">
        <template #header>
          <div class="card-header">
            <el-icon><Document /></el-icon>
            <span>基本信息</span>
          </div>
        </template>

        <el-form-item label="商品标题" prop="title">
          <el-input
            v-model="form.title"
            placeholder="简短清晰地描述你的商品"
            maxlength="100"
            show-word-limit
            clearable
          >
            <template #prefix>
              <el-icon><EditPen /></el-icon>
            </template>
          </el-input>
        </el-form-item>

        <el-row :gutter="20">
          <el-col :xs="24" :sm="12">
            <el-form-item label="商品分类" prop="category_id">
              <el-select
                v-model="form.category_id"
                placeholder="选择合适的分类"
                clearable
                filterable
                style="width: 100%"
              >
                <el-option
                  v-for="category in categories"
                  :key="category.category_id"
                  :value="category.category_id"
                  :label="category.category_name"
                >
                  <span>{{ category.category_name }}</span>
                </el-option>
              </el-select>
            </el-form-item>
          </el-col>

          <el-col :xs="24" :sm="12">
            <el-form-item label="成色" prop="condition_level">
              <el-select
                v-model="form.condition_level"
                placeholder="选择商品成色"
                clearable
                style="width: 100%"
              >
                <el-option value="brand_new" label="全新">
                  <el-tag type="success" size="small">全新</el-tag>
                  <span style="margin-left: 8px; color: #909399; font-size: 13px;">未拆封使用</span>
                </el-option>
                <el-option value="like_new" label="几乎全新">
                  <el-tag type="success" size="small" effect="plain">几乎全新</el-tag>
                  <span style="margin-left: 8px; color: #909399; font-size: 13px;">轻度使用</span>
                </el-option>
                <el-option value="very_good" label="非常好">
                  <el-tag type="" size="small">非常好</el-tag>
                  <span style="margin-left: 8px; color: #909399; font-size: 13px;">正常使用</span>
                </el-option>
                <el-option value="good" label="良好">
                  <el-tag type="warning" size="small" effect="plain">良好</el-tag>
                  <span style="margin-left: 8px; color: #909399; font-size: 13px;">有使用痕迹</span>
                </el-option>
                <el-option value="acceptable" label="可接受">
                  <el-tag type="info" size="small">可接受</el-tag>
                  <span style="margin-left: 8px; color: #909399; font-size: 13px;">明显磨损</span>
                </el-option>
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :xs="24" :sm="12">
            <el-form-item label="售价" prop="price">
              <el-input
                v-model="form.price"
                type="number"
                placeholder="0.00"
                clearable
              >
                <template #prefix>
                  <span style="color: #ff4d4f; font-weight: bold;">¥</span>
                </template>
              </el-input>
              <template #extra>
                <span class="form-hint">
                  <el-icon><InfoFilled /></el-icon>
                  请设置合理的价格，更容易成交
                </span>
              </template>
            </el-form-item>
          </el-col>

          <el-col :xs="24" :sm="12">
            <el-form-item label="原价（选填）" prop="original_price">
              <el-input
                v-model="form.original_price"
                type="number"
                placeholder="0.00"
                clearable
              >
                <template #prefix>
                  <span style="color: #909399;">¥</span>
                </template>
              </el-input>
              <template #extra>
                <span class="form-hint">
                  <el-icon><InfoFilled /></el-icon>
                  可选，用于显示折扣力度
                </span>
              </template>
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item label="交易地点" prop="location">
          <el-input
            v-model="form.location"
            placeholder="如：北航学院路校区、沙河校区宿舍楼等"
            clearable
          >
            <template #prefix>
              <el-icon><Location /></el-icon>
            </template>
          </el-input>
        </el-form-item>
      </el-card>

      <!-- 商品描述卡片 -->
      <el-card shadow="hover" class="form-card">
        <template #header>
          <div class="card-header">
            <el-icon><Reading /></el-icon>
            <span>商品描述</span>
          </div>
        </template>

        <el-form-item label="详细描述" prop="description">
          <el-input
            v-model="form.description"
            type="textarea"
            :rows="8"
            placeholder="详细描述商品的特点、使用情况、购买时间、使用频率等信息&#10;&#10;提示：&#10;• 说明商品的使用状况&#10;• 是否有配件或包装盒&#10;• 是否存在瑕疵或问题&#10;• 购买/使用时间"
            maxlength="1000"
            show-word-limit
          />
          <template #extra>
            <span class="form-hint">
              <el-icon><InfoFilled /></el-icon>
              详细的描述能让买家更了解商品，提高成交率
            </span>
          </template>
        </el-form-item>
      </el-card>

      <!-- 商品图片卡片 -->
      <el-card shadow="hover" class="form-card">
        <template #header>
          <div class="card-header">
            <el-icon><Picture /></el-icon>
            <span>商品图片</span>
            <el-tag size="small" type="info" class="image-count">
              {{ form.images.length }}/9
            </el-tag>
          </div>
        </template>

        <div class="image-upload-section">
          <!-- 上传区域 -->
          <el-upload
            ref="uploadRef"
            :auto-upload="false"
            :on-change="handleImageChange"
            :show-file-list="false"
            :accept="'image/*'"
            :multiple="true"
            :limit="9"
            :disabled="form.images.length >= 9"
          >
            <el-button
              type="primary"
              :icon="Plus"
              :disabled="form.images.length >= 9"
              size="large"
            >
              {{ form.images.length > 0 ? '继续添加' : '上传图片' }}
            </el-button>
          </el-upload>

          <div class="upload-tips">
            <el-alert
              title="图片要求"
              type="info"
              :closable="false"
              show-icon
            >
              <template #default>
                <ul class="tips-list">
                  <li>最多上传 9 张图片</li>
                  <li>每张图片不超过 5MB</li>
                  <li>支持 JPG、PNG、GIF 格式</li>
                  <li>建议上传清晰的商品实拍图</li>
                </ul>
              </template>
            </el-alert>
          </div>

          <!-- 图片预览 -->
          <div v-if="form.images.length > 0" class="image-preview-grid">
            <el-card
              v-for="(image, index) in form.images"
              :key="index"
              class="image-preview-item"
              body-style="padding: 0"
              shadow="hover"
            >
              <div class="image-wrapper">
                <el-image
                  :src="image"
                  fit="cover"
                  :preview-src-list="form.images"
                  :initial-index="index"
                  class="preview-image"
                >
                  <template #error>
                    <div class="image-error">
                      <el-icon><Picture /></el-icon>
                    </div>
                  </template>
                </el-image>
                <div class="image-overlay">
                  <el-button
                    circle
                    type="danger"
                    :icon="Delete"
                    size="small"
                    @click="removeImage(index)"
                  />
                  <el-tag v-if="index === 0" size="small" type="success" class="cover-badge">
                    封面
                  </el-tag>
                </div>
              </div>
            </el-card>
          </div>

          <!-- 空状态 -->
          <el-empty
            v-else
            description="还没有上传图片"
            :image-size="120"
          >
            <template #image>
              <el-icon :size="80" color="#c0c4cc"><PictureFilled /></el-icon>
            </template>
          </el-empty>
        </div>
      </el-card>

      <!-- 操作按钮 -->
      <div class="form-actions">
        <el-button size="large" @click="handleReset" :icon="RefreshLeft">
          重置
        </el-button>
        <el-button
          type="primary"
          size="large"
          @click="handleSubmit"
          :loading="loading"
          :icon="loading ? Loading : SuccessFilled"
        >
          {{ loading ? '发布中...' : '立即发布' }}
        </el-button>
      </div>
    </el-form>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { itemAPI } from '@/api'
import { ElMessage, ElMessageBox, type FormInstance, type FormRules, type UploadFile } from 'element-plus'
import {
  Plus, Document, EditPen, Location, Reading, Picture, PictureFilled,
  Delete, InfoFilled, SuccessFilled, Loading, RefreshLeft
} from '@element-plus/icons-vue'
import type { ConditionLevel } from '@/types'

interface Category {
  category_id: number
  category_name: string
}

interface PublishForm {
  title: string
  category_id: number | string
  price: number | string
  original_price: number | string
  condition_level: ConditionLevel | ''
  location: string
  description: string
  images: string[]
}

const router = useRouter()
const userStore = useUserStore()

const formRef = ref<FormInstance>()
const uploadRef = ref()

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

// 表单验证规则
const rules: FormRules<PublishForm> = {
  title: [
    { required: true, message: '请输入商品标题', trigger: 'blur' },
    { min: 5, max: 100, message: '标题长度在 5 到 100 个字符', trigger: 'blur' }
  ],
  category_id: [
    { required: true, message: '请选择商品分类', trigger: 'change' }
  ],
  price: [
    { required: true, message: '请输入售价', trigger: 'blur' },
    {
      validator: (rule, value, callback) => {
        if (value && parseFloat(value as string) <= 0) {
          callback(new Error('售价必须大于0'))
        } else {
          callback()
        }
      },
      trigger: 'blur'
    }
  ],
  original_price: [
    {
      validator: (rule, value, callback) => {
        if (value && form.value.price) {
          if (parseFloat(value as string) < parseFloat(form.value.price as string)) {
            callback(new Error('原价不能低于售价'))
          }
        }
        callback()
      },
      trigger: 'blur'
    }
  ],
  condition_level: [
    { required: true, message: '请选择商品成色', trigger: 'change' }
  ],
  location: [
    { required: true, message: '请输入交易地点', trigger: 'blur' },
    { min: 2, max: 100, message: '地点长度在 2 到 100 个字符', trigger: 'blur' }
  ],
  description: [
    { required: true, message: '请输入商品描述', trigger: 'blur' },
    { min: 10, max: 1000, message: '描述长度在 10 到 1000 个字符', trigger: 'blur' }
  ]
}

// 加载分类
const loadCategories = async (): Promise<void> => {
  try {
    const response = await itemAPI.getCategories()
    categories.value = response.categories || []
  } catch (error) {
    console.error('Failed to load categories:', error)
    ElMessage.error('加载分类失败')
  }
}

// 处理图片上传
const handleImageChange = (file: UploadFile): void => {
  if (form.value.images.length >= 9) {
    ElMessage.warning('最多只能上传9张图片')
    return
  }

  const rawFile = file.raw
  if (!rawFile) return

  // 检查文件大小
  if (rawFile.size > 5 * 1024 * 1024) {
    ElMessage.error('图片大小不能超过5MB')
    return
  }

  // 检查文件类型
  if (!rawFile.type.startsWith('image/')) {
    ElMessage.error('只能上传图片文件')
    return
  }

  // 读取图片为base64
  const reader = new FileReader()
  reader.onload = (e) => {
    if (e.target?.result) {
      form.value.images.push(e.target.result as string)
    }
  }
  reader.onerror = () => {
    ElMessage.error('图片读取失败')
  }
  reader.readAsDataURL(rawFile)
}

// 删除图片
const removeImage = (index: number): void => {
  form.value.images.splice(index, 1)
}

// 提交表单
const handleSubmit = async (): Promise<void> => {
  if (!formRef.value) return

  try {
    // 验证表单
    await formRef.value.validate()

    // 检查是否登录
    if (!userStore.isLoggedIn || !userStore.currentUser) {
      ElMessage.warning('请先登录')
      router.push('/login')
      return
    }

    // 检查图片
    if (form.value.images.length === 0) {
      ElMessage.warning('请至少上传一张商品图片')
      return
    }

    loading.value = true

    const publishData = {
      user_id: userStore.currentUser.user_id,
      title: form.value.title.trim(),
      category_id: Number(form.value.category_id),
      price: parseFloat(form.value.price as string),
      original_price: form.value.original_price ? parseFloat(form.value.original_price as string) : null,
      condition_level: form.value.condition_level as ConditionLevel,
      location: form.value.location.trim(),
      description: form.value.description.trim(),
      images: form.value.images
    }

    const response = await itemAPI.createItem(publishData)

    if (response.item_id) {
      ElMessage.success('商品发布成功！')
      setTimeout(() => {
        router.push(`/items/${response.item_id}`)
      }, 1500)
    }
  } catch (error: any) {
    if (error !== 'cancel') {
      console.error('Failed to publish item:', error)
      ElMessage.error(error.response?.data?.error || '发布失败，请重试')
    }
  } finally {
    loading.value = false
  }
}

// 重置表单
const handleReset = async (): Promise<void> => {
  try {
    await ElMessageBox.confirm('确定要重置表单吗？所有填写的内容将被清空', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })

    formRef.value?.resetFields()
    form.value.images = []
    ElMessage.success('表单已重置')
  } catch {
    // 用户取消
  }
}

onMounted(() => {
  if (!userStore.isLoggedIn) {
    ElMessage.warning('请先登录')
    router.push('/login')
    return
  }

  loadCategories()
})
</script>

<style scoped>
/* 现代扁平化风格 - Twitter/YouTube/Google 风格 */

.publish-view {
  width: 100%;
  padding: var(--spacing-6) var(--spacing-8);
  background: var(--color-bg-page);
  min-height: 100vh;
}

.publish-view .publish-form {
  max-width: 1400px;
  margin: 0 auto;
}

/* 页面头部 - 扁平简洁 */
.page-header {
  display: flex;
  align-items: center;
  gap: var(--spacing-4);
  margin-bottom: var(--spacing-8);
}

.page-header h1 {
  margin: 0;
  font-size: var(--font-size-4xl);
  font-weight: var(--font-weight-bold);
  color: var(--color-text-primary);
}

.page-header .el-icon {
  color: var(--color-primary);
  font-size: 32px;
}

.subtitle {
  margin: var(--spacing-2) 0 0 0;
  font-size: var(--font-size-base);
  color: var(--color-text-secondary);
}

/* 表单 */
.publish-form {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-6);
}

/* 表单卡片 - 扁平带边框 */
.form-card {
  background: var(--color-bg-card);
  border: 1px solid var(--color-border-base);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-sm);
  transition: all var(--transition-base);
}

.form-card:hover {
  border-color: var(--color-border-light);
  box-shadow: var(--shadow-md);
  transform: translateY(-2px);
}

.form-card :deep(.el-card__header) {
  background: var(--color-bg-section);
  border-bottom: 1px solid var(--color-border-light);
}

.card-header {
  display: flex;
  align-items: center;
  gap: var(--spacing-3);
  font-size: var(--font-size-lg);
  font-weight: var(--font-weight-medium);
  color: var(--color-text-primary);
}

.card-header .el-icon {
  color: var(--color-primary);
}

.image-count {
  margin-left: auto;
}

/* 表单提示 */
.form-hint {
  display: flex;
  align-items: center;
  gap: var(--spacing-xs);
  font-size: var(--font-size-xs);
  color: var(--color-text-secondary);
}

/* 图片上传区域 */
.image-upload-section {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-lg);
}

.upload-tips {
  margin-top: var(--spacing-md);
}

.tips-list {
  margin: 0;
  padding-left: var(--spacing-lg);
  list-style: disc;
}

.tips-list li {
  margin: var(--spacing-xs) 0;
  color: var(--color-text-regular);
  font-size: var(--font-size-sm);
}

/* 图片预览网格 */
.image-preview-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
  gap: var(--spacing-4);
  margin-top: var(--spacing-4);
}

/* 图片预览卡片 - 扁平带边框 */
.image-preview-item {
  aspect-ratio: 1;
  overflow: hidden;
  border: 1px solid var(--color-border-base);
  border-radius: var(--radius-base);
  transition: all var(--transition-base);
}

.image-preview-item:hover {
  border-color: var(--color-border-light);
  box-shadow: var(--shadow-md);
  transform: translateY(-2px);
}

.image-wrapper {
  position: relative;
  width: 100%;
  height: 100%;
}

.preview-image {
  width: 100%;
  height: 100%;
}

.preview-image :deep(.el-image__inner) {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.image-error {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
  font-size: var(--font-size-5xl);
  color: var(--color-text-placeholder);
  background: var(--color-neutral-100);
}

.image-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(255, 255, 255, 0.95);
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--spacing-2);
  opacity: 0;
  transition: opacity var(--transition-base);
}

.image-wrapper:hover .image-overlay {
  opacity: 1;
}

.cover-badge {
  position: absolute;
  top: var(--spacing-2);
  left: var(--spacing-2);
}

/* 操作按钮 */
.form-actions {
  display: flex;
  gap: var(--spacing-4);
  justify-content: center;
  padding: var(--spacing-8) 0;
  margin-top: var(--spacing-4);
}

.form-actions .el-button {
  min-width: 140px;
}

/* 响应式 */
@media (max-width: 768px) {
  .publish-view {
    padding: var(--spacing-4);
  }

  .page-header {
    flex-direction: column;
    align-items: flex-start;
    gap: var(--spacing-2);
  }

  .page-header h1 {
    font-size: var(--font-size-3xl);
  }

  .image-preview-grid {
    grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
    gap: var(--spacing-3);
  }

  .form-actions {
    flex-direction: column;
    padding: var(--spacing-6) 0;
  }

  .form-actions .el-button {
    width: 100%;
  }
}
</style>
