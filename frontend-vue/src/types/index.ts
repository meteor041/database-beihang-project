// 用户相关类型定义

export interface User {
  user_id: number
  student_id: string
  username: string
  password?: string // 密码在前端不应该保存
  real_name: string
  phone: string
  email: string
  avatar?: string
  credit_score: number
  registration_date: string
  last_login?: string
  status: 'active' | 'frozen' | 'deleted'
}

export interface LoginParams {
  login_field: string // 可以是用户名、学号或手机号
  password: string
}

export interface RegisterParams {
  student_id: string
  username: string
  password: string
  real_name: string
  phone: string
  email: string
}

// 商品相关类型定义

export type ConditionLevel = 'brand_new' | 'like_new' | 'very_good' | 'good' | 'acceptable'

export interface Item {
  item_id: number
  user_id: number
  category_id: number
  title: string
  description: string
  price: number
  original_price?: number
  condition_level: ConditionLevel
  images: string[] // JSON数组
  location: string
  publish_date: string
  view_count: number
  status: 'available' | 'sold' | 'deleted'
  username?: string // 卖家用户名 (JOIN查询时包含)
  avatar?: string // 卖家头像 (JOIN查询时包含)
  credit_score?: number // 卖家信用分 (JOIN查询时包含)
  category_name?: string // 分类名称 (JOIN查询时包含)
}

export interface Category {
  category_id: number
  category_name: string
  parent_category_id?: number
  description?: string
  icon?: string
  sort_order: number
  item_count?: number // 商品数量统计
}

export interface ItemsParams {
  page?: number
  limit?: number
  category_id?: number
  user_id?: number
  status?: string
  sort_by?: 'publish_date' | 'price' | 'view_count'
  sort_order?: 'ASC' | 'DESC'
}

export interface SearchParams {
  keyword: string
  category_id?: number
  min_price?: number
  max_price?: number
  condition_level?: ConditionLevel
  sort_by?: string
  sort_order?: string
}

// 订单相关类型定义

export type OrderStatus = 'pending' | 'paid' | 'shipped' | 'completed' | 'cancelled'
export type PaymentMethod = 'alipay' | 'wechat' | 'cash'
export type PaymentStatus = 'unpaid' | 'paid' | 'refunded'
export type DeliveryMethod = 'pickup' | 'express'

export interface Order {
  order_id: number
  order_number: string
  buyer_id: number
  seller_id: number
  item_id: number
  address_id?: number
  order_status: OrderStatus
  payment_method: PaymentMethod
  payment_status: PaymentStatus
  delivery_method: DeliveryMethod
  total_amount: number
  remarks?: string
  order_date: string
  payment_date?: string
  delivery_date?: string
  completion_date?: string
  // 关联信息
  item_title?: string
  item_images?: string[]
  buyer_username?: string
  seller_username?: string
}

export interface CreateOrderParams {
  item_id: number
  address_id?: number
  payment_method: PaymentMethod
  delivery_method: DeliveryMethod
  remarks?: string
}

export interface OrderStatistics {
  total_orders: number
  pending_orders: number
  completed_orders: number
  cancelled_orders: number
  total_amount: number
}

// 消息相关类型定义

export interface Message {
  message_id: number
  sender_id: number
  receiver_id: number
  item_id?: number
  content: string
  message_type: 'text' | 'image'
  is_read: boolean
  send_time: string
  // 关联信息
  sender_username?: string
  sender_avatar?: string
  receiver_username?: string
  item_title?: string
}

export interface Conversation {
  other_user_id: number
  other_username: string
  other_avatar?: string
  item_id?: number
  item_title?: string
  last_message: string
  last_message_time: string
  unread_count: number
}

export interface SendMessageParams {
  sender_id?: number
  receiver_id: number
  item_id?: number
  content: string
  message_type: 'text' | 'image'
}

// 收藏相关类型定义

export interface Wishlist {
  wishlist_id: number
  user_id: number
  item_id: number
  notes?: string
  wishlist_date: string
  // 商品信息
  item?: Item
}

export interface WishlistParams {
  user_id: number
  item_id: number
  notes?: string
}

export interface WishlistStatistics {
  total_count: number
  available_count: number
  sold_count: number
}

// 地址相关类型定义

export interface Address {
  address_id: number
  user_id: number
  receiver_name: string
  receiver_phone: string
  province: string
  city: string
  district: string
  detailed_address: string
  postal_code?: string
  address_type: 'dorm' | 'home' | 'other'
  is_default: boolean
}

export interface AddressParams {
  receiver_name: string
  receiver_phone: string
  province: string
  city: string
  district: string
  detailed_address: string
  postal_code?: string
  address_type: 'dorm' | 'home' | 'other'
  is_default?: boolean
}

// API响应类型定义

export interface ApiResponse<T = any> {
  success?: boolean
  message: string
  data?: T
  error?: string
}

export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  limit: number
  total_pages: number
}

// 表单验证规则类型
export interface FormRule {
  required?: boolean
  message: string
  trigger?: 'blur' | 'change'
  min?: number
  max?: number
  pattern?: RegExp
  validator?: (rule: any, value: any, callback: any) => void
}

export type FormRules = Record<string, FormRule[]>
