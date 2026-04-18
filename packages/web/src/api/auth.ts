/**
 * 认证相关 API
 */
import request from './request'

// API 响应类型
export interface SendCodeResponse {
  message: string
}

export interface LoginRequest {
  phone: string
  code: string
}

export interface LoginResponse {
  access_token: string
  token_type: string
  expires_in: number
  user: UserInfo
}

export interface UserInfo {
  id: string
  phone: string
  nickname?: string
  role: string
  is_pro: boolean
}

/**
 * 发送验证码
 */
export function sendCode(phone: string): Promise<SendCodeResponse> {
  return request.post('/auth/send-code', { phone })
}

/**
 * 手机号验证码登录
 */
export function loginByCode(data: LoginRequest): Promise<LoginResponse> {
  return request.post('/auth/login', data)
}

/**
 * 手机号密码登录
 */
export function loginByPassword(phone: string, password: string): Promise<LoginResponse> {
  return request.post('/auth/login/password', { phone, password })
}

/**
 * 用户注册
 */
export function register(phone: string, code: string, password?: string): Promise<LoginResponse> {
  return request.post('/auth/register', { phone, code, password })
}

/**
 * 获取当前用户信息
 */
export function getCurrentUser(): Promise<UserInfo> {
  return request.get('/auth/me')
}

/**
 * 退出登录
 */
export function logout(): Promise<any> {
  return request.post('/auth/logout')
}

/**
 * 修改密码
 */
export function changePassword(oldPassword: string, newPassword: string): Promise<any> {
  return request.post('/auth/change-password', {
    old_password: oldPassword,
    new_password: newPassword,
  })
}
