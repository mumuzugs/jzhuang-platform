/**
 * AI 验房 API
 */
import request from './request'

// ============ 类型定义 ============

// 问题类型
export interface IssueType {
  code: string
  name: string
  description: string
  ai_model: string
}

// 问题详情
export interface IssueDetail {
  type: string
  name: string
  description: string
  risk_level: string
  suggestion: string
  location: string
  ai_model: string
  confidence: number
  estimated_cost: number
  image_url?: string
}

// 验房报告
export interface InspectionReport {
  report_id: string
  issues: IssueDetail[]
  issue_count: number
  high_risk_count: number
  medium_risk_count: number
  low_risk_count: number
  total_estimated_cost: number
  report_content?: string
  ai_accuracy: number
  response_time_ms: number
  analyzed_at: string
}

// 验房项目
export interface InspectionProject {
  id: string
  house_type: string
  city?: string
  district?: string
  area?: number
  report?: InspectionReport
  created_at: string
  updated_at: string
}

// 创建验房请求
export interface CreateInspectionRequest {
  house_type: string
  city?: string
  district?: string
  area?: number
}

// 验房报告请求
export interface CreateReportRequest {
  project_id: string
  images: string[]
}

// ============ API 接口 ============

/**
 * 获取支持的问题类型（8类）
 */
export function getIssueTypes(): Promise<{ total: number; types: IssueType[] }> {
  return request.get('/inspection/issue-types')
}

/**
 * 获取城市高频风险
 */
export function getCityRisks(city: string): Promise<any> {
  return request.get('/inspection/city-risks', { city })
}

/**
 * 创建验房项目
 */
export function createInspection(data: CreateInspectionRequest): Promise<{ project_id: string }> {
  return request.post('/inspection/create', data)
}

/**
 * 获取验房项目列表
 */
export function getInspectionList(params?: {
  page?: number
  page_size?: number
}): Promise<{ total: number; projects: InspectionProject[] }> {
  return request.get('/inspection/list', params || {})
}

/**
 * 获取验房项目详情
 */
export function getInspectionDetail(projectId: string): Promise<InspectionProject> {
  return request.get(`/inspection/detail/${projectId}`)
}

/**
 * 上传验房图片并生成报告
 */
export function createReport(data: CreateReportRequest): Promise<InspectionReport> {
  return request.post('/inspection/report', data)
}

/**
 * 获取验房报告
 */
export function getReport(reportId: string): Promise<InspectionReport> {
  return request.get(`/inspection/report/${reportId}`)
}

/**
 * 删除验房项目
 */
export function deleteInspection(projectId: string): Promise<any> {
  return request.delete(`/inspection/delete/${projectId}`)
}
