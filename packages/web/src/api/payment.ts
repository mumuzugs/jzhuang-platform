/**
 * 支付相关 API
 */
import request from './request'

// ============ 类型定义 ============

// 订单
export interface Order {
  id: string
  order_no: string
  type: 'vip' | 'design' | 'inspection' | 'supervision'
  title: string
  amount: number
  status: 'pending' | 'paid' | 'refunded' | 'cancelled'
  paid_at?: string
  created_at: string
}

// 支付参数
export interface PayParams {
  order_id: string
  pay_method: 'wechat' | 'alipay'
}

// ============ API 接口 ============

/**
 * 创建订单
 */
export function createOrder(data: {
  type: 'vip' | 'design' | 'inspection' | 'supervision'
  title: string
  amount: number
  related_id?: string
}): Promise<{ order_id: string; order_no: string }> {
  return request.post('/payment/create', data)
}

/**
 * 获取订单详情
 */
export function getOrderDetail(orderId: string): Promise<Order> {
  return request.get(`/payment/order/${orderId}`)
}

/**
 * 获取订单列表
 */
export function getOrderList(params?: {
  page?: number
  page_size?: number
  type?: string
}): Promise<{ total: number; orders: Order[] }> {
  return request.get('/payment/orders', params || {})
}

/**
 * 获取支付参数（微信支付）
 */
export function getWechatPayParams(orderId: string): Promise<{
  appid: string
  timestamp: string
  nonceStr: string
  package: string
  signType: string
  paySign: string
}> {
  return request.post('/payment/wechat', { order_id: orderId })
}

/**
 * 获取支付参数（支付宝）
 */
export function getAlipayParams(orderId: string): Promise<{
  order_string: string
}> {
  return request.post('/payment/alipay', { order_id: orderId })
}

/**
 * 支付结果查询
 */
export function queryPayResult(orderId: string): Promise<{
  status: 'pending' | 'paid' | 'failed'
  paid_at?: string
}> {
  return request.get(`/payment/query/${orderId}`)
}

/**
 * 取消订单
 */
export function cancelOrder(orderId: string): Promise<any> {
  return request.post(`/payment/cancel/${orderId}`)
}
