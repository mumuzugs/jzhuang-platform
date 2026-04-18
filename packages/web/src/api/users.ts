/**
 * 用户相关 API
 */
import request from './request'

/**
 * 获取用户资料
 */
export function getProfile(): Promise<any> {
  return request.get('/users/profile')
}

/**
 * 更新用户资料
 */
export function updateProfile(data: {
  nickname?: string
  avatar?: string
}): Promise<any> {
  return request.put('/users/profile', data)
}

/**
 * 获取 VIP 状态
 */
export function getVipStatus(): Promise<any> {
  return request.get('/users/vip/status')
}
