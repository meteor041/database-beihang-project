import axios from 'axios'
import type {
  User,
  LoginParams,
  RegisterParams,
  Item,
  Category,
  ItemsParams,
  SearchParams,
  Order,
  CreateOrderParams,
  OrderStatistics,
  Message,
  Conversation,
  SendMessageParams,
  Wishlist,
  WishlistParams,
  WishlistStatistics,
  Address,
  AddressParams
} from '@/types'

// API响应类型定义
interface ApiResponse<T = any> {
  success?: boolean
  message?: string
  error?: string
  data?: T
  [key: string]: any
}

interface ItemResponse {
  item: Item
  is_favorited?: boolean
}

interface ItemsResponse {
  items: Item[]
  pagination: {
    page: number
    limit: number
    total: number
    pages: number
  }
}

interface CategoriesResponse {
  categories: Category[]
}

interface ConversationsResponse {
  conversations: Conversation[]
}

interface MessagesResponse {
  messages: Message[]
}

interface OrdersResponse {
  orders: Order[]
}

interface AddressesResponse {
  addresses: Address[]
}

interface WishlistResponse {
  wishlist: Wishlist[]
}

// 创建axios实例
const api = axios.create({
  baseURL: 'http://localhost:5001/api',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json; charset=utf-8'
  }
})

// 请求拦截器
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 响应拦截器 - 返回 response.data
api.interceptors.response.use(
  (response) => {
    return response.data
  },
  (error) => {
    console.error('API Error:', error)
    return Promise.reject(error)
  }
)

// 用户相关API
export const userAPI = {
  register: (data: RegisterParams): Promise<ApiResponse<{ user_id: number }>> =>
    api.post('/users/register', data),

  login: (data: LoginParams): Promise<ApiResponse<{ token: string; user: User }>> =>
    api.post('/users/login', data),

  getUser: (userId: number): Promise<ApiResponse<{ user: User }>> =>
    api.get(`/users/${userId}`),

  updateUser: (userId: number, data: Partial<User>): Promise<ApiResponse> =>
    api.put(`/users/${userId}`, data),

  deleteUser: (userId: number): Promise<ApiResponse> =>
    api.delete(`/users/${userId}`),

  searchUsers: (params: any): Promise<ApiResponse<{ users: User[] }>> =>
    api.get('/users/search', { params }),

  updateCredit: (userId: number, data: { credit_score: number }): Promise<ApiResponse> =>
    api.put(`/users/${userId}/credit`, data)
}

// 商品相关API
export const itemAPI = {
  createItem: (data: any): Promise<ApiResponse<{ item_id: number }>> =>
    api.post('/items/', data),

  getItems: (params: ItemsParams): Promise<ItemsResponse> =>
    api.get('/items/', { params }),

  searchItems: (params: SearchParams): Promise<ItemsResponse> =>
    api.get('/items/search', { params }),

  getItem: (itemId: number): Promise<ItemResponse> =>
    api.get(`/items/${itemId}`),

  updateItem: (itemId: number, data: Partial<Item>): Promise<ApiResponse> =>
    api.put(`/items/${itemId}`, data),

  deleteItem: (itemId: number, data: any): Promise<ApiResponse> =>
    api.delete(`/items/${itemId}`, { data }),

  getCategories: (): Promise<CategoriesResponse> =>
    api.get('/items/categories'),

  getUserItems: (userId: number, params: any): Promise<ItemsResponse> =>
    api.get(`/items/user/${userId}`, { params })
}

// 订单相关API
export const orderAPI = {
  createOrder: (data: CreateOrderParams): Promise<ApiResponse<{ order_id: number }>> =>
    api.post('/orders', data),

  getOrder: (orderId: number): Promise<ApiResponse<{ order: Order }>> =>
    api.get(`/orders/${orderId}`),

  getUserOrders: (userId: number, params: any): Promise<OrdersResponse> =>
    api.get(`/orders/user/${userId}`, { params }),

  updateOrderStatus: (orderId: number, data: any): Promise<ApiResponse> =>
    api.put(`/orders/${orderId}/status`, data),

  updatePaymentStatus: (orderId: number, data: any): Promise<ApiResponse> =>
    api.put(`/orders/${orderId}/payment`, data),

  cancelOrder: (orderId: number, data: any): Promise<ApiResponse> =>
    api.put(`/orders/${orderId}/cancel`, data),

  getOrderStatistics: (params: any): Promise<ApiResponse<OrderStatistics>> =>
    api.get('/orders/statistics', { params })
}

// 消息相关API
export const messageAPI = {
  sendMessage: (data: SendMessageParams): Promise<ApiResponse<{ message_id: number }>> =>
    api.post('/messages', data),

  getConversations: (userId: number): Promise<ConversationsResponse> =>
    api.get(`/messages/conversations/${userId}`),

  getConversationMessages: (params: { user_id: number; other_user_id: number; item_id?: number; page?: number; limit?: number }): Promise<MessagesResponse> =>
    api.get('/messages/conversation', { params }),

  markMessageRead: (messageId: number, data: any): Promise<ApiResponse> =>
    api.put(`/messages/${messageId}/read`, data),

  getUnreadCount: (userId: number): Promise<ApiResponse<{ unread_count: number }>> =>
    api.get(`/messages/unread/${userId}`),

  searchMessages: (params: any): Promise<MessagesResponse> =>
    api.get('/messages/search', { params }),

  deleteMessage: (messageId: number, data: any): Promise<ApiResponse> =>
    api.delete(`/messages/${messageId}`, { data }),

  batchMarkRead: (data: any): Promise<ApiResponse> =>
    api.put('/messages/batch-read', data)
}

// 收藏相关API
export const wishlistAPI = {
  addToWishlist: (data: WishlistParams): Promise<ApiResponse<{ wishlist_id: number }>> =>
    api.post('/wishlist', data),

  getWishlist: (userId: number, params: any): Promise<WishlistResponse> =>
    api.get(`/wishlist/${userId}`, { params }),

  removeFromWishlist: (data: { user_id: number; item_id: number }): Promise<ApiResponse> =>
    api.delete('/wishlist', { data }),

  checkWishlistStatus: (params: { user_id: number; item_id: number }): Promise<ApiResponse<{ is_favorited: boolean }>> =>
    api.get('/wishlist/check', { params }),

  batchRemoveFromWishlist: (data: any): Promise<ApiResponse> =>
    api.delete('/wishlist/batch', { data }),

  updateWishlistNotes: (wishlistId: number, data: { notes: string }): Promise<ApiResponse> =>
    api.put(`/wishlist/${wishlistId}/notes`, data),

  getWishlistStatistics: (userId: number): Promise<ApiResponse<WishlistStatistics>> =>
    api.get(`/wishlist/statistics/${userId}`),

  getItemWishlistCount: (itemId: number): Promise<ApiResponse<{ count: number }>> =>
    api.get(`/wishlist/item/${itemId}/count`)
}

// 地址相关API
export const addressAPI = {
  addAddress: (data: AddressParams): Promise<ApiResponse<{ address_id: number }>> =>
    api.post('/addresses', data),

  getUserAddresses: (userId: number): Promise<AddressesResponse> =>
    api.get(`/addresses/user/${userId}`),

  getAddress: (addressId: number): Promise<ApiResponse<{ address: Address }>> =>
    api.get(`/addresses/${addressId}`),

  updateAddress: (addressId: number, data: Partial<AddressParams>): Promise<ApiResponse> =>
    api.put(`/addresses/${addressId}`, data),

  deleteAddress: (addressId: number, data: any): Promise<ApiResponse> =>
    api.delete(`/addresses/${addressId}`, { data }),

  setDefaultAddress: (addressId: number, data: any): Promise<ApiResponse> =>
    api.put(`/addresses/${addressId}/default`, data),

  searchAddresses: (params: any): Promise<AddressesResponse> =>
    api.get('/addresses/search', { params }),

  getDefaultAddress: (userId: number): Promise<ApiResponse<{ address: Address }>> =>
    api.get(`/addresses/default/${userId}`),

  getAddressStatistics: (userId: number): Promise<ApiResponse> =>
    api.get(`/addresses/statistics/${userId}`)
}

export default api
