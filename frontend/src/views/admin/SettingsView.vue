<script setup lang="ts">
import { ref, reactive, onMounted, onUnmounted, computed } from 'vue'
import { useSettingsStore } from '@/stores/settings'
import { useAppToast } from '@/composables/useToast'
import { getMediaUrl } from '@/utils/media'
import {
  Save,
  Upload,
  X,
  Trash2,
  Building2,
  User,
  Phone,
  Globe,
  Image,
  FileText,
  Loader2,
  AlertCircle,
} from 'lucide-vue-next'

const settingsStore = useSettingsStore()
const toast = useAppToast()

const saving = ref(false)
const activeTab = ref<'identity' | 'president' | 'contact' | 'hero' | 'content'>('identity')

const tabs = [
  { id: 'identity' as const, label: 'Identité', icon: Building2 },
  { id: 'president' as const, label: 'Président', icon: User },
  { id: 'contact' as const, label: 'Contact', icon: Phone },
  { id: 'hero' as const, label: 'Accueil', icon: Image },
  { id: 'content' as const, label: 'Contenus', icon: FileText },
]

const form = reactive({
  site_name: '',
  slogan: '',
  president_name: '',
  president_message: '',
  whatsapp_number: '',
  contact_email: '',
  address: '',
  facebook_url: '',
  twitter_url: '',
  instagram_url: '',
  youtube_url: '',
  hero_title: '',
  hero_subtitle: '',
  about_text: '',
  vision_text: '',
  values_text: '',
})

const fileInputs = reactive<{
  logo: File | null
  hero_image: File | null
  president_photo: File | null
}>({
  logo: null,
  hero_image: null,
  president_photo: null,
})

const previews = reactive<{
  logo: string | null
  hero_image: string | null
  president_photo: string | null
}>({
  logo: null,
  hero_image: null,
  president_photo: null,
})

const existingImages = reactive<{
  logo: string | null
  hero_image: string | null
  president_photo: string | null
}>({
  logo: null,
  hero_image: null,
  president_photo: null,
})

const MAX_SIZE_MB = 5
const MAX_SIZE_BYTES = MAX_SIZE_MB * 1024 * 1024
const ALLOWED_TYPES = ['image/jpeg', 'image/png', 'image/webp']
const fileErrors = reactive<Record<string, string>>({ logo: '', hero_image: '', president_photo: '' })

function populateForm() {
  const s = settingsStore.settings
  if (!s) return
  form.site_name = s.site_name || ''
  form.slogan = s.slogan || ''
  form.president_name = s.president_name || ''
  form.president_message = s.president_message || ''
  form.whatsapp_number = s.whatsapp_number || ''
  form.contact_email = s.contact_email || ''
  form.address = s.address || ''
  form.facebook_url = s.facebook_url || ''
  form.twitter_url = s.twitter_url || ''
  form.instagram_url = s.instagram_url || ''
  form.youtube_url = s.youtube_url || ''
  form.hero_title = s.hero_title || ''
  form.hero_subtitle = s.hero_subtitle || ''
  form.about_text = s.about_text || ''
  form.vision_text = s.vision_text || ''
  form.values_text = s.values_text || ''

  existingImages.logo = s.logo || null
  existingImages.hero_image = s.hero_image || null
  existingImages.president_photo = s.president_photo || null
}

onMounted(async () => {
  await settingsStore.fetchAdminSettings()
  populateForm()
})

function onFileSelect(field: 'logo' | 'hero_image' | 'president_photo', event: Event) {
  const input = event.target as HTMLInputElement
  const file = input.files?.[0]
  if (!file) return

  fileErrors[field] = ''

  if (!ALLOWED_TYPES.includes(file.type)) {
    fileErrors[field] = 'Format non supporté. Utilisez JPG, PNG ou WebP.'
    input.value = ''
    return
  }
  if (file.size > MAX_SIZE_BYTES) {
    fileErrors[field] = `Fichier trop lourd (max ${MAX_SIZE_MB} Mo).`
    input.value = ''
    return
  }

  if (previews[field]) URL.revokeObjectURL(previews[field]!)
  fileInputs[field] = file
  previews[field] = URL.createObjectURL(file)
}

function removeFile(field: 'logo' | 'hero_image' | 'president_photo') {
  if (previews[field]) URL.revokeObjectURL(previews[field]!)
  fileInputs[field] = null
  previews[field] = null
  fileErrors[field] = ''
}

onUnmounted(() => {
  for (const key of ['logo', 'hero_image', 'president_photo'] as const) {
    if (previews[key]) URL.revokeObjectURL(previews[key]!)
  }
})

const imageUrl = computed(() => (field: 'logo' | 'hero_image' | 'president_photo') => {
  if (previews[field]) return previews[field]!
  if (existingImages[field]) return getMediaUrl(existingImages[field])
  return null
})

const hasChanges = computed(() => {
  if (!settingsStore.settings) return false
  const s = settingsStore.settings
  const textChanged = (
    form.site_name !== (s.site_name || '') ||
    form.slogan !== (s.slogan || '') ||
    form.president_name !== (s.president_name || '') ||
    form.president_message !== (s.president_message || '') ||
    form.whatsapp_number !== (s.whatsapp_number || '') ||
    form.contact_email !== (s.contact_email || '') ||
    form.address !== (s.address || '') ||
    form.facebook_url !== (s.facebook_url || '') ||
    form.twitter_url !== (s.twitter_url || '') ||
    form.instagram_url !== (s.instagram_url || '') ||
    form.youtube_url !== (s.youtube_url || '') ||
    form.hero_title !== (s.hero_title || '') ||
    form.hero_subtitle !== (s.hero_subtitle || '') ||
    form.about_text !== (s.about_text || '') ||
    form.vision_text !== (s.vision_text || '') ||
    form.values_text !== (s.values_text || '')
  )
  const filesChanged = !!(fileInputs.logo || fileInputs.hero_image || fileInputs.president_photo)
  return textChanged || filesChanged
})

async function handleSave() {
  saving.value = true
  try {
    const hasFiles = fileInputs.logo || fileInputs.hero_image || fileInputs.president_photo

    if (hasFiles) {
      const fd = new FormData()
      for (const [key, val] of Object.entries(form)) {
        fd.append(key, val)
      }
      if (fileInputs.logo) fd.append('logo', fileInputs.logo)
      if (fileInputs.hero_image) fd.append('hero_image', fileInputs.hero_image)
      if (fileInputs.president_photo) fd.append('president_photo', fileInputs.president_photo)
      await settingsStore.updateSettingsWithFiles(fd)
    } else {
      await settingsStore.updateSettings({ ...form })
    }

    fileInputs.logo = null
    fileInputs.hero_image = null
    fileInputs.president_photo = null
    for (const key of ['logo', 'hero_image', 'president_photo'] as const) {
      if (previews[key]) URL.revokeObjectURL(previews[key]!)
      previews[key] = null
    }
    populateForm()

    toast.success('Succès', 'Paramètres mis à jour avec succès.')
  } catch (err: any) {
    const detail = err?.response?.data?.detail || err?.response?.data
    toast.error('Erreur', typeof detail === 'string' ? detail : 'Impossible de sauvegarder les paramètres.')
  } finally {
    saving.value = false
  }
}
</script>

<template>
  <div>
    <!-- Header -->
    <div class="mb-5">
      <h2 class="font-heading text-xl sm:text-2xl font-bold text-[var(--color-primary)]">
        Paramètres du site
      </h2>
      <p class="text-xs sm:text-sm text-[var(--color-muted)] mt-0.5">
        Configurez les informations du site public.
      </p>
    </div>

    <!-- Loading -->
    <div v-if="settingsStore.loading" class="flex items-center justify-center py-20">
      <Loader2 :size="32" class="animate-spin text-[var(--color-accent)]" />
    </div>

    <template v-else>
      <!-- Tabs — scrollable, compact on mobile -->
      <div class="flex gap-1 mb-5 overflow-x-auto bg-white border border-gray-200 rounded-lg p-1 no-scrollbar">
        <button
          v-for="tab in tabs"
          :key="tab.id"
          @click="activeTab = tab.id"
          class="flex items-center gap-1.5 px-3 py-2 text-xs sm:text-sm font-medium rounded-md transition-all whitespace-nowrap cursor-pointer shrink-0"
          :class="activeTab === tab.id
            ? 'bg-[var(--color-accent)] text-white shadow-sm'
            : 'text-gray-500 hover:text-gray-800 hover:bg-gray-50'"
        >
          <component :is="tab.icon" :size="14" class="shrink-0" />
          <span>{{ tab.label }}</span>
        </button>
      </div>

      <!-- ═══ TAB: Identité ═══ -->
      <div v-show="activeTab === 'identity'">
        <div class="bg-white rounded-xl border border-gray-200 p-4 sm:p-6">
          <h3 class="text-sm font-bold text-gray-900 mb-4 flex items-center gap-2">
            <Building2 :size="16" class="text-[var(--color-accent)]" />
            Identité du parti
          </h3>

          <div class="grid grid-cols-1 lg:grid-cols-2 gap-4">
            <div>
              <label class="block text-xs font-bold uppercase tracking-wide text-gray-500 mb-1.5">Nom du site *</label>
              <input
                v-model="form.site_name"
                type="text"
                class="w-full px-3 py-2.5 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-[var(--color-accent)] focus:border-transparent outline-none transition"
                placeholder="FPP - Front Patriotique Panafricain"
              />
            </div>
            <div>
              <label class="block text-xs font-bold uppercase tracking-wide text-gray-500 mb-1.5">Slogan</label>
              <input
                v-model="form.slogan"
                type="text"
                class="w-full px-3 py-2.5 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-[var(--color-accent)] focus:border-transparent outline-none transition"
                placeholder="Notre slogan..."
              />
            </div>
          </div>

          <!-- Logo -->
          <div class="mt-5 pt-5 border-t border-gray-100">
            <label class="block text-xs font-bold uppercase tracking-wide text-gray-500 mb-2">Logo du parti</label>

            <div v-if="imageUrl('logo')" class="flex items-center gap-3">
              <img
                :src="imageUrl('logo')!"
                alt="Logo"
                class="w-16 h-16 sm:w-20 sm:h-20 object-contain rounded-lg border border-gray-200 bg-gray-50 shrink-0"
              />
              <div class="flex flex-col gap-1.5">
                <label class="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-gray-600 border border-gray-300 rounded-lg hover:bg-gray-50 transition cursor-pointer w-fit">
                  <Upload :size="13" /> Modifier
                  <input type="file" accept="image/jpeg,image/png,image/webp" class="hidden" @change="onFileSelect('logo', $event)" />
                </label>
                <button type="button" @click="removeFile('logo')" class="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-red-500 border border-red-200 rounded-lg hover:bg-red-50 transition cursor-pointer w-fit">
                  <Trash2 :size="13" /> Supprimer
                </button>
              </div>
            </div>

            <label v-else class="flex flex-col items-center justify-center gap-1.5 py-6 border-2 border-dashed border-gray-300 rounded-xl cursor-pointer hover:border-[var(--color-accent)] hover:bg-green-50/30 transition">
              <Upload :size="22" class="text-gray-400" />
              <span class="text-xs font-medium text-gray-500">Choisir un logo</span>
              <span class="text-[10px] text-gray-400">JPG, PNG ou WebP — Max {{ MAX_SIZE_MB }} Mo</span>
              <input type="file" accept="image/jpeg,image/png,image/webp" class="hidden" @change="onFileSelect('logo', $event)" />
            </label>

            <p v-if="fileErrors.logo" class="mt-1.5 flex items-center gap-1 text-xs text-red-500">
              <AlertCircle :size="12" /> {{ fileErrors.logo }}
            </p>
          </div>
        </div>
      </div>

      <!-- ═══ TAB: Président ═══ -->
      <div v-show="activeTab === 'president'">
        <div class="bg-white rounded-xl border border-gray-200 p-4 sm:p-6">
          <h3 class="text-sm font-bold text-gray-900 mb-4 flex items-center gap-2">
            <User :size="16" class="text-[var(--color-accent)]" />
            Mot du Président
          </h3>

          <!-- Photo — centered on mobile -->
          <div class="mb-5">
            <label class="block text-xs font-bold uppercase tracking-wide text-gray-500 mb-2">Photo</label>

            <div v-if="imageUrl('president_photo')" class="flex items-center gap-3">
              <img
                :src="imageUrl('president_photo')!"
                alt="Président"
                class="w-24 h-28 sm:w-32 sm:h-40 object-cover rounded-xl border border-gray-200 shrink-0"
              />
              <div class="flex flex-col gap-1.5">
                <label class="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-gray-600 border border-gray-300 rounded-lg hover:bg-gray-50 transition cursor-pointer w-fit">
                  <Upload :size="13" /> Modifier
                  <input type="file" accept="image/jpeg,image/png,image/webp" class="hidden" @change="onFileSelect('president_photo', $event)" />
                </label>
                <button type="button" @click="removeFile('president_photo')" class="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-red-500 border border-red-200 rounded-lg hover:bg-red-50 transition cursor-pointer w-fit">
                  <Trash2 :size="13" /> Supprimer
                </button>
              </div>
            </div>

            <label v-else class="flex flex-col items-center justify-center gap-1.5 py-8 border-2 border-dashed border-gray-300 rounded-xl cursor-pointer hover:border-[var(--color-accent)] hover:bg-green-50/30 transition">
              <Upload :size="22" class="text-gray-400" />
              <span class="text-xs font-medium text-gray-500">Ajouter une photo</span>
              <span class="text-[10px] text-gray-400">JPG, PNG ou WebP — Max {{ MAX_SIZE_MB }} Mo</span>
              <input type="file" accept="image/jpeg,image/png,image/webp" class="hidden" @change="onFileSelect('president_photo', $event)" />
            </label>

            <p v-if="fileErrors.president_photo" class="mt-1.5 flex items-center gap-1 text-xs text-red-500">
              <AlertCircle :size="12" /> {{ fileErrors.president_photo }}
            </p>
          </div>

          <!-- Name + Message -->
          <div class="space-y-4 pt-4 border-t border-gray-100">
            <div>
              <label class="block text-xs font-bold uppercase tracking-wide text-gray-500 mb-1.5">Nom complet</label>
              <input
                v-model="form.president_name"
                type="text"
                class="w-full px-3 py-2.5 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-[var(--color-accent)] focus:border-transparent outline-none transition"
                placeholder="Nom et prénom du président"
              />
            </div>
            <div>
              <label class="block text-xs font-bold uppercase tracking-wide text-gray-500 mb-1.5">Message du président</label>
              <textarea
                v-model="form.president_message"
                rows="5"
                class="w-full px-3 py-2.5 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-[var(--color-accent)] focus:border-transparent outline-none transition resize-y"
                placeholder="Message affiché sur la page d'accueil..."
              ></textarea>
              <p class="mt-1 text-[10px] sm:text-xs text-gray-400">Affiché dans la section « Mot du Président ».</p>
            </div>
          </div>
        </div>
      </div>

      <!-- ═══ TAB: Contact & Réseaux ═══ -->
      <div v-show="activeTab === 'contact'" class="space-y-4">
        <!-- Contact -->
        <div class="bg-white rounded-xl border border-gray-200 p-4 sm:p-6">
          <h3 class="text-sm font-bold text-gray-900 mb-4 flex items-center gap-2">
            <Phone :size="16" class="text-[var(--color-accent)]" />
            Contact
          </h3>

          <div class="grid grid-cols-1 lg:grid-cols-2 gap-4">
            <div>
              <label class="block text-xs font-bold uppercase tracking-wide text-gray-500 mb-1.5">Email</label>
              <input
                v-model="form.contact_email"
                type="email"
                class="w-full px-3 py-2.5 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-[var(--color-accent)] focus:border-transparent outline-none transition"
                placeholder="info@fpp-ci.online"
              />
            </div>
            <div>
              <label class="block text-xs font-bold uppercase tracking-wide text-gray-500 mb-1.5">WhatsApp / Téléphone</label>
              <input
                v-model="form.whatsapp_number"
                type="text"
                class="w-full px-3 py-2.5 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-[var(--color-accent)] focus:border-transparent outline-none transition"
                placeholder="+225 01 01 36 31 31"
              />
            </div>
          </div>

          <div class="mt-4">
            <label class="block text-xs font-bold uppercase tracking-wide text-gray-500 mb-1.5">Adresse</label>
            <textarea
              v-model="form.address"
              rows="2"
              class="w-full px-3 py-2.5 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-[var(--color-accent)] focus:border-transparent outline-none transition resize-y"
              placeholder="Abidjan, Côte d'Ivoire"
            ></textarea>
          </div>
        </div>

        <!-- Social -->
        <div class="bg-white rounded-xl border border-gray-200 p-4 sm:p-6">
          <h3 class="text-sm font-bold text-gray-900 mb-1 flex items-center gap-2">
            <Globe :size="16" class="text-[var(--color-accent)]" />
            Réseaux sociaux
          </h3>
          <p class="text-[10px] sm:text-xs text-gray-400 mb-4">Les liens vides ne seront pas affichés.</p>

          <div class="grid grid-cols-1 lg:grid-cols-2 gap-4">
            <div>
              <label class="block text-xs font-bold uppercase tracking-wide text-gray-500 mb-1.5">Facebook</label>
              <input
                v-model="form.facebook_url"
                type="url"
                class="w-full px-3 py-2.5 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-[var(--color-accent)] focus:border-transparent outline-none transition"
                placeholder="https://facebook.com/..."
              />
            </div>
            <div>
              <label class="block text-xs font-bold uppercase tracking-wide text-gray-500 mb-1.5">X / Twitter</label>
              <input
                v-model="form.twitter_url"
                type="url"
                class="w-full px-3 py-2.5 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-[var(--color-accent)] focus:border-transparent outline-none transition"
                placeholder="https://x.com/..."
              />
            </div>
            <div>
              <label class="block text-xs font-bold uppercase tracking-wide text-gray-500 mb-1.5">Instagram</label>
              <input
                v-model="form.instagram_url"
                type="url"
                class="w-full px-3 py-2.5 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-[var(--color-accent)] focus:border-transparent outline-none transition"
                placeholder="https://instagram.com/..."
              />
            </div>
            <div>
              <label class="block text-xs font-bold uppercase tracking-wide text-gray-500 mb-1.5">YouTube</label>
              <input
                v-model="form.youtube_url"
                type="url"
                class="w-full px-3 py-2.5 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-[var(--color-accent)] focus:border-transparent outline-none transition"
                placeholder="https://youtube.com/..."
              />
            </div>
          </div>
        </div>
      </div>

      <!-- ═══ TAB: Page d'accueil (Hero) ═══ -->
      <div v-show="activeTab === 'hero'">
        <div class="bg-white rounded-xl border border-gray-200 p-4 sm:p-6">
          <h3 class="text-sm font-bold text-gray-900 mb-4 flex items-center gap-2">
            <Image :size="16" class="text-[var(--color-accent)]" />
            Bannière d'accueil
          </h3>

          <!-- Hero image -->
          <div class="mb-5">
            <label class="block text-xs font-bold uppercase tracking-wide text-gray-500 mb-2">Image de fond</label>

            <div v-if="imageUrl('hero_image')">
              <div class="rounded-xl overflow-hidden border border-gray-200">
                <img :src="imageUrl('hero_image')!" alt="Hero" class="w-full h-32 sm:h-48 object-cover" />
              </div>
              <div class="flex gap-2 mt-2">
                <label class="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-gray-600 border border-gray-300 rounded-lg hover:bg-gray-50 transition cursor-pointer">
                  <Upload :size="13" /> Modifier
                  <input type="file" accept="image/jpeg,image/png,image/webp" class="hidden" @change="onFileSelect('hero_image', $event)" />
                </label>
                <button type="button" @click="removeFile('hero_image')" class="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-red-500 border border-red-200 rounded-lg hover:bg-red-50 transition cursor-pointer">
                  <Trash2 :size="13" /> Supprimer
                </button>
              </div>
            </div>

            <label v-else class="flex flex-col items-center justify-center gap-1.5 py-8 border-2 border-dashed border-gray-300 rounded-xl cursor-pointer hover:border-[var(--color-accent)] hover:bg-green-50/30 transition">
              <Upload :size="22" class="text-gray-400" />
              <span class="text-xs font-medium text-gray-500">Choisir une image</span>
              <span class="text-[10px] text-gray-400">1920×600px recommandé — JPG, PNG, WebP</span>
              <input type="file" accept="image/jpeg,image/png,image/webp" class="hidden" @change="onFileSelect('hero_image', $event)" />
            </label>

            <p v-if="fileErrors.hero_image" class="mt-1.5 flex items-center gap-1 text-xs text-red-500">
              <AlertCircle :size="12" /> {{ fileErrors.hero_image }}
            </p>
          </div>

          <div class="grid grid-cols-1 lg:grid-cols-2 gap-4 pt-4 border-t border-gray-100">
            <div>
              <label class="block text-xs font-bold uppercase tracking-wide text-gray-500 mb-1.5">Titre principal</label>
              <input
                v-model="form.hero_title"
                type="text"
                class="w-full px-3 py-2.5 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-[var(--color-accent)] focus:border-transparent outline-none transition"
                placeholder="Bienvenue sur le site du FPP"
              />
            </div>
            <div>
              <label class="block text-xs font-bold uppercase tracking-wide text-gray-500 mb-1.5">Sous-titre</label>
              <textarea
                v-model="form.hero_subtitle"
                rows="3"
                class="w-full px-3 py-2.5 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-[var(--color-accent)] focus:border-transparent outline-none transition resize-y"
                placeholder="Un message d'accroche..."
              ></textarea>
            </div>
          </div>
        </div>
      </div>

      <!-- ═══ TAB: Contenus ═══ -->
      <div v-show="activeTab === 'content'">
        <div class="bg-white rounded-xl border border-gray-200 p-4 sm:p-6">
          <h3 class="text-sm font-bold text-gray-900 mb-1 flex items-center gap-2">
            <FileText :size="16" class="text-[var(--color-accent)]" />
            Textes du site
          </h3>
          <p class="text-[10px] sm:text-xs text-gray-400 mb-4">Pages « À propos » et « Le Parti ».</p>

          <div class="space-y-5">
            <div>
              <label class="block text-xs font-bold uppercase tracking-wide text-gray-500 mb-1.5">À propos du parti</label>
              <textarea
                v-model="form.about_text"
                rows="4"
                class="w-full px-3 py-2.5 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-[var(--color-accent)] focus:border-transparent outline-none transition resize-y"
                placeholder="Présentation générale du parti..."
              ></textarea>
            </div>
            <div>
              <label class="block text-xs font-bold uppercase tracking-wide text-gray-500 mb-1.5">Notre vision</label>
              <textarea
                v-model="form.vision_text"
                rows="4"
                class="w-full px-3 py-2.5 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-[var(--color-accent)] focus:border-transparent outline-none transition resize-y"
                placeholder="La vision et les objectifs..."
              ></textarea>
            </div>
            <div>
              <label class="block text-xs font-bold uppercase tracking-wide text-gray-500 mb-1.5">Nos valeurs</label>
              <textarea
                v-model="form.values_text"
                rows="4"
                class="w-full px-3 py-2.5 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-[var(--color-accent)] focus:border-transparent outline-none transition resize-y"
                placeholder="Les valeurs fondamentales..."
              ></textarea>
            </div>
          </div>
        </div>
      </div>

      <!-- Sticky save bar -->
      <Transition
        enter-active-class="transition-all duration-300 ease-out"
        enter-from-class="translate-y-4 opacity-0"
        enter-to-class="translate-y-0 opacity-100"
        leave-active-class="transition-all duration-200 ease-in"
        leave-from-class="translate-y-0 opacity-100"
        leave-to-class="translate-y-4 opacity-0"
      >
        <div
          v-if="hasChanges"
          class="sticky bottom-0 mt-5 -mx-3 sm:-mx-6 bg-white border-t border-gray-200 px-3 sm:px-6 py-3 flex items-center justify-between gap-3 z-20 shadow-[0_-4px_12px_rgba(0,0,0,0.08)]"
        >
          <p class="text-xs sm:text-sm text-amber-600 font-medium flex items-center gap-1.5 min-w-0">
            <AlertCircle :size="14" class="shrink-0" />
            <span class="truncate">Modifications non enregistrées</span>
          </p>
          <button
            @click="handleSave"
            :disabled="saving"
            class="inline-flex items-center gap-1.5 px-4 py-2 text-xs sm:text-sm font-semibold bg-[var(--color-accent)] text-white rounded-lg hover:bg-[var(--color-accent-hover)] transition cursor-pointer disabled:opacity-50 shrink-0"
          >
            <Loader2 v-if="saving" :size="14" class="animate-spin" />
            <Save v-else :size="14" />
            Enregistrer
          </button>
        </div>
      </Transition>
    </template>
  </div>
</template>

<style scoped>
.no-scrollbar::-webkit-scrollbar { display: none; }
.no-scrollbar { -ms-overflow-style: none; scrollbar-width: none; }
</style>
