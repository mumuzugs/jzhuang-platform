/**
 * Store 统一导出
 */
import { createPinia } from 'pinia'

const pinia = createPinia()

export default pinia

// 用户状态
export * from './user'

// 应用状态
export * from './app'
