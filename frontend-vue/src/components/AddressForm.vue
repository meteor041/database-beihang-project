<template>
  <form class="address-form" @submit.prevent="handleSubmit">
    <div class="form-row">
      <input
        v-model="form.recipient_name"
        type="text"
        placeholder="收件人姓名 *"
        maxlength="50"
      />
      <input
        v-model="form.phone"
        type="tel"
        placeholder="手机号 *"
        maxlength="11"
      />
    </div>

    <div class="form-row">
      <input
        v-model="form.province"
        type="text"
        placeholder="省份 *"
        maxlength="20"
      />
      <input
        v-model="form.city"
        type="text"
        placeholder="城市 *"
        maxlength="20"
      />
      <input
        v-model="form.district"
        type="text"
        placeholder="区县 *"
        maxlength="20"
      />
    </div>

    <input
      v-model="form.detailed_address"
      type="text"
      class="full-width"
      placeholder="详细地址 *"
      maxlength="200"
    />

    <div class="form-row">
      <input
        v-model="form.postal_code"
        type="text"
        placeholder="邮政编码（可选）"
        maxlength="6"
      />
      <select v-model="form.address_type" class="address-type">
        <option value="dormitory">宿舍</option>
        <option value="home">家庭</option>
        <option value="other">其他</option>
      </select>
    </div>

    <label class="checkbox">
      <input v-model="form.is_default" type="checkbox" />
      设为默认地址
    </label>

    <div class="form-actions">
      <button
        v-if="showCancel"
        type="button"
        class="btn-cancel"
        @click="emit('cancel')"
      >
        取消
      </button>
      <button
        type="submit"
        class="btn-primary"
        :disabled="loading"
      >
        {{ loading ? '提交中...' : submitText }}
      </button>
    </div>
  </form>
</template>

<script setup lang="ts">
import { reactive, watch } from 'vue'
import { ElMessage } from 'element-plus'
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
  submitText: '保存',
  loading: false
})

const emit = defineEmits<{
  (e: 'save', value: AddressFormValue): void
  (e: 'cancel'): void
}>()

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

const phonePattern = /^1[3-9]\d{9}$/
const postalPattern = /^\d{6}$/

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
}

watch(
  () => props.address,
  (newVal) => {
    resetForm(newVal)
  },
  { immediate: true }
)

const validate = (): string | null => {
  if (!form.recipient_name.trim() ||
      !form.phone.trim() ||
      !form.province.trim() ||
      !form.city.trim() ||
      !form.district.trim() ||
      !form.detailed_address.trim()) {
    return '请完整填写带 * 的必填项'
  }

  if (!phonePattern.test(form.phone.trim())) {
    return '请输入合法的手机号'
  }

  if (form.postal_code && form.postal_code.trim() && !postalPattern.test(form.postal_code.trim())) {
    return '邮政编码需为 6 位数字'
  }

  if (form.detailed_address.trim().length > 200) {
    return '详细地址不能超过 200 个字符'
  }

  return null
}

const sanitize = (): AddressFormValue => ({
  recipient_name: form.recipient_name.trim(),
  phone: form.phone.trim(),
  province: form.province.trim(),
  city: form.city.trim(),
  district: form.district.trim(),
  detailed_address: form.detailed_address.trim(),
  postal_code: form.postal_code?.trim() ? form.postal_code.trim() : undefined,
  address_type: (form.address_type ?? 'dormitory') as AddressType,
  is_default: form.is_default
})

const handleSubmit = () => {
  const validationError = validate()
  if (validationError) {
    ElMessage.warning(validationError)
    return
  }

  emit('save', sanitize())
}
</script>

<style scoped>
.address-form {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.form-row {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
  gap: 12px;
}

.address-form input,
.address-form select {
  padding: 10px 12px;
  border: 1px solid #dcdfe6;
  border-radius: 6px;
  font-size: 14px;
  width: 100%;
  box-sizing: border-box;
  transition: border-color 0.2s;
}

.address-form input:focus,
.address-form select:focus {
  outline: none;
  border-color: #409eff;
  box-shadow: 0 0 0 1px rgba(64, 158, 255, 0.15);
}

.full-width {
  width: 100%;
}

.address-type {
  max-width: 180px;
}

.checkbox {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #606266;
  font-size: 14px;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

.btn-primary,
.btn-cancel {
  padding: 10px 18px;
  border-radius: 6px;
  border: none;
  cursor: pointer;
  font-size: 14px;
  transition: background-color 0.3s;
}

.btn-primary {
  background: #409eff;
  color: #fff;
}

.btn-primary:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.btn-primary:not(:disabled):hover {
  background: #66b1ff;
}

.btn-cancel {
  background: #f5f5f5;
  color: #606266;
}

.btn-cancel:hover {
  background: #ebeef5;
}
</style>
