/**
 * 全局配置状态管理
 */
import { defineStore } from 'pinia'

interface AppState {
  // 主题
  theme: 'light' | 'dark'
  // 主题色
  color: string
  // 页面加载状态
  loading: boolean
  // 全局提示
  toast: {
    show: boolean
    message: string
    type: 'success' | 'error' | 'info' | 'warning'
  }
}

export const useAppStore = defineStore('app', {
  state: (): AppState => ({
    theme: 'light',
    color: '#007AFF',
    loading: false,
    toast: {
      show: false,
      message: '',
      type: 'info',
    },
  }),

  actions: {
    /**
     * 设置主题
     */
    setTheme(theme: 'light' | 'dark') {
      this.theme = theme
      uni.setStorageSync('theme', theme)
    },

    /**
     * 设置主题色
     */
    setColor(color: string) {
      this.color = color
      uni.setStorageSync('color', color)
    },

    /**
     * 显示加载
     */
    showLoading(title: string = '加载中...') {
      this.loading = true
      uni.showLoading({ title, mask: true })
    },

    /**
     * 隐藏加载
     */
    hideLoading() {
      this.loading = false
      uni.hideLoading()
    },

    /**
     * 显示提示
     */
    showToast(message: string, type: 'success' | 'error' | 'info' | 'warning' = 'info') {
      uni.showToast({
        title: message,
        icon: type === 'success' ? 'success' : 'none',
      })
    },

    /**
     * 显示成功
     */
    showSuccess(message: string = '操作成功') {
      uni.showToast({ title: message, icon: 'success' })
    },

    /**
     * 显示错误
     */
    showError(message: string = '操作失败') {
      uni.showToast({ title: message, icon: 'none' })
    },

    /**
     * 初始化
     */
    init() {
      const theme = uni.getStorageSync('theme')
      if (theme) {
        this.theme = theme
      }
      const color = uni.getStorageSync('color')
      if (color) {
        this.color = color
      }
    },
  },
})
