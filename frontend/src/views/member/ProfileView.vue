<script setup lang="ts">
import { computed, ref } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useAppToast } from '@/composables/useToast'
import { RouterLink } from 'vue-router'
import api from '@/api'
import { getMediaUrl } from '@/utils/media'
import {
  ArrowLeft,
  Camera,
  Save,
  Loader2,
  MapPin,
  Mail,
  Phone,
  Calendar,
  Briefcase,
  User,
} from 'lucide-vue-next'
import dayjs from 'dayjs'
import 'dayjs/locale/fr'

dayjs.locale('fr')

const authStore = useAuthStore()
const toast = useAppToast()
const user = computed(() => authStore.user)
const membership = computed(() => user.value?.membership)

const editing = ref(false)
const saving = ref(false)
const avatarFile = ref<File | null>(null)
const avatarPreview = ref<string | null>(null)

const form = ref({
  first_name: user.value?.first_name ?? '',
  last_name: user.value?.last_name ?? '',
  phone: user.value?.phone ?? '',
})

function startEdit() {
  form.value = {
    first_name: user.value?.first_name ?? '',
    last_name: user.value?.last_name ?? '',
    phone: user.value?.phone ?? '',
  }
  editing.value = true
}

function onAvatarChange(event: Event) {
  const target = event.target as HTMLInputElement
  const file = target.files?.[0]
  if (!file) return
  avatarFile.value = file
  avatarPreview.value = URL.createObjectURL(file)
}

async function handleSave() {
  saving.value = true
  try {
    const formData = new FormData()
    formData.append('first_name', form.value.first_name)
    formData.append('last_name', form.value.last_name)
    if (form.value.phone) formData.append('phone', form.value.phone)
    if (avatarFile.value) formData.append('avatar', avatarFile.value)

    await api.patch('/auth/me/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
    await authStore.fetchUser()
    editing.value = false
    avatarFile.value = null
    avatarPreview.value = null
    toast.success('Profil mis à jour', 'Vos informations ont été enregistrées.')
  } catch (err: any) {
    toast.error('Erreur', err?.response?.data?.detail || 'Impossible de mettre à jour le profil.')
  } finally {
    saving.value = false
  }
}

const infoItems = computed(() => [
  { icon: Mail, label: 'Email', value: user.value?.email, verified: user.value?.email_verified },
  { icon: Phone, label: 'Téléphone', value: user.value?.phone || 'Non renseigné' },
  { icon: User, label: 'Sexe', value: user.value?.sex === 'M' ? 'Homme' : user.value?.sex === 'F' ? 'Femme' : 'Non renseigné' },
  { icon: Calendar, label: 'Date de naissance', value: user.value?.date_of_birth ? dayjs(user.value.date_of_birth).format('D MMMM YYYY') : 'Non renseigné' },
  { icon: MapPin, label: 'Ville', value: membership.value ? `${membership.value.city}, ${membership.value.commune}` : 'Non renseigné' },
  { icon: Briefcase, label: 'Profession', value: membership.value?.profession || 'Non renseigné' },
])
</script>

<template>
  <div>
    <!-- Header -->
    <div class="flex items-center gap-3 mb-6 sm:mb-8">
      <RouterLink to="/mon-espace" class="w-9 h-9 rounded-xl bg-white border border-gray-200 flex items-center justify-center text-gray-500 hover:text-gray-900 hover:border-gray-300 transition-all no-underline">
        <ArrowLeft :size="18" />
      </RouterLink>
      <div>
        <h1 class="text-xl font-bold text-gray-900">Mon profil</h1>
        <p class="text-xs text-gray-500">Informations personnelles et adhésion</p>
      </div>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-3 gap-4 sm:gap-6">

      <!-- ─── AVATAR + IDENTITÉ ─── -->
      <div class="bg-white rounded-2xl border border-gray-200/80 p-4 sm:p-6 shadow-sm text-center">
        <div class="relative w-24 h-24 mx-auto mb-4">
          <div class="w-24 h-24 rounded-2xl bg-gradient-to-br from-green-400 to-green-600 flex items-center justify-center text-white text-2xl font-bold overflow-hidden shadow-md">
            <img
              v-if="avatarPreview || user?.avatar"
              :src="avatarPreview || getMediaUrl(user?.avatar)"
              class="w-full h-full object-cover"
              alt=""
            >
            <span v-else>{{ user?.first_name?.charAt(0) }}{{ user?.last_name?.charAt(0) }}</span>
          </div>
          <label
            v-if="editing"
            class="absolute -bottom-1 -right-1 w-8 h-8 rounded-full bg-gray-900 flex items-center justify-center cursor-pointer hover:bg-gray-700 transition-colors shadow-md"
          >
            <Camera :size="14" class="text-white" />
            <input type="file" accept="image/*" class="hidden" @change="onAvatarChange">
          </label>
        </div>

        <template v-if="!editing">
          <h2 class="text-lg font-bold text-gray-900">{{ user?.first_name }} {{ user?.last_name }}</h2>
          <p v-if="membership?.matricule" class="text-xs font-mono text-green-600 mt-1">{{ membership.matricule }}</p>
          <span
            class="inline-flex items-center gap-1.5 text-[11px] font-semibold uppercase tracking-wide px-2.5 py-1 rounded-full mt-3"
            :class="{
              'bg-green-50 text-green-700': membership?.status === 'validated',
              'bg-amber-50 text-amber-700': membership?.status === 'pending',
              'bg-red-50 text-red-700': membership?.status === 'rejected',
              'bg-gray-100 text-gray-500': !membership,
            }"
          >
            <span class="w-1.5 h-1.5 rounded-full" :class="{
              'bg-green-500': membership?.status === 'validated',
              'bg-amber-500': membership?.status === 'pending',
              'bg-red-500': membership?.status === 'rejected',
              'bg-gray-400': !membership,
            }" />
            {{ membership?.status === 'validated' ? 'Membre actif' : membership?.status === 'pending' ? 'En attente' : membership?.status === 'rejected' ? 'Refusé' : 'Partisan sympathisant' }}
          </span>
          <button
            @click="startEdit"
            class="mt-5 w-full py-2.5 text-sm font-semibold text-gray-700 bg-gray-50 rounded-xl hover:bg-gray-100 transition-colors cursor-pointer"
          >
            Modifier le profil
          </button>
        </template>

        <template v-else>
          <div class="space-y-3 text-left mt-2">
            <div>
              <label class="text-[11px] font-semibold text-gray-500 uppercase tracking-wide">Prénom</label>
              <input v-model="form.first_name" type="text" class="w-full mt-1 px-3 py-2 text-sm border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-400/50">
            </div>
            <div>
              <label class="text-[11px] font-semibold text-gray-500 uppercase tracking-wide">Nom</label>
              <input v-model="form.last_name" type="text" class="w-full mt-1 px-3 py-2 text-sm border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-400/50">
            </div>
            <div>
              <label class="text-[11px] font-semibold text-gray-500 uppercase tracking-wide">Téléphone</label>
              <input v-model="form.phone" type="tel" class="w-full mt-1 px-3 py-2 text-sm border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-400/50">
            </div>
          </div>
          <div class="flex gap-2 mt-5">
            <button
              @click="editing = false; avatarPreview = null; avatarFile = null"
              class="flex-1 py-2.5 text-sm font-semibold text-gray-600 bg-gray-50 rounded-xl hover:bg-gray-100 transition-colors cursor-pointer"
            >
              Annuler
            </button>
            <button
              @click="handleSave"
              :disabled="saving"
              class="flex-1 flex items-center justify-center gap-1.5 py-2.5 text-sm font-semibold text-white bg-green-600 rounded-xl hover:bg-green-700 transition-colors cursor-pointer disabled:opacity-50"
            >
              <Loader2 v-if="saving" :size="14" class="animate-spin" />
              <Save v-else :size="14" />
              Enregistrer
            </button>
          </div>
        </template>
      </div>

      <!-- ─── INFORMATIONS DÉTAILLÉES ─── -->
      <div class="lg:col-span-2 bg-white rounded-2xl border border-gray-200/80 p-4 sm:p-6 shadow-sm">
        <h3 class="text-sm font-bold text-gray-900 uppercase tracking-wide mb-4 sm:mb-5">Informations personnelles</h3>
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div
            v-for="(item, i) in infoItems"
            :key="i"
            class="flex items-start gap-3 p-3 rounded-xl bg-gray-50/80"
          >
            <div class="w-9 h-9 rounded-lg bg-white border border-gray-100 flex items-center justify-center shrink-0">
              <component :is="item.icon" :size="16" class="text-gray-500" />
            </div>
            <div class="min-w-0">
              <p class="text-[11px] font-semibold text-gray-400 uppercase tracking-wide">{{ item.label }}</p>
              <p class="text-sm text-gray-800 font-medium truncate mt-0.5">{{ item.value }}</p>
              <span
                v-if="item.label === 'Email' && item.verified"
                class="text-[10px] text-green-600 font-semibold"
              >
                Vérifié
              </span>
            </div>
          </div>
        </div>

        <!-- Adhésion section -->
        <div v-if="membership" class="mt-5 pt-5 sm:mt-6 sm:pt-6 border-t border-gray-100">
          <h3 class="text-sm font-bold text-gray-900 uppercase tracking-wide mb-3 sm:mb-4">Détails de l'adhésion</h3>
          <div class="grid grid-cols-1 sm:grid-cols-3 gap-3 sm:gap-4">
            <div class="p-3 rounded-xl bg-gray-50/80">
              <p class="text-[11px] font-semibold text-gray-400 uppercase tracking-wide">Document d'identité</p>
              <p class="text-sm text-gray-800 font-medium mt-0.5">{{ membership.id_document_type?.toUpperCase() }}</p>
              <p class="text-xs text-gray-500 font-mono">{{ membership.id_document_number }}</p>
            </div>
            <div class="p-3 rounded-xl bg-gray-50/80">
              <p class="text-[11px] font-semibold text-gray-400 uppercase tracking-wide">Région</p>
              <p class="text-sm text-gray-800 font-medium mt-0.5">{{ membership.region || 'Non renseigné' }}</p>
            </div>
            <div class="p-3 rounded-xl bg-gray-50/80">
              <p class="text-[11px] font-semibold text-gray-400 uppercase tracking-wide">Date d'adhésion</p>
              <p class="text-sm text-gray-800 font-medium mt-0.5">
                {{ membership.membership_validated_at ? dayjs(membership.membership_validated_at).format('D MMMM YYYY') : 'En attente' }}
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
