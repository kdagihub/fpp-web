<script setup lang="ts">
import { ref, shallowRef, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useAppToast } from '@/composables/useToast'
import api from '@/api'
import { getMediaUrl } from '@/utils/media'
import type { AdminMemberDetail } from '@/types'
import dayjs from 'dayjs'
import 'dayjs/locale/fr'

import Tag from 'primevue/tag'
import Select from 'primevue/select'
import Textarea from 'primevue/textarea'
import Skeleton from 'primevue/skeleton'

import {
  ArrowLeft,
  FileDown,
  Loader2,
  User,
  Mail,
  Phone,
  Calendar,
  MapPin,
  Briefcase,
  FileText,
  CreditCard,
  Clock,
  ShieldCheck,
  Pencil,
  UserX,
  UserCheck as UserCheckIcon,
  ExternalLink,
  X,
  Upload,
  Save,
  AlertTriangle,
  Camera,
} from 'lucide-vue-next'

dayjs.locale('fr')

const props = defineProps<{ id: string }>()
const router = useRouter()
const authStore = useAuthStore()
const toast = useAppToast()

const canManage = computed(() => authStore.hasPermission('can_manage_members'))
const canValidate = computed(() => authStore.hasPermission('can_validate_membership'))

const member = ref<AdminMemberDetail | null>(null)
const loading = ref(true)
const pdfDownloading = ref(false)

/* ── Status dialog ── */
const statusDialogOpen = ref(false)
const statusForm = ref({ status: '', reason: '' })
const statusSaving = ref(false)
const statusChangeOptions = [
  { label: 'Validé', value: 'validated' },
  { label: 'En attente', value: 'pending' },
  { label: 'Suspendu', value: 'suspended' },
  { label: 'Rejeté', value: 'rejected' },
]

/* ── Edit dialog ── */
const editDialogOpen = ref(false)
const editForm = ref({ city: '', commune: '', region: '', neighborhood: '', profession: '', address: '' })
const editSaving = ref(false)
const editPhotoFile = shallowRef<File | null>(null)
const editPhotoPreview = ref<string | null>(null)
const editPhotoRemoved = ref(false)

/* ── Deactivate dialog ── */
const deactivateDialogOpen = ref(false)
const deactivating = ref(false)

/* ── Fetch ── */
async function fetchMember() {
  loading.value = true
  try {
    const { data } = await api.get<AdminMemberDetail>(`/admin/members/${props.id}/`)
    member.value = data
  } catch {
    toast.error('Erreur', 'Impossible de charger les détails du membre.')
    router.push('/admin/membres')
  } finally {
    loading.value = false
  }
}

onMounted(fetchMember)

/* ── Actions ── */
async function downloadPdf() {
  pdfDownloading.value = true
  try {
    const response = await api.get(`/admin/members/${props.id}/pdf/`, { responseType: 'blob' })
    const url = URL.createObjectURL(response.data)
    const a = document.createElement('a')
    a.href = url
    a.download = `Fiche-${member.value?.last_name ?? 'Membre'}-FPP.pdf`
    a.click()
    URL.revokeObjectURL(url)
  } catch {
    toast.error('Erreur', 'Le téléchargement de la fiche a échoué.')
  } finally {
    pdfDownloading.value = false
  }
}

/* ── Status ── */
function openStatusDialog() {
  if (!member.value) return
  statusForm.value = { status: member.value.membership_status, reason: '' }
  statusDialogOpen.value = true
}

async function saveStatus() {
  if (!member.value || statusForm.value.status === member.value.membership_status) {
    statusDialogOpen.value = false
    return
  }
  statusSaving.value = true
  try {
    await api.patch(`/admin/members/${props.id}/status/`, statusForm.value)
    toast.success('Statut modifié', 'Le statut du membre a été mis à jour.')
    statusDialogOpen.value = false
    await fetchMember()
  } catch (err: any) {
    toast.error('Erreur', err?.response?.data?.detail || 'La modification a échoué.')
  } finally {
    statusSaving.value = false
  }
}

/* ── Edit ── */
function openEditDialog() {
  if (!member.value) return
  editForm.value = {
    city: member.value.city,
    commune: member.value.commune,
    region: member.value.region,
    neighborhood: member.value.neighborhood,
    profession: member.value.profession,
    address: member.value.address,
  }
  editPhotoFile.value = null
  editPhotoPreview.value = member.value.photo ? getMediaUrl(member.value.photo) : null
  editPhotoRemoved.value = false
  editDialogOpen.value = true
}

function onEditPhotoChange(event: Event) {
  const input = event.target as HTMLInputElement
  const file = input.files?.[0]
  if (!file) return
  editPhotoFile.value = file
  editPhotoPreview.value = URL.createObjectURL(file)
  editPhotoRemoved.value = false
}

function removeEditPhoto() {
  editPhotoFile.value = null
  editPhotoPreview.value = null
  editPhotoRemoved.value = true
}

async function saveEdit() {
  editSaving.value = true
  try {
    const fd = new FormData()
    fd.append('city', editForm.value.city)
    fd.append('commune', editForm.value.commune)
    fd.append('region', editForm.value.region)
    fd.append('neighborhood', editForm.value.neighborhood)
    fd.append('profession', editForm.value.profession)
    fd.append('address', editForm.value.address)

    if (editPhotoFile.value) {
      fd.append('photo', editPhotoFile.value)
    } else if (editPhotoRemoved.value) {
      fd.append('clear_photo', 'true')
    }

    const { data } = await api.patch(`/admin/members/${props.id}/update/`, fd, {
      headers: { 'Content-Type': undefined },
    })
    member.value = data
    toast.success('Membre modifié', 'Les informations ont été mises à jour.')
    editDialogOpen.value = false
  } catch (err: any) {
    toast.error('Erreur', err?.response?.data?.detail || 'La modification a échoué.')
  } finally {
    editSaving.value = false
  }
}

/* ── Deactivate / Reactivate ── */
function openDeactivateDialog() {
  deactivateDialogOpen.value = true
}

async function confirmToggleActive() {
  if (!member.value) return
  deactivating.value = true
  const isActive = member.value.is_active
  try {
    await api.patch(`/admin/members/${props.id}/status/`, {
      status: isActive ? 'suspended' : 'validated',
      reason: isActive ? 'Désactivation par admin' : 'Réactivation par admin',
    })
    toast.success('Succès', isActive ? 'Compte désactivé.' : 'Compte réactivé.')
    deactivateDialogOpen.value = false
    await fetchMember()
  } catch {
    toast.error('Erreur', "L'opération a échoué.")
  } finally {
    deactivating.value = false
  }
}

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

function formatDate(d: string | null) {
  if (!d) return '—'
  return dayjs(d).format('D MMMM YYYY')
}

function formatDateTime(d: string | null) {
  if (!d) return '—'
  return dayjs(d).format('D MMMM YYYY à HH:mm')
}

const sexDisplay = computed(() => {
  if (!member.value) return ''
  return member.value.sex === 'M' ? 'Homme' : member.value.sex === 'F' ? 'Femme' : '—'
})

const docTypeDisplay = computed(() => {
  if (!member.value) return ''
  const map: Record<string, string> = {
    cni: "Carte Nationale d'Identité", passport: 'Passeport', driver_license: 'Permis de conduire',
  }
  return map[member.value.id_document_type] || member.value.id_document_type
})

const sourceDisplay = computed(() => {
  if (!member.value) return ''
  const map: Record<string, string> = { web: 'Site web', mobile: 'Application', admin: 'Saisie admin' }
  return map[member.value.registration_source] || member.value.registration_source
})
</script>

<template>
  <div class="max-w-[1200px]">
    <!-- ═══ Header ═══ -->
    <div class="flex flex-col gap-4 mb-8">
      <!-- Back + identity -->
      <div class="flex items-center gap-3">
        <button
          @click="router.push('/admin/membres')"
          class="p-2 rounded-lg hover:bg-[var(--color-surface)] transition-colors cursor-pointer bg-transparent border-none"
          aria-label="Retour à la liste"
        >
          <ArrowLeft :size="20" class="text-[var(--color-muted)]" />
        </button>
        <div v-if="member">
          <h2 class="font-heading text-xl lg:text-2xl font-bold text-[var(--color-primary)]">
            {{ member.first_name }} {{ member.last_name }}
          </h2>
          <div class="flex items-center gap-2 mt-1">
            <Tag
              :value="statusLabel(member.membership_status)"
              :severity="statusSeverity(member.membership_status)"
              class="!text-[10px] !font-bold !uppercase !tracking-wider !px-2.5 !py-1"
              role="status"
            />
            <span v-if="member.matricule" class="text-xs font-mono text-[var(--color-accent)] font-semibold">
              {{ member.matricule }}
            </span>
          </div>
        </div>
        <div v-else-if="loading">
          <Skeleton height="1.75rem" width="12rem" class="mb-2" />
          <Skeleton height="1rem" width="8rem" />
        </div>
      </div>

      <!-- Action buttons -->
      <div v-if="member" class="flex items-center gap-2 flex-wrap ml-0 sm:ml-11">
        <button
          @click="downloadPdf"
          :disabled="pdfDownloading"
          class="inline-flex items-center gap-2 px-4 py-2.5 text-sm font-medium rounded-lg border border-[var(--color-border)] bg-white text-[var(--color-primary)] hover:bg-[var(--color-surface)] transition-all cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
          aria-label="Télécharger la fiche PDF"
        >
          <Loader2 v-if="pdfDownloading" :size="15" class="animate-spin" />
          <FileDown v-else :size="15" class="text-[var(--color-accent)]" />
          Fiche PDF
        </button>

        <button
          v-if="canValidate"
          @click="openStatusDialog"
          class="inline-flex items-center gap-2 px-4 py-2.5 text-sm font-medium rounded-lg border border-blue-200 bg-blue-50 text-blue-700 hover:bg-blue-100 transition-all cursor-pointer"
          aria-label="Modifier le statut"
        >
          <ShieldCheck :size="15" />
          Statut
        </button>

        <button
          v-if="canManage"
          @click="openEditDialog"
          class="inline-flex items-center gap-2 px-4 py-2.5 text-sm font-medium rounded-lg border border-[var(--color-accent)]/30 bg-[var(--color-accent-light)] text-[var(--color-accent)] hover:bg-[var(--color-accent)]/15 transition-all cursor-pointer"
          aria-label="Modifier les informations"
        >
          <Pencil :size="15" />
          Modifier
        </button>

        <button
          v-if="canManage"
          @click="openDeactivateDialog"
          class="inline-flex items-center gap-2 px-4 py-2.5 text-sm font-medium rounded-lg border transition-all cursor-pointer"
          :class="member.is_active
            ? 'border-red-200 bg-red-50 text-red-600 hover:bg-red-100'
            : 'border-green-200 bg-green-50 text-green-700 hover:bg-green-100'"
          :aria-label="member.is_active ? 'Désactiver le compte' : 'Réactiver le compte'"
        >
          <UserX v-if="member.is_active" :size="15" />
          <UserCheckIcon v-else :size="15" />
          {{ member.is_active ? 'Désactiver' : 'Réactiver' }}
        </button>
      </div>
    </div>

    <!-- ═══ Loading state ═══ -->
    <div v-if="loading" class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <div class="bg-white rounded-xl border border-[var(--color-border)] p-6">
        <div class="flex flex-col items-center">
          <Skeleton shape="circle" size="7rem" class="mb-4" />
          <Skeleton height="1.25rem" width="60%" class="mb-2" />
          <Skeleton height="0.875rem" width="40%" />
        </div>
      </div>
      <div class="lg:col-span-2 space-y-5">
        <div v-for="i in 3" :key="i" class="bg-white rounded-xl border border-[var(--color-border)] p-6">
          <Skeleton height="1rem" width="30%" class="mb-4" />
          <div class="grid grid-cols-2 gap-3">
            <Skeleton height="3.5rem" v-for="j in 4" :key="j" />
          </div>
        </div>
      </div>
    </div>

    <!-- ═══ Member detail ═══ -->
    <div v-else-if="member" class="grid grid-cols-1 lg:grid-cols-3 gap-6">

      <!-- Left column -->
      <div class="space-y-5">
        <!-- Photo card -->
        <div class="bg-white rounded-xl border border-[var(--color-border)] p-6 text-center">
          <div class="w-28 h-28 rounded-2xl mx-auto mb-4 overflow-hidden bg-[var(--color-surface)] ring-2 ring-[var(--color-border)]">
            <img
              v-if="member.photo"
              :src="getMediaUrl(member.photo)"
              class="w-full h-full object-cover"
              :alt="`Photo de ${member.first_name} ${member.last_name}`"
            />
            <div v-else class="w-full h-full flex items-center justify-center">
              <User :size="40" class="text-[var(--color-muted)] opacity-25" />
            </div>
          </div>
          <h3 class="text-lg font-bold text-[var(--color-primary)] font-heading">{{ member.first_name }} {{ member.last_name }}</h3>
          <p v-if="member.matricule" class="text-xs font-mono text-[var(--color-accent)] font-semibold mt-1">
            {{ member.matricule }}
          </p>

          <div class="mt-5 space-y-2 text-left">
            <div class="flex items-start gap-2.5 p-3 rounded-lg bg-[var(--color-surface)]">
              <Clock :size="14" class="text-[var(--color-muted)] mt-0.5 shrink-0 opacity-60" />
              <div>
                <p class="text-[10px] font-semibold text-[var(--color-muted)] uppercase tracking-wide">Inscription</p>
                <p class="text-xs text-[var(--color-primary)] font-medium">{{ formatDateTime(member.registered_at) }}</p>
              </div>
            </div>
            <div class="flex items-start gap-2.5 p-3 rounded-lg bg-[var(--color-surface)]">
              <FileText :size="14" class="text-[var(--color-muted)] mt-0.5 shrink-0 opacity-60" />
              <div>
                <p class="text-[10px] font-semibold text-[var(--color-muted)] uppercase tracking-wide">Demande d'adhésion</p>
                <p class="text-xs text-[var(--color-primary)] font-medium">{{ formatDateTime(member.created_at) }}</p>
              </div>
            </div>
            <div v-if="member.membership_date" class="flex items-start gap-2.5 p-3 rounded-lg bg-green-50">
              <ShieldCheck :size="14" class="text-green-500 mt-0.5 shrink-0" />
              <div>
                <p class="text-[10px] font-semibold text-green-600 uppercase tracking-wide">Validé le</p>
                <p class="text-xs text-green-800 font-medium">{{ formatDateTime(member.membership_date) }}</p>
              </div>
            </div>
          </div>
        </div>

        <!-- Account status -->
        <div class="bg-white rounded-xl border border-[var(--color-border)] p-5">
          <h4 class="text-[11px] font-bold text-[var(--color-primary)] uppercase tracking-wider mb-3 font-heading">Compte</h4>
          <div class="space-y-2.5">
            <div class="flex items-center justify-between">
              <span class="text-xs text-[var(--color-muted)]">Compte actif</span>
              <span class="text-xs font-semibold" :class="member.is_active ? 'text-green-600' : 'text-red-600'">
                {{ member.is_active ? 'Oui' : 'Non' }}
              </span>
            </div>
            <div class="flex items-center justify-between">
              <span class="text-xs text-[var(--color-muted)]">Source</span>
              <span class="text-xs font-medium text-[var(--color-primary)]">{{ sourceDisplay }}</span>
            </div>
          </div>
        </div>

        <!-- Roles -->
        <div v-if="member.active_roles?.length" class="bg-white rounded-xl border border-[var(--color-border)] p-5">
          <h4 class="text-[11px] font-bold text-[var(--color-primary)] uppercase tracking-wider mb-3 font-heading">Rôles actifs</h4>
          <div class="space-y-2">
            <div
              v-for="(role, i) in member.active_roles"
              :key="i"
              class="flex items-center gap-2 p-2.5 rounded-lg bg-[var(--color-accent-light)]"
            >
              <ShieldCheck :size="14" class="text-[var(--color-accent)] shrink-0" />
              <div>
                <p class="text-xs font-semibold text-[var(--color-primary)]">{{ role.role_name }}</p>
                <p v-if="role.zone_name" class="text-[10px] text-[var(--color-muted)]">{{ role.zone_name }}</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Right column -->
      <div class="lg:col-span-2 space-y-5">
        <!-- Personal info -->
        <div class="bg-white rounded-xl border border-[var(--color-border)] p-6">
          <h4 class="text-[11px] font-bold text-[var(--color-primary)] uppercase tracking-wider mb-4 font-heading">Informations personnelles</h4>
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <div v-for="(info, i) in [
              { icon: Mail, label: 'Email', value: member.email, truncate: true },
              { icon: Phone, label: 'Téléphone', value: member.phone || '—' },
              { icon: User, label: 'Sexe', value: sexDisplay },
              { icon: Calendar, label: 'Date de naissance', value: formatDate(member.date_of_birth) },
              { icon: Briefcase, label: 'Profession', value: member.profession || '—' },
            ]" :key="i" class="flex items-start gap-3 p-3.5 rounded-xl bg-[var(--color-surface)]">
              <component :is="info.icon" :size="16" class="text-[var(--color-muted)] mt-0.5 shrink-0 opacity-50" />
              <div class="min-w-0">
                <p class="text-[10px] font-semibold text-[var(--color-muted)] uppercase tracking-wide">{{ info.label }}</p>
                <p class="text-sm text-[var(--color-primary)] font-medium" :class="{ 'truncate': info.truncate }">{{ info.value }}</p>
              </div>
            </div>
          </div>
        </div>

        <!-- ID Document -->
        <div class="bg-white rounded-xl border border-[var(--color-border)] p-6">
          <h4 class="text-[11px] font-bold text-[var(--color-primary)] uppercase tracking-wider mb-4 font-heading">Pièce d'identité</h4>
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <div class="flex items-start gap-3 p-3.5 rounded-xl bg-[var(--color-surface)]">
              <FileText :size="16" class="text-[var(--color-muted)] mt-0.5 shrink-0 opacity-50" />
              <div>
                <p class="text-[10px] font-semibold text-[var(--color-muted)] uppercase tracking-wide">Type</p>
                <p class="text-sm text-[var(--color-primary)] font-medium">{{ docTypeDisplay }}</p>
              </div>
            </div>
            <div class="flex items-start gap-3 p-3.5 rounded-xl bg-[var(--color-surface)]">
              <CreditCard :size="16" class="text-[var(--color-muted)] mt-0.5 shrink-0 opacity-50" />
              <div>
                <p class="text-[10px] font-semibold text-[var(--color-muted)] uppercase tracking-wide">Numéro</p>
                <p class="text-sm text-[var(--color-primary)] font-medium font-mono tracking-wide">{{ member.id_document_number }}</p>
              </div>
            </div>
          </div>
          <div v-if="member.id_document_scan" class="mt-4">
            <a
              :href="getMediaUrl(member.id_document_scan)"
              target="_blank"
              rel="noopener noreferrer"
              class="inline-flex items-center gap-1.5 text-xs font-semibold text-[var(--color-accent)] hover:underline no-underline"
            >
              <ExternalLink :size="14" />
              Voir le scan du document
            </a>
          </div>
        </div>

        <!-- Location -->
        <div class="bg-white rounded-xl border border-[var(--color-border)] p-6">
          <h4 class="text-[11px] font-bold text-[var(--color-primary)] uppercase tracking-wider mb-4 font-heading">Localisation</h4>
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <div v-for="(loc, i) in [
              { label: 'Ville', value: member.city },
              { label: 'Commune', value: member.commune },
              { label: 'Région', value: member.region || '—' },
              { label: 'Quartier', value: member.neighborhood || '—' },
            ]" :key="i" class="flex items-start gap-3 p-3.5 rounded-xl bg-[var(--color-surface)]">
              <MapPin :size="16" class="text-[var(--color-muted)] mt-0.5 shrink-0 opacity-50" />
              <div>
                <p class="text-[10px] font-semibold text-[var(--color-muted)] uppercase tracking-wide">{{ loc.label }}</p>
                <p class="text-sm text-[var(--color-primary)] font-medium">{{ loc.value }}</p>
              </div>
            </div>
          </div>
        </div>

        <!-- Motivation -->
        <div v-if="member.motivation" class="bg-white rounded-xl border border-[var(--color-border)] p-6">
          <h4 class="text-[11px] font-bold text-[var(--color-primary)] uppercase tracking-wider mb-3 font-heading">Motivation</h4>
          <p class="text-sm text-[var(--color-muted)] leading-relaxed whitespace-pre-wrap">{{ member.motivation }}</p>
        </div>
      </div>
    </div>

    <!-- ═══ Status Dialog ═══ -->
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
        >
          <div class="bg-white w-full sm:rounded-2xl sm:max-w-md sm:w-full shadow-xl rounded-t-2xl max-h-[85vh] overflow-y-auto">
            <div class="flex items-center justify-between p-5 pb-0">
              <div>
                <h3 class="font-heading text-base font-bold text-[var(--color-primary)]">Modifier le statut</h3>
                <p v-if="member" class="text-xs text-[var(--color-muted)] mt-0.5">
                  {{ member.first_name }} {{ member.last_name }}
                </p>
              </div>
              <button @click="statusDialogOpen = false" class="p-1.5 rounded-lg hover:bg-[var(--color-surface)] transition-colors cursor-pointer bg-transparent border-none" aria-label="Fermer">
                <X :size="18" />
              </button>
            </div>

            <form @submit.prevent="saveStatus" class="p-5 space-y-4">
              <div>
                <label class="block text-[11px] font-semibold text-[var(--color-muted)] uppercase tracking-wide mb-2">Nouveau statut</label>
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
                <Textarea v-model="statusForm.reason" rows="2" class="w-full" placeholder="Raison du changement..." />
              </div>

              <div class="flex items-center justify-end gap-3 pt-2">
                <button type="button" @click="statusDialogOpen = false" class="px-4 py-2.5 text-sm font-medium text-[var(--color-muted)] cursor-pointer bg-transparent border-none">Annuler</button>
                <button
                  type="submit"
                  :disabled="statusSaving || statusForm.status === member?.membership_status"
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

    <!-- ═══ Edit Dialog ═══ -->
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
          v-if="editDialogOpen"
          class="fixed inset-0 z-50 flex items-end sm:items-center justify-center p-0 sm:p-4 bg-black/40 backdrop-blur-sm"
          @click.self="editDialogOpen = false"
          role="dialog"
          aria-modal="true"
        >
          <div class="bg-white w-full sm:rounded-2xl sm:max-w-lg sm:w-full shadow-xl rounded-t-2xl max-h-[90vh] overflow-y-auto">
            <div class="flex items-center justify-between p-5 pb-0">
              <h3 class="font-heading text-base font-bold text-[var(--color-primary)]">Modifier les informations</h3>
              <button @click="editDialogOpen = false" class="p-1.5 rounded-lg hover:bg-[var(--color-surface)] transition-colors cursor-pointer bg-transparent border-none" aria-label="Fermer">
                <X :size="18" />
              </button>
            </div>

            <form @submit.prevent="saveEdit" class="p-5 space-y-5">
              <!-- Photo section -->
              <div>
                <label class="block text-[11px] font-semibold text-[var(--color-muted)] uppercase tracking-wide mb-3">Photo du membre</label>
                <div class="flex items-center gap-4">
                  <div class="w-20 h-20 rounded-xl bg-[var(--color-surface)] border border-[var(--color-border)] overflow-hidden flex items-center justify-center shrink-0">
                    <img v-if="editPhotoPreview" :src="editPhotoPreview" alt="" class="w-full h-full object-cover" />
                    <Camera v-else :size="24" class="text-[var(--color-muted)] opacity-25" />
                  </div>
                  <div class="flex flex-col gap-2">
                    <label class="inline-flex items-center gap-1.5 px-3 py-2 text-xs font-semibold text-[var(--color-accent)] bg-[var(--color-accent-light)] rounded-lg cursor-pointer hover:bg-[var(--color-accent)]/15 transition-colors">
                      <Upload :size="14" />
                      {{ editPhotoPreview ? 'Remplacer' : 'Ajouter une photo' }}
                      <input type="file" accept="image/*" class="hidden" @change="onEditPhotoChange" />
                    </label>
                    <button
                      v-if="editPhotoPreview"
                      type="button"
                      @click="removeEditPhoto"
                      class="text-xs text-red-500 hover:text-red-700 text-left cursor-pointer bg-transparent border-none p-0"
                    >
                      Retirer la photo
                    </button>
                  </div>
                </div>
              </div>

              <!-- Separator -->
              <div class="border-t border-[var(--color-border)]/50" />

              <!-- Fields -->
              <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div v-for="field in [
                  { key: 'city', label: 'Ville', placeholder: 'Ex: Abidjan' },
                  { key: 'commune', label: 'Commune', placeholder: 'Ex: Cocody' },
                  { key: 'region', label: 'Région', placeholder: 'Ex: Lagunes' },
                  { key: 'neighborhood', label: 'Quartier', placeholder: 'Ex: Angré' },
                  { key: 'profession', label: 'Profession', placeholder: 'Ex: Ingénieur' },
                ]" :key="field.key">
                  <label :for="`edit-${field.key}`" class="block text-[11px] font-semibold text-[var(--color-muted)] uppercase tracking-wide mb-1.5">
                    {{ field.label }}
                  </label>
                  <input
                    :id="`edit-${field.key}`"
                    v-model="(editForm as any)[field.key]"
                    type="text"
                    :placeholder="field.placeholder"
                    class="w-full px-3.5 py-2.5 text-sm border border-[var(--color-border)] rounded-lg bg-white focus:ring-2 focus:ring-[var(--color-accent)]/20 focus:border-[var(--color-accent)] outline-none transition-all placeholder:text-[var(--color-muted)]/40"
                    :aria-label="field.label"
                  />
                </div>
                <div class="sm:col-span-2">
                  <label for="edit-address" class="block text-[11px] font-semibold text-[var(--color-muted)] uppercase tracking-wide mb-1.5">Adresse</label>
                  <textarea
                    id="edit-address"
                    v-model="editForm.address"
                    rows="2"
                    placeholder="Adresse complète..."
                    class="w-full px-3.5 py-2.5 text-sm border border-[var(--color-border)] rounded-lg bg-white focus:ring-2 focus:ring-[var(--color-accent)]/20 focus:border-[var(--color-accent)] outline-none transition-all resize-y placeholder:text-[var(--color-muted)]/40"
                    aria-label="Adresse"
                  />
                </div>
              </div>

              <!-- Actions -->
              <div class="flex items-center justify-end gap-3 pt-2 border-t border-[var(--color-border)]/50">
                <button type="button" @click="editDialogOpen = false" class="px-4 py-2.5 text-sm font-medium text-[var(--color-muted)] cursor-pointer bg-transparent border-none">
                  Annuler
                </button>
                <button
                  type="submit"
                  :disabled="editSaving"
                  class="inline-flex items-center gap-2 px-5 py-2.5 text-sm font-semibold text-white bg-[var(--color-accent)] rounded-lg hover:bg-[var(--color-accent-hover)] transition-colors cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <Loader2 v-if="editSaving" :size="14" class="animate-spin" />
                  <Save v-else :size="14" />
                  Enregistrer
                </button>
              </div>
            </form>
          </div>
        </div>
      </Transition>
    </Teleport>

    <!-- ═══ Deactivate / Reactivate Dialog ═══ -->
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
          v-if="deactivateDialogOpen"
          class="fixed inset-0 z-50 flex items-end sm:items-center justify-center p-0 sm:p-4 bg-black/40 backdrop-blur-sm"
          @click.self="deactivateDialogOpen = false"
          role="dialog"
          aria-modal="true"
        >
          <div class="bg-white w-full sm:rounded-2xl sm:max-w-sm sm:w-full shadow-xl rounded-t-2xl p-6 text-center">
            <div
              class="w-14 h-14 rounded-full flex items-center justify-center mx-auto mb-4"
              :class="member?.is_active ? 'bg-red-100' : 'bg-green-100'"
            >
              <AlertTriangle v-if="member?.is_active" :size="24" class="text-red-600" />
              <UserCheckIcon v-else :size="24" class="text-green-600" />
            </div>
            <h3 class="font-heading text-lg font-bold text-[var(--color-primary)] mb-2">
              {{ member?.is_active ? 'Désactiver le compte' : 'Réactiver le compte' }}
            </h3>
            <p class="text-sm text-[var(--color-muted)] mb-6 max-w-xs mx-auto">
              {{ member?.is_active
                ? `Le compte de ${member?.first_name} ${member?.last_name} sera suspendu et n'aura plus accès à la plateforme.`
                : `Le compte de ${member?.first_name} ${member?.last_name} sera réactivé avec le statut "Validé".` }}
            </p>
            <div class="flex items-center justify-center gap-3">
              <button
                @click="deactivateDialogOpen = false"
                class="px-4 py-2.5 text-sm font-medium text-[var(--color-muted)] cursor-pointer bg-transparent border-none"
              >
                Annuler
              </button>
              <button
                @click="confirmToggleActive"
                :disabled="deactivating"
                class="inline-flex items-center gap-2 px-5 py-2.5 text-sm font-semibold text-white rounded-lg transition-colors cursor-pointer disabled:opacity-50"
                :class="member?.is_active ? 'bg-red-600 hover:bg-red-700' : 'bg-green-600 hover:bg-green-700'"
              >
                <Loader2 v-if="deactivating" :size="14" class="animate-spin" />
                {{ member?.is_active ? 'Désactiver' : 'Réactiver' }}
              </button>
            </div>
          </div>
        </div>
      </Transition>
    </Teleport>
  </div>
</template>
