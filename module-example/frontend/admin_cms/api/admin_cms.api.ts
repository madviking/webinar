import { apiClient } from '@/shared/api/client'

// ---------- Content Blocks ----------
export interface ContentBlockDTO {
  id: number
  key: string
  category: string
  title: string
  html_content: string
  description?: string
  variables: string[]
}

export async function listContentBlocks(params?: { category?: string }) {
  const { data } = await apiClient.get<ContentBlockDTO[]>('/admin/cms/blocks', { params })
  return data
}

export async function createContentBlock(payload: Omit<ContentBlockDTO, 'id'>) {
  const { data } = await apiClient.post<ContentBlockDTO>('/admin/cms/blocks', payload)
  return data
}

export async function updateContentBlock(id: number, payload: Partial<Omit<ContentBlockDTO, 'id' | 'key'>>) {
  const { data } = await apiClient.put<ContentBlockDTO>(`/admin/cms/blocks/${id}`, payload)
  return data
}

export async function deleteContentBlock(id: number) {
  await apiClient.delete(`/admin/cms/blocks/${id}`)
}

export async function importAllContentBlockDefaults() {
  const { data } = await apiClient.post<ContentBlockDTO[]>('/admin/cms/blocks/import-missing')
  return data
}

export async function loadTermsDefaultBlock() {
  const { data } = await apiClient.post<ContentBlockDTO>('/admin/cms/blocks/load-terms-default')
  return data
}

// ---------- Email Templates ----------
export interface EmailTemplateDTO {
  id: number
  name: string
  category: string
  subject_template: string
  body_html: string
  variables?: string[]
  is_active: boolean
}

export async function listEmailTemplates(params?: { skip?: number; limit?: number; search?: string }) {
  const { data } = await apiClient.get<EmailTemplateDTO[]>('/admin/cms/email-templates', { params })
  return data
}

export async function createEmailTemplate(payload: Omit<EmailTemplateDTO, 'id'>) {
  const { data } = await apiClient.post<EmailTemplateDTO>('/admin/cms/email-templates', payload)
  return data
}

export async function updateEmailTemplate(id: number, payload: Partial<Omit<EmailTemplateDTO, 'id' | 'name'>>) {
  const { data } = await apiClient.put<EmailTemplateDTO>(`/admin/cms/email-templates/${id}`, payload)
  return data
}

export async function deleteEmailTemplate(id: number) {
  await apiClient.delete(`/admin/cms/email-templates/${id}`)
}

export async function getTemplateVariables(): Promise<Record<string, string[]>> {
  const { data } = await apiClient.get<Record<string, string[]>>('/admin/cms/variables')
  return data
}

export async function importInviteDefaults() {
  const { data } = await apiClient.post<EmailTemplateDTO>('/admin/cms/email-templates/load-defaults')
  return data
}

export async function importAllEmailDefaults() {
  const { data } = await apiClient.post<EmailTemplateDTO[]>('/admin/cms/email-templates/import-missing')
  return data
}

// ---------- Notification Templates ----------
export interface NotificationTemplateDTO {
  id: number
  name: string
  template_type: 'email' | 'slack'
  category: string
  subject_template?: string
  body_template: string
  variables?: string[]
  is_active: boolean
  is_default: boolean
}

export async function listNotificationTemplates(params?: { template_type?: 'email' | 'slack' }) {
  const { data } = await apiClient.get<NotificationTemplateDTO[]>('/admin/cms/notification-templates', { params })
  return data
}

export async function createNotificationTemplate(payload: Omit<NotificationTemplateDTO, 'id'>) {
  const { data } = await apiClient.post<NotificationTemplateDTO>('/admin/cms/notification-templates', payload)
  return data
}

export async function updateNotificationTemplate(id: number, payload: Partial<Omit<NotificationTemplateDTO, 'id' | 'name' | 'template_type'>>) {
  const { data } = await apiClient.put<NotificationTemplateDTO>(`/admin/cms/notification-templates/${id}`, payload)
  return data
}

export async function deleteNotificationTemplate(id: number) {
  await apiClient.delete(`/admin/cms/notification-templates/${id}`)
}

export async function importAllNotificationDefaults() {
  const { data } = await apiClient.post<NotificationTemplateDTO[]>('/admin/cms/notification-templates/import-missing')
  return data
}
