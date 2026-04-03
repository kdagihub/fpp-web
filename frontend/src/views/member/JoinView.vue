<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
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

const documentTypes = [
  { value: 'cni', label: "Carte Nationale d'Identité" },
  { value: 'passport', label: 'Passeport' },
  { value: 'driver_license', label: 'Permis de conduire' },
]

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

function onFileChange(type: 'photo' | 'scan', event: Event) {
  const target = event.target as HTMLInputElement
  const file = target.files?.[0] ?? null
  if (type === 'photo') photoFile.value = file
  else idScanFile.value = file
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
        <p class="text-sm text-gray-500">
          Complétez votre dossier pour devenir membre officiel du FPP et recevoir votre carte.
        </p>
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
          <div>
            <label class="block text-xs font-bold uppercase tracking-wide text-gray-500 mb-1.5">Photo d'identité *</label>
            <label class="flex items-center gap-3 px-4 py-3 border border-dashed border-gray-300 rounded-xl cursor-pointer hover:border-green-500 transition">
              <Upload :size="18" class="text-gray-400" />
              <span class="text-sm text-gray-500 truncate">{{ photoFile?.name ?? 'Choisir un fichier' }}</span>
              <input type="file" accept="image/*" class="hidden" @change="onFileChange('photo', $event)">
            </label>
          </div>
          <div>
            <label class="block text-xs font-bold uppercase tracking-wide text-gray-500 mb-1.5">Scan de la pièce *</label>
            <label class="flex items-center gap-3 px-4 py-3 border border-dashed border-gray-300 rounded-xl cursor-pointer hover:border-green-500 transition">
              <Upload :size="18" class="text-gray-400" />
              <span class="text-sm text-gray-500 truncate">{{ idScanFile?.name ?? 'Choisir un fichier' }}</span>
              <input type="file" accept="image/jpeg,image/png,image/webp" class="hidden" @change="onFileChange('scan', $event)">
            </label>
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
