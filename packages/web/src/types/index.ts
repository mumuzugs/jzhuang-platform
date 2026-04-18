/**
 * 全局类型定义
 */

// 扩展 uni 对象
declare global {
  namespace Uni {
    interface App {
      $store?: any
    }
  }
}

// 页面参数
export interface PageOptions {
  [key: string]: string | number | undefined
}

// API 响应基础结构
export interface ApiResponse<T = any> {
  code: number
  message: string
  data: T
}

// 分页参数
export interface PageParams {
  page: number
  page_size: number
}

// 分页响应
export interface PageResponse<T> {
  total: number
  page: number
  page_size: number
  list: T[]
}

// 图片上传结果
export interface UploadResult {
  url: string
  file_name: string
  file_size: number
}

// 位置信息
export interface LocationInfo {
  latitude: number
  longitude: number
  address?: string
  city?: string
  district?: string
}
