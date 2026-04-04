<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useAppToast } from '@/composables/useToast'
import api from '@/api'
import type { AdminMediaContent } from '@/types'
import dayjs from 'dayjs'
import 'dayjs/locale/fr'

import Tag from 'primevue/tag'

import {
  Tv,
  Plus,
  Search,
  SlidersHorizontal,
  X,
  Edit3,
  Trash2,
  ExternalLink,
  Star,
  StarOff,
  Loader2,
  RotateCcw,
  Youtube,
  Facebook,
  Eye,
  EyeOff,
} from 'lucide-vue-next'

dayjs.locale('fr')

const toast = useAppToast()

const items = ref<AdminMediaContent[]>([])
const loading = ref(true)
const filterPlatform = ref<string | null>(null)
const searchQuery = ref('')
const showFilters = ref(false)

const platformOptions = [
  { label: 'Toutes', value: null },
  { label: 'Facebook', value: 'facebook' },
  { label: 'YouTube', value: 'youtube' },
]

const filteredItems = computed(() => {
  let list = items.value
  if (filterPlatform.value) {
    list = list.filter(m => m.platform === filterPlatform.value)
  }
  if (searchQuery.value.trim()) {
    const q = searchQuery.value.toLowerCase()
    list = list.filter(m =>
      m.title.toLowerCase().includes(q)
      || m.description.toLowerCase().includes(q)
      || m.category.toLowerCase().includes(q),
    )
  }
  return list
})

const hasActiveFilters = computed(() => !!filterPlatform.value)

async function fetchMedia() {
  loading.value = true
  try {
    const { data } = await api.get<AdminMediaContent[]>('/admin/media/')
    items.value = data
  } catch {
    toast.error('Erreur', 'Impossible de charger les médias.')
  } finally {
    loading.value = false
  }
}

onMounted(fetchMedia)

/* ── Form dialog ── */
const dialogOpen = ref(false)
const dialogMode = ref<'create' | 'edit'>('create')
const saving = ref(false)

const formDefaults = {
  title: '',
  description: '',
  source_url: '',
  category: '',
  is_featured: false,
  is_active: true,
  published_at: dayjs().format('YYYY-MM-DD'),
}
const form = ref({ ...formDefaults })
const editId = ref<string | null>(null)

function openCreate() {
  dialogMode.value = 'create'
  form.value = { ...formDefaults, published_at: dayjs().format('YYYY-MM-DD') }
  editId.value = null
  dialogOpen.value = true
}

function openEdit(m: AdminMediaContent) {
  dialogMode.value = 'edit'
  form.value = {
    title: m.title,
    description: m.description,
    source_url: m.source_url,
    category: m.category,
    is_featured: m.is_featured,
    is_active: m.is_active,
    published_at: m.published_at,
  }
  editId.value = m.id
  dialogOpen.value = true
}

async function saveMedia() {
  if (!form.value.title.trim() || !form.value.source_url.trim()) {
    toast.error('Champs requis', 'Le titre et l\'URL sont obligatoires.')
    return
  }
  saving.value = true
  try {
    if (dialogMode.value === 'create') {
      await api.post('/admin/media/', form.value)
      toast.success('Média ajouté', 'Le contenu média a été créé.')
    } else {
      await api.patch(`/admin/media/${editId.value}/`, form.value)
      toast.success('Média modifié', 'Les modifications ont été enregistrées.')
    }
    dialogOpen.value = false
    await fetchMedia()
  } catch (err: any) {
    const detail = err?.response?.data?.source_url?.[0]
      || err?.response?.data?.detail
      || 'Une erreur est survenue.'
    toast.error('Erreur', detail)
  } finally {
    saving.value = false
  }
}

/* ── Delete ── */
const deleteTarget = ref<AdminMediaContent | null>(null)
const deleteOpen = ref(false)
const deleting = ref(false)

function confirmDelete(m: AdminMediaContent) {
  deleteTarget.value = m
  deleteOpen.value = true
}

async function executeDelete() {
  if (!deleteTarget.value) return
  deleting.value = true
  try {
    await api.delete(`/admin/media/${deleteTarget.value.id}/`)
    toast.success('Supprimé', `"${deleteTarget.value.title}" a été supprimé.`)
    deleteOpen.value = false
    await fetchMedia()
  } catch {
    toast.error('Erreur', 'La suppression a échoué.')
  } finally {
    deleting.value = false
  }
}

/* ── Toggle featured ── */
async function toggleFeatured(m: AdminMediaContent) {
  try {
    await api.patch(`/admin/media/${m.id}/`, { is_featured: !m.is_featured })
    m.is_featured = !m.is_featured
  } catch {
    toast.error('Erreur', 'Impossible de modifier la mise en avant.')
  }
}

/* ── Toggle active ── */
async function toggleActive(m: AdminMediaContent) {
  try {
    await api.patch(`/admin/media/${m.id}/`, { is_active: !m.is_active })
    m.is_active = !m.is_active
  } catch {
    toast.error('Erreur', 'Impossible de modifier la visibilité.')
  }
}

/* ── Helpers ── */
function formatDate(d: string) {
  return dayjs(d).format('DD MMM YYYY')
}

function platformIcon(p: string) {
  return p === 'youtube' ? Youtube : Facebook
}

function platformColor(p: string) {
  return p === 'youtube' ? 'text-red-600' : 'text-blue-600'
}

function platformBg(p: string) {
  return p === 'youtube' ? 'bg-red-50' : 'bg-blue-50'
}

function clearFilters() {
  filterPlatform.value = null
  searchQuery.value = ''
}
</script>

<template>
  <div class="max-w-[1400px]">
    <!-- Header -->
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-5 sm:mb-6">
      <div>
        <h2 class="font-heading text-xl sm:text-2xl font-bold text-[var(--color-primary)]">
          FPP TV — Médias
        </h2>
        <p class="text-xs sm:text-sm text-[var(--color-muted)] mt-0.5">
          Gérez les vidéos et publications Facebook/YouTube.
        </p>
      </div>
      <button
        @click="openCreate"
        class="inline-flex items-center gap-2 px-4 py-2.5 text-sm font-semibold text-white bg-[var(--color-accent)] rounded-lg hover:bg-[var(--color-accent-hover)] transition-colors cursor-pointer self-start sm:self-auto"
      >
        <Plus :size="16" />
        Ajouter un média
      </button>
    </div>

    <!-- ═══ KPI Stats ═══ -->
    <div class="grid grid-cols-4 gap-2 sm:gap-3 mb-5 sm:mb-6">
      <div class="bg-white rounded-xl border border-gray-200 p-2.5 sm:p-4 min-w-0">
        <div class="flex items-center gap-1.5 sm:gap-2 mb-1.5 min-w-0">
          <div class="w-7 h-7 sm:w-8 sm:h-8 rounded-lg bg-purple-50 flex items-center justify-center shrink-0">
            <Tv :size="14" class="text-purple-600 sm:[&]:!w-[15px] sm:[&]:!h-[15px]" />
          </div>
          <span class="text-[9px] sm:text-xs font-semibold text-gray-500 uppercase sm:tracking-wide truncate">Total</span>
        </div>
        <p class="text-lg sm:text-2xl font-bold text-gray-900">{{ items.length }}</p>
      </div>
      <div class="bg-white rounded-xl border border-gray-200 p-2.5 sm:p-4 min-w-0">
        <div class="flex items-center gap-1.5 sm:gap-2 mb-1.5 min-w-0">
          <div class="w-7 h-7 sm:w-8 sm:h-8 rounded-lg bg-blue-50 flex items-center justify-center shrink-0">
            <Facebook :size="14" class="text-blue-600 sm:[&]:!w-[15px] sm:[&]:!h-[15px]" />
          </div>
          <span class="text-[9px] sm:text-xs font-semibold text-gray-500 uppercase sm:tracking-wide truncate">Facebook</span>
        </div>
        <p class="text-lg sm:text-2xl font-bold text-gray-900">{{ items.filter(m => m.platform === 'facebook').length }}</p>
      </div>
      <div class="bg-white rounded-xl border border-gray-200 p-2.5 sm:p-4 min-w-0">
        <div class="flex items-center gap-1.5 sm:gap-2 mb-1.5 min-w-0">
          <div class="w-7 h-7 sm:w-8 sm:h-8 rounded-lg bg-red-50 flex items-center justify-center shrink-0">
            <Youtube :size="14" class="text-red-600 sm:[&]:!w-[15px] sm:[&]:!h-[15px]" />
          </div>
          <span class="text-[9px] sm:text-xs font-semibold text-gray-500 uppercase sm:tracking-wide truncate">YouTube</span>
        </div>
        <p class="text-lg sm:text-2xl font-bold text-gray-900">{{ items.filter(m => m.platform === 'youtube').length }}</p>
      </div>
      <div class="bg-white rounded-xl border border-gray-200 p-2.5 sm:p-4 min-w-0">
        <div class="flex items-center gap-1.5 sm:gap-2 mb-1.5 min-w-0">
          <div class="w-7 h-7 sm:w-8 sm:h-8 rounded-lg bg-amber-50 flex items-center justify-center shrink-0">
            <Star :size="14" class="text-amber-600 sm:[&]:!w-[15px] sm:[&]:!h-[15px]" />
          </div>
          <span class="text-[9px] sm:text-xs font-semibold text-gray-500 uppercase sm:tracking-wide truncate">En avant</span>
        </div>
        <p class="text-lg sm:text-2xl font-bold text-gray-900">{{ items.filter(m => m.is_featured).length }}</p>
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
              placeholder="Rechercher par titre, description, catégorie..."
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
          <div v-if="showFilters" class="flex flex-wrap items-center gap-2 mt-3 pt-3 border-t border-gray-100">
            <button
              v-for="opt in platformOptions"
              :key="String(opt.value)"
              @click="filterPlatform = opt.value"
              class="px-3 py-1.5 text-xs font-semibold rounded-lg border transition-all cursor-pointer"
              :class="filterPlatform === opt.value
                ? 'bg-[var(--color-accent)] text-white border-[var(--color-accent)]'
                : 'bg-white text-gray-500 border-gray-200 hover:border-gray-300'"
            >
              {{ opt.label }}
            </button>
            <button
              v-if="hasActiveFilters"
              @click="clearFilters"
              class="inline-flex items-center gap-1 px-3 py-1.5 text-xs font-semibold text-red-500 hover:bg-red-50 rounded-lg transition-colors cursor-pointer"
            >
              <RotateCcw :size="12" />
              Reset
            </button>
          </div>
        </Transition>
      </div>
      <div class="px-3 sm:px-4 py-2 bg-gray-50/60 border-t border-gray-100 text-xs text-gray-500">
        <span class="font-semibold text-gray-900">{{ filteredItems.length }}</span> média{{ filteredItems.length > 1 ? 's' : '' }}
      </div>
    </div>

    <!-- ═══ Desktop Table (lg+) ═══ -->
    <div class="hidden lg:block bg-white rounded-xl border border-gray-200 overflow-hidden mb-4">
      <div v-if="loading" class="p-8">
        <div v-for="i in 4" :key="i" class="flex items-center gap-4 py-4 border-b border-gray-100 last:border-0 animate-pulse">
          <div class="w-10 h-10 rounded-lg bg-gray-100" />
          <div class="flex-1 space-y-2">
            <div class="h-3.5 bg-gray-100 rounded w-48" />
            <div class="h-3 bg-gray-100 rounded w-64" />
          </div>
          <div class="h-6 bg-gray-100 rounded-full w-20" />
        </div>
      </div>

      <div v-else-if="filteredItems.length === 0" class="py-16 text-center">
        <Tv :size="44" class="mx-auto mb-3 text-gray-300" />
        <p class="text-sm font-medium text-gray-500">Aucun média trouvé</p>
        <p class="text-xs text-gray-400 mt-1">Ajoutez votre premier contenu ou modifiez vos filtres.</p>
      </div>

      <table v-else class="w-full">
        <thead>
          <tr class="border-b border-gray-200">
            <th class="text-left pl-5 pr-2 py-3.5 text-[11px] font-bold text-gray-400 uppercase tracking-wider" style="width: 3rem"></th>
            <th class="text-left px-3 py-3.5 text-[11px] font-bold text-gray-400 uppercase tracking-wider">Titre</th>
            <th class="text-left px-3 py-3.5 text-[11px] font-bold text-gray-400 uppercase tracking-wider">Plateforme</th>
            <th class="text-left px-3 py-3.5 text-[11px] font-bold text-gray-400 uppercase tracking-wider">Type</th>
            <th class="text-left px-3 py-3.5 text-[11px] font-bold text-gray-400 uppercase tracking-wider">Catégorie</th>
            <th class="text-left px-3 py-3.5 text-[11px] font-bold text-gray-400 uppercase tracking-wider">Publié</th>
            <th class="text-left px-3 py-3.5 text-[11px] font-bold text-gray-400 uppercase tracking-wider">État</th>
            <th class="text-right pr-5 py-3.5 text-[11px] font-bold text-gray-400 uppercase tracking-wider">Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="m in filteredItems"
            :key="m.id"
            class="border-b border-gray-100 last:border-0 hover:bg-gray-50/50 transition-colors group"
          >
            <td class="pl-5 pr-2 py-3">
              <div class="w-9 h-9 rounded-lg flex items-center justify-center" :class="platformBg(m.platform)">
                <component :is="platformIcon(m.platform)" :size="16" :class="platformColor(m.platform)" />
              </div>
            </td>
            <td class="px-3 py-3">
              <p class="text-sm font-semibold text-gray-900 truncate max-w-[18rem]">{{ m.title }}</p>
              <p v-if="m.description" class="text-[11px] text-gray-400 truncate max-w-[18rem] mt-0.5">{{ m.description }}</p>
            </td>
            <td class="px-3 py-3">
              <span class="text-xs font-semibold capitalize" :class="platformColor(m.platform)">{{ m.platform }}</span>
            </td>
            <td class="px-3 py-3">
              <Tag
                :value="m.embed_type === 'video' ? 'Vidéo' : 'Post'"
                :severity="m.embed_type === 'video' ? 'info' : 'secondary'"
                class="!text-[10px] !font-bold !uppercase !tracking-wider !px-2 !py-0.5"
              />
            </td>
            <td class="px-3 py-3">
              <span class="text-xs text-gray-500">{{ m.category || '—' }}</span>
            </td>
            <td class="px-3 py-3">
              <span class="text-xs text-gray-500">{{ formatDate(m.published_at) }}</span>
            </td>
            <td class="px-3 py-3">
              <div class="flex items-center gap-2">
                <button
                  @click="toggleFeatured(m)"
                  class="p-1 rounded transition-colors cursor-pointer bg-transparent border-none"
                  :class="m.is_featured ? 'text-amber-500 hover:text-amber-600' : 'text-gray-300 hover:text-amber-400'"
                  :title="m.is_featured ? 'Retirer de la mise en avant' : 'Mettre en avant'"
                >
                  <Star v-if="m.is_featured" :size="14" fill="currentColor" />
                  <StarOff v-else :size="14" />
                </button>
                <button
                  @click="toggleActive(m)"
                  class="p-1 rounded transition-colors cursor-pointer bg-transparent border-none"
                  :class="m.is_active ? 'text-green-500 hover:text-green-600' : 'text-gray-300 hover:text-red-400'"
                  :title="m.is_active ? 'Masquer' : 'Rendre visible'"
                >
                  <Eye v-if="m.is_active" :size="14" />
                  <EyeOff v-else :size="14" />
                </button>
              </div>
            </td>
            <td class="pr-5 py-3">
              <div class="flex items-center justify-end gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                <a
                  :href="m.source_url"
                  target="_blank"
                  rel="noopener"
                  class="p-2 rounded-lg hover:bg-gray-100 text-gray-400 hover:text-gray-600 transition-all"
                  title="Ouvrir le lien"
                >
                  <ExternalLink :size="15" />
                </a>
                <button
                  @click="openEdit(m)"
                  class="p-2 rounded-lg hover:bg-blue-50 text-gray-400 hover:text-blue-600 transition-all cursor-pointer bg-transparent border-none"
                  title="Modifier"
                >
                  <Edit3 :size="15" />
                </button>
                <button
                  @click="confirmDelete(m)"
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
          <div class="flex items-center gap-3 mb-3">
            <div class="w-10 h-10 rounded-lg bg-gray-100" />
            <div class="flex-1 space-y-2">
              <div class="h-3.5 bg-gray-100 rounded w-40" />
              <div class="h-3 bg-gray-100 rounded w-24" />
            </div>
          </div>
        </div>
      </template>

      <div v-else-if="filteredItems.length === 0" class="bg-white rounded-xl border border-gray-200 py-16 text-center">
        <Tv :size="40" class="mx-auto mb-3 text-gray-300" />
        <p class="text-sm font-medium text-gray-500">Aucun média trouvé</p>
      </div>

      <template v-else>
        <div
          v-for="m in filteredItems"
          :key="m.id"
          class="bg-white rounded-xl border border-gray-200 overflow-hidden"
        >
          <div class="p-4">
            <div class="flex items-start gap-3">
              <div class="w-10 h-10 rounded-lg flex items-center justify-center shrink-0" :class="platformBg(m.platform)">
                <component :is="platformIcon(m.platform)" :size="18" :class="platformColor(m.platform)" />
              </div>
              <div class="flex-1 min-w-0">
                <div class="flex items-start justify-between gap-2">
                  <h3 class="text-sm font-bold text-gray-900 leading-snug line-clamp-2">{{ m.title }}</h3>
                  <div class="flex items-center gap-1 shrink-0">
                    <button
                      @click="toggleFeatured(m)"
                      class="p-1 cursor-pointer bg-transparent border-none"
                      :class="m.is_featured ? 'text-amber-500' : 'text-gray-300'"
                    >
                      <Star v-if="m.is_featured" :size="14" fill="currentColor" />
                      <StarOff v-else :size="14" />
                    </button>
                    <button
                      @click="toggleActive(m)"
                      class="p-1 cursor-pointer bg-transparent border-none"
                      :class="m.is_active ? 'text-green-500' : 'text-gray-300'"
                    >
                      <Eye v-if="m.is_active" :size="14" />
                      <EyeOff v-else :size="14" />
                    </button>
                  </div>
                </div>
                <div class="flex flex-wrap items-center gap-2 mt-1.5">
                  <Tag
                    :value="m.embed_type === 'video' ? 'Vidéo' : 'Post'"
                    :severity="m.embed_type === 'video' ? 'info' : 'secondary'"
                    class="!text-[9px] !font-bold !uppercase !tracking-wider !px-2 !py-0.5"
                  />
                  <span v-if="m.category" class="text-[11px] text-gray-400">{{ m.category }}</span>
                  <span class="text-[11px] text-gray-400">{{ formatDate(m.published_at) }}</span>
                </div>
              </div>
            </div>
          </div>

          <div class="flex items-center border-t border-gray-100 divide-x divide-gray-100">
            <a
              :href="m.source_url"
              target="_blank"
              rel="noopener"
              class="flex-1 flex items-center justify-center gap-1.5 py-2.5 text-[11px] font-semibold text-gray-500 hover:text-gray-700 hover:bg-gray-50 transition-all no-underline"
            >
              <ExternalLink :size="13" />
              Ouvrir
            </a>
            <button
              @click="openEdit(m)"
              class="flex-1 flex items-center justify-center gap-1.5 py-2.5 text-[11px] font-semibold text-gray-500 hover:text-blue-600 hover:bg-blue-50/50 transition-all cursor-pointer bg-transparent border-none"
            >
              <Edit3 :size="13" />
              Modifier
            </button>
            <button
              @click="confirmDelete(m)"
              class="flex-1 flex items-center justify-center gap-1.5 py-2.5 text-[11px] font-semibold text-gray-500 hover:text-red-600 hover:bg-red-50/50 transition-all cursor-pointer bg-transparent border-none"
            >
              <Trash2 :size="13" />
              Supprimer
            </button>
          </div>
        </div>
      </template>
    </div>

    <!-- ═══ Create / Edit Dialog ═══ -->
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
          v-if="dialogOpen"
          class="fixed inset-0 z-50 flex items-end sm:items-center justify-center p-0 sm:p-4 bg-black/40 backdrop-blur-sm"
          @click.self="dialogOpen = false"
        >
          <div class="bg-white w-full sm:rounded-2xl sm:max-w-lg sm:w-full shadow-xl rounded-t-2xl max-h-[90vh] overflow-y-auto">
            <div class="flex items-center justify-between p-5 pb-0">
              <h3 class="font-heading text-base font-bold text-[var(--color-primary)]">
                {{ dialogMode === 'create' ? 'Ajouter un média' : 'Modifier le média' }}
              </h3>
              <button
                @click="dialogOpen = false"
                class="p-1.5 rounded-lg hover:bg-gray-100 transition-colors cursor-pointer bg-transparent border-none"
              >
                <X :size="18" />
              </button>
            </div>

            <form @submit.prevent="saveMedia" class="p-5 space-y-4">
              <div>
                <label class="block text-[11px] font-semibold text-gray-500 uppercase tracking-wide mb-1.5">
                  URL source <span class="text-red-400">*</span>
                </label>
                <input
                  v-model="form.source_url"
                  type="url"
                  placeholder="https://www.facebook.com/... ou https://youtube.com/..."
                  class="w-full px-3.5 py-2.5 text-sm border border-gray-200 rounded-lg bg-gray-50 focus:bg-white focus:ring-2 focus:ring-[var(--color-accent)]/20 focus:border-[var(--color-accent)] outline-none transition-all"
                  required
                />
                <p class="text-[10px] text-gray-400 mt-1">La plateforme et le type seront détectés automatiquement.</p>
              </div>

              <div>
                <label class="block text-[11px] font-semibold text-gray-500 uppercase tracking-wide mb-1.5">
                  Titre <span class="text-red-400">*</span>
                </label>
                <input
                  v-model="form.title"
                  type="text"
                  placeholder="Ex: Meeting du FPP à Yopougon"
                  class="w-full px-3.5 py-2.5 text-sm border border-gray-200 rounded-lg bg-gray-50 focus:bg-white focus:ring-2 focus:ring-[var(--color-accent)]/20 focus:border-[var(--color-accent)] outline-none transition-all"
                  required
                />
              </div>

              <div>
                <label class="block text-[11px] font-semibold text-gray-500 uppercase tracking-wide mb-1.5">
                  Description
                </label>
                <textarea
                  v-model="form.description"
                  rows="2"
                  placeholder="Brève description du contenu..."
                  class="w-full px-3.5 py-2.5 text-sm border border-gray-200 rounded-lg bg-gray-50 focus:bg-white focus:ring-2 focus:ring-[var(--color-accent)]/20 focus:border-[var(--color-accent)] outline-none transition-all resize-none"
                />
              </div>

              <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label class="block text-[11px] font-semibold text-gray-500 uppercase tracking-wide mb-1.5">Catégorie</label>
                  <input
                    v-model="form.category"
                    type="text"
                    placeholder="Ex: Meetings, Interviews"
                    class="w-full px-3.5 py-2.5 text-sm border border-gray-200 rounded-lg bg-gray-50 focus:bg-white focus:ring-2 focus:ring-[var(--color-accent)]/20 focus:border-[var(--color-accent)] outline-none transition-all"
                  />
                </div>
                <div>
                  <label class="block text-[11px] font-semibold text-gray-500 uppercase tracking-wide mb-1.5">Date de publication</label>
                  <input
                    v-model="form.published_at"
                    type="date"
                    class="w-full px-3.5 py-2.5 text-sm border border-gray-200 rounded-lg bg-gray-50 focus:bg-white focus:ring-2 focus:ring-[var(--color-accent)]/20 focus:border-[var(--color-accent)] outline-none transition-all"
                  />
                </div>
              </div>

              <div class="flex flex-wrap items-center gap-4 pt-1">
                <label class="inline-flex items-center gap-2 cursor-pointer">
                  <input v-model="form.is_featured" type="checkbox" class="w-4 h-4 rounded accent-[var(--color-accent)]" />
                  <span class="text-sm text-gray-700">Mettre en avant</span>
                </label>
                <label class="inline-flex items-center gap-2 cursor-pointer">
                  <input v-model="form.is_active" type="checkbox" class="w-4 h-4 rounded accent-[var(--color-accent)]" />
                  <span class="text-sm text-gray-700">Visible sur le site</span>
                </label>
              </div>

              <div class="flex items-center justify-end gap-3 pt-2">
                <button
                  type="button"
                  @click="dialogOpen = false"
                  class="px-4 py-2.5 text-sm font-medium text-gray-500 hover:text-gray-700 transition-colors cursor-pointer bg-transparent border-none"
                >
                  Annuler
                </button>
                <button
                  type="submit"
                  :disabled="saving"
                  class="inline-flex items-center gap-2 px-5 py-2.5 text-sm font-semibold text-white bg-[var(--color-accent)] rounded-lg hover:bg-[var(--color-accent-hover)] transition-colors cursor-pointer disabled:opacity-40 disabled:cursor-not-allowed"
                >
                  <Loader2 v-if="saving" :size="14" class="animate-spin" />
                  {{ dialogMode === 'create' ? 'Ajouter' : 'Enregistrer' }}
                </button>
              </div>
            </form>
          </div>
        </div>
      </Transition>
    </Teleport>

    <!-- ═══ Delete Confirmation ═══ -->
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
            <h3 class="font-heading text-base font-bold text-gray-900 mb-2">Supprimer ce média ?</h3>
            <p class="text-sm text-gray-500 mb-5">
              <strong>« {{ deleteTarget?.title }} »</strong> sera définitivement supprimé. Cette action est irréversible.
            </p>
            <div class="flex items-center justify-end gap-3">
              <button
                @click="deleteOpen = false"
                class="px-4 py-2.5 text-sm font-medium text-gray-500 hover:text-gray-700 cursor-pointer bg-transparent border-none"
              >
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
  </div>
</template>
