<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useAppToast } from '@/composables/useToast'
import api from '@/api'
import type { AdminContactListItem, AdminContactDetail, PaginatedResponse } from '@/types'
import dayjs from 'dayjs'
import relativeTime from 'dayjs/plugin/relativeTime'
import 'dayjs/locale/fr'

import Tag from 'primevue/tag'

import {
  Mail,
  MailOpen,
  Search,
  SlidersHorizontal,
  X,
  Download,
  Loader2,
  RotateCcw,
  ChevronLeft,
  ChevronRight,
  ChevronsLeft,
  ChevronsRight,
  Eye,
  Clock,
  User,
  Phone,
  AtSign,
  MessageSquare,
  ArrowLeft,
  MailCheck,
  MailX,
  Inbox,
} from 'lucide-vue-next'

dayjs.extend(relativeTime)
dayjs.locale('fr')

const authStore = useAuthStore()
const toast = useAppToast()

const canExport = computed(() => authStore.hasPermission('can_export_contacts'))

/* ── Data ── */
const messages = ref<AdminContactListItem[]>([])
const loading = ref(true)
const totalCount = ref(0)
const currentPage = ref(1)
const pageSize = ref(20)

/* ── Filters ── */
const searchQuery = ref('')
const filterRead = ref<string | null>(null)
const showFilters = ref(false)
const sortField = ref('created_at')
const sortOrder = ref(-1)

const readOptions = [
  { label: 'Tous', value: null },
  { label: 'Non lus', value: 'false' },
  { label: 'Lus', value: 'true' },
]

const totalPages = computed(() => Math.ceil(totalCount.value / pageSize.value))
const hasActiveFilters = computed(() => !!filterRead.value)

/* ── Stats ── */
const unreadCount = computed(() => messages.value.filter(m => !m.is_read).length)

/* ── Detail drawer ── */
const drawerOpen = ref(false)
const drawerMessage = ref<AdminContactDetail | null>(null)
const drawerLoading = ref(false)
const togglingRead = ref(false)

/* ── Export ── */
const exporting = ref(false)

/* ── Data fetching ── */
async function fetchMessages() {
  loading.value = true
  try {
    const params: Record<string, unknown> = {
      page: currentPage.value,
      page_size: pageSize.value,
      ordering: `${sortOrder.value === -1 ? '-' : ''}${sortField.value}`,
    }
    if (searchQuery.value.trim()) params.search = searchQuery.value.trim()
    if (filterRead.value) params.is_read = filterRead.value
    const { data } = await api.get<PaginatedResponse<AdminContactListItem>>('/admin/contacts/', { params })
    messages.value = data.results
    totalCount.value = data.count
  } catch {
    toast.error('Erreur', 'Impossible de charger les messages.')
  } finally {
    loading.value = false
  }
}

async function openMessage(msg: AdminContactListItem) {
  drawerOpen.value = true
  drawerLoading.value = true
  try {
    const { data } = await api.get<AdminContactDetail>(`/admin/contacts/${msg.id}/`)
    drawerMessage.value = data
    if (!msg.is_read) {
      msg.is_read = true
    }
  } catch {
    toast.error('Erreur', 'Impossible de charger le message.')
    drawerOpen.value = false
  } finally {
    drawerLoading.value = false
  }
}

async function toggleRead() {
  if (!drawerMessage.value) return
  togglingRead.value = true
  try {
    const newState = !drawerMessage.value.is_read
    const { data } = await api.patch<AdminContactDetail>(`/admin/contacts/${drawerMessage.value.id}/`, {
      is_read: newState,
    })
    drawerMessage.value = data
    const listItem = messages.value.find(m => m.id === data.id)
    if (listItem) listItem.is_read = data.is_read
  } catch {
    toast.error('Erreur', 'Impossible de modifier le statut.')
  } finally {
    togglingRead.value = false
  }
}

async function exportContacts() {
  exporting.value = true
  try {
    const params: Record<string, string> = {}
    if (filterRead.value) params.is_read = filterRead.value
    const response = await api.get('/admin/contacts/export/', { params, responseType: 'blob' })
    const url = URL.createObjectURL(response.data)
    const a = document.createElement('a')
    a.href = url
    a.download = 'contacts_fpp.csv'
    a.click()
    URL.revokeObjectURL(url)
    toast.success('Export réussi', 'Fichier CSV téléchargé.')
  } catch {
    toast.error('Erreur', "L'export a échoué.")
  } finally {
    exporting.value = false
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
  fetchMessages()
}

function goToPage(page: number) {
  if (page < 1 || page > totalPages.value) return
  currentPage.value = page
  fetchMessages()
}

function clearFilters() {
  filterRead.value = null
  searchQuery.value = ''
  currentPage.value = 1
  fetchMessages()
}

let searchTimeout: ReturnType<typeof setTimeout> | null = null
watch(searchQuery, () => {
  if (searchTimeout) clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => {
    currentPage.value = 1
    fetchMessages()
  }, 400)
})

watch(filterRead, () => {
  currentPage.value = 1
  fetchMessages()
})

onMounted(fetchMessages)

/* ── Helpers ── */
function formatDate(d: string) {
  return dayjs(d).format('DD MMM YYYY [à] HH:mm')
}

function formatRelative(d: string) {
  return dayjs(d).fromNow()
}

function sortIcon(field: string) {
  if (sortField.value !== field) return ''
  return sortOrder.value === -1 ? '↓' : '↑'
}

function subjectTruncated(s: string, max = 50) {
  return s.length > max ? s.slice(0, max) + '…' : s
}
</script>

<template>
  <div class="max-w-[1400px]">
    <!-- Header -->
    <div class="mb-5 sm:mb-6">
      <h2 class="font-heading text-xl sm:text-2xl font-bold text-[var(--color-primary)]">
        Messages de contact
      </h2>
      <p class="text-xs sm:text-sm text-[var(--color-muted)] mt-0.5">
        Consultez et gérez les messages envoyés via le formulaire de contact.
      </p>
    </div>

    <!-- ═══ KPI Stats ═══ -->
    <div class="grid grid-cols-3 gap-3 mb-5 sm:mb-6">
      <div class="bg-white rounded-xl border border-gray-200 p-3 sm:p-4">
        <div class="flex items-center gap-2 mb-1.5">
          <div class="w-8 h-8 rounded-lg bg-blue-50 flex items-center justify-center">
            <Inbox :size="15" class="text-blue-600" />
          </div>
          <span class="text-[10px] sm:text-xs font-semibold text-gray-500 uppercase tracking-wide leading-tight">Total</span>
        </div>
        <p class="text-xl sm:text-2xl font-bold text-gray-900">{{ totalCount }}</p>
      </div>
      <div class="bg-white rounded-xl border border-gray-200 p-3 sm:p-4">
        <div class="flex items-center gap-2 mb-1.5">
          <div class="w-8 h-8 rounded-lg flex items-center justify-center"
            :class="unreadCount > 0 ? 'bg-red-50' : 'bg-gray-50'"
          >
            <Mail :size="15" :class="unreadCount > 0 ? 'text-red-600' : 'text-gray-400'" />
          </div>
          <span class="text-[10px] sm:text-xs font-semibold text-gray-500 uppercase tracking-wide leading-tight">Non lus</span>
        </div>
        <p class="text-xl sm:text-2xl font-bold" :class="unreadCount > 0 ? 'text-red-600' : 'text-gray-900'">{{ unreadCount }}</p>
      </div>
      <div class="bg-white rounded-xl border border-gray-200 p-3 sm:p-4">
        <div class="flex items-center gap-2 mb-1.5">
          <div class="w-8 h-8 rounded-lg bg-green-50 flex items-center justify-center">
            <MailOpen :size="15" class="text-green-600" />
          </div>
          <span class="text-[10px] sm:text-xs font-semibold text-gray-500 uppercase tracking-wide leading-tight">Lus</span>
        </div>
        <p class="text-xl sm:text-2xl font-bold text-gray-900">{{ messages.filter(m => m.is_read).length }}</p>
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
              placeholder="Rechercher par nom, email, sujet..."
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
            <button
              v-if="canExport"
              @click="exportContacts"
              :disabled="exporting"
              class="inline-flex items-center gap-1.5 px-3 py-2.5 text-sm font-medium rounded-lg border border-gray-200 bg-white text-gray-500 hover:border-gray-300 hover:text-gray-700 transition-all cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <Loader2 v-if="exporting" :size="14" class="animate-spin" />
              <Download v-else :size="14" />
              <span class="hidden sm:inline">CSV</span>
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
              v-for="opt in readOptions"
              :key="String(opt.value)"
              @click="filterRead = opt.value"
              class="px-3 py-1.5 text-xs font-semibold rounded-lg border transition-all cursor-pointer"
              :class="filterRead === opt.value
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
        <span class="font-semibold text-gray-900">{{ totalCount }}</span> message{{ totalCount > 1 ? 's' : '' }}
        <template v-if="hasActiveFilters || searchQuery.trim()"> — filtres actifs</template>
      </div>
    </div>

    <!-- ═══ Desktop Table (lg+) ═══ -->
    <div class="hidden lg:block bg-white rounded-xl border border-gray-200 overflow-hidden mb-4">
      <div v-if="loading" class="p-8">
        <div v-for="i in 6" :key="i" class="flex items-center gap-4 py-4 border-b border-gray-100 last:border-0 animate-pulse">
          <div class="w-3 h-3 rounded-full bg-gray-100" />
          <div class="flex-1 space-y-2">
            <div class="h-3.5 bg-gray-100 rounded w-40" />
            <div class="h-3 bg-gray-100 rounded w-64" />
          </div>
          <div class="h-3 bg-gray-100 rounded w-24" />
        </div>
      </div>

      <div v-else-if="messages.length === 0" class="py-16 text-center">
        <Inbox :size="44" class="mx-auto mb-3 text-gray-300" />
        <p class="text-sm font-medium text-gray-500">Aucun message trouvé</p>
        <p class="text-xs text-gray-400 mt-1">Modifiez vos filtres ou votre recherche.</p>
      </div>

      <table v-else class="w-full">
        <thead>
          <tr class="border-b border-gray-200">
            <th class="text-left pl-5 pr-1 py-3.5 text-[11px] font-bold text-gray-400 uppercase tracking-wider" style="width: 2rem"></th>
            <th class="text-left px-3 py-3.5 text-[11px] font-bold text-gray-400 uppercase tracking-wider">
              <button @click="toggleSort('name')" class="inline-flex items-center gap-1 cursor-pointer bg-transparent border-none p-0 text-[11px] font-bold text-gray-400 uppercase tracking-wider hover:text-gray-700 transition-colors">
                Expéditeur {{ sortIcon('name') }}
              </button>
            </th>
            <th class="text-left px-3 py-3.5 text-[11px] font-bold text-gray-400 uppercase tracking-wider">Sujet</th>
            <th class="text-left px-3 py-3.5 text-[11px] font-bold text-gray-400 uppercase tracking-wider">Email</th>
            <th class="text-left px-3 py-3.5 text-[11px] font-bold text-gray-400 uppercase tracking-wider">Statut</th>
            <th class="text-left px-3 py-3.5 text-[11px] font-bold text-gray-400 uppercase tracking-wider">
              <button @click="toggleSort('created_at')" class="inline-flex items-center gap-1 cursor-pointer bg-transparent border-none p-0 text-[11px] font-bold text-gray-400 uppercase tracking-wider hover:text-gray-700 transition-colors">
                Date {{ sortIcon('created_at') }}
              </button>
            </th>
            <th class="text-right pr-5 py-3.5 text-[11px] font-bold text-gray-400 uppercase tracking-wider">Action</th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="msg in messages"
            :key="msg.id"
            class="border-b border-gray-100 last:border-0 hover:bg-gray-50/50 transition-colors group cursor-pointer"
            :class="{ 'bg-blue-50/30': !msg.is_read }"
            @click="openMessage(msg)"
          >
            <td class="pl-5 pr-1 py-3.5">
              <div
                class="w-2.5 h-2.5 rounded-full shrink-0 transition-colors"
                :class="msg.is_read ? 'bg-transparent' : 'bg-[var(--color-accent)]'"
              />
            </td>
            <td class="px-3 py-3.5">
              <span class="text-sm text-gray-900" :class="{ 'font-bold': !msg.is_read }">
                {{ msg.name }}
              </span>
            </td>
            <td class="px-3 py-3.5">
              <span class="text-sm text-gray-700 truncate block max-w-[20rem]" :class="{ 'font-semibold': !msg.is_read }">
                {{ msg.subject }}
              </span>
            </td>
            <td class="px-3 py-3.5">
              <span class="text-xs text-gray-500 truncate block max-w-[14rem]">{{ msg.email }}</span>
            </td>
            <td class="px-3 py-3.5">
              <Tag
                :value="msg.is_read ? 'Lu' : 'Non lu'"
                :severity="msg.is_read ? 'secondary' : 'warn'"
                class="!text-[10px] !font-bold !uppercase !tracking-wider !px-2 !py-0.5"
              />
            </td>
            <td class="px-3 py-3.5">
              <span class="text-xs text-gray-500" :title="formatDate(msg.created_at)">
                {{ formatRelative(msg.created_at) }}
              </span>
            </td>
            <td class="pr-5 py-3.5">
              <div class="flex items-center justify-end opacity-0 group-hover:opacity-100 transition-opacity">
                <button
                  @click.stop="openMessage(msg)"
                  class="p-2 rounded-lg hover:bg-[var(--color-accent-light)] text-gray-400 hover:text-[var(--color-accent)] transition-all cursor-pointer bg-transparent border-none"
                  title="Lire le message"
                >
                  <Eye :size="15" />
                </button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- ═══ Mobile Cards (< lg) ═══ -->
    <div class="lg:hidden space-y-2 mb-4">
      <template v-if="loading">
        <div v-for="i in 4" :key="i" class="bg-white rounded-xl border border-gray-200 p-4 animate-pulse">
          <div class="flex items-start gap-3">
            <div class="w-2.5 h-2.5 rounded-full bg-gray-100 mt-1.5 shrink-0" />
            <div class="flex-1 space-y-2">
              <div class="h-3.5 bg-gray-100 rounded w-32" />
              <div class="h-3 bg-gray-100 rounded w-full" />
              <div class="h-3 bg-gray-100 rounded w-20" />
            </div>
          </div>
        </div>
      </template>

      <div v-else-if="messages.length === 0" class="bg-white rounded-xl border border-gray-200 py-16 text-center">
        <Inbox :size="40" class="mx-auto mb-3 text-gray-300" />
        <p class="text-sm font-medium text-gray-500">Aucun message trouvé</p>
      </div>

      <template v-else>
        <button
          v-for="msg in messages"
          :key="msg.id"
          class="w-full text-left bg-white rounded-xl border border-gray-200 p-4 transition-all hover:shadow-sm cursor-pointer"
          :class="{ 'border-l-4 border-l-[var(--color-accent)]': !msg.is_read }"
          @click="openMessage(msg)"
        >
          <div class="flex items-start gap-3">
            <div
              class="w-2.5 h-2.5 rounded-full mt-1.5 shrink-0"
              :class="msg.is_read ? 'bg-gray-200' : 'bg-[var(--color-accent)]'"
            />
            <div class="flex-1 min-w-0">
              <div class="flex items-center justify-between gap-2">
                <span class="text-sm text-gray-900 truncate" :class="{ 'font-bold': !msg.is_read }">
                  {{ msg.name }}
                </span>
                <span class="text-[10px] text-gray-400 shrink-0">{{ formatRelative(msg.created_at) }}</span>
              </div>
              <p class="text-sm text-gray-700 mt-0.5 truncate" :class="{ 'font-semibold': !msg.is_read }">
                {{ msg.subject }}
              </p>
              <p class="text-xs text-gray-400 mt-1 truncate">{{ msg.email }}</p>
            </div>
          </div>
        </button>
      </template>
    </div>

    <!-- ═══ Pagination ═══ -->
    <div
      v-if="totalPages > 1 && !loading"
      class="flex items-center justify-between sm:justify-center gap-2 sm:gap-1"
    >
      <div class="flex items-center gap-1">
        <button
          @click="goToPage(1)"
          :disabled="currentPage <= 1"
          class="p-2 rounded-lg hover:bg-gray-100 text-gray-500 transition-colors cursor-pointer bg-transparent border-none disabled:opacity-30 disabled:cursor-not-allowed"
        >
          <ChevronsLeft :size="16" />
        </button>
        <button
          @click="goToPage(currentPage - 1)"
          :disabled="currentPage <= 1"
          class="p-2 rounded-lg hover:bg-gray-100 text-gray-500 transition-colors cursor-pointer bg-transparent border-none disabled:opacity-30 disabled:cursor-not-allowed"
        >
          <ChevronLeft :size="16" />
        </button>
      </div>
      <span class="text-xs font-medium text-gray-500 px-3 tabular-nums">
        Page <span class="font-bold text-gray-900">{{ currentPage }}</span> sur {{ totalPages }}
      </span>
      <div class="flex items-center gap-1">
        <button
          @click="goToPage(currentPage + 1)"
          :disabled="currentPage >= totalPages"
          class="p-2 rounded-lg hover:bg-gray-100 text-gray-500 transition-colors cursor-pointer bg-transparent border-none disabled:opacity-30 disabled:cursor-not-allowed"
        >
          <ChevronRight :size="16" />
        </button>
        <button
          @click="goToPage(totalPages)"
          :disabled="currentPage >= totalPages"
          class="p-2 rounded-lg hover:bg-gray-100 text-gray-500 transition-colors cursor-pointer bg-transparent border-none disabled:opacity-30 disabled:cursor-not-allowed"
        >
          <ChevronsRight :size="16" />
        </button>
      </div>
    </div>

    <!-- ═══ Message Detail Drawer ═══ -->
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
          v-if="drawerOpen"
          class="fixed inset-0 z-50 bg-black/40 backdrop-blur-sm"
          @click.self="drawerOpen = false"
        >
          <!-- Drawer panel -->
          <Transition
            enter-active-class="transition-transform duration-250 ease-out"
            enter-from-class="translate-x-full"
            enter-to-class="translate-x-0"
            leave-active-class="transition-transform duration-200 ease-in"
            leave-from-class="translate-x-0"
            leave-to-class="translate-x-full"
            appear
          >
            <aside
              v-if="drawerOpen"
              class="fixed inset-y-0 right-0 w-full sm:w-[28rem] md:w-[32rem] bg-white shadow-xl flex flex-col z-50"
            >
              <!-- Drawer header -->
              <div class="flex items-center justify-between px-4 sm:px-6 py-4 border-b border-gray-200 shrink-0">
                <button
                  @click="drawerOpen = false"
                  class="inline-flex items-center gap-1.5 text-sm font-medium text-gray-500 hover:text-gray-700 transition-colors cursor-pointer bg-transparent border-none"
                >
                  <ArrowLeft :size="16" />
                  <span class="sm:hidden">Retour</span>
                </button>
                <div class="flex items-center gap-2">
                  <button
                    v-if="drawerMessage"
                    @click="toggleRead"
                    :disabled="togglingRead"
                    class="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold rounded-lg border transition-all cursor-pointer"
                    :class="drawerMessage.is_read
                      ? 'border-gray-200 text-gray-500 hover:border-amber-300 hover:text-amber-600 hover:bg-amber-50'
                      : 'border-green-200 text-green-600 bg-green-50 hover:bg-green-100'"
                  >
                    <Loader2 v-if="togglingRead" :size="13" class="animate-spin" />
                    <MailCheck v-else-if="drawerMessage.is_read" :size="13" />
                    <MailX v-else :size="13" />
                    {{ drawerMessage.is_read ? 'Marquer non lu' : 'Marquer lu' }}
                  </button>
                  <button
                    @click="drawerOpen = false"
                    class="p-1.5 rounded-lg hover:bg-gray-100 transition-colors cursor-pointer bg-transparent border-none hidden sm:flex"
                  >
                    <X :size="18" />
                  </button>
                </div>
              </div>

              <!-- Drawer body -->
              <div class="flex-1 overflow-y-auto">
                <div v-if="drawerLoading" class="p-6 space-y-4 animate-pulse">
                  <div class="h-5 bg-gray-100 rounded w-3/4" />
                  <div class="h-4 bg-gray-100 rounded w-1/2" />
                  <div class="h-4 bg-gray-100 rounded w-full mt-6" />
                  <div class="h-4 bg-gray-100 rounded w-full" />
                  <div class="h-4 bg-gray-100 rounded w-3/4" />
                </div>

                <div v-else-if="drawerMessage" class="p-4 sm:p-6">
                  <!-- Subject -->
                  <div class="mb-6">
                    <div class="flex items-start justify-between gap-3 mb-2">
                      <h3 class="font-heading text-lg sm:text-xl font-bold text-gray-900 leading-snug">
                        {{ drawerMessage.subject }}
                      </h3>
                      <Tag
                        :value="drawerMessage.is_read ? 'Lu' : 'Non lu'"
                        :severity="drawerMessage.is_read ? 'secondary' : 'warn'"
                        class="!text-[9px] !font-bold !uppercase !tracking-wider !px-2 !py-0.5 shrink-0"
                      />
                    </div>
                    <div class="flex items-center gap-2 text-xs text-gray-400">
                      <Clock :size="12" />
                      <span>{{ formatDate(drawerMessage.created_at) }}</span>
                      <span class="opacity-50">·</span>
                      <span>{{ formatRelative(drawerMessage.created_at) }}</span>
                    </div>
                  </div>

                  <!-- Sender info -->
                  <div class="bg-gray-50 rounded-xl p-4 mb-6 space-y-2.5">
                    <div class="flex items-center gap-3">
                      <div class="w-10 h-10 rounded-full bg-[var(--color-accent-light)] flex items-center justify-center text-sm font-bold text-[var(--color-accent)]">
                        {{ drawerMessage.name.charAt(0).toUpperCase() }}
                      </div>
                      <div>
                        <p class="text-sm font-semibold text-gray-900">{{ drawerMessage.name }}</p>
                        <p class="text-xs text-gray-500">Expéditeur</p>
                      </div>
                    </div>
                    <div class="flex items-center gap-2 text-sm text-gray-600 pl-1">
                      <AtSign :size="14" class="text-gray-400 shrink-0" />
                      <a :href="`mailto:${drawerMessage.email}`" class="hover:text-[var(--color-accent)] transition-colors">
                        {{ drawerMessage.email }}
                      </a>
                    </div>
                    <div v-if="drawerMessage.phone" class="flex items-center gap-2 text-sm text-gray-600 pl-1">
                      <Phone :size="14" class="text-gray-400 shrink-0" />
                      <a :href="`tel:${drawerMessage.phone}`" class="hover:text-[var(--color-accent)] transition-colors">
                        {{ drawerMessage.phone }}
                      </a>
                    </div>
                  </div>

                  <!-- Message body -->
                  <div>
                    <div class="flex items-center gap-2 mb-3">
                      <MessageSquare :size="14" class="text-gray-400" />
                      <span class="text-[11px] font-semibold text-gray-400 uppercase tracking-wide">Message</span>
                    </div>
                    <div class="bg-white border border-gray-200 rounded-xl p-4 sm:p-5">
                      <p class="text-sm text-gray-700 leading-relaxed whitespace-pre-wrap">{{ drawerMessage.message }}</p>
                    </div>
                  </div>

                  <!-- Read info -->
                  <div v-if="drawerMessage.read_at" class="mt-6 text-xs text-gray-400 flex items-center gap-1.5">
                    <MailOpen :size="12" />
                    Lu le {{ formatDate(drawerMessage.read_at) }}
                  </div>
                </div>
              </div>
            </aside>
          </Transition>
        </div>
      </Transition>
    </Teleport>
  </div>
</template>
