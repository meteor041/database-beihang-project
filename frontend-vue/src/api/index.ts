import axios from 'axios'

// 创建axios实例
const api = axios.create({
  baseURL: 'http://localhost:5000/api',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json; charset=utf-8'
  }
})

// 请求拦截器
api.interceptors.request.use(
  (config) => {
    // 可以在这里添加token等认证信息
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

// 响应拦截器
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
  // 用户注册
  register: (data: any) => api.post('/users/register', data),
  
  // 用户登录
  login: (data: any) => api.post('/users/login', data),
  
  // 获取用户信息
  getUser: (userId: number) => api.get(`/users/${userId}`),
  
  // 更新用户信息
  updateUser: (userId: number, data: any) => api.put(`/users/${userId}`, data),
  
  // 删除用户
  deleteUser: (userId: number) => api.delete(`/users/${userId}`),
  
  // 搜索用户
  searchUsers: (params: any) => api.get('/users/search', { params }),
  
  // 更新信用分
  updateCredit: (userId: number, data: any) => api.put(`/users/${userId}/credit`, data)
}

// 商品相关API
export const itemAPI = {
  // 发布商品
  createItem: (data: any) => api.post('/items/', data),
  
  // 获取商品列表
  getItems: (params: any) => api.get('/items/', { params }),
  
  // 搜索商品
  searchItems: (params: any) => api.get('/items/search', { params }),
  
  // 获取商品详情
  getItem: (itemId: number) => api.get(`/items/${itemId}`),
  
  // 更新商品
  updateItem: (itemId: number, data: any) => api.put(`/items/${itemId}`, data),
  
  // 删除商品
  deleteItem: (itemId: number, data: any) => api.delete(`/items/${itemId}`, { data }),
  
  // 获取分类
  getCategories: () => api.get('/items/categories'),
  
  // 获取用户商品
  getUserItems: (userId: number, params: any) => api.get(`/items/user/${userId}`, { params })
}

// 订单相关API
export const orderAPI = {
  // 创建订单
  createOrder: (data: any) => api.post('/orders', data),
  
  // 获取订单详情
  getOrder: (orderId: number) => api.get(`/orders/${orderId}`),
  
  // 获取用户订单
  getUserOrders: (userId: number, params: any) => api.get(`/orders/user/${userId}`, { params }),
  
  // 更新订单状态
  updateOrderStatus: (orderId: number, data: any) => api.put(`/orders/${orderId}/status`, data),
  
  // 更新支付状态
  updatePaymentStatus: (orderId: number, data: any) => api.put(`/orders/${orderId}/payment`, data),
  
  // 取消订单
  cancelOrder: (orderId: number, data: any) => api.put(`/orders/${orderId}/cancel`, data),
  
  // 订单统计
  getOrderStatistics: (params: any) => api.get('/orders/statistics', { params })
}

// 消息相关API
export const messageAPI = {
  // 发送消息
  sendMessage: (data: any) => api.post('/messages', data),
  
  // 获取会话列表
  getConversations: (userId: number) => api.get(`/messages/conversations/${userId}`),
  
  // 获取会话消息
  getConversationMessages: (params: any) => api.get('/messages/conversation', { params }),
  
  // 标记消息已读
  markMessageRead: (messageId: number, data: any) => api.put(`/messages/${messageId}/read`, data),
  
  // 获取未读消息数
  getUnreadCount: (userId: number) => api.get(`/messages/unread/${userId}`),
  
  // 搜索消息
  searchMessages: (params: any) => api.get('/messages/search', { params }),
  
  // 删除消息
  deleteMessage: (messageId: number, data: any) => api.delete(`/messages/${messageId}`, { data }),
  
  // 批量标记已读
  batchMarkRead: (data: any) => api.put('/messages/batch-read', data)
}

// 收藏相关API
export const wishlistAPI = {
  // 添加收藏
  addToWishlist: (data: any) => api.post('/wishlist', data),
  
  // 获取收藏列表
  getWishlist: (userId: number, params: any) => api.get(`/wishlist/${userId}`, { params }),
  
  // 取消收藏
  removeFromWishlist: (data: any) => api.delete('/wishlist', { data }),
  
  // 检查收藏状态
  checkWishlistStatus: (params: any) => api.get('/wishlist/check', { params }),
  
  // 批量删除收藏
  batchRemoveFromWishlist: (data: any) => api.delete('/wishlist/batch', { data }),
  
  // 更新收藏备注
  updateWishlistNotes: (wishlistId: number, data: any) => api.put(`/wishlist/${wishlistId}/notes`, data),
  
  // 收藏统计
  getWishlistStatistics: (userId: number) => api.get(`/wishlist/statistics/${userId}`),
  
  // 获取商品收藏数
  getItemWishlistCount: (itemId: number) => api.get(`/wishlist/item/${itemId}/count`)
}

// 地址相关API
export const addressAPI = {
  // 添加地址
  addAddress: (data: any) => api.post('/addresses', data),
  
  // 获取用户地址列表
  getUserAddresses: (userId: number) => api.get(`/addresses/user/${userId}`),
  
  // 获取地址详情
  getAddress: (addressId: number) => api.get(`/addresses/${addressId}`),
  
  // 更新地址
  updateAddress: (addressId: number, data: any) => api.put(`/addresses/${addressId}`, data),
  
  // 删除地址
  deleteAddress: (addressId: number, data: any) => api.delete(`/addresses/${addressId}`, { data }),
  
  // 设置默认地址
  setDefaultAddress: (addressId: number, data: any) => api.put(`/addresses/${addressId}/default`, data),
  
  // 搜索地址
  searchAddresses: (params: any) => api.get('/addresses/search', { params }),
  
  // 获取默认地址
  getDefaultAddress: (userId: number) => api.get(`/addresses/default/${userId}`),
  
  // 地址统计
  getAddressStatistics: (userId: number) => api.get(`/addresses/statistics/${userId}`)
}

export default api