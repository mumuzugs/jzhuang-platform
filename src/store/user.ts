/**
 * 用户状态管理
 */
import { defineStore } from 'pinia'
import { getCurrentUser, logout as apiLogout } from '@/api/auth'
import { getToken, setToken, clearToken, setUserInfo, getUserInfo } from '@/utils/auth'

interface UserState {
  token: string | null
  userInfo: any | null
  isLoggedIn: boolean
}

export const useUserStore = defineStore('user', {
  state: (): UserState => ({
    token: getToken(),
    userInfo: getUserInfo(),
    isLoggedIn: !!getToken(),
  }),

  getters: {
    // 是否 VIP
    isVip: (state) => state.userInfo?.is_pro === true,
    
    // 用户角色
    role: (state) => state.userInfo?.role || 'free',
    
    // 用户手机号
    phone: (state) => state.userInfo?.phone || '',
  },

  actions: {
    /**
     * 设置 Token
     */
    setToken(token: string) {
      this.token = token
      setToken(token)
      this.isLoggedIn = true
    },

    /**
     * 设置用户信息
     */
    setUserInfo(info: any) {
      this.userInfo = info
      setUserInfo(info)
    },

    /**
     * 获取用户信息
     */
    async fetchUserInfo() {
      try {
        const userInfo = await getCurrentUser()
        this.setUserInfo(userInfo)
        return userInfo
      } catch (e) {
        console.error('获取用户信息失败', e)
        return null
      }
    },

    /**
     * 登录成功
     */
    loginSuccess(token: string, userInfo: any) {
      this.setToken(token)
      this.setUserInfo(userInfo)
      this.isLoggedIn = true
    },

    /**
     * 退出登录
     */
    async logout() {
      try {
        await apiLogout()
      } catch (e) {
        // 忽略错误
      }
      this.token = null
      this.userInfo = null
      this.isLoggedIn = false
      clearToken()
    },

    /**
     * 初始化（检查登录状态）
     */
    async init() {
      if (this.token && !this.userInfo) {
        await this.fetchUserInfo()
      }
    },
  },
})
