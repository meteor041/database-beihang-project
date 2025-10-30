<template>
  <el-form
    ref="formRef"
    :model="form"
    :rules="rules"
    label-position="top"
    class="address-form"
    @submit.prevent="handleSubmit"
  >
    <!-- 联系信息 -->
    <div class="form-section">
      <h4 class="section-title">联系信息</h4>
      <el-row :gutter="16">
        <el-col :span="12">
          <el-form-item label="收件人姓名" prop="recipient_name" required>
            <el-input
              v-model="form.recipient_name"
              placeholder="请输入收件人姓名"
              maxlength="50"
              clearable
            />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="手机号" prop="phone" required>
            <el-input
              v-model="form.phone"
              placeholder="请输入手机号"
              maxlength="11"
              clearable
            />
          </el-form-item>
        </el-col>
      </el-row>
    </div>

    <!-- 地址信息 -->
    <div class="form-section">
      <h4 class="section-title">地址信息</h4>
      <el-row :gutter="16">
        <el-col :span="8">
          <el-form-item label="省份" prop="province" required>
            <el-input
              v-model="form.province"
              placeholder="请输入省份"
              maxlength="20"
              clearable
            />
          </el-form-item>
        </el-col>
        <el-col :span="8">
          <el-form-item label="城市" prop="city" required>
            <el-input
              v-model="form.city"
              placeholder="请输入城市"
              maxlength="20"
              clearable
            />
          </el-form-item>
        </el-col>
        <el-col :span="8">
          <el-form-item label="区县" prop="district" required>
            <el-input
              v-model="form.district"
              placeholder="请输入区县"
              maxlength="20"
              clearable
            />
          </el-form-item>
        </el-col>
      </el-row>

      <el-form-item label="详细地址" prop="detailed_address" required>
        <el-input
          v-model="form.detailed_address"
          type="textarea"
          :rows="3"
          placeholder="请输入详细地址（街道、门牌号、楼栋等）"
          maxlength="200"
          show-word-limit
        />
      </el-form-item>
    </div>

    <!-- 其他信息 -->
    <div class="form-section">
      <h4 class="section-title">其他信息</h4>
      <el-row :gutter="16">
        <el-col :span="12">
          <el-form-item label="邮政编码" prop="postal_code">
            <el-input
              v-model="form.postal_code"
              placeholder="请输入邮政编码（可选）"
              maxlength="6"
              clearable
            />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="地址类型" prop="address_type">
            <el-select v-model="form.address_type" placeholder="请选择地址类型" style="width: 100%">
              <el-option label="宿舍" value="dormitory" />
              <el-option label="家庭" value="home" />
              <el-option label="其他" value="other" />
            </el-select>
          </el-form-item>
        </el-col>
      </el-row>

      <el-form-item>
        <el-checkbox v-model="form.is_default">
          设为默认地址
        </el-checkbox>
      </el-form-item>
    </div>

    <!-- 操作按钮 -->
    <el-form-item class="form-actions">
      <el-button
        v-if="showCancel"
        @click="emit('cancel')"
      >
        取消
      </el-button>
      <el-button
        type="primary"
        :loading="loading"
        @click="handleSubmit"
      >
        {{ submitText }}
      </el-button>
    </el-form-item>
  </el-form>
</template>

<script setup lang="ts">
import { reactive, watch, ref } from 'vue'
import { ElMessage } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import type { AddressParams } from '@/types'

type AddressFormValue = Omit<AddressParams, 'user_id'>
type AddressType = AddressFormValue['address_type']

const props = withDefaults(defineProps<{
  address?: Partial<AddressFormValue> | null
  showCancel?: boolean
  submitText?: string
  loading?: boolean
}>(), {
  address: null,
  showCancel: true,
  submitText: '添加地址',
  loading: false
})

const emit = defineEmits<{
  (e: 'save', value: AddressFormValue): void
  (e: 'cancel'): void
}>()

const formRef = ref<FormInstance>()

const form = reactive<AddressFormValue>({
  recipient_name: '',
  phone: '',
  province: '',
  city: '',
  district: '',
  detailed_address: '',
  postal_code: undefined,
  address_type: 'dormitory',
  is_default: false
})

// 表单验证规则
const rules: FormRules = {
  recipient_name: [
    { required: true, message: '请输入收件人姓名', trigger: 'blur' },
    { min: 2, max: 50, message: '姓名长度应在 2-50 个字符之间', trigger: 'blur' }
  ],
  phone: [
    { required: true, message: '请输入手机号', trigger: 'blur' },
    {
      pattern: /^1[3-9]\d{9}$/,
      message: '请输入正确的手机号格式',
      trigger: 'blur'
    }
  ],
  province: [
    { required: true, message: '请输入省份', trigger: 'blur' },
    { max: 20, message: '省份名称不能超过 20 个字符', trigger: 'blur' }
  ],
  city: [
    { required: true, message: '请输入城市', trigger: 'blur' },
    { max: 20, message: '城市名称不能超过 20 个字符', trigger: 'blur' }
  ],
  district: [
    { required: true, message: '请输入区县', trigger: 'blur' },
    { max: 20, message: '区县名称不能超过 20 个字符', trigger: 'blur' }
  ],
  detailed_address: [
    { required: true, message: '请输入详细地址', trigger: 'blur' },
    { min: 5, max: 200, message: '详细地址应在 5-200 个字符之间', trigger: 'blur' }
  ],
  postal_code: [
    {
      pattern: /^\d{6}$/,
      message: '邮政编码应为 6 位数字',
      trigger: 'blur'
    }
  ]
}

const resetForm = (value?: Partial<AddressFormValue> | null) => {
  form.recipient_name = value?.recipient_name ?? ''
  form.phone = value?.phone ?? ''
  form.province = value?.province ?? ''
  form.city = value?.city ?? ''
  form.district = value?.district ?? ''
  form.detailed_address = value?.detailed_address ?? ''
  form.postal_code = value?.postal_code ?? undefined
  form.address_type = value?.address_type ?? 'dormitory'
  form.is_default = value?.is_default ?? false

  // 重置表单验证状态
  formRef.value?.clearValidate()
}

watch(
  () => props.address,
  (newVal) => {
    resetForm(newVal)
  },
  { immediate: true }
)

const handleSubmit = async () => {
  if (!formRef.value) return

  try {
    await formRef.value.validate()

    // 数据清理
    const sanitizedData: AddressFormValue = {
      recipient_name: form.recipient_name.trim(),
      phone: form.phone.trim(),
      province: form.province.trim(),
      city: form.city.trim(),
      district: form.district.trim(),
      detailed_address: form.detailed_address.trim(),
      postal_code: form.postal_code?.trim() || undefined,
      address_type: form.address_type as AddressType,
      is_default: form.is_default
    }

    emit('save', sanitizedData)
  } catch (error) {
    console.error('Form validation failed:', error)
  }
}
</script>

<style scoped>
/* 现代化表单样式 */
.address-form {
  padding: var(--spacing-4) 0;
}

/* 表单区块分组 */
.form-section {
  margin-bottom: var(--spacing-6);
  padding: var(--spacing-5);
  background: var(--color-bg-section);
  border: 1px solid var(--color-border-light);
  border-radius: var(--radius-lg);
}

.form-section:last-of-type {
  margin-bottom: var(--spacing-4);
}

/* 区块标题 */
.section-title {
  margin: 0 0 var(--spacing-4) 0;
  padding-bottom: var(--spacing-3);
  border-bottom: 2px solid var(--el-color-primary);
  font-size: var(--font-size-lg);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
  display: flex;
  align-items: center;
  gap: var(--spacing-2);
}

.section-title::before {
  content: '';
  width: 4px;
  height: 18px;
  background: var(--el-color-primary);
  border-radius: 2px;
}

/* 表单项样式优化 */
.address-form :deep(.el-form-item) {
  margin-bottom: var(--spacing-4);
}

.address-form :deep(.el-form-item__label) {
  font-weight: var(--font-weight-medium);
  color: var(--color-text-primary);
  padding-bottom: var(--spacing-2);
}

/* 输入框样式 */
.address-form :deep(.el-input__wrapper) {
  border-radius: var(--radius-base);
  box-shadow: 0 0 0 1px var(--color-border-base) inset;
  transition: all var(--transition-base);
}

.address-form :deep(.el-input__wrapper:hover) {
  box-shadow: 0 0 0 1px var(--color-border-light) inset;
}

.address-form :deep(.el-input__wrapper.is-focus) {
  box-shadow: 0 0 0 1px var(--el-color-primary) inset;
}

/* 文本域样式 */
.address-form :deep(.el-textarea__inner) {
  border-radius: var(--radius-base);
  border: 1px solid var(--color-border-base);
  transition: border-color var(--transition-base);
}

.address-form :deep(.el-textarea__inner:hover) {
  border-color: var(--color-border-light);
}

.address-form :deep(.el-textarea__inner:focus) {
  border-color: var(--el-color-primary);
}

/* 选择框样式 */
.address-form :deep(.el-select) {
  width: 100%;
}

/* 复选框样式 */
.address-form :deep(.el-checkbox) {
  font-size: var(--font-size-base);
  color: var(--color-text-secondary);
}

.address-form :deep(.el-checkbox__label) {
  font-weight: var(--font-weight-medium);
}

/* 按钮操作区 */
.form-actions {
  margin-top: var(--spacing-6);
  margin-bottom: 0;
  padding-top: var(--spacing-5);
  border-top: 1px solid var(--color-border-light);
}

.form-actions :deep(.el-form-item__content) {
  display: flex;
  justify-content: flex-end;
  gap: var(--spacing-3);
}

.form-actions :deep(.el-button) {
  min-width: 100px;
  padding: var(--spacing-3) var(--spacing-6);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .form-section {
    padding: var(--spacing-4);
  }

  .section-title {
    font-size: var(--font-size-base);
  }

  .address-form :deep(.el-col) {
    max-width: 100% !important;
    flex: 0 0 100% !important;
  }

  .form-actions :deep(.el-form-item__content) {
    flex-direction: column-reverse;
  }

  .form-actions :deep(.el-button) {
    width: 100%;
  }
}
</style>
