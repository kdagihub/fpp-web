<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useAppToast } from '@/composables/useToast'
import api from '@/api'
import {
  ArrowLeft,
  ArrowRight,
  Upload,
  CheckCircle2,
  Clock,
  XCircle,
  Loader2,
  FileDown,
  X,
  ImageIcon,
  AlertCircle,
} from 'lucide-vue-next'

const authStore = useAuthStore()
const router = useRouter()
const toast = useAppToast()
const submitting = ref(false)

const membership = computed(() => authStore.user?.membership)
const membershipStatus = computed(() => membership.value?.status ?? null)

const membershipForm = ref({
  id_document_type: 'cni',
  id_document_number: '',
  city: '',
  commune: '',
  region: '',
  neighborhood: '',
  profession: '',
  motivation: '',
})
const photoFile = ref<File | null>(null)
const idScanFile = ref<File | null>(null)
const photoPreview = ref<string | null>(null)
const idScanPreview = ref<string | null>(null)
const photoError = ref('')
const idScanError = ref('')
const photoInputRef = ref<HTMLInputElement | null>(null)
const idScanInputRef = ref<HTMLInputElement | null>(null)

const MAX_SIZE_MB = 5
const MAX_SIZE_BYTES = MAX_SIZE_MB * 1024 * 1024
const ALLOWED_TYPES = ['image/jpeg', 'image/png', 'image/webp']
const ALLOWED_EXTENSIONS = 'JPG, PNG, WebP'

const documentTypes = [
  { value: 'cni', label: "Carte Nationale d'Identité" },
  { value: 'passport', label: 'Passeport' },
  { value: 'driver_license', label: 'Permis de conduire' },
]

function formatFileSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} o`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} Ko`
  return `${(bytes / (1024 * 1024)).toFixed(1)} Mo`
}

function validateFile(file: File, label: string): string {
  if (!ALLOWED_TYPES.includes(file.type)) {
    return `${label} : format non accepté. Utilisez ${ALLOWED_EXTENSIONS}.`
  }
  if (file.size > MAX_SIZE_BYTES) {
    return `${label} : fichier trop volumineux (${formatFileSize(file.size)}). Maximum ${MAX_SIZE_MB} Mo.`
  }
  return ''
}

function revokePreview(url: string | null) {
  if (url) URL.revokeObjectURL(url)
}

function onFileChange(type: 'photo' | 'scan', event: Event) {
  const target = event.target as HTMLInputElement
  const file = target.files?.[0] ?? null
  if (!file) return

  if (type === 'photo') {
    const err = validateFile(file, 'Photo')
    photoError.value = err
    if (err) { target.value = ''; return }
    revokePreview(photoPreview.value)
    photoFile.value = file
    photoPreview.value = URL.createObjectURL(file)
  } else {
    const err = validateFile(file, 'Scan')
    idScanError.value = err
    if (err) { target.value = ''; return }
    revokePreview(idScanPreview.value)
    idScanFile.value = file
    idScanPreview.value = URL.createObjectURL(file)
  }
}

function removeFile(type: 'photo' | 'scan') {
  if (type === 'photo') {
    revokePreview(photoPreview.value)
    photoFile.value = null
    photoPreview.value = null
    photoError.value = ''
    if (photoInputRef.value) photoInputRef.value.value = ''
  } else {
    revokePreview(idScanPreview.value)
    idScanFile.value = null
    idScanPreview.value = null
    idScanError.value = ''
    if (idScanInputRef.value) idScanInputRef.value.value = ''
  }
}

onUnmounted(() => {
  revokePreview(photoPreview.value)
  revokePreview(idScanPreview.value)
})

async function handleSubmit() {
  if (!photoFile.value || !idScanFile.value) {
    toast.error('Erreur', "Veuillez ajouter votre photo et le scan de votre pièce d'identité.")
    return
  }
  submitting.value = true
  const formData = new FormData()
  formData.append('id_document_type', membershipForm.value.id_document_type)
  formData.append('id_document_number', membershipForm.value.id_document_number)
  formData.append('id_document_scan', idScanFile.value)
  formData.append('photo', photoFile.value)
  formData.append('city', membershipForm.value.city)
  formData.append('commune', membershipForm.value.commune)
  if (membershipForm.value.region) formData.append('region', membershipForm.value.region)
  if (membershipForm.value.neighborhood) formData.append('neighborhood', membershipForm.value.neighborhood)
  if (membershipForm.value.profession) formData.append('profession', membershipForm.value.profession)
  if (membershipForm.value.motivation) formData.append('motivation', membershipForm.value.motivation)

  try {
    await api.post('/membership/request/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
    toast.success('Demande envoyée', "Votre demande d'adhésion a bien été soumise.")
    await authStore.fetchUser()
  } catch (err: any) {
    const data = err?.response?.data
    const msg = data?.detail || data?.id_document_number?.[0] || "Erreur lors de l'envoi de la demande."
    toast.error('Erreur', msg)
  } finally {
    submitting.value = false
  }
}

const pdfDownloading = ref(false)

async function downloadMembershipPdf() {
  pdfDownloading.value = true
  try {
    const response = await api.get('/public/membership-form/pdf/', { responseType: 'blob' })
    const url = URL.createObjectURL(response.data)
    const a = document.createElement('a')
    a.href = url
    a.download = 'Formulaire-Adhesion-FPP.pdf'
    a.click()
    URL.revokeObjectURL(url)
  } catch {
    toast.error('Erreur', 'Le téléchargement a échoué. Réessayez plus tard.')
  } finally {
    pdfDownloading.value = false
  }
}

onMounted(() => {
  if (membershipStatus.value === 'validated') {
    router.replace('/mon-espace/carte')
  }
})
</script>

<template>
  <div class="max-w-2xl mx-auto">
    <!-- Retour -->
    <button
      @click="router.push('/mon-espace')"
      class="inline-flex items-center gap-1.5 text-sm text-gray-500 hover:text-gray-800 mb-6 cursor-pointer transition-colors"
    >
      <ArrowLeft :size="16" />
      Retour au tableau de bord
    </button>

    <!-- ── Demande en attente ── -->
    <div v-if="membershipStatus === 'pending'" class="bg-white border border-gray-300/80 rounded-2xl p-8 text-center shadow-sm">
      <div class="w-16 h-16 rounded-full bg-amber-50 flex items-center justify-center mx-auto mb-5">
        <Clock :size="32" class="text-amber-500" />
      </div>
      <h2 class="text-xl font-extrabold text-gray-900 mb-3">Demande en cours de traitement</h2>
      <p class="text-sm text-gray-500 max-w-md mx-auto">
        Votre demande d'adhésion a bien été reçue. Notre équipe l'examine actuellement. Vous serez notifié par email dès qu'une décision sera prise.
      </p>
    </div>

    <!-- ── Demande rejetée ── -->
    <div v-else-if="membershipStatus === 'rejected'" class="bg-white border border-gray-300/80 rounded-2xl p-8 text-center shadow-sm">
      <div class="w-16 h-16 rounded-full bg-red-50 flex items-center justify-center mx-auto mb-5">
        <XCircle :size="32" class="text-red-500" />
      </div>
      <h2 class="text-xl font-extrabold text-gray-900 mb-3">Demande non acceptée</h2>
      <p class="text-sm text-gray-500 max-w-md mx-auto mb-5">
        Votre demande d'adhésion n'a pas été retenue. Vous pouvez nous contacter pour plus d'informations ou soumettre une nouvelle demande.
      </p>
    </div>

    <!-- ── Formulaire ── -->
    <div v-else class="bg-white border border-gray-300/80 rounded-2xl p-8 shadow-sm">
      <div class="text-center mb-8">
        <h2 class="text-xl font-extrabold text-gray-900 mb-2">Devenir membre officiel du FPP</h2>
        <p class="text-sm text-gray-500 mb-3">
          Complétez votre dossier pour devenir membre officiel du FPP et recevoir votre carte.
        </p>
        <button
          type="button"
          @click="downloadMembershipPdf"
          :disabled="pdfDownloading"
          class="inline-flex items-center gap-1.5 text-sm text-green-600 font-semibold hover:underline cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <Loader2 v-if="pdfDownloading" :size="14" class="animate-spin" />
          <FileDown v-else :size="14" />
          Télécharger le formulaire d'adhésion (PDF)
        </button>
      </div>

      <form @submit.prevent="handleSubmit" class="space-y-5">
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-5">
          <div>
            <label class="block text-xs font-bold uppercase tracking-wide text-gray-500 mb-1.5">Type de pièce *</label>
            <select
              v-model="membershipForm.id_document_type"
              required
              class="w-full px-4 py-3 border border-gray-300 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-green-500 transition bg-white"
            >
              <option v-for="doc in documentTypes" :key="doc.value" :value="doc.value">{{ doc.label }}</option>
            </select>
          </div>
          <div>
            <label class="block text-xs font-bold uppercase tracking-wide text-gray-500 mb-1.5">N° du document *</label>
            <input
              v-model="membershipForm.id_document_number"
              required
              type="text"
              class="w-full px-4 py-3 border border-gray-300 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-green-500 transition"
            >
          </div>
        </div>

        <div class="grid grid-cols-1 sm:grid-cols-2 gap-5">
          <!-- Photo d'identité -->
          <div>
            <label class="block text-xs font-bold uppercase tracking-wide text-gray-500 mb-1.5">Photo d'identité *</label>

            <div v-if="photoPreview" class="relative group rounded-xl border border-gray-200 overflow-hidden bg-gray-50">
              <img :src="photoPreview" alt="Aperçu photo" class="w-full h-44 object-contain bg-white" />
              <div class="absolute inset-0 bg-black/0 group-hover:bg-black/40 transition-colors flex items-center justify-center gap-2 opacity-0 group-hover:opacity-100">
                <label class="p-2 bg-white rounded-full shadow cursor-pointer hover:bg-gray-100 transition" title="Modifier">
                  <Upload :size="16" class="text-gray-700" />
                  <input ref="photoInputRef" type="file" accept="image/jpeg,image/png,image/webp" class="hidden" @change="onFileChange('photo', $event)">
                </label>
                <button type="button" @click="removeFile('photo')" class="p-2 bg-white rounded-full shadow cursor-pointer hover:bg-red-50 transition" title="Supprimer">
                  <X :size="16" class="text-red-500" />
                </button>
              </div>
              <div class="px-3 py-2 border-t border-gray-200 flex items-center gap-2">
                <ImageIcon :size="14" class="text-gray-400 shrink-0" />
                <span class="text-xs text-gray-600 truncate flex-1">{{ photoFile?.name }}</span>
                <span class="text-xs text-gray-400 shrink-0">{{ photoFile ? formatFileSize(photoFile.size) : '' }}</span>
              </div>
            </div>

            <label v-else class="flex flex-col items-center justify-center gap-2 px-4 py-6 border-2 border-dashed rounded-xl cursor-pointer transition"
              :class="photoError ? 'border-red-300 bg-red-50' : 'border-gray-300 hover:border-green-500 hover:bg-green-50/30'"
            >
              <Upload :size="24" :class="photoError ? 'text-red-400' : 'text-gray-400'" />
              <span class="text-sm font-medium" :class="photoError ? 'text-red-500' : 'text-gray-500'">Choisir une photo</span>
              <input ref="photoInputRef" type="file" accept="image/jpeg,image/png,image/webp" class="hidden" @change="onFileChange('photo', $event)">
            </label>

            <p v-if="photoError" class="mt-1.5 flex items-start gap-1 text-xs text-red-500">
              <AlertCircle :size="13" class="shrink-0 mt-0.5" /> {{ photoError }}
            </p>
            <p v-else class="mt-1.5 text-xs text-gray-400">
              Formats : {{ ALLOWED_EXTENSIONS }} — Max {{ MAX_SIZE_MB }} Mo
            </p>
          </div>

          <!-- Scan de la pièce -->
          <div>
            <label class="block text-xs font-bold uppercase tracking-wide text-gray-500 mb-1.5">Scan de la pièce *</label>

            <div v-if="idScanPreview" class="relative group rounded-xl border border-gray-200 overflow-hidden bg-gray-50">
              <img :src="idScanPreview" alt="Aperçu scan" class="w-full h-44 object-contain bg-white" />
              <div class="absolute inset-0 bg-black/0 group-hover:bg-black/40 transition-colors flex items-center justify-center gap-2 opacity-0 group-hover:opacity-100">
                <label class="p-2 bg-white rounded-full shadow cursor-pointer hover:bg-gray-100 transition" title="Modifier">
                  <Upload :size="16" class="text-gray-700" />
                  <input ref="idScanInputRef" type="file" accept="image/jpeg,image/png,image/webp" class="hidden" @change="onFileChange('scan', $event)">
                </label>
                <button type="button" @click="removeFile('scan')" class="p-2 bg-white rounded-full shadow cursor-pointer hover:bg-red-50 transition" title="Supprimer">
                  <X :size="16" class="text-red-500" />
                </button>
              </div>
              <div class="px-3 py-2 border-t border-gray-200 flex items-center gap-2">
                <ImageIcon :size="14" class="text-gray-400 shrink-0" />
                <span class="text-xs text-gray-600 truncate flex-1">{{ idScanFile?.name }}</span>
                <span class="text-xs text-gray-400 shrink-0">{{ idScanFile ? formatFileSize(idScanFile.size) : '' }}</span>
              </div>
            </div>

            <label v-else class="flex flex-col items-center justify-center gap-2 px-4 py-6 border-2 border-dashed rounded-xl cursor-pointer transition"
              :class="idScanError ? 'border-red-300 bg-red-50' : 'border-gray-300 hover:border-green-500 hover:bg-green-50/30'"
            >
              <Upload :size="24" :class="idScanError ? 'text-red-400' : 'text-gray-400'" />
              <span class="text-sm font-medium" :class="idScanError ? 'text-red-500' : 'text-gray-500'">Choisir un fichier</span>
              <input ref="idScanInputRef" type="file" accept="image/jpeg,image/png,image/webp" class="hidden" @change="onFileChange('scan', $event)">
            </label>

            <p v-if="idScanError" class="mt-1.5 flex items-start gap-1 text-xs text-red-500">
              <AlertCircle :size="13" class="shrink-0 mt-0.5" /> {{ idScanError }}
            </p>
            <p v-else class="mt-1.5 text-xs text-gray-400">
              Formats : {{ ALLOWED_EXTENSIONS }} — Max {{ MAX_SIZE_MB }} Mo
            </p>
          </div>
        </div>

        <div class="grid grid-cols-1 sm:grid-cols-2 gap-5">
          <div>
            <label class="block text-xs font-bold uppercase tracking-wide text-gray-500 mb-1.5">Ville *</label>
            <input v-model="membershipForm.city" required type="text" class="w-full px-4 py-3 border border-gray-300 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-green-500 transition">
          </div>
          <div>
            <label class="block text-xs font-bold uppercase tracking-wide text-gray-500 mb-1.5">Commune *</label>
            <input v-model="membershipForm.commune" required type="text" class="w-full px-4 py-3 border border-gray-300 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-green-500 transition">
          </div>
        </div>

        <div class="grid grid-cols-1 sm:grid-cols-2 gap-5">
          <div>
            <label class="block text-xs font-bold uppercase tracking-wide text-gray-500 mb-1.5">Région</label>
            <input v-model="membershipForm.region" type="text" class="w-full px-4 py-3 border border-gray-300 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-green-500 transition">
          </div>
          <div>
            <label class="block text-xs font-bold uppercase tracking-wide text-gray-500 mb-1.5">Quartier</label>
            <input v-model="membershipForm.neighborhood" type="text" class="w-full px-4 py-3 border border-gray-300 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-green-500 transition">
          </div>
        </div>

        <div>
          <label class="block text-xs font-bold uppercase tracking-wide text-gray-500 mb-1.5">Profession</label>
          <input v-model="membershipForm.profession" type="text" class="w-full px-4 py-3 border border-gray-300 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-green-500 transition">
        </div>

        <div>
          <label class="block text-xs font-bold uppercase tracking-wide text-gray-500 mb-1.5">Motivation</label>
          <textarea
            v-model="membershipForm.motivation"
            rows="3"
            class="w-full px-4 py-3 border border-gray-300 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-green-500 transition resize-none"
            placeholder="Pourquoi souhaitez-vous rejoindre le FPP ?"
          ></textarea>
        </div>

        <button
          type="submit"
          :disabled="submitting"
          class="w-full flex items-center justify-center gap-2 px-6 py-3.5 text-sm font-bold uppercase tracking-wide bg-green-600 text-white rounded-xl transition-all hover:bg-green-500 cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <Loader2 v-if="submitting" :size="18" class="animate-spin" />
          <template v-else>
            Soumettre ma demande
            <ArrowRight :size="18" />
          </template>
        </button>
      </form>
    </div>
  </div>
</template>
