export interface ApiResponse<T = any> {
  message?: string
  error?: string
  data?: T
  [key: string]: any
}

// 用户相关类型
export interface User {
  user_id: number
  student_id: string
  username: string
  real_name: string
  phone: string
  email: string
  avatar?: string | null
  credit_score: number
  registration_date: string
  last_login?: string | null
  status: 'active' | 'frozen' | 'deleted'
}

export interface LoginParams {
  login_field: string
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

// 商品相关类型
export type ConditionLevel = 'brand_new' | 'like_new' | 'very_good' | 'good' | 'acceptable'

export interface Category {
  category_id: number
  category_name: string
  parent_category_id?: number | null
  description?: string | null
  icon?: string | null
  sort_order: number
  item_count?: number
  children?: Category[]
}

export interface Item {
  item_id: number
  user_id: number
  category_id: number
  title: string
  description: string
  price: number
  original_price?: number | null
  condition_level: ConditionLevel
  images: string[]
  location: string
  publish_date?: string
  update_date?: string
  status?: 'available' | 'sold' | 'removed'
  view_count?: number
  username?: string
  avatar?: string | null
  credit_score?: number
  category_name?: string
  phone?: string
}

export interface ItemsParams {
  page?: number
  limit?: number
  category_id?: number | string
  status?: 'available' | 'sold' | 'removed'
  sort_by?: 'publish_date' | 'price' | 'view_count'
  sort_order?: 'ASC' | 'DESC'
}

export interface SearchParams {
  keyword?: string
  category_id?: number | string
  min_price?: number
  max_price?: number
  condition_level?: ConditionLevel
  sort_by?: 'publish_date' | 'price' | 'view_count'
  sort_order?: 'ASC' | 'DESC'
  page?: number
  limit?: number
}

// 订单相关类型
export type OrderStatus = 'pending_payment' | 'paid' | 'shipped' | 'completed' | 'cancelled'
export type PaymentMethod = 'alipay' | 'wechat' | 'cash'
export type PaymentStatus = 'pending' | 'paid' | 'refunded'
export type DeliveryMethod = 'meet' | 'express'

export interface Order {
  order_id: number
  order_number: string
  buyer_id: number
  seller_id: number
  item_id: number
  address_id: number
  total_amount: number
  payment_method: PaymentMethod
  payment_status: PaymentStatus
  delivery_method: DeliveryMethod
  order_status: OrderStatus
  create_time: string
  payment_time?: string | null
  ship_time?: string | null
  complete_time?: string | null
  notes?: string | null
  item_title?: string
  item_images?: string[]
  buyer_name?: string
  buyer_phone?: string
  seller_name?: string
  seller_phone?: string
}

export interface CreateOrderParams {
  buyer_id: number
  item_id: number
  address_id?: number  // 可选字段，自取时不需要地址
  payment_method: PaymentMethod
  delivery_method: DeliveryMethod
  notes?: string
}

export interface OrderStatistics {
  buyer_stats?: {
    total_orders: number
    completed_orders: number
    pending_orders: number
    total_spent: number
  }
  seller_stats?: {
    total_sales: number
    completed_sales: number
    pending_sales: number
    total_earned: number
  }
}

// 消息相关类型
export interface Message {
  message_id: number
  sender_id: number
  receiver_id: number
  item_id: number
  content: string
  message_type: 'text' | 'image'
  send_time: string
  is_read: boolean
  reply_to?: number | null
  sender_name?: string
  sender_avatar?: string | null
}

export interface Conversation {
  other_user_id: number
  other_username: string
  other_avatar?: string | null
  item_id: number
  item_title?: string
  item_images?: string[]
  last_message: string
  last_message_time: string
  unread_count: number
}

export interface SendMessageParams {
  sender_id: number
  receiver_id: number
  item_id: number
  content: string
  message_type?: 'text' | 'image'
  reply_to?: number
}

// 收藏相关类型
export interface Wishlist {
  wishlist_id: number
  user_id: number
  item_id: number
  add_time: string
  notes?: string | null
  title?: string
  price?: number
  images?: string[]
  status?: 'available' | 'sold' | 'removed'
  view_count?: number
  condition_level?: ConditionLevel
  location?: string
  seller_name?: string
  credit_score?: number
  category_name?: string
}

export interface WishlistParams {
  user_id: number
  item_id: number
  notes?: string
}

export interface WishlistStatistics {
  total_count: number
  category_stats: Array<{ category_name: string; count: number }>
  status_stats: Array<{ status: string; count: number }>
}

// 地址相关类型
export type AddressType = 'dormitory' | 'home' | 'other'

export interface Address {
  address_id: number
  user_id: number
  recipient_name: string
  phone: string
  province: string
  city: string
  district: string
  detailed_address: string
  postal_code?: string | null
  address_type: AddressType
  is_default: boolean
}

export interface AddressParams {
  user_id: number
  recipient_name: string
  phone: string
  province: string
  city: string
  district: string
  detailed_address: string
  postal_code?: string
  address_type?: AddressType
  is_default?: boolean
}

// 通用类型
export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  limit: number
  total_pages: number
}

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
