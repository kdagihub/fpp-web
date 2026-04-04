<script setup lang="ts">
import { ref, computed } from 'vue'
import { useAppToast } from '@/composables/useToast'
import api from '@/api'
import { getMediaUrl } from '@/utils/media'
import {
  Search,
  Loader2,
  ShieldCheck,
  ShieldX,
  User,
  Mail,
  Phone,
  Calendar,
  MapPin,
  Briefcase,
  FileText,
  CreditCard,
  Clock,
  FileDown,
  X,
} from 'lucide-vue-next'
import dayjs from 'dayjs'
import 'dayjs/locale/fr'

dayjs.locale('fr')

const toast = useAppToast()
const matricule = ref('')
const loading = ref(false)
const member = ref<any>(null)
const notFound = ref(false)
const pdfDownloading = ref(false)

async function verify() {
  const cleaned = matricule.value.trim()
  if (!cleaned) {
    toast.error('Erreur', 'Veuillez saisir un matricule.')
    return
  }
  loading.value = true
  member.value = null
  notFound.value = false

  try {
    const { data } = await api.post('/admin/verify-matricule/', { matricule: cleaned })
    member.value = data
  } catch (err: any) {
    if (err?.response?.status === 404) {
      notFound.value = true
    } else {
      toast.error('Erreur', err?.response?.data?.detail || 'Erreur lors de la vérification.')
    }
  } finally {
    loading.value = false
  }
}

function reset() {
  member.value = null
  notFound.value = false
  matricule.value = ''
}

const statusConfig = computed(() => {
  if (!member.value) return null
  const s = member.value.membership_status
  if (s === 'validated') return { label: 'Membre actif', color: 'green', icon: ShieldCheck }
  if (s === 'pending') return { label: 'En attente', color: 'amber', icon: Clock }
  if (s === 'suspended') return { label: 'Suspendu', color: 'red', icon: ShieldX }
  if (s === 'rejected') return { label: 'Rejeté', color: 'red', icon: ShieldX }
  return { label: s, color: 'gray', icon: ShieldX }
})

const sexDisplay = computed(() => {
  if (!member.value) return ''
  return member.value.sex === 'M' ? 'Homme' : member.value.sex === 'F' ? 'Femme' : 'Non renseigné'
})

const docTypeDisplay = computed(() => {
  if (!member.value) return ''
  const map: Record<string, string> = {
    cni: "Carte Nationale d'Identité",
    passport: 'Passeport',
    driver_license: 'Permis de conduire',
  }
  return map[member.value.id_document_type] || member.value.id_document_type
})

function formatDate(d: string | null) {
  if (!d) return '—'
  return dayjs(d).format('D MMMM YYYY')
}

function formatDateTime(d: string | null) {
  if (!d) return '—'
  return dayjs(d).format('D MMMM YYYY à HH:mm')
}

async function downloadPdf() {
  if (!member.value?.matricule) return
  pdfDownloading.value = true
  try {
    const response = await api.post('/admin/verify-matricule/', { matricule: member.value.matricule }, { responseType: 'blob' })
    toast.info('Info', 'Pour télécharger la fiche PDF, rendez-vous sur la fiche membre dans la section Membres.')
  } catch {
    toast.error('Erreur', 'Le téléchargement a échoué.')
  } finally {
    pdfDownloading.value = false
  }
}
</script>

<template>
  <div>
    <h2 class="font-heading text-2xl font-bold text-[var(--color-primary)] mb-2">
      Vérification de matricule
    </h2>
    <p class="text-sm text-[var(--color-muted)] mb-8">
      Saisissez un numéro de matricule pour vérifier son authenticité et consulter les informations du membre.
    </p>

    <!-- Search bar -->
    <div class="max-w-xl mx-auto mb-8">
      <form @submit.prevent="verify" class="relative">
        <div class="flex gap-3">
          <div class="flex-1 relative">
            <CreditCard :size="18" class="absolute left-4 top-1/2 -translate-y-1/2 text-gray-400" />
            <input
              v-model="matricule"
              type="text"
              placeholder="Entrez le matricule (ex: FPP-ABJ-2025-A1B2)"
              class="w-full pl-11 pr-4 py-3.5 border border-gray-300 rounded-xl text-sm font-mono tracking-wide focus:outline-none focus:ring-2 focus:ring-[var(--color-accent)] focus:border-[var(--color-accent)] transition"
              :disabled="loading"
              autofocus
            >
          </div>
          <button
            type="submit"
            :disabled="loading || !matricule.trim()"
            class="flex items-center gap-2 px-6 py-3.5 bg-[var(--color-accent)] text-white text-sm font-bold rounded-xl hover:bg-[var(--color-accent-hover)] transition-all cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <Loader2 v-if="loading" :size="18" class="animate-spin" />
            <Search v-else :size="18" />
            Vérifier
          </button>
        </div>
      </form>
    </div>

    <!-- Not found -->
    <Transition
      enter-active-class="transition duration-200 ease-out"
      enter-from-class="opacity-0 translate-y-2"
      enter-to-class="opacity-100 translate-y-0"
    >
      <div v-if="notFound" class="max-w-xl mx-auto">
        <div class="bg-red-50 border border-red-200 rounded-2xl p-8 text-center">
          <div class="w-16 h-16 rounded-full bg-red-100 flex items-center justify-center mx-auto mb-4">
            <ShieldX :size="32" class="text-red-500" />
          </div>
          <h3 class="text-lg font-bold text-red-800 mb-2">Matricule non reconnu</h3>
          <p class="text-sm text-red-600 mb-4">
            Aucun membre trouvé avec le matricule <strong class="font-mono">{{ matricule }}</strong>.
            Ce numéro est invalide ou n'existe pas dans notre base.
          </p>
          <button
            @click="reset"
            class="inline-flex items-center gap-1.5 px-4 py-2 text-sm font-semibold text-red-700 bg-red-100 rounded-lg hover:bg-red-200 transition-colors cursor-pointer"
          >
            <X :size="14" />
            Nouvelle recherche
          </button>
        </div>
      </div>
    </Transition>

    <!-- Member result -->
    <Transition
      enter-active-class="transition duration-300 ease-out"
      enter-from-class="opacity-0 translate-y-4"
      enter-to-class="opacity-100 translate-y-0"
    >
      <div v-if="member" class="max-w-4xl mx-auto space-y-6">

        <!-- Authenticity banner -->
        <div
          class="rounded-2xl p-6 flex items-center gap-5"
          :class="{
            'bg-green-50 border border-green-200': member.membership_status === 'validated',
            'bg-amber-50 border border-amber-200': member.membership_status === 'pending',
            'bg-red-50 border border-red-200': member.membership_status === 'rejected' || member.membership_status === 'suspended',
          }"
        >
          <div
            class="w-14 h-14 rounded-full flex items-center justify-center shrink-0"
            :class="{
              'bg-green-100': member.membership_status === 'validated',
              'bg-amber-100': member.membership_status === 'pending',
              'bg-red-100': member.membership_status === 'rejected' || member.membership_status === 'suspended',
            }"
          >
            <component
              :is="statusConfig!.icon"
              :size="28"
              :class="{
                'text-green-600': member.membership_status === 'validated',
                'text-amber-600': member.membership_status === 'pending',
                'text-red-600': member.membership_status === 'rejected' || member.membership_status === 'suspended',
              }"
            />
          </div>
          <div class="flex-1">
            <div class="flex items-center gap-3 mb-1">
              <h3 class="text-lg font-bold" :class="{
                'text-green-800': member.membership_status === 'validated',
                'text-amber-800': member.membership_status === 'pending',
                'text-red-800': member.membership_status === 'rejected' || member.membership_status === 'suspended',
              }">
                {{ member.membership_status === 'validated' ? 'Matricule authentique' : 'Matricule trouvé' }}
              </h3>
              <span
                class="text-[11px] font-bold uppercase tracking-wide px-2.5 py-1 rounded-full"
                :class="{
                  'bg-green-200 text-green-800': member.membership_status === 'validated',
                  'bg-amber-200 text-amber-800': member.membership_status === 'pending',
                  'bg-red-200 text-red-800': member.membership_status === 'rejected' || member.membership_status === 'suspended',
                }"
              >
                {{ statusConfig!.label }}
              </span>
            </div>
            <p class="text-sm font-mono tracking-wide" :class="{
              'text-green-700': member.membership_status === 'validated',
              'text-amber-700': member.membership_status === 'pending',
              'text-red-700': member.membership_status === 'rejected' || member.membership_status === 'suspended',
            }">
              {{ member.matricule || 'Matricule en attente' }}
            </p>
          </div>
          <button
            @click="reset"
            class="p-2 rounded-lg hover:bg-black/5 transition-colors cursor-pointer shrink-0"
            title="Nouvelle recherche"
          >
            <X :size="20" class="text-gray-500" />
          </button>
        </div>

        <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">

          <!-- Photo + Identity -->
          <div class="bg-white rounded-2xl border border-gray-200 p-6 text-center">
            <div class="w-28 h-28 rounded-2xl mx-auto mb-4 overflow-hidden bg-gray-100 border-2 border-gray-200">
              <img
                v-if="member.photo"
                :src="getMediaUrl(member.photo)"
                class="w-full h-full object-cover"
                alt="Photo du membre"
              >
              <div v-else class="w-full h-full flex items-center justify-center">
                <User :size="40" class="text-gray-300" />
              </div>
            </div>
            <h3 class="text-lg font-bold text-gray-900">{{ member.first_name }} {{ member.last_name }}</h3>
            <p v-if="member.matricule" class="text-xs font-mono text-[var(--color-accent)] font-semibold mt-1">{{ member.matricule }}</p>

            <!-- Dates -->
            <div class="mt-5 space-y-2.5 text-left">
              <div class="flex items-start gap-2.5 p-2.5 rounded-lg bg-gray-50">
                <Clock :size="14" class="text-gray-400 mt-0.5 shrink-0" />
                <div>
                  <p class="text-[10px] font-semibold text-gray-400 uppercase tracking-wide">Inscription</p>
                  <p class="text-xs text-gray-700 font-medium">{{ formatDateTime(member.registered_at) }}</p>
                </div>
              </div>
              <div class="flex items-start gap-2.5 p-2.5 rounded-lg bg-gray-50">
                <FileText :size="14" class="text-gray-400 mt-0.5 shrink-0" />
                <div>
                  <p class="text-[10px] font-semibold text-gray-400 uppercase tracking-wide">Demande d'adhésion</p>
                  <p class="text-xs text-gray-700 font-medium">{{ formatDateTime(member.membership_requested_at) }}</p>
                </div>
              </div>
              <div v-if="member.membership_validated_at" class="flex items-start gap-2.5 p-2.5 rounded-lg bg-green-50">
                <ShieldCheck :size="14" class="text-green-500 mt-0.5 shrink-0" />
                <div>
                  <p class="text-[10px] font-semibold text-green-600 uppercase tracking-wide">Validé le</p>
                  <p class="text-xs text-green-800 font-medium">{{ formatDateTime(member.membership_validated_at) }}</p>
                </div>
              </div>
            </div>
          </div>

          <!-- Info cards -->
          <div class="lg:col-span-2 space-y-5">

            <!-- Personal info -->
            <div class="bg-white rounded-2xl border border-gray-200 p-6">
              <h4 class="text-xs font-bold text-gray-900 uppercase tracking-wide mb-4">Informations personnelles</h4>
              <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <div class="flex items-start gap-3 p-3 rounded-xl bg-gray-50">
                  <Mail :size="16" class="text-gray-400 mt-0.5 shrink-0" />
                  <div class="min-w-0">
                    <p class="text-[10px] font-semibold text-gray-400 uppercase tracking-wide">Email</p>
                    <p class="text-sm text-gray-800 font-medium truncate">{{ member.email }}</p>
                  </div>
                </div>
                <div class="flex items-start gap-3 p-3 rounded-xl bg-gray-50">
                  <Phone :size="16" class="text-gray-400 mt-0.5 shrink-0" />
                  <div class="min-w-0">
                    <p class="text-[10px] font-semibold text-gray-400 uppercase tracking-wide">Téléphone</p>
                    <p class="text-sm text-gray-800 font-medium">{{ member.phone || 'Non renseigné' }}</p>
                  </div>
                </div>
                <div class="flex items-start gap-3 p-3 rounded-xl bg-gray-50">
                  <User :size="16" class="text-gray-400 mt-0.5 shrink-0" />
                  <div>
                    <p class="text-[10px] font-semibold text-gray-400 uppercase tracking-wide">Sexe</p>
                    <p class="text-sm text-gray-800 font-medium">{{ sexDisplay }}</p>
                  </div>
                </div>
                <div class="flex items-start gap-3 p-3 rounded-xl bg-gray-50">
                  <Calendar :size="16" class="text-gray-400 mt-0.5 shrink-0" />
                  <div>
                    <p class="text-[10px] font-semibold text-gray-400 uppercase tracking-wide">Date de naissance</p>
                    <p class="text-sm text-gray-800 font-medium">{{ formatDate(member.date_of_birth) }}</p>
                  </div>
                </div>
                <div class="flex items-start gap-3 p-3 rounded-xl bg-gray-50">
                  <Briefcase :size="16" class="text-gray-400 mt-0.5 shrink-0" />
                  <div>
                    <p class="text-[10px] font-semibold text-gray-400 uppercase tracking-wide">Profession</p>
                    <p class="text-sm text-gray-800 font-medium">{{ member.profession || 'Non renseignée' }}</p>
                  </div>
                </div>
                <div class="flex items-start gap-3 p-3 rounded-xl bg-gray-50">
                  <ShieldCheck :size="16" class="text-gray-400 mt-0.5 shrink-0" />
                  <div>
                    <p class="text-[10px] font-semibold text-gray-400 uppercase tracking-wide">Compte actif</p>
                    <p class="text-sm font-medium" :class="member.is_active ? 'text-green-600' : 'text-red-600'">
                      {{ member.is_active ? 'Oui' : 'Non' }}
                    </p>
                  </div>
                </div>
              </div>
            </div>

            <!-- Document -->
            <div class="bg-white rounded-2xl border border-gray-200 p-6">
              <h4 class="text-xs font-bold text-gray-900 uppercase tracking-wide mb-4">Pièce d'identité</h4>
              <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <div class="flex items-start gap-3 p-3 rounded-xl bg-gray-50">
                  <FileText :size="16" class="text-gray-400 mt-0.5 shrink-0" />
                  <div>
                    <p class="text-[10px] font-semibold text-gray-400 uppercase tracking-wide">Type</p>
                    <p class="text-sm text-gray-800 font-medium">{{ docTypeDisplay }}</p>
                  </div>
                </div>
                <div class="flex items-start gap-3 p-3 rounded-xl bg-gray-50">
                  <CreditCard :size="16" class="text-gray-400 mt-0.5 shrink-0" />
                  <div>
                    <p class="text-[10px] font-semibold text-gray-400 uppercase tracking-wide">Numéro</p>
                    <p class="text-sm text-gray-800 font-medium font-mono tracking-wide">{{ member.id_document_number }}</p>
                  </div>
                </div>
              </div>
              <div v-if="member.id_document_scan" class="mt-3">
                <a
                  :href="getMediaUrl(member.id_document_scan)"
                  target="_blank"
                  class="inline-flex items-center gap-1.5 text-xs font-semibold text-[var(--color-accent)] hover:underline no-underline"
                >
                  <FileDown :size="14" />
                  Voir le scan du document
                </a>
              </div>
            </div>

            <!-- Location -->
            <div class="bg-white rounded-2xl border border-gray-200 p-6">
              <h4 class="text-xs font-bold text-gray-900 uppercase tracking-wide mb-4">Localisation</h4>
              <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <div class="flex items-start gap-3 p-3 rounded-xl bg-gray-50">
                  <MapPin :size="16" class="text-gray-400 mt-0.5 shrink-0" />
                  <div>
                    <p class="text-[10px] font-semibold text-gray-400 uppercase tracking-wide">Ville</p>
                    <p class="text-sm text-gray-800 font-medium">{{ member.city }}</p>
                  </div>
                </div>
                <div class="flex items-start gap-3 p-3 rounded-xl bg-gray-50">
                  <MapPin :size="16" class="text-gray-400 mt-0.5 shrink-0" />
                  <div>
                    <p class="text-[10px] font-semibold text-gray-400 uppercase tracking-wide">Commune</p>
                    <p class="text-sm text-gray-800 font-medium">{{ member.commune }}</p>
                  </div>
                </div>
                <div class="flex items-start gap-3 p-3 rounded-xl bg-gray-50">
                  <MapPin :size="16" class="text-gray-400 mt-0.5 shrink-0" />
                  <div>
                    <p class="text-[10px] font-semibold text-gray-400 uppercase tracking-wide">Région</p>
                    <p class="text-sm text-gray-800 font-medium">{{ member.region || 'Non renseignée' }}</p>
                  </div>
                </div>
                <div class="flex items-start gap-3 p-3 rounded-xl bg-gray-50">
                  <MapPin :size="16" class="text-gray-400 mt-0.5 shrink-0" />
                  <div>
                    <p class="text-[10px] font-semibold text-gray-400 uppercase tracking-wide">Quartier</p>
                    <p class="text-sm text-gray-800 font-medium">{{ member.neighborhood || 'Non renseigné' }}</p>
                  </div>
                </div>
              </div>
            </div>

            <!-- Motivation -->
            <div v-if="member.motivation" class="bg-white rounded-2xl border border-gray-200 p-6">
              <h4 class="text-xs font-bold text-gray-900 uppercase tracking-wide mb-3">Motivation</h4>
              <p class="text-sm text-gray-700 leading-relaxed whitespace-pre-wrap">{{ member.motivation }}</p>
            </div>
          </div>
        </div>
      </div>
    </Transition>

    <!-- Empty state -->
    <div v-if="!member && !notFound && !loading" class="max-w-md mx-auto text-center mt-8">
      <div class="w-20 h-20 rounded-full bg-gray-100 flex items-center justify-center mx-auto mb-4">
        <CreditCard :size="36" class="text-gray-300" />
      </div>
      <p class="text-sm text-gray-400">
        Saisissez un matricule ci-dessus pour vérifier son authenticité.
      </p>
    </div>
  </div>
</template>
