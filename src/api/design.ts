/**
 * AI 设计 + 预算联动 API
 */
import request from './request'

// ============ 类型定义 ============

// 装修风格
export interface Style {
  code: string
  name: string
  description: string
  colors: string[]
  materials: string[]
  price_range: string
}

// 布局类型
export interface Layout {
  code: string
  name: string
  description: string
  features: string[]
  suitable_for: string[]
}

// 平面方案
export interface LayoutPlan {
  id: string
  name: string
  style: string
  layout_type: string
  area: number
  rooms: number
  image_url?: string
  rooms_data?: any
  budget_range: string
  created_at: string
}

// 效果图
export interface RenderImage {
  id: string
  style: string
  room_type: string
  image_url: string
  thumbnail_url: string
  created_at: string
}

// 预算项目
export interface BudgetItem {
  category: string
  name: string
  unit: string
  quantity: number
  unit_price: number
  total_price: number
  material?: string
  brand?: string
}

// 预算详情
export interface BudgetDetail {
  project_id: string
  total_budget: number
  material_cost: number
  labor_cost: number
  design_fee: number
  items: BudgetItem[]
  city: string
  created_at: string
}

// ============ API 接口 ============

/**
 * 获取装修风格列表
 */
export function getStyles(): Promise<{ total: number; styles: Style[] }> {
  return request.get('/design/styles')
}

/**
 * 获取布局类型列表
 */
export function getLayouts(): Promise<{ total: number; layouts: Layout[] }> {
  return request.get('/design/layouts')
}

/**
 * 生成布局方案（3套）
 */
export function generateLayouts(data: {
  project_id: string
  area: number
  rooms: number
  style?: string
  layout_type?: string
}): Promise<{ plans: LayoutPlan[] }> {
  return request.post('/design/generate-layouts', data)
}

/**
 * 获取布局方案详情
 */
export function getLayoutDetail(planId: string): Promise<LayoutPlan> {
  return request.get(`/design/layout/${planId}`)
}

/**
 * 生成效果图
 */
export function generateRenderImages(data: {
  plan_id: string
  room_types: string[]
  style: string
}): Promise<{ images: RenderImage[] }> {
  return request.post('/design/render', data)
}

/**
 * 获取效果图列表
 */
export function getRenderImages(planId: string): Promise<{ images: RenderImage[] }> {
  return request.get('/design/renders', { plan_id: planId })
}

/**
 * 识别户型图
 */
export function recognizeFloorPlan(imageUrl: string): Promise<{
  rooms: number
  area: number
  rooms_data: any
  image_url: string
}> {
  return request.post('/design/recognize', { image_url: imageUrl })
}

/**
 * 计算预算
 */
export function calculateBudget(data: {
  project_id: string
  materials: any[]
  city?: string
  budget_limit?: number
}): Promise<BudgetDetail> {
  return request.post('/design/budget', data)
}

/**
 * 获取预算详情
 */
export function getBudgetDetail(projectId: string): Promise<BudgetDetail> {
  return request.get(`/design/budget/${projectId}`)
}

/**
 * 获取设计方案列表
 */
export function getDesignList(params?: {
  page?: number
  page_size?: number
}): Promise<{ total: number; designs: any[] }> {
  return request.get('/design/list', params || {})
}

/**
 * 获取设计方案详情
 */
export function getDesignDetail(projectId: string): Promise<any> {
  return request.get(`/design/detail/${projectId}`)
}
