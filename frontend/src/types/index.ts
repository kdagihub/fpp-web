/* ── User & Auth ── */

export interface User {
  id: string
  email: string
  email_verified: boolean
  phone?: string
  first_name: string
  last_name: string
  sex?: 'M' | 'F'
  date_of_birth?: string
  avatar?: string
  is_staff: boolean
  is_active: boolean
  created_at: string
  membership?: MembershipSummary | null
  active_roles?: ActiveRole[]
  permissions?: string[]
}

export interface MembershipSummary {
  matricule: string | null
  status: MembershipStatus
  id_document_type: string
  id_document_number: string
  city: string
  commune: string
  region: string
  neighborhood: string
  profession: string
  membership_validated_at: string | null
  membership_requested_at: string | null
}

export type MembershipStatus = 'pending' | 'validated' | 'rejected' | 'suspended'

export interface ActiveRole {
  role_id: string
  role_name: string
  role_level: string
  zone_name: string | null
  assigned_at: string | null
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
  phone?: string
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
  region?: string
  profession?: string
  neighborhood?: string
  address?: string
  motivation?: string
}

export interface MembershipDetail {
  id: string
  user_full_name: string
  user_email: string
  user_sex: string
  user_date_of_birth: string
  matricule: string | null
  id_document_type: string
  id_document_number: string
  city: string
  commune: string
  region: string
  neighborhood: string
  profession: string
  motivation: string
  membership_status: MembershipStatus
  registered_at: string
  membership_requested_at: string
  membership_validated_at: string | null
  registration_source: string
}

/* ── Content — Articles ── */

export interface ArticleListItem {
  id: number
  title: string
  slug: string
  summary: string
  cover_image: string | null
  author_name: string
  category_name: string
  category_slug: string
  is_featured: boolean
  published_at: string
}

export interface ArticleDetail extends ArticleListItem {
  content: string
  created_at: string
}

/* ── Content — Categories ── */

export interface Category {
  id: number
  name: string
  slug: string
  description: string
  article_count: number
}

/* ── Contact ── */

export interface ContactPayload {
  name: string
  email: string
  phone?: string
  subject: string
  message: string
}

export interface Contact {
  id: number
  name: string
  email: string
  phone?: string
  subject: string
  message: string
  is_read: boolean
  read_at: string | null
  created_at: string
}

/* ── Settings (matches Django SiteSettings model) ── */

export interface SiteSettings {
  site_name: string
  slogan: string
  president_name: string
  president_message: string
  president_photo: string | null
  whatsapp_number: string
  contact_email: string
  address: string
  facebook_url: string
  twitter_url: string
  instagram_url: string
  youtube_url: string
  logo: string | null
  hero_image: string | null
  hero_title: string
  hero_subtitle: string
  about_text: string
  vision_text: string
  values_text: string
}

/* ── Content — MediaContent ── */

export type MediaPlatform = 'facebook' | 'youtube'
export type MediaEmbedType = 'video' | 'post'

export interface MediaContent {
  id: string
  title: string
  description: string
  platform: MediaPlatform
  embed_type: MediaEmbedType
  source_url: string
  category: string
  is_featured: boolean
  published_at: string
}

/* ── Content — Programme ── */

export interface ProgramItem {
  id: string
  title: string
  description: string
  order: number
}

export interface ProgramSectionListItem {
  id: string
  title: string
  slug: string
  description: string
  icon: string
  cover_image: string | null
  order: number
  item_count: number
}

export interface ProgramSectionDetail extends Omit<ProgramSectionListItem, 'item_count'> {
  items: ProgramItem[]
}

/* ── Content — Événements / Agenda ── */

export type EventType = 'meeting' | 'rally' | 'conference' | 'workshop' | 'ceremony' | 'campaign' | 'other'
export type EventStatus = 'upcoming' | 'ongoing' | 'completed' | 'cancelled'

export interface EventListItem {
  id: string
  title: string
  slug: string
  short_description: string
  cover_image: string | null
  event_type: EventType
  status: EventStatus
  computed_status: EventStatus
  start_date: string
  end_date: string | null
  location: string
  city: string
  is_featured: boolean
  published_at: string
}

export interface EventDetail extends EventListItem {
  description: string
  address: string
  map_url: string
  organizer: string
  contact_email: string
  contact_phone: string
  created_at: string
}

/* ── Public Stats ── */

export interface PublicStats {
  total_members: number
  total_articles: number
  total_categories: number
}

/* ── Dashboard (admin) ── */

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

/* ── Audit (admin) ── */

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
