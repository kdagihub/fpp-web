/* ── User & Auth ── */

export interface User {
  id: string
  email: string
  first_name: string
  last_name: string
  phone?: string
  avatar?: string
  sex?: 'M' | 'F'
  date_of_birth?: string
  is_staff: boolean
  is_active: boolean
  membership?: MembershipInfo
  roles?: Role[]
  permissions?: string[]
}

export interface MembershipInfo {
  status: 'none' | 'pending' | 'validated' | 'rejected' | 'suspended'
  matricule?: string
  submitted_at?: string
  validated_at?: string
}

export interface Role {
  id: number
  name: string
  permissions: string[]
}

export interface LoginPayload {
  email: string
  password: string
}

export interface RegisterPayload {
  email: string
  password: string
  password_confirm: string
  first_name: string
  last_name: string
  sex: 'M' | 'F'
  date_of_birth: string
}

/* ── Membership ── */

export interface MembershipRequestPayload {
  id_document_type: string
  id_document_number: string
  id_document_scan: File
  photo: File
  city: string
  commune: string
  region: string
  profession: string
  neighborhood?: string
  address?: string
  motivation?: string
}

/* ── Content ── */

export interface Article {
  id: number
  title: string
  slug: string
  summary: string
  content: string
  cover_image?: string
  category: Category
  author: ArticleAuthor
  status: 'draft' | 'published'
  featured: boolean
  created_at: string
  updated_at: string
}

export interface ArticleAuthor {
  first_name: string
  last_name: string
}

export interface Category {
  id: number
  name: string
  slug: string
  article_count?: number
}

export interface ContactPayload {
  name: string
  email: string
  subject: string
  message: string
}

export interface Contact {
  id: number
  name: string
  email: string
  subject: string
  message: string
  is_read: boolean
  created_at: string
}

/* ── Settings ── */

export interface SiteSettings {
  site_name: string
  slogan: string
  president_name: string
  president_photo?: string
  president_message?: string
  hero_image?: string
  hero_title?: string
  hero_subtitle?: string
  logo?: string
  about_text?: string
  vision_text?: string
  values_text?: string
  email?: string
  phone?: string
  whatsapp?: string
  address?: string
  facebook?: string
  twitter?: string
  instagram?: string
  youtube?: string
  tiktok?: string
}

/* ── Dashboard ── */

export interface DashboardData {
  total_members: number
  pending_members: number
  validated_members: number
  total_articles: number
  published_articles: number
  unread_contacts: number
  members_by_city: Record<string, number>[]
  members_by_sex: { M: number; F: number }
  membership_evolution: { date: string; count: number }[]
}

/* ── Audit ── */

export interface AuditLog {
  id: number
  user: string
  action: string
  entity_type: string
  entity_id: string
  details?: string
  created_at: string
}

/* ── Pagination (Django REST) ── */

export interface PaginatedResponse<T> {
  count: number
  next: string | null
  previous: string | null
  results: T[]
}

/* ── API Error ── */

export interface ApiError {
  detail?: string
  [key: string]: unknown
}
