/**
 * API 请求封装
 */
import config from '@/config'
import { getToken, clearToken } from '@/utils/auth'

// 响应码
const CODE = {
  SUCCESS: 0,
  UNAUTHORIZED: 401,
  FORBIDDEN: 403,
  NOT_FOUND: 404,
  SERVER_ERROR: 500,
}

// 错误消息
const ERROR_MSG = {
  [CODE.UNAUTHORIZED]: '登录已过期，请重新登录',
  [CODE.FORBIDDEN]: '没有权限访问该资源',
  [CODE.NOT_FOUND]: '请求的资源不存在',
  [CODE.SERVER_ERROR]: '服务器错误，请稍后重试',
  default: '网络请求失败，请稍后重试',
}

/**
 * 请求封装
 */
class Request {
  private baseUrl: string
  private timeout: number

  constructor() {
    this.baseUrl = config.baseUrl
    this.timeout = config.timeout
  }

  /**
   * 获取请求头
   */
  private getHeaders(): Record<string, string> {
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
    }
    
    const token = getToken()
    if (token) {
      headers['Authorization'] = `Bearer ${token}`
    }
    
    return headers
  }

  /**
   * 处理响应
   */
  private handleResponse(res: any, resolve: any, reject: any) {
    // #ifdef MP-WEIXIN
    // 小程序特殊处理
    if (res.statusCode === 200) {
      if (res.data.code === CODE.SUCCESS || res.data.code === undefined) {
        resolve(res.data)
      } else if (res.data.code === CODE.UNAUTHORIZED) {
        clearToken()
        uni.reLaunch({ url: '/pages/auth/login/login' })
        reject(new Error(res.data.message || ERROR_MSG[CODE.UNAUTHORIZED]))
      } else {
        uni.showToast({
          title: res.data.message || ERROR_MSG.default,
          icon: 'none',
        })
        reject(new Error(res.data.message || ERROR_MSG.default))
      }
    } else {
      // HTTP 状态码非 200
      if (res.statusCode === CODE.UNAUTHORIZED) {
        clearToken()
        uni.reLaunch({ url: '/pages/auth/login/login' })
      }
      uni.showToast({
        title: ERROR_MSG[res.statusCode] || ERROR_MSG.default,
        icon: 'none',
      })
      reject(new Error(ERROR_MSG[res.statusCode] || ERROR_MSG.default))
    }
    // #endif
    
    // #ifndef MP-WEIXIN
    // H5 / App 处理
    if (res.statusCode === 200) {
      if (res.data.code === CODE.SUCCESS || res.data.code === undefined) {
        resolve(res.data)
      } else if (res.data.code === CODE.UNAUTHORIZED) {
        clearToken()
        uni.reLaunch({ url: '/pages/auth/login/login' })
        reject(new Error(res.data.message || ERROR_MSG[CODE.UNAUTHORIZED]))
      } else {
        reject(new Error(res.data.message || ERROR_MSG.default))
      }
    } else {
      if (res.statusCode === CODE.UNAUTHORIZED) {
        clearToken()
        uni.reLaunch({ url: '/pages/auth/login/login' })
      }
      reject(new Error(ERROR_MSG[res.statusCode] || ERROR_MSG.default))
    }
    // #endif
  }

  /**
   * GET 请求
   */
  get<T = any>(url: string, params?: Record<string, any>): Promise<T> {
    return new Promise((resolve, reject) => {
      const query = params ? '?' + new URLSearchParams(params).toString() : ''
      
      // #ifdef MP-WEIXIN
      wx.request({
        url: this.baseUrl + url + query,
        method: 'GET',
        header: this.getHeaders(),
        timeout: this.timeout,
        success: (res) => this.handleResponse(res, resolve, reject),
        fail: (err) => {
          uni.showToast({ title: '网络请求失败', icon: 'none' })
          reject(err)
        },
      })
      // #endif
      
      // #ifndef MP-WEIXIN
      uni.request({
        url: this.baseUrl + url + query,
        method: 'GET',
        header: this.getHeaders(),
        timeout: this.timeout,
        success: (res) => this.handleResponse(res, resolve, reject),
        fail: (err) => {
          uni.showToast({ title: '网络请求失败', icon: 'none' })
          reject(err)
        },
      })
      // #endif
    })
  }

  /**
   * POST 请求
   */
  post<T = any>(url: string, data?: Record<string, any>): Promise<T> {
    return new Promise((resolve, reject) => {
      // #ifdef MP-WEIXIN
      wx.request({
        url: this.baseUrl + url,
        method: 'POST',
        header: this.getHeaders(),
        data: data,
        timeout: this.timeout,
        success: (res) => this.handleResponse(res, resolve, reject),
        fail: (err) => {
          uni.showToast({ title: '网络请求失败', icon: 'none' })
          reject(err)
        },
      })
      // #endif
      
      // #ifndef MP-WEIXIN
      uni.request({
        url: this.baseUrl + url,
        method: 'POST',
        header: this.getHeaders(),
        data: data,
        timeout: this.timeout,
        success: (res) => this.handleResponse(res, resolve, reject),
        fail: (err) => {
          uni.showToast({ title: '网络请求失败', icon: 'none' })
          reject(err)
        },
      })
      // #endif
    })
  }

  /**
   * PUT 请求
   */
  put<T = any>(url: string, data?: Record<string, any>): Promise<T> {
    return new Promise((resolve, reject) => {
      uni.request({
        url: this.baseUrl + url,
        method: 'PUT',
        header: this.getHeaders(),
        data: data,
        timeout: this.timeout,
        success: (res) => this.handleResponse(res, resolve, reject),
        fail: (err) => {
          uni.showToast({ title: '网络请求失败', icon: 'none' })
          reject(err)
        },
      })
    })
  }

  /**
   * DELETE 请求
   */
  delete<T = any>(url: string, data?: Record<string, any>): Promise<T> {
    return new Promise((resolve, reject) => {
      uni.request({
        url: this.baseUrl + url,
        method: 'DELETE',
        header: this.getHeaders(),
        data: data,
        timeout: this.timeout,
        success: (res) => this.handleResponse(res, resolve, reject),
        fail: (err) => {
          uni.showToast({ title: '网络请求失败', icon: 'none' })
          reject(err)
        },
      })
    })
  }

  /**
   * 文件上传
   */
  upload<T = any>(url: string, filePath: string, formData?: Record<string, any>): Promise<T> {
    return new Promise((resolve, reject) => {
      uni.uploadFile({
        url: config.uploadUrl + url,
        filePath: filePath,
        name: 'file',
        formData: formData,
        header: this.getHeaders(),
        success: (res) => {
          if (res.statusCode === 200) {
            const data = typeof res.data === 'string' ? JSON.parse(res.data) : res.data
            if (data.code === CODE.SUCCESS || data.code === undefined) {
              resolve(data)
            } else {
              uni.showToast({ title: data.message || '上传失败', icon: 'none' })
              reject(new Error(data.message || '上传失败'))
            }
          } else {
            uni.showToast({ title: '上传失败', icon: 'none' })
            reject(new Error('上传失败'))
          }
        },
        fail: (err) => {
          uni.showToast({ title: '上传失败', icon: 'none' })
          reject(err)
        },
      })
    })
  }
}

export default new Request()
