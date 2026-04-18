/**
 * 施工/云监工 API
 */
import request from './request'

// ============ 类型定义 ============

// 标准施工节点
export interface StandardNode {
  id: string
  name: string
  description: string
  duration_days: number
  order: number
  critical: boolean
}

// 施工项目
export interface ConstructionProject {
  id: string
  name: string
  design_project_id?: string
  address?: string
  area?: number
  total_cycle: number
  start_date?: string
  end_date?: string
  status: 'pending' | 'in_progress' | 'completed' | 'paused'
  progress: number
  nodes: ConstructionNode[]
  created_at: string
  updated_at: string
}

// 施工节点
export interface ConstructionNode {
  id: string
  name: string
  status: 'pending' | 'in_progress' | 'completed' | 'delayed'
  progress: number
  start_date?: string
  end_date?: string
  actual_start?: string
  actual_end?: string
  progress_records?: ProgressRecord[]
}

// 进度记录
export interface ProgressRecord {
  id: string
  node_id: string
  progress: number
  description?: string
  images?: string[]
  created_at: string
}

// 延期预警
export interface DelayWarning {
  node_id: string
  node_name: string
  current_progress: number
  expected_progress: number
  delay_days: number
  reason?: string
}

// 验收记录
export interface AcceptanceRecord {
  id: string
  node_id: string
  node_name: string
  status: 'pending' | 'accepted' | 'rejected'
  images: string[]
  feedback?: string
  accepted_at?: string
}

// ============ API 接口 ============

/**
 * 获取标准施工节点（8大核心节点）
 */
export function getStandardNodes(): Promise<{ total: number; nodes: StandardNode[] }> {
  return request.get('/construction/standard-nodes')
}

/**
 * 创建装修项目
 */
export function createProject(data: {
  name: string
  design_project_id?: string
  address?: string
  area?: number
  total_cycle?: number
  start_date?: string
}): Promise<{ project_id: string }> {
  return request.post('/construction/create', data)
}

/**
 * 获取项目列表
 */
export function getProjectList(params?: {
  page?: number
  page_size?: number
}): Promise<{ total: number; projects: ConstructionProject[] }> {
  return request.get('/construction/list', params || {})
}

/**
 * 获取项目详情
 */
export function getProjectDetail(projectId: string): Promise<ConstructionProject> {
  return request.get(`/construction/detail/${projectId}`)
}

/**
 * 获取项目进度
 */
export function getProjectProgress(projectId: string): Promise<{
  progress: number
  node_progress: { [key: string]: number }
}> {
  return request.get(`/construction/progress/${projectId}`)
}

/**
 * 更新节点进度
 */
export function updateNodeProgress(data: {
  node_id: string
  progress: number
  description?: string
  images?: string[]
}): Promise<any> {
  return request.post('/construction/node-progress', data)
}

/**
 * 获取延期预警列表
 */
export function getDelayWarnings(projectId: string): Promise<{ warnings: DelayWarning[] }> {
  return request.get(`/construction/delay-warnings/${projectId}`)
}

/**
 * 获取验收记录
 */
export function getAcceptanceRecords(projectId: string): Promise<{
  records: AcceptanceRecord[]
}> {
  return request.get(`/construction/acceptance/${projectId}`)
}

/**
 * 提交验收
 */
export function submitAcceptance(data: {
  node_id: string
  images: string[]
  description?: string
}): Promise<any> {
  return request.post('/construction/acceptance', data)
}

/**
 * 验收确认
 */
export function confirmAcceptance(data: {
  record_id: string
  status: 'accepted' | 'rejected'
  feedback?: string
}): Promise<any> {
  return request.post('/construction/acceptance/confirm', data)
}

/**
 * 获取施工照片
 */
export function getConstructionPhotos(projectId: string, nodeId?: string): Promise<{
  photos: { url: string; node_id: string; created_at: string }[]
}> {
  return request.get(`/construction/photos/${projectId}`, { node_id: nodeId })
}

/**
 * 上传施工照片
 */
export function uploadConstructionPhoto(projectId: string, data: {
  node_id: string
  image: string
  description?: string
}): Promise<any> {
  return request.post(`/construction/photos/${projectId}`, data)
}

/**
 * 删除项目
 */
export function deleteProject(projectId: string): Promise<any> {
  return request.delete(`/construction/delete/${projectId}`)
}
