// Vuetify
import 'vuetify/styles'
import { createVuetify } from 'vuetify'
import * as components from 'vuetify/components'
import * as directives from 'vuetify/directives'
import { aliases, mdi } from 'vuetify/iconsets/mdi'
import '@mdi/font/css/materialdesignicons.css'
import { zhHans } from 'vuetify/locale'

// 自定义主题 - 保持与原Element Plus蓝色主题一致
const customTheme = {
  dark: false,
  colors: {
    primary: '#409EFF', // Element Plus 主色
    secondary: '#909399',
    accent: '#67C23A',
    error: '#F56C6C',
    warning: '#E6A23C',
    info: '#409EFF',
    success: '#67C23A',
    background: '#F5F7FA',
    surface: '#FFFFFF',
    'on-primary': '#FFFFFF',
    'on-secondary': '#FFFFFF',
    'on-background': '#303133',
    'on-surface': '#303133',
  }
}

const vuetify = createVuetify({
  components,
  directives,

  // 图标配置
  icons: {
    defaultSet: 'mdi',
    aliases,
    sets: {
      mdi,
    }
  },

  // 主题配置
  theme: {
    defaultTheme: 'customTheme',
    themes: {
      customTheme,
    },
  },

  // 本地化 - 中文
  locale: {
    locale: 'zhHans',
    messages: { zhHans },
  },

  // 默认配置
  defaults: {
    VBtn: {
      style: 'text-transform: none;', // 按钮文字不大写
      variant: 'elevated',
    },
    VCard: {
      elevation: 2,
    },
    VTextField: {
      variant: 'outlined',
      density: 'comfortable',
    },
    VSelect: {
      variant: 'outlined',
      density: 'comfortable',
    },
    VTextarea: {
      variant: 'outlined',
      density: 'comfortable',
    },
  },
})

export default vuetify
