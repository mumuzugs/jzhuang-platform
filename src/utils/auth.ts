/**
 * Token 工具函数
 */

// Token 存储键名
const TOKEN_KEY = 'jzhuang_token'
const USER_KEY = 'jzhuang_user'

/**
 * 获取 Token
 */
export function getToken(): string | null {
  return uni.getStorageSync(TOKEN_KEY)
}

/**
 * 设置 Token
 */
export function setToken(token: string): void {
  uni.setStorageSync(TOKEN_KEY, token)
}

/**
 * 清除 Token
 */
export function clearToken(): void {
  uni.removeStorageSync(TOKEN_KEY)
  uni.removeStorageSync(USER_KEY)
}

/**
 * 获取用户信息
 */
export function getUserInfo(): any {
  const userStr = uni.getStorageSync(USER_KEY)
  return userStr ? JSON.parse(userStr) : null
}

/**
 * 设置用户信息
 */
export function setUserInfo(user: any): void {
  uni.setStorageSync(USER_KEY, JSON.stringify(user))
}

/**
 * 检查是否已登录
 */
export function isLoggedIn(): boolean {
  return !!getToken()
}
