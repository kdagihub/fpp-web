<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useAppToast } from '@/composables/useToast'
import api from '@/api'
import { getMediaUrl } from '@/utils/media'
import type { AdminArticleListItem, AdminCategory, PaginatedResponse } from '@/types'
import dayjs from 'dayjs'
import 'dayjs/locale/fr'

import Tag from 'primevue/tag'

import { useShare, buildShareOgUrl } from '@/composables/useShare'
import ShareDialog from '@/components/ShareDialog.vue'

import {
  FileText,
  Plus,
  Search,
  SlidersHorizontal,
  X,
  Edit3,
  Trash2,
  Star,
  StarOff,
  Loader2,
  RotateCcw,
  Eye,
  Send,
  FilePen,
  Archive,
  ChevronLeft,
  ChevronRight,
  ChevronsLeft,
  ChevronsRight,
  ImageIcon,
  Share2,
} from 'lucide-vue-next'

dayjs.locale('fr')

const router = useRouter()
const authStore = useAuthStore()
const toast = useAppToast()

const canEdit = computed(() => authStore.hasPermission('can_edit_article'))
const canDelete = computed(() => authStore.hasPermission('can_delete_article'))

const { showDialog: shareOpen, shareData, copied, openShare, closeShare, shareOn } = useShare()

function openShareDialog(a: AdminArticleListItem) {
  const publicUrl = `${window.location.origin}/actualites/${a.slug}`
  openShare({
    title: a.title,
    description: a.summary,
    url: publicUrl,
    ogUrl: buildShareOgUrl('article', a.slug),
    image: a.cover_image ? getMediaUrl(a.cover_image) : undefined,
  })
}

/* ── Data ── */
const articles = ref<AdminArticleListItem[]>([])
const categories = ref<AdminCategory[]>([])
const loading = ref(true)
const totalCount = ref(0)
const currentPage = ref(1)
const pageSize = ref(20)

/* ── Filters ── */
const searchQuery = ref('')
const filterStatus = ref<string | null>(null)
const filterCategory = ref<string | null>(null)
const showFilters = ref(false)
const sortField = ref('created_at')
const sortOrder = ref(-1)

const statusOptions = [
  { label: 'Tous', value: null, icon: FileText },
  { label: 'Brouillons', value: 'draft', icon: FilePen },
  { label: 'Publiés', value: 'published', icon: Send },
  { label: 'Archivés', value: 'archived', icon: Archive },
]

const totalPages = computed(() => Math.ceil(totalCount.value / pageSize.value))
const hasActiveFilters = computed(() => !!filterStatus.value || !!filterCategory.value)
const filterCount = computed(() => {
  let c = 0
  if (filterStatus.value) c++
  if (filterCategory.value) c++
  return c
})

/* ── Stats ── */
const publishedCount = computed(() => articles.value.filter(a => a.status === 'published').length)
const draftCount = computed(() => articles.value.filter(a => a.status === 'draft').length)
const featuredCount = computed(() => articles.value.filter(a => a.is_featured).length)

/* ── Delete ── */
const deleteTarget = ref<AdminArticleListItem | null>(null)
const deleteOpen = ref(false)
const deleting = ref(false)

/* ── Data fetching ── */
async function fetchArticles() {
  loading.value = true
  try {
    const params: Record<string, unknown> = {
      page: currentPage.value,
      page_size: pageSize.value,
      ordering: `${sortOrder.value === -1 ? '-' : ''}${sortField.value}`,
    }
    if (searchQuery.value.trim()) params.search = searchQuery.value.trim()
    if (filterStatus.value) params.status = filterStatus.value
    if (filterCategory.value) params.category = filterCategory.value
    const { data } = await api.get<PaginatedResponse<AdminArticleListItem>>('/admin/articles/', { params })
    articles.value = data.results
    totalCount.value = data.count
  } catch {
    toast.error('Erreur', 'Impossible de charger les articles.')
  } finally {
    loading.value = false
  }
}

async function fetchCategories() {
  try {
    const { data } = await api.get<AdminCategory[]>('/admin/categories/')
    categories.value = data
  } catch { /* silent */ }
}

function confirmDelete(a: AdminArticleListItem) {
  deleteTarget.value = a
  deleteOpen.value = true
}

async function executeDelete() {
  if (!deleteTarget.value) return
  deleting.value = true
  try {
    await api.delete(`/admin/articles/${deleteTarget.value.id}/`)
    toast.success('Supprimé', `"${deleteTarget.value.title}" a été supprimé.`)
    deleteOpen.value = false
    await fetchArticles()
  } catch {
    toast.error('Erreur', 'La suppression a échoué.')
  } finally {
    deleting.value = false
  }
}

async function toggleFeatured(a: AdminArticleListItem) {
  try {
    await api.patch(`/admin/articles/${a.id}/`, { is_featured: !a.is_featured })
    a.is_featured = !a.is_featured
  } catch (err: any) {
    const detail = err?.response?.data?.is_featured?.[0] || 'Impossible de modifier la mise en avant.'
    toast.error('Erreur', detail)
  }
}

function toggleSort(field: string) {
  if (sortField.value === field) {
    sortOrder.value = sortOrder.value === -1 ? 1 : -1
  } else {
    sortField.value = field
    sortOrder.value = -1
  }
  currentPage.value = 1
  fetchArticles()
}

function goToPage(page: number) {
  if (page < 1 || page > totalPages.value) return
  currentPage.value = page
  fetchArticles()
}

function clearFilters() {
  filterStatus.value = null
  filterCategory.value = null
  searchQuery.value = ''
  currentPage.value = 1
  fetchArticles()
}

let searchTimeout: ReturnType<typeof setTimeout> | null = null
watch(searchQuery, () => {
  if (searchTimeout) clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => {
    currentPage.value = 1
    fetchArticles()
  }, 400)
})

watch([filterStatus, filterCategory], () => {
  currentPage.value = 1
  fetchArticles()
})

onMounted(() => {
  fetchArticles()
  fetchCategories()
})

/* ── Helpers ── */
function statusSeverity(s: string): 'success' | 'warn' | 'secondary' | undefined {
  const map: Record<string, 'success' | 'warn' | 'secondary'> = {
    published: 'success',
    draft: 'warn',
    archived: 'secondary',
  }
  return map[s]
}

function statusLabel(s: string) {
  const map: Record<string, string> = {
    published: 'Publié',
    draft: 'Brouillon',
    archived: 'Archivé',
  }
  return map[s] || s
}

function formatDate(d: string | null) {
  if (!d) return '—'
  return dayjs(d).format('DD MMM YYYY')
}

function sortIcon(field: string) {
  if (sortField.value !== field) return ''
  return sortOrder.value === -1 ? '↓' : '↑'
}
</script>

<template>
  <div class="max-w-[1400px]">
    <!-- Header -->
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-5 sm:mb-6">
      <div>
        <h2 class="font-heading text-xl sm:text-2xl font-bold text-[var(--color-primary)]">
          Gestion des articles
        </h2>
        <p class="text-xs sm:text-sm text-[var(--color-muted)] mt-0.5">
          Créez, modifiez et publiez les actualités du parti.
        </p>
      </div>
      <RouterLink
        to="/admin/articles/new"
        class="inline-flex items-center gap-2 px-4 py-2.5 text-sm font-semibold text-white bg-[var(--color-accent)] rounded-lg hover:bg-[var(--color-accent-hover)] transition-colors no-underline self-start sm:self-auto"
      >
        <Plus :size="16" />
        Nouvel article
      </RouterLink>
    </div>

    <!-- ═══ KPI Stats ═══ -->
    <div class="grid grid-cols-4 gap-2 sm:gap-3 mb-5 sm:mb-6">
      <div class="bg-white rounded-xl border border-gray-200 p-2.5 sm:p-4 min-w-0">
        <div class="flex items-center gap-1.5 sm:gap-2 mb-1.5 min-w-0">
          <div class="w-7 h-7 sm:w-8 sm:h-8 rounded-lg bg-blue-50 flex items-center justify-center shrink-0">
            <FileText :size="14" class="text-blue-600 sm:[&]:!w-[15px] sm:[&]:!h-[15px]" />
          </div>
          <span class="text-[9px] sm:text-xs font-semibold text-gray-500 uppercase sm:tracking-wide truncate">Total</span>
        </div>
        <p class="text-lg sm:text-2xl font-bold text-gray-900">{{ totalCount }}</p>
      </div>
      <div class="bg-white rounded-xl border border-gray-200 p-2.5 sm:p-4 min-w-0">
        <div class="flex items-center gap-1.5 sm:gap-2 mb-1.5 min-w-0">
          <div class="w-7 h-7 sm:w-8 sm:h-8 rounded-lg bg-green-50 flex items-center justify-center shrink-0">
            <Send :size="14" class="text-green-600 sm:[&]:!w-[15px] sm:[&]:!h-[15px]" />
          </div>
          <span class="text-[9px] sm:text-xs font-semibold text-gray-500 uppercase sm:tracking-wide truncate">Publiés</span>
        </div>
        <p class="text-lg sm:text-2xl font-bold text-gray-900">{{ publishedCount }}</p>
      </div>
      <div class="bg-white rounded-xl border border-gray-200 p-2.5 sm:p-4 min-w-0">
        <div class="flex items-center gap-1.5 sm:gap-2 mb-1.5 min-w-0">
          <div class="w-7 h-7 sm:w-8 sm:h-8 rounded-lg bg-amber-50 flex items-center justify-center shrink-0">
            <FilePen :size="14" class="text-amber-600 sm:[&]:!w-[15px] sm:[&]:!h-[15px]" />
          </div>
          <span class="text-[9px] sm:text-xs font-semibold text-gray-500 uppercase sm:tracking-wide truncate">Brouillons</span>
        </div>
        <p class="text-lg sm:text-2xl font-bold text-gray-900">{{ draftCount }}</p>
      </div>
      <div class="bg-white rounded-xl border border-gray-200 p-2.5 sm:p-4 min-w-0">
        <div class="flex items-center gap-1.5 sm:gap-2 mb-1.5 min-w-0">
          <div class="w-7 h-7 sm:w-8 sm:h-8 rounded-lg bg-purple-50 flex items-center justify-center shrink-0">
            <Star :size="14" class="text-purple-600 sm:[&]:!w-[15px] sm:[&]:!h-[15px]" />
          </div>
          <span class="text-[9px] sm:text-xs font-semibold text-gray-500 uppercase sm:tracking-wide truncate">En avant</span>
        </div>
        <p class="text-lg sm:text-2xl font-bold text-gray-900">{{ featuredCount }}</p>
      </div>
    </div>

    <!-- ═══ Toolbar ═══ -->
    <div class="bg-white rounded-xl border border-gray-200 mb-4 sm:mb-6 overflow-hidden">
      <div class="p-3 sm:p-4">
        <div class="flex flex-col sm:flex-row gap-3">
          <div class="flex-1 relative">
            <Search :size="16" class="absolute left-3.5 top-1/2 -translate-y-1/2 text-gray-400 pointer-events-none" />
            <input
              v-model="searchQuery"
              type="search"
              placeholder="Rechercher par titre ou résumé..."
              class="w-full pl-10 pr-4 py-2.5 text-sm border border-gray-200 rounded-lg bg-gray-50 focus:bg-white focus:ring-2 focus:ring-[var(--color-accent)]/20 focus:border-[var(--color-accent)] outline-none transition-all placeholder:text-gray-400"
            />
          </div>
          <div class="flex items-center gap-2 shrink-0">
            <button
              @click="showFilters = !showFilters"
              class="inline-flex items-center gap-2 px-3.5 py-2.5 text-sm font-medium rounded-lg border transition-all cursor-pointer"
              :class="hasActiveFilters
                ? 'bg-[var(--color-accent-light)] border-[var(--color-accent)]/30 text-[var(--color-accent)]'
                : 'bg-white border-gray-200 text-gray-500 hover:border-gray-300 hover:text-gray-700'"
            >
              <SlidersHorizontal :size="15" />
              <span class="hidden sm:inline">Filtres</span>
              <span
                v-if="filterCount"
                class="w-5 h-5 rounded-full bg-[var(--color-accent)] text-white text-[10px] font-bold flex items-center justify-center"
              >
                {{ filterCount }}
              </span>
            </button>
          </div>
        </div>

        <Transition
          enter-active-class="transition-all duration-200 ease-out"
          enter-from-class="opacity-0 -translate-y-1"
          enter-to-class="opacity-100 translate-y-0"
          leave-active-class="transition-all duration-150 ease-in"
          leave-from-class="opacity-100"
          leave-to-class="opacity-0 -translate-y-1"
        >
          <div v-if="showFilters" class="mt-3 pt-3 border-t border-gray-100 space-y-3">
            <!-- Status pills -->
            <div>
              <label class="block text-[11px] font-semibold text-gray-400 uppercase tracking-wide mb-2">Statut</label>
              <div class="flex flex-wrap gap-2">
                <button
                  v-for="opt in statusOptions"
                  :key="String(opt.value)"
                  @click="filterStatus = opt.value"
                  class="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold rounded-lg border transition-all cursor-pointer"
                  :class="filterStatus === opt.value
                    ? 'bg-[var(--color-accent)] text-white border-[var(--color-accent)]'
                    : 'bg-white text-gray-500 border-gray-200 hover:border-gray-300'"
                >
                  <component :is="opt.icon" :size="12" />
                  {{ opt.label }}
                </button>
              </div>
            </div>

            <!-- Category pills -->
            <div v-if="categories.length > 0">
              <label class="block text-[11px] font-semibold text-gray-400 uppercase tracking-wide mb-2">Catégorie</label>
              <div class="flex flex-wrap gap-2">
                <button
                  @click="filterCategory = null"
                  class="px-3 py-1.5 text-xs font-semibold rounded-lg border transition-all cursor-pointer"
                  :class="!filterCategory
                    ? 'bg-[var(--color-accent)] text-white border-[var(--color-accent)]'
                    : 'bg-white text-gray-500 border-gray-200 hover:border-gray-300'"
                >
                  Toutes
                </button>
                <button
                  v-for="cat in categories"
                  :key="cat.id"
                  @click="filterCategory = cat.id"
                  class="px-3 py-1.5 text-xs font-semibold rounded-lg border transition-all cursor-pointer"
                  :class="filterCategory === cat.id
                    ? 'bg-[var(--color-accent)] text-white border-[var(--color-accent)]'
                    : 'bg-white text-gray-500 border-gray-200 hover:border-gray-300'"
                >
                  {{ cat.name }}
                  <span class="opacity-60 ml-1">({{ cat.article_count }})</span>
                </button>
              </div>
            </div>

            <button
              v-if="hasActiveFilters"
              @click="clearFilters"
              class="inline-flex items-center gap-1 px-3 py-1.5 text-xs font-semibold text-red-500 hover:bg-red-50 rounded-lg transition-colors cursor-pointer"
            >
              <RotateCcw :size="12" />
              Réinitialiser
            </button>
          </div>
        </Transition>
      </div>
      <div class="px-3 sm:px-4 py-2 bg-gray-50/60 border-t border-gray-100 text-xs text-gray-500">
        <span class="font-semibold text-gray-900">{{ totalCount }}</span> article{{ totalCount > 1 ? 's' : '' }}
        <template v-if="hasActiveFilters || searchQuery.trim()"> — filtres actifs</template>
      </div>
    </div>

    <!-- ═══ Desktop Table (lg+) ═══ -->
    <div class="hidden lg:block bg-white rounded-xl border border-gray-200 overflow-hidden mb-4">
      <div v-if="loading" class="p-8">
        <div v-for="i in 5" :key="i" class="flex items-center gap-4 py-4 border-b border-gray-100 last:border-0 animate-pulse">
          <div class="w-16 h-10 rounded-lg bg-gray-100" />
          <div class="flex-1 space-y-2">
            <div class="h-3.5 bg-gray-100 rounded w-48" />
            <div class="h-3 bg-gray-100 rounded w-64" />
          </div>
          <div class="h-6 bg-gray-100 rounded-full w-20" />
        </div>
      </div>

      <div v-else-if="articles.length === 0" class="py-16 text-center">
        <FileText :size="44" class="mx-auto mb-3 text-gray-300" />
        <p class="text-sm font-medium text-gray-500">Aucun article trouvé</p>
        <p class="text-xs text-gray-400 mt-1">Créez votre premier article ou modifiez vos filtres.</p>
      </div>

      <table v-else class="w-full">
        <thead>
          <tr class="border-b border-gray-200">
            <th class="text-left pl-5 pr-2 py-3.5 text-[11px] font-bold text-gray-400 uppercase tracking-wider" style="width: 4.5rem"></th>
            <th class="text-left px-3 py-3.5 text-[11px] font-bold text-gray-400 uppercase tracking-wider">
              <button @click="toggleSort('title')" class="inline-flex items-center gap-1 cursor-pointer bg-transparent border-none p-0 text-[11px] font-bold text-gray-400 uppercase tracking-wider hover:text-gray-700 transition-colors">
                Titre {{ sortIcon('title') }}
              </button>
            </th>
            <th class="text-left px-3 py-3.5 text-[11px] font-bold text-gray-400 uppercase tracking-wider">Catégorie</th>
            <th class="text-left px-3 py-3.5 text-[11px] font-bold text-gray-400 uppercase tracking-wider">Statut</th>
            <th class="text-left px-3 py-3.5 text-[11px] font-bold text-gray-400 uppercase tracking-wider">Auteur</th>
            <th class="text-left px-3 py-3.5 text-[11px] font-bold text-gray-400 uppercase tracking-wider">
              <button @click="toggleSort('created_at')" class="inline-flex items-center gap-1 cursor-pointer bg-transparent border-none p-0 text-[11px] font-bold text-gray-400 uppercase tracking-wider hover:text-gray-700 transition-colors">
                Créé {{ sortIcon('created_at') }}
              </button>
            </th>
            <th class="text-right pr-5 py-3.5 text-[11px] font-bold text-gray-400 uppercase tracking-wider">Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="a in articles"
            :key="a.id"
            class="border-b border-gray-100 last:border-0 hover:bg-gray-50/50 transition-colors group"
          >
            <!-- Cover -->
            <td class="pl-5 pr-2 py-3">
              <div class="w-14 h-9 rounded-lg overflow-hidden bg-gray-100 flex items-center justify-center shrink-0">
                <img
                  v-if="a.cover_image"
                  :src="getMediaUrl(a.cover_image)"
                  :alt="a.title"
                  class="w-full h-full object-cover"
                  loading="lazy"
                />
                <ImageIcon v-else :size="14" class="text-gray-300" />
              </div>
            </td>

            <!-- Title -->
            <td class="px-3 py-3">
              <button
                class="text-left bg-transparent border-none p-0 cursor-pointer group/title"
                @click="router.push(`/admin/articles/${a.id}/edit`)"
              >
                <span class="text-sm font-semibold text-gray-900 group-hover/title:text-[var(--color-accent)] transition-colors line-clamp-1">
                  {{ a.title }}
                </span>
                <span class="block text-[11px] text-gray-400 mt-0.5 line-clamp-1 max-w-[20rem]">{{ a.summary }}</span>
              </button>
            </td>

            <!-- Category -->
            <td class="px-3 py-3">
              <span class="text-xs text-gray-500">{{ a.category_name || '—' }}</span>
            </td>

            <!-- Status -->
            <td class="px-3 py-3">
              <div class="flex items-center gap-2">
                <Tag
                  :value="statusLabel(a.status)"
                  :severity="statusSeverity(a.status)"
                  class="!text-[10px] !font-bold !uppercase !tracking-wider !px-2 !py-0.5"
                />
                <button
                  @click="toggleFeatured(a)"
                  class="p-0.5 rounded transition-colors cursor-pointer bg-transparent border-none"
                  :class="a.is_featured ? 'text-amber-500' : 'text-gray-300 hover:text-amber-400'"
                  :title="a.is_featured ? 'Retirer de la une' : 'Mettre à la une'"
                >
                  <Star v-if="a.is_featured" :size="13" fill="currentColor" />
                  <StarOff v-else :size="13" />
                </button>
              </div>
            </td>

            <!-- Author -->
            <td class="px-3 py-3">
              <span class="text-xs text-gray-500">{{ a.author_name || '—' }}</span>
            </td>

            <!-- Date -->
            <td class="px-3 py-3">
              <span class="text-xs text-gray-500">{{ formatDate(a.created_at) }}</span>
              <span v-if="a.published_at" class="block text-[10px] text-green-600 mt-0.5">
                Publié {{ formatDate(a.published_at) }}
              </span>
            </td>

            <!-- Actions -->
            <td class="pr-5 py-3">
              <div class="flex items-center justify-end gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                <RouterLink
                  v-if="canEdit"
                  :to="`/admin/articles/${a.id}/edit`"
                  class="p-2 rounded-lg hover:bg-blue-50 text-gray-400 hover:text-blue-600 transition-all no-underline"
                  title="Modifier"
                >
                  <Edit3 :size="15" />
                </RouterLink>
                <a
                  v-if="a.status === 'published'"
                  :href="`/actualites/${a.slug}`"
                  target="_blank"
                  class="p-2 rounded-lg hover:bg-green-50 text-gray-400 hover:text-green-600 transition-all"
                  title="Voir sur le site"
                >
                  <Eye :size="15" />
                </a>
                <button
                  v-if="a.status === 'published'"
                  @click="openShareDialog(a)"
                  class="p-2 rounded-lg hover:bg-indigo-50 text-gray-400 hover:text-indigo-600 transition-all cursor-pointer bg-transparent border-none"
                  title="Partager"
                >
                  <Share2 :size="15" />
                </button>
                <button
                  v-if="canDelete"
                  @click="confirmDelete(a)"
                  class="p-2 rounded-lg hover:bg-red-50 text-gray-400 hover:text-red-600 transition-all cursor-pointer bg-transparent border-none"
                  title="Supprimer"
                >
                  <Trash2 :size="15" />
                </button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- ═══ Mobile Cards (< lg) ═══ -->
    <div class="lg:hidden space-y-3 mb-4">
      <template v-if="loading">
        <div v-for="i in 3" :key="i" class="bg-white rounded-xl border border-gray-200 p-4 animate-pulse">
          <div class="flex items-start gap-3">
            <div class="w-16 h-12 rounded-lg bg-gray-100 shrink-0" />
            <div class="flex-1 space-y-2">
              <div class="h-3.5 bg-gray-100 rounded w-40" />
              <div class="h-3 bg-gray-100 rounded w-full" />
              <div class="h-3 bg-gray-100 rounded w-20" />
            </div>
          </div>
        </div>
      </template>

      <div v-else-if="articles.length === 0" class="bg-white rounded-xl border border-gray-200 py-16 text-center">
        <FileText :size="40" class="mx-auto mb-3 text-gray-300" />
        <p class="text-sm font-medium text-gray-500">Aucun article trouvé</p>
      </div>

      <template v-else>
        <div
          v-for="a in articles"
          :key="a.id"
          class="bg-white rounded-xl border border-gray-200 overflow-hidden"
        >
          <button
            class="w-full p-4 pb-3 text-left bg-transparent border-none cursor-pointer"
            @click="router.push(`/admin/articles/${a.id}/edit`)"
          >
            <div class="flex items-start gap-3">
              <div class="w-16 h-12 rounded-lg overflow-hidden bg-gray-100 flex items-center justify-center shrink-0">
                <img
                  v-if="a.cover_image"
                  :src="getMediaUrl(a.cover_image)"
                  :alt="a.title"
                  class="w-full h-full object-cover"
                  loading="lazy"
                />
                <ImageIcon v-else :size="16" class="text-gray-300" />
              </div>
              <div class="flex-1 min-w-0">
                <div class="flex items-start justify-between gap-2">
                  <h3 class="text-sm font-bold text-gray-900 line-clamp-2 leading-snug">{{ a.title }}</h3>
                  <div class="flex items-center gap-1 shrink-0">
                    <Tag
                      :value="statusLabel(a.status)"
                      :severity="statusSeverity(a.status)"
                      class="!text-[9px] !font-bold !uppercase !tracking-wider !px-1.5 !py-0.5"
                    />
                    <button
                      @click.stop="toggleFeatured(a)"
                      class="p-0.5 cursor-pointer bg-transparent border-none"
                      :class="a.is_featured ? 'text-amber-500' : 'text-gray-300'"
                    >
                      <Star v-if="a.is_featured" :size="13" fill="currentColor" />
                      <StarOff v-else :size="13" />
                    </button>
                  </div>
                </div>
                <p class="text-xs text-gray-400 mt-1 line-clamp-1">{{ a.summary }}</p>
                <div class="flex flex-wrap items-center gap-2 mt-1.5 text-[11px] text-gray-400">
                  <span v-if="a.category_name">{{ a.category_name }}</span>
                  <span v-if="a.category_name" class="opacity-30">·</span>
                  <span>{{ formatDate(a.created_at) }}</span>
                  <span v-if="a.author_name" class="opacity-30">·</span>
                  <span v-if="a.author_name">{{ a.author_name }}</span>
                </div>
              </div>
            </div>
          </button>

          <div class="flex items-center border-t border-gray-100 divide-x divide-gray-100">
            <RouterLink
              v-if="canEdit"
              :to="`/admin/articles/${a.id}/edit`"
              class="flex-1 flex items-center justify-center gap-1.5 py-2.5 text-[11px] font-semibold text-gray-500 hover:text-blue-600 hover:bg-blue-50/50 transition-all no-underline"
            >
              <Edit3 :size="13" />
              Modifier
            </RouterLink>
            <a
              v-if="a.status === 'published'"
              :href="`/actualites/${a.slug}`"
              target="_blank"
              class="flex-1 flex items-center justify-center gap-1.5 py-2.5 text-[11px] font-semibold text-gray-500 hover:text-green-600 hover:bg-green-50/50 transition-all no-underline"
            >
              <Eye :size="13" />
              Voir
            </a>
            <button
              v-if="a.status === 'published'"
              @click="openShareDialog(a)"
              class="flex-1 flex items-center justify-center gap-1.5 py-2.5 text-[11px] font-semibold text-gray-500 hover:text-indigo-600 hover:bg-indigo-50/50 transition-all cursor-pointer bg-transparent border-none"
            >
              <Share2 :size="13" />
              Partager
            </button>
            <button
              v-if="canDelete"
              @click="confirmDelete(a)"
              class="flex-1 flex items-center justify-center gap-1.5 py-2.5 text-[11px] font-semibold text-gray-500 hover:text-red-600 hover:bg-red-50/50 transition-all cursor-pointer bg-transparent border-none"
            >
              <Trash2 :size="13" />
              Supprimer
            </button>
          </div>
        </div>
      </template>
    </div>

    <!-- ═══ Pagination ═══ -->
    <div
      v-if="totalPages > 1 && !loading"
      class="flex items-center justify-between sm:justify-center gap-2 sm:gap-1"
    >
      <div class="flex items-center gap-1">
        <button @click="goToPage(1)" :disabled="currentPage <= 1" class="p-2 rounded-lg hover:bg-gray-100 text-gray-500 transition-colors cursor-pointer bg-transparent border-none disabled:opacity-30 disabled:cursor-not-allowed">
          <ChevronsLeft :size="16" />
        </button>
        <button @click="goToPage(currentPage - 1)" :disabled="currentPage <= 1" class="p-2 rounded-lg hover:bg-gray-100 text-gray-500 transition-colors cursor-pointer bg-transparent border-none disabled:opacity-30 disabled:cursor-not-allowed">
          <ChevronLeft :size="16" />
        </button>
      </div>
      <span class="text-xs font-medium text-gray-500 px-3 tabular-nums">
        Page <span class="font-bold text-gray-900">{{ currentPage }}</span> sur {{ totalPages }}
      </span>
      <div class="flex items-center gap-1">
        <button @click="goToPage(currentPage + 1)" :disabled="currentPage >= totalPages" class="p-2 rounded-lg hover:bg-gray-100 text-gray-500 transition-colors cursor-pointer bg-transparent border-none disabled:opacity-30 disabled:cursor-not-allowed">
          <ChevronRight :size="16" />
        </button>
        <button @click="goToPage(totalPages)" :disabled="currentPage >= totalPages" class="p-2 rounded-lg hover:bg-gray-100 text-gray-500 transition-colors cursor-pointer bg-transparent border-none disabled:opacity-30 disabled:cursor-not-allowed">
          <ChevronsRight :size="16" />
        </button>
      </div>
    </div>

    <!-- ═══ Delete Dialog ═══ -->
    <Teleport to="body">
      <Transition
        enter-active-class="transition-opacity duration-200"
        enter-from-class="opacity-0"
        enter-to-class="opacity-100"
        leave-active-class="transition-opacity duration-150"
        leave-from-class="opacity-100"
        leave-to-class="opacity-0"
      >
        <div
          v-if="deleteOpen"
          class="fixed inset-0 z-50 flex items-end sm:items-center justify-center p-0 sm:p-4 bg-black/40 backdrop-blur-sm"
          @click.self="deleteOpen = false"
        >
          <div class="bg-white w-full sm:rounded-2xl sm:max-w-sm sm:w-full shadow-xl rounded-t-2xl p-5">
            <h3 class="font-heading text-base font-bold text-gray-900 mb-2">Supprimer cet article ?</h3>
            <p class="text-sm text-gray-500 mb-5">
              <strong>« {{ deleteTarget?.title }} »</strong> sera marqué comme supprimé (soft delete). Cette action est réversible par un administrateur.
            </p>
            <div class="flex items-center justify-end gap-3">
              <button @click="deleteOpen = false" class="px-4 py-2.5 text-sm font-medium text-gray-500 hover:text-gray-700 cursor-pointer bg-transparent border-none">
                Annuler
              </button>
              <button
                @click="executeDelete"
                :disabled="deleting"
                class="inline-flex items-center gap-2 px-5 py-2.5 text-sm font-semibold text-white bg-red-600 rounded-lg hover:bg-red-700 transition-colors cursor-pointer disabled:opacity-50"
              >
                <Loader2 v-if="deleting" :size="14" class="animate-spin" />
                Supprimer
              </button>
            </div>
          </div>
        </div>
      </Transition>
    </Teleport>

    <!-- ═══ Share Dialog ═══ -->
    <ShareDialog
      :show="shareOpen"
      :title="shareData.title"
      :description="shareData.description"
      :image="shareData.image"
      :copied="copied"
      @close="closeShare"
      @share="shareOn"
    />
  </div>
</template>
