<template>
  <v-form class="address-form" @submit.prevent="handleSubmit">
    <v-row>
      <v-col cols="12" sm="6">
        <v-text-field
          v-model="form.recipient_name"
          label="收件人姓名"
          placeholder="请输入收件人姓名"
          variant="outlined"
          density="comfortable"
          counter="50"
          maxlength="50"
          required
          prepend-inner-icon="mdi-account"
        ></v-text-field>
      </v-col>
      <v-col cols="12" sm="6">
        <v-text-field
          v-model="form.phone"
          label="手机号"
          placeholder="请输入手机号"
          type="tel"
          variant="outlined"
          density="comfortable"
          counter="11"
          maxlength="11"
          required
          prepend-inner-icon="mdi-phone"
        ></v-text-field>
      </v-col>
    </v-row>

    <v-row>
      <v-col cols="12" sm="4">
        <v-text-field
          v-model="form.province"
          label="省份"
          placeholder="请输入省份"
          variant="outlined"
          density="comfortable"
          counter="20"
          maxlength="20"
          required
          prepend-inner-icon="mdi-map-marker"
        ></v-text-field>
      </v-col>
      <v-col cols="12" sm="4">
        <v-text-field
          v-model="form.city"
          label="城市"
          placeholder="请输入城市"
          variant="outlined"
          density="comfortable"
          counter="20"
          maxlength="20"
          required
          prepend-inner-icon="mdi-city"
        ></v-text-field>
      </v-col>
      <v-col cols="12" sm="4">
        <v-text-field
          v-model="form.district"
          label="区县"
          placeholder="请输入区县"
          variant="outlined"
          density="comfortable"
          counter="20"
          maxlength="20"
          required
          prepend-inner-icon="mdi-map"
        ></v-text-field>
      </v-col>
    </v-row>

    <v-text-field
      v-model="form.detailed_address"
      label="详细地址"
      placeholder="请输入详细地址"
      variant="outlined"
      density="comfortable"
      counter="200"
      maxlength="200"
      required
      prepend-inner-icon="mdi-home-city"
      class="mb-4"
    ></v-text-field>

    <v-row>
      <v-col cols="12" sm="6">
        <v-text-field
          v-model="form.postal_code"
          label="邮政编码"
          placeholder="选填"
          variant="outlined"
          density="comfortable"
          counter="6"
          maxlength="6"
          prepend-inner-icon="mdi-email-outline"
        ></v-text-field>
      </v-col>
      <v-col cols="12" sm="6">
        <v-select
          v-model="form.address_type"
          :items="addressTypeOptions"
          label="地址类型"
          variant="outlined"
          density="comfortable"
          prepend-inner-icon="mdi-tag"
        ></v-select>
      </v-col>
    </v-row>

    <v-checkbox
      v-model="form.is_default"
      label="设为默认地址"
      color="primary"
      density="comfortable"
    ></v-checkbox>

    <div class="d-flex justify-end ga-3 mt-4">
      <v-btn
        v-if="showCancel"
        variant="outlined"
        @click="emit('cancel')"
      >
        取消
      </v-btn>
      <v-btn
        type="submit"
        color="primary"
        :loading="loading"
      >
        {{ submitText }}
      </v-btn>
    </div>
  </v-form>
</template>

<script setup lang="ts">
import { reactive, watch } from 'vue'
import { useNotification } from '@/composables/useNotification'
import type { AddressParams } from '@/types'

type AddressFormValue = Omit<AddressParams, 'user_id'>
type AddressType = AddressFormValue['address_type']

const notification = useNotification()

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

const addressTypeOptions = [
  { title: '宿舍', value: 'dormitory' },
  { title: '家庭', value: 'home' },
  { title: '其他', value: 'other' }
]

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
    notification.warning(validationError)
    return
  }

  emit('save', sanitize())
}
</script>

<style scoped>
.address-form {
  width: 100%;
}
</style>
