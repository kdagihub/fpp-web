<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useAppToast } from '@/composables/useToast'
import api from '@/api'
import { getMediaUrl } from '@/utils/media'
import type { AdminMemberListItem, DashboardData, PaginatedResponse } from '@/types'
import dayjs from 'dayjs'
import 'dayjs/locale/fr'

import Tag from 'primevue/tag'
import Select from 'primevue/select'
import Textarea from 'primevue/textarea'

import {
  Users,
  UserCheck,
  Clock,
  TrendingUp,
  Search,
  SlidersHorizontal,
  X,
  Download,
  FileSpreadsheet,
  Eye,
  ShieldCheck,
  FileDown,
  ChevronLeft,
  ChevronRight,
  ChevronsLeft,
  ChevronsRight,
  Loader2,
  RotateCcw,
} from 'lucide-vue-next'

dayjs.locale('fr')

const router = useRouter()
const authStore = useAuthStore()
const toast = useAppToast()

const canExport = computed(() => authStore.hasPermission('can_export_members'))
const canManage = computed(() => authStore.hasPermission('can_manage_members'))
const canValidate = computed(() => authStore.hasPermission('can_validate_membership'))

/* ── Stats ── */
const stats = ref<DashboardData | null>(null)
const statsLoading = ref(true)

/* ── Members list ── */
const members = ref<AdminMemberListItem[]>([])
const loading = ref(true)
const totalCount = ref(0)
const currentPage = ref(1)
const pageSize = ref(20)

/* ── Filters ── */
const searchQuery = ref('')
const filterStatus = ref<string | null>(null)
const filterSex = ref<string | null>(null)
const filterActive = ref<string | null>(null)
const sortField = ref('created_at')
const sortOrder = ref(-1)
const showFilters = ref(false)

const statusOptions = [
  { label: 'Tous les statuts', value: null },
  { label: 'En attente', value: 'pending' },
  { label: 'Validé', value: 'validated' },
  { label: 'Suspendu', value: 'suspended' },
  { label: 'Rejeté', value: 'rejected' },
]
const sexOptions = [
  { label: 'Tous', value: null },
  { label: 'Homme', value: 'M' },
  { label: 'Femme', value: 'F' },
]
const activeOptions = [
  { label: 'Tous', value: null },
  { label: 'Actif', value: 'true' },
  { label: 'Inactif', value: 'false' },
]

const totalPages = computed(() => Math.ceil(totalCount.value / pageSize.value))
const hasActiveFilters = computed(
  () => !!filterStatus.value || !!filterSex.value || !!filterActive.value,
)
const filterCount = computed(() => {
  let c = 0
  if (filterStatus.value) c++
  if (filterSex.value) c++
  if (filterActive.value) c++
  return c
})

/* ── Status change dialog (inline) ── */
const statusDialogOpen = ref(false)
const statusTarget = ref<AdminMemberListItem | null>(null)
const statusForm = ref({ status: '', reason: '' })
const statusSaving = ref(false)
const statusChangeOptions = [
  { label: 'Validé', value: 'validated' },
  { label: 'En attente', value: 'pending' },
  { label: 'Suspendu', value: 'suspended' },
  { label: 'Rejeté', value: 'rejected' },
]

function openStatusDialog(m: AdminMemberListItem) {
  statusTarget.value = m
  statusForm.value = { status: m.membership_status, reason: '' }
  statusDialogOpen.value = true
}

async function saveStatus() {
  if (!statusTarget.value) return
  if (statusForm.value.status === statusTarget.value.membership_status) {
    statusDialogOpen.value = false
    return
  }
  statusSaving.value = true
  try {
    await api.patch(`/admin/members/${statusTarget.value.id}/status/`, statusForm.value)
    toast.success('Statut modifié', `${statusTarget.value.first_name} ${statusTarget.value.last_name} est maintenant "${statusLabel(statusForm.value.status)}".`)
    statusDialogOpen.value = false
    await fetchMembers()
    fetchStats()
  } catch (err: any) {
    toast.error('Erreur', err?.response?.data?.detail || 'La modification du statut a échoué.')
  } finally {
    statusSaving.value = false
  }
}

/* ── Export ── */
const exporting = ref<'csv' | 'excel' | null>(null)

async function exportMembers(format: 'csv' | 'excel') {
  exporting.value = format
  try {
    const params: Record<string, string> = { format }
    if (filterStatus.value) params.membership_status = filterStatus.value
    if (filterSex.value) params.sex = filterSex.value
    const response = await api.get('/admin/members/export/', { params, responseType: 'blob' })
    const ext = format === 'excel' ? 'xlsx' : 'csv'
    const url = URL.createObjectURL(response.data)
    const a = document.createElement('a')
    a.href = url
    a.download = `membres_fpp.${ext}`
    a.click()
    URL.revokeObjectURL(url)
    toast.success('Export réussi', `Fichier ${ext.toUpperCase()} téléchargé.`)
  } catch {
    toast.error('Erreur', "L'export a échoué.")
  } finally {
    exporting.value = null
  }
}

/* ── PDF download ── */
const pdfDownloading = ref<string | null>(null)

async function downloadPdf(m: AdminMemberListItem) {
  pdfDownloading.value = m.id
  try {
    const response = await api.get(`/admin/members/${m.id}/pdf/`, { responseType: 'blob' })
    const url = URL.createObjectURL(response.data)
    const a = document.createElement('a')
    a.href = url
    a.download = `Fiche-${m.last_name}-FPP.pdf`
    a.click()
    URL.revokeObjectURL(url)
  } catch {
    toast.error('Erreur', 'Le téléchargement de la fiche a échoué.')
  } finally {
    pdfDownloading.value = null
  }
}

/* ── Data fetching ── */
async function fetchStats() {
  statsLoading.value = true
  try {
    const { data } = await api.get<DashboardData>('/admin/dashboard/')
    stats.value = data
  } catch { /* silent */ } finally {
    statsLoading.value = false
  }
}

async function fetchMembers() {
  loading.value = true
  try {
    const params: Record<string, unknown> = {
      page: currentPage.value,
      page_size: pageSize.value,
      ordering: `${sortOrder.value === -1 ? '-' : ''}${sortField.value}`,
    }
    if (searchQuery.value.trim()) params.search = searchQuery.value.trim()
    if (filterStatus.value) params.membership_status = filterStatus.value
    if (filterSex.value) params.sex = filterSex.value
    if (filterActive.value) params.is_active = filterActive.value
    const { data } = await api.get<PaginatedResponse<AdminMemberListItem>>('/admin/members/', { params })
    members.value = data.results
    totalCount.value = data.count
  } catch {
    toast.error('Erreur', 'Impossible de charger la liste des membres.')
  } finally {
    loading.value = false
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
  fetchMembers()
}

function goToPage(page: number) {
  if (page < 1 || page > totalPages.value) return
  currentPage.value = page
  fetchMembers()
}

function clearFilters() {
  filterStatus.value = null
  filterSex.value = null
  filterActive.value = null
  searchQuery.value = ''
  currentPage.value = 1
  fetchMembers()
}

let searchTimeout: ReturnType<typeof setTimeout> | null = null
watch(searchQuery, () => {
  if (searchTimeout) clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => {
    currentPage.value = 1
    fetchMembers()
  }, 400)
})

watch([filterStatus, filterSex, filterActive], () => {
  currentPage.value = 1
  fetchMembers()
})

onMounted(() => {
  fetchStats()
  fetchMembers()
})

/* ── Helpers ── */
function statusSeverity(s: string): 'success' | 'warn' | 'danger' | 'secondary' | undefined {
  const map: Record<string, 'success' | 'warn' | 'danger' | 'secondary'> = {
    validated: 'success', pending: 'warn', rejected: 'danger', suspended: 'secondary',
  }
  return map[s]
}

function statusLabel(s: string) {
  const map: Record<string, string> = {
    validated: 'Validé', pending: 'En attente', rejected: 'Rejeté', suspended: 'Suspendu',
  }
  return map[s] || s
}

function formatDate(d: string) {
  return dayjs(d).format('DD MMM YYYY')
}

function memberInitials(m: AdminMemberListItem) {
  return `${m.first_name.charAt(0)}${m.last_name.charAt(0)}`.toUpperCase()
}

function sortIcon(field: string) {
  if (sortField.value !== field) return ''
  return sortOrder.value === -1 ? '↓' : '↑'
}
</script>

<template>
  <div class="max-w-[1400px]">
    <!-- Header -->
    <div class="mb-8">
      <h2 class="font-heading text-2xl font-bold text-[var(--color-primary)]">
        Gestion des membres
      </h2>
      <p class="text-sm text-[var(--color-muted)] mt-1">
        Consultez, filtrez et gérez les membres du parti.
      </p>
    </div>

    <!-- ═══ KPI Stats ═══ -->
    <div class="grid grid-cols-2 lg:grid-cols-4 gap-3 sm:gap-4 mb-8">
      <div
        v-for="(stat, i) in [
          { label: 'Membres validés', value: stats?.members.total_validated ?? 0, icon: UserCheck, color: 'text-green-600', bg: 'bg-green-50', ring: 'ring-green-100' },
          { label: 'En attente', value: stats?.members.pending ?? 0, icon: Clock, color: 'text-amber-600', bg: 'bg-amber-50', ring: 'ring-amber-100' },
          { label: 'Nouveaux (30j)', value: stats?.members.recent_30d ?? 0, icon: TrendingUp, color: 'text-blue-600', bg: 'bg-blue-50', ring: 'ring-blue-100' },
          { label: 'Total inscrits', value: totalCount, icon: Users, color: 'text-[var(--color-primary)]', bg: 'bg-[var(--color-surface)]', ring: 'ring-[var(--color-border)]' },
        ]"
        :key="i"
        class="bg-white rounded-xl border border-[var(--color-border)] p-4 sm:p-5 transition-shadow hover:shadow-[var(--shadow-sm)]"
      >
        <template v-if="statsLoading && i < 3">
          <div class="animate-pulse">
            <div class="h-3 bg-[var(--color-surface)] rounded w-24 mb-4" />
            <div class="h-8 bg-[var(--color-surface)] rounded w-16" />
          </div>
        </template>
        <template v-else>
          <div class="flex items-center gap-2.5 mb-3">
            <div class="w-8 h-8 sm:w-9 sm:h-9 rounded-lg flex items-center justify-center ring-1" :class="[stat.bg, stat.ring]">
              <component :is="stat.icon" :size="16" :class="stat.color" />
            </div>
            <span class="text-[11px] font-semibold text-[var(--color-muted)] uppercase tracking-wide leading-tight">
              {{ stat.label }}
            </span>
          </div>
          <p class="text-2xl sm:text-3xl font-bold text-[var(--color-primary)] font-heading tabular-nums">
            {{ stat.value.toLocaleString('fr-FR') }}
          </p>
        </template>
      </div>
    </div>

    <!-- ═══ Toolbar ═══ -->
    <div class="bg-white rounded-xl border border-[var(--color-border)] mb-6 overflow-hidden">
      <div class="p-4 sm:p-5">
        <div class="flex flex-col sm:flex-row gap-3">
          <!-- Search -->
          <div class="flex-1 relative">
            <Search :size="16" class="absolute left-3.5 top-1/2 -translate-y-1/2 text-[var(--color-muted)] opacity-50 pointer-events-none" />
            <input
              v-model="searchQuery"
              type="search"
              placeholder="Rechercher par nom, email, matricule, téléphone..."
              class="w-full pl-10 pr-4 py-2.5 text-sm border border-[var(--color-border)] rounded-lg bg-[var(--color-surface)] focus:bg-white focus:ring-2 focus:ring-[var(--color-accent)]/20 focus:border-[var(--color-accent)] outline-none transition-all placeholder:text-[var(--color-muted)]/50"
              aria-label="Rechercher un membre"
            />
          </div>

          <!-- Actions row -->
          <div class="flex items-center gap-2 shrink-0">
            <button
              @click="showFilters = !showFilters"
              class="inline-flex items-center gap-2 px-3.5 py-2.5 text-sm font-medium rounded-lg border transition-all cursor-pointer"
              :class="hasActiveFilters
                ? 'bg-[var(--color-accent-light)] border-[var(--color-accent)]/30 text-[var(--color-accent)]'
                : 'bg-white border-[var(--color-border)] text-[var(--color-muted)] hover:border-[var(--color-primary)]/20 hover:text-[var(--color-primary)]'"
              :aria-expanded="showFilters"
              aria-controls="filter-panel"
              aria-label="Afficher les filtres"
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

            <template v-if="canExport">
              <button
                @click="exportMembers('csv')"
                :disabled="!!exporting"
                class="inline-flex items-center gap-1.5 px-3 py-2.5 text-sm font-medium rounded-lg border border-[var(--color-border)] bg-white text-[var(--color-muted)] hover:border-[var(--color-primary)]/20 hover:text-[var(--color-primary)] transition-all cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
                aria-label="Exporter en CSV"
              >
                <Loader2 v-if="exporting === 'csv'" :size="14" class="animate-spin" />
                <Download v-else :size="14" />
                <span class="hidden sm:inline">CSV</span>
              </button>
              <button
                @click="exportMembers('excel')"
                :disabled="!!exporting"
                class="inline-flex items-center gap-1.5 px-3 py-2.5 text-sm font-medium rounded-lg border border-[var(--color-border)] bg-white text-[var(--color-muted)] hover:border-[var(--color-primary)]/20 hover:text-[var(--color-primary)] transition-all cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
                aria-label="Exporter en Excel"
              >
                <Loader2 v-if="exporting === 'excel'" :size="14" class="animate-spin" />
                <FileSpreadsheet v-else :size="14" />
                <span class="hidden sm:inline">Excel</span>
              </button>
            </template>
          </div>
        </div>

        <!-- Filter panel -->
        <Transition
          enter-active-class="transition-all duration-200 ease-out"
          enter-from-class="opacity-0 -translate-y-1"
          enter-to-class="opacity-100 translate-y-0"
          leave-active-class="transition-all duration-150 ease-in"
          leave-from-class="opacity-100"
          leave-to-class="opacity-0 -translate-y-1"
        >
          <div
            v-if="showFilters"
            id="filter-panel"
            class="flex flex-col sm:flex-row items-start sm:items-end gap-3 mt-4 pt-4 border-t border-[var(--color-border)]/50"
          >
            <div class="w-full sm:w-auto sm:min-w-[10rem]">
              <label class="block text-[11px] font-semibold text-[var(--color-muted)] uppercase tracking-wide mb-1.5">Statut</label>
              <Select
                v-model="filterStatus"
                :options="statusOptions"
                optionLabel="label"
                optionValue="value"
                placeholder="Tous"
                class="w-full !text-sm"
                aria-label="Filtrer par statut"
              />
            </div>
            <div class="w-full sm:w-auto sm:min-w-[8rem]">
              <label class="block text-[11px] font-semibold text-[var(--color-muted)] uppercase tracking-wide mb-1.5">Sexe</label>
              <Select
                v-model="filterSex"
                :options="sexOptions"
                optionLabel="label"
                optionValue="value"
                placeholder="Tous"
                class="w-full !text-sm"
                aria-label="Filtrer par sexe"
              />
            </div>
            <div class="w-full sm:w-auto sm:min-w-[8rem]">
              <label class="block text-[11px] font-semibold text-[var(--color-muted)] uppercase tracking-wide mb-1.5">Compte</label>
              <Select
                v-model="filterActive"
                :options="activeOptions"
                optionLabel="label"
                optionValue="value"
                placeholder="Tous"
                class="w-full !text-sm"
                aria-label="Filtrer par état du compte"
              />
            </div>
            <button
              v-if="hasActiveFilters"
              @click="clearFilters"
              class="inline-flex items-center gap-1.5 px-3 py-2 text-xs font-semibold text-[var(--color-error)] hover:bg-red-50 rounded-lg transition-colors cursor-pointer shrink-0"
              aria-label="Réinitialiser les filtres"
            >
              <RotateCcw :size="13" />
              Réinitialiser
            </button>
          </div>
        </Transition>
      </div>

      <!-- Result count -->
      <div class="px-4 sm:px-5 py-2.5 bg-[var(--color-surface)]/60 border-t border-[var(--color-border)]/50 text-xs text-[var(--color-muted)]">
        <span class="font-semibold text-[var(--color-primary)]">{{ totalCount }}</span> résultat{{ totalCount > 1 ? 's' : '' }}
        <template v-if="hasActiveFilters || searchQuery.trim()"> — filtres actifs</template>
      </div>
    </div>

    <!-- ═══ Desktop Table (lg+) ═══ -->
    <div class="hidden lg:block bg-white rounded-xl border border-[var(--color-border)] overflow-hidden mb-4">
      <!-- Loading -->
      <div v-if="loading" class="p-8">
        <div v-for="i in 6" :key="i" class="flex items-center gap-4 py-4 border-b border-[var(--color-border)]/30 last:border-0 animate-pulse">
          <div class="w-10 h-10 rounded-full bg-[var(--color-surface)]" />
          <div class="flex-1 space-y-2">
            <div class="h-3.5 bg-[var(--color-surface)] rounded w-40" />
            <div class="h-3 bg-[var(--color-surface)] rounded w-56" />
          </div>
          <div class="h-6 bg-[var(--color-surface)] rounded-full w-20" />
        </div>
      </div>

      <!-- Empty -->
      <div v-else-if="members.length === 0" class="py-16 text-center">
        <Users :size="44" class="mx-auto mb-3 text-[var(--color-muted)] opacity-20" />
        <p class="text-sm font-medium text-[var(--color-muted)]">Aucun membre trouvé</p>
        <p class="text-xs text-[var(--color-muted)] opacity-60 mt-1">Modifiez vos filtres ou votre recherche.</p>
      </div>

      <!-- Table -->
      <table v-else class="w-full" role="table">
        <thead>
          <tr class="border-b border-[var(--color-border)]">
            <th class="text-left pl-5 pr-2 py-3.5 text-[11px] font-bold text-[var(--color-muted)] uppercase tracking-wider" style="width: 3rem"></th>
            <th class="text-left px-3 py-3.5 text-[11px] font-bold text-[var(--color-muted)] uppercase tracking-wider">
              <button @click="toggleSort('last_name')" class="inline-flex items-center gap-1 cursor-pointer bg-transparent border-none p-0 text-[11px] font-bold text-[var(--color-muted)] uppercase tracking-wider hover:text-[var(--color-primary)] transition-colors">
                Nom {{ sortIcon('last_name') }}
              </button>
            </th>
            <th class="text-left px-3 py-3.5 text-[11px] font-bold text-[var(--color-muted)] uppercase tracking-wider">Matricule</th>
            <th class="text-left px-3 py-3.5 text-[11px] font-bold text-[var(--color-muted)] uppercase tracking-wider">Email</th>
            <th class="text-left px-3 py-3.5 text-[11px] font-bold text-[var(--color-muted)] uppercase tracking-wider">
              <button @click="toggleSort('city')" class="inline-flex items-center gap-1 cursor-pointer bg-transparent border-none p-0 text-[11px] font-bold text-[var(--color-muted)] uppercase tracking-wider hover:text-[var(--color-primary)] transition-colors">
                Ville {{ sortIcon('city') }}
              </button>
            </th>
            <th class="text-left px-3 py-3.5 text-[11px] font-bold text-[var(--color-muted)] uppercase tracking-wider">
              <button @click="toggleSort('membership_status')" class="inline-flex items-center gap-1 cursor-pointer bg-transparent border-none p-0 text-[11px] font-bold text-[var(--color-muted)] uppercase tracking-wider hover:text-[var(--color-primary)] transition-colors">
                Statut {{ sortIcon('membership_status') }}
              </button>
            </th>
            <th class="text-left px-3 py-3.5 text-[11px] font-bold text-[var(--color-muted)] uppercase tracking-wider">
              <button @click="toggleSort('created_at')" class="inline-flex items-center gap-1 cursor-pointer bg-transparent border-none p-0 text-[11px] font-bold text-[var(--color-muted)] uppercase tracking-wider hover:text-[var(--color-primary)] transition-colors">
                Inscrit {{ sortIcon('created_at') }}
              </button>
            </th>
            <th class="text-right pr-5 py-3.5 text-[11px] font-bold text-[var(--color-muted)] uppercase tracking-wider">Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="m in members"
            :key="m.id"
            class="border-b border-[var(--color-border)]/40 last:border-0 hover:bg-[var(--color-surface)]/50 transition-colors group"
          >
            <!-- Avatar -->
            <td class="pl-5 pr-2 py-3">
              <div class="w-9 h-9 rounded-full overflow-hidden bg-[var(--color-surface)] flex items-center justify-center text-xs font-bold text-[var(--color-muted)] shrink-0 ring-1 ring-[var(--color-border)]">
                <img
                  v-if="m.photo"
                  :src="getMediaUrl(m.photo)"
                  :alt="`${m.first_name} ${m.last_name}`"
                  class="w-full h-full object-cover"
                  loading="lazy"
                />
                <span v-else>{{ memberInitials(m) }}</span>
              </div>
            </td>

            <!-- Name -->
            <td class="px-3 py-3">
              <button
                class="text-left bg-transparent border-none p-0 cursor-pointer group/name"
                @click="router.push(`/admin/membres/${m.id}`)"
              >
                <span class="text-sm font-semibold text-[var(--color-primary)] group-hover/name:text-[var(--color-accent)] transition-colors">
                  {{ m.last_name }} {{ m.first_name }}
                </span>
                <span v-if="m.phone" class="block text-[11px] text-[var(--color-muted)] mt-0.5">
                  {{ m.phone }}
                </span>
              </button>
            </td>

            <!-- Matricule -->
            <td class="px-3 py-3">
              <span
                class="text-xs font-mono tracking-wide"
                :class="m.matricule ? 'text-[var(--color-accent)] font-semibold' : 'text-[var(--color-muted)] opacity-40'"
              >
                {{ m.matricule || '—' }}
              </span>
            </td>

            <!-- Email -->
            <td class="px-3 py-3">
              <span class="text-sm text-[var(--color-muted)] block max-w-[16rem] truncate">{{ m.email }}</span>
            </td>

            <!-- City -->
            <td class="px-3 py-3">
              <span class="text-sm text-[var(--color-primary)]">{{ m.city }}</span>
            </td>

            <!-- Status -->
            <td class="px-3 py-3">
              <Tag
                :value="statusLabel(m.membership_status)"
                :severity="statusSeverity(m.membership_status)"
                class="!text-[10px] !font-bold !uppercase !tracking-wider !px-2.5 !py-1"
                role="status"
                :aria-label="`Statut: ${statusLabel(m.membership_status)}`"
              />
            </td>

            <!-- Date -->
            <td class="px-3 py-3">
              <span class="text-xs text-[var(--color-muted)]">{{ formatDate(m.created_at) }}</span>
            </td>

            <!-- Actions -->
            <td class="pr-5 py-3">
              <div class="flex items-center justify-end gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                <button
                  @click="router.push(`/admin/membres/${m.id}`)"
                  class="p-2 rounded-lg hover:bg-[var(--color-accent-light)] text-[var(--color-muted)] hover:text-[var(--color-accent)] transition-all cursor-pointer bg-transparent border-none"
                  :aria-label="`Voir ${m.first_name} ${m.last_name}`"
                  title="Voir le détail"
                >
                  <Eye :size="15" />
                </button>
                <button
                  v-if="canValidate"
                  @click.stop="openStatusDialog(m)"
                  class="p-2 rounded-lg hover:bg-blue-50 text-[var(--color-muted)] hover:text-blue-600 transition-all cursor-pointer bg-transparent border-none"
                  :aria-label="`Changer le statut de ${m.first_name} ${m.last_name}`"
                  title="Modifier le statut"
                >
                  <ShieldCheck :size="15" />
                </button>
                <button
                  v-if="canManage"
                  @click.stop="downloadPdf(m)"
                  :disabled="pdfDownloading === m.id"
                  class="p-2 rounded-lg hover:bg-green-50 text-[var(--color-muted)] hover:text-green-600 transition-all cursor-pointer bg-transparent border-none disabled:opacity-40 disabled:cursor-not-allowed"
                  :aria-label="`Télécharger la fiche de ${m.first_name} ${m.last_name}`"
                  title="Télécharger la fiche PDF"
                >
                  <Loader2 v-if="pdfDownloading === m.id" :size="15" class="animate-spin" />
                  <FileDown v-else :size="15" />
                </button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- ═══ Mobile Cards (< lg) ═══ -->
    <div class="lg:hidden space-y-3 mb-4">
      <!-- Loading -->
      <template v-if="loading">
        <div v-for="i in 4" :key="i" class="bg-white rounded-xl border border-[var(--color-border)] p-4 animate-pulse">
          <div class="flex items-center gap-3 mb-4">
            <div class="w-11 h-11 rounded-full bg-[var(--color-surface)]" />
            <div class="flex-1 space-y-2">
              <div class="h-3.5 bg-[var(--color-surface)] rounded w-32" />
              <div class="h-3 bg-[var(--color-surface)] rounded w-48" />
            </div>
          </div>
          <div class="h-8 bg-[var(--color-surface)] rounded w-full" />
        </div>
      </template>

      <!-- Empty -->
      <div v-else-if="members.length === 0" class="bg-white rounded-xl border border-[var(--color-border)] py-16 text-center">
        <Users :size="40" class="mx-auto mb-3 text-[var(--color-muted)] opacity-20" />
        <p class="text-sm font-medium text-[var(--color-muted)]">Aucun membre trouvé</p>
      </div>

      <!-- Cards -->
      <template v-else>
        <div
          v-for="m in members"
          :key="m.id"
          class="bg-white rounded-xl border border-[var(--color-border)] overflow-hidden transition-all hover:shadow-[var(--shadow-sm)]"
        >
          <!-- Card header (clickable) -->
          <button
            class="w-full p-4 pb-3 text-left bg-transparent border-none cursor-pointer"
            @click="router.push(`/admin/membres/${m.id}`)"
          >
            <div class="flex items-start gap-3">
              <div class="w-11 h-11 rounded-full overflow-hidden bg-[var(--color-surface)] flex items-center justify-center text-xs font-bold text-[var(--color-muted)] shrink-0 ring-1 ring-[var(--color-border)]">
                <img
                  v-if="m.photo"
                  :src="getMediaUrl(m.photo)"
                  :alt="`${m.first_name} ${m.last_name}`"
                  class="w-full h-full object-cover"
                  loading="lazy"
                />
                <span v-else>{{ memberInitials(m) }}</span>
              </div>
              <div class="flex-1 min-w-0">
                <div class="flex items-center justify-between gap-2">
                  <h3 class="text-sm font-bold text-[var(--color-primary)] truncate">
                    {{ m.last_name }} {{ m.first_name }}
                  </h3>
                  <Tag
                    :value="statusLabel(m.membership_status)"
                    :severity="statusSeverity(m.membership_status)"
                    class="!text-[9px] !font-bold !uppercase !tracking-wider !px-2 !py-0.5 shrink-0"
                    role="status"
                  />
                </div>
                <p v-if="m.matricule" class="text-[11px] font-mono text-[var(--color-accent)] font-semibold mt-0.5">
                  {{ m.matricule }}
                </p>
                <p class="text-xs text-[var(--color-muted)] mt-1 truncate">{{ m.email }}</p>
                <div class="flex items-center gap-2 mt-1.5 text-[11px] text-[var(--color-muted)]">
                  <span>{{ m.city }}</span>
                  <span class="opacity-30">·</span>
                  <span>{{ formatDate(m.created_at) }}</span>
                  <template v-if="m.phone">
                    <span class="opacity-30">·</span>
                    <span>{{ m.phone }}</span>
                  </template>
                </div>
              </div>
            </div>
          </button>

          <!-- Card actions -->
          <div class="flex items-center border-t border-[var(--color-border)]/50 divide-x divide-[var(--color-border)]/50">
            <button
              @click="router.push(`/admin/membres/${m.id}`)"
              class="flex-1 flex items-center justify-center gap-1.5 py-2.5 text-[11px] font-semibold text-[var(--color-muted)] hover:text-[var(--color-accent)] hover:bg-[var(--color-accent-light)]/50 transition-all cursor-pointer bg-transparent border-none"
              aria-label="Voir le détail"
            >
              <Eye :size="13" />
              Détail
            </button>
            <button
              v-if="canValidate"
              @click="openStatusDialog(m)"
              class="flex-1 flex items-center justify-center gap-1.5 py-2.5 text-[11px] font-semibold text-[var(--color-muted)] hover:text-blue-600 hover:bg-blue-50/50 transition-all cursor-pointer bg-transparent border-none"
              aria-label="Modifier le statut"
            >
              <ShieldCheck :size="13" />
              Statut
            </button>
            <button
              v-if="canManage"
              @click="downloadPdf(m)"
              :disabled="pdfDownloading === m.id"
              class="flex-1 flex items-center justify-center gap-1.5 py-2.5 text-[11px] font-semibold text-[var(--color-muted)] hover:text-green-600 hover:bg-green-50/50 transition-all cursor-pointer bg-transparent border-none disabled:opacity-40"
              aria-label="Télécharger la fiche PDF"
            >
              <Loader2 v-if="pdfDownloading === m.id" :size="13" class="animate-spin" />
              <FileDown v-else :size="13" />
              PDF
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
        <button
          @click="goToPage(1)"
          :disabled="currentPage <= 1"
          class="p-2 rounded-lg hover:bg-[var(--color-surface)] text-[var(--color-muted)] transition-colors cursor-pointer bg-transparent border-none disabled:opacity-30 disabled:cursor-not-allowed"
          aria-label="Première page"
        >
          <ChevronsLeft :size="16" />
        </button>
        <button
          @click="goToPage(currentPage - 1)"
          :disabled="currentPage <= 1"
          class="p-2 rounded-lg hover:bg-[var(--color-surface)] text-[var(--color-muted)] transition-colors cursor-pointer bg-transparent border-none disabled:opacity-30 disabled:cursor-not-allowed"
          aria-label="Page précédente"
        >
          <ChevronLeft :size="16" />
        </button>
      </div>

      <span class="text-xs font-medium text-[var(--color-muted)] px-3 tabular-nums">
        Page <span class="font-bold text-[var(--color-primary)]">{{ currentPage }}</span> sur {{ totalPages }}
      </span>

      <div class="flex items-center gap-1">
        <button
          @click="goToPage(currentPage + 1)"
          :disabled="currentPage >= totalPages"
          class="p-2 rounded-lg hover:bg-[var(--color-surface)] text-[var(--color-muted)] transition-colors cursor-pointer bg-transparent border-none disabled:opacity-30 disabled:cursor-not-allowed"
          aria-label="Page suivante"
        >
          <ChevronRight :size="16" />
        </button>
        <button
          @click="goToPage(totalPages)"
          :disabled="currentPage >= totalPages"
          class="p-2 rounded-lg hover:bg-[var(--color-surface)] text-[var(--color-muted)] transition-colors cursor-pointer bg-transparent border-none disabled:opacity-30 disabled:cursor-not-allowed"
          aria-label="Dernière page"
        >
          <ChevronsRight :size="16" />
        </button>
      </div>
    </div>

    <!-- ═══ Status Change Dialog ═══ -->
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
          v-if="statusDialogOpen"
          class="fixed inset-0 z-50 flex items-end sm:items-center justify-center p-0 sm:p-4 bg-black/40 backdrop-blur-sm"
          @click.self="statusDialogOpen = false"
          role="dialog"
          aria-modal="true"
          aria-labelledby="status-dialog-title"
        >
          <div class="bg-white w-full sm:rounded-2xl sm:max-w-md sm:w-full shadow-xl rounded-t-2xl max-h-[85vh] overflow-y-auto">
            <!-- Header -->
            <div class="flex items-center justify-between p-5 pb-0">
              <div>
                <h3 id="status-dialog-title" class="font-heading text-base font-bold text-[var(--color-primary)]">
                  Modifier le statut
                </h3>
                <p v-if="statusTarget" class="text-xs text-[var(--color-muted)] mt-0.5">
                  {{ statusTarget.first_name }} {{ statusTarget.last_name }}
                </p>
              </div>
              <button
                @click="statusDialogOpen = false"
                class="p-1.5 rounded-lg hover:bg-[var(--color-surface)] transition-colors cursor-pointer bg-transparent border-none"
                aria-label="Fermer"
              >
                <X :size="18" />
              </button>
            </div>

            <form @submit.prevent="saveStatus" class="p-5 space-y-4">
              <div>
                <label class="block text-[11px] font-semibold text-[var(--color-muted)] uppercase tracking-wide mb-2">
                  Nouveau statut
                </label>
                <div class="grid grid-cols-2 gap-2">
                  <button
                    v-for="opt in statusChangeOptions"
                    :key="opt.value"
                    type="button"
                    @click="statusForm.status = opt.value"
                    class="px-3 py-2.5 rounded-lg text-sm font-medium border-2 transition-all cursor-pointer"
                    :class="statusForm.status === opt.value
                      ? 'border-[var(--color-accent)] bg-[var(--color-accent-light)] text-[var(--color-accent)]'
                      : 'border-[var(--color-border)] bg-white text-[var(--color-muted)] hover:border-[var(--color-primary)]/20'"
                  >
                    {{ opt.label }}
                  </button>
                </div>
              </div>

              <div>
                <label class="block text-[11px] font-semibold text-[var(--color-muted)] uppercase tracking-wide mb-2">
                  Raison <span class="font-normal normal-case tracking-normal">(optionnel)</span>
                </label>
                <Textarea
                  v-model="statusForm.reason"
                  rows="2"
                  class="w-full"
                  placeholder="Raison du changement..."
                  aria-label="Raison du changement de statut"
                />
              </div>

              <div class="flex items-center justify-end gap-3 pt-2">
                <button
                  type="button"
                  @click="statusDialogOpen = false"
                  class="px-4 py-2.5 text-sm font-medium text-[var(--color-muted)] hover:text-[var(--color-primary)] transition-colors cursor-pointer bg-transparent border-none"
                >
                  Annuler
                </button>
                <button
                  type="submit"
                  :disabled="statusSaving || !!(statusTarget && statusForm.status === statusTarget.membership_status)"
                  class="inline-flex items-center gap-2 px-5 py-2.5 text-sm font-semibold text-white bg-[var(--color-accent)] rounded-lg hover:bg-[var(--color-accent-hover)] transition-colors cursor-pointer disabled:opacity-40 disabled:cursor-not-allowed"
                >
                  <Loader2 v-if="statusSaving" :size="14" class="animate-spin" />
                  Enregistrer
                </button>
              </div>
            </form>
          </div>
        </div>
      </Transition>
    </Teleport>
  </div>
</template>
