<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { RouterLink } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useAppToast } from '@/composables/useToast'
import {
  ArrowRight,
  Users,
  CalendarDays,
  Megaphone,
  BookOpen,
  FileDown,
  CheckCircle2,
  Loader2,
  Eye,
  EyeOff,
  ChevronDown,
  Search,
} from 'lucide-vue-next'

const authStore = useAuthStore()
const toast = useAppToast()

const step = ref<'register' | 'success'>('register')
const submitting = ref(false)
const showPwd = ref(false)
const showConfirm = ref(false)
const phoneError = ref('')

interface Country { name: string; code: string; dial: string; flag: string }

const countries: Country[] = [
  { name: "Côte d'Ivoire", code: 'CI', dial: '+225', flag: '🇨🇮' },
  { name: 'Sénégal', code: 'SN', dial: '+221', flag: '🇸🇳' },
  { name: 'Mali', code: 'ML', dial: '+223', flag: '🇲🇱' },
  { name: 'Burkina Faso', code: 'BF', dial: '+226', flag: '🇧🇫' },
  { name: 'Guinée', code: 'GN', dial: '+224', flag: '🇬🇳' },
  { name: 'Ghana', code: 'GH', dial: '+233', flag: '🇬🇭' },
  { name: 'Togo', code: 'TG', dial: '+228', flag: '🇹🇬' },
  { name: 'Bénin', code: 'BJ', dial: '+229', flag: '🇧🇯' },
  { name: 'Niger', code: 'NE', dial: '+227', flag: '🇳🇪' },
  { name: 'Nigeria', code: 'NG', dial: '+234', flag: '🇳🇬' },
  { name: 'Cameroun', code: 'CM', dial: '+237', flag: '🇨🇲' },
  { name: 'Gabon', code: 'GA', dial: '+241', flag: '🇬🇦' },
  { name: 'Congo', code: 'CG', dial: '+242', flag: '🇨🇬' },
  { name: 'RD Congo', code: 'CD', dial: '+243', flag: '🇨🇩' },
  { name: 'Maroc', code: 'MA', dial: '+212', flag: '🇲🇦' },
  { name: 'Tunisie', code: 'TN', dial: '+216', flag: '🇹🇳' },
  { name: 'Algérie', code: 'DZ', dial: '+213', flag: '🇩🇿' },
  { name: 'France', code: 'FR', dial: '+33', flag: '🇫🇷' },
  { name: 'Belgique', code: 'BE', dial: '+32', flag: '🇧🇪' },
  { name: 'Suisse', code: 'CH', dial: '+41', flag: '🇨🇭' },
  { name: 'Canada', code: 'CA', dial: '+1', flag: '🇨🇦' },
  { name: 'Allemagne', code: 'DE', dial: '+49', flag: '🇩🇪' },
  { name: 'États-Unis', code: 'US', dial: '+1', flag: '🇺🇸' },
]

const selectedCountry = ref<Country>(countries[0]!)
const phoneDropdownOpen = ref(false)
const phoneSearch = ref('')
const phoneDropdownRef = ref<HTMLElement | null>(null)
const phoneSearchRef = ref<HTMLInputElement | null>(null)

const filteredCountries = computed(() => {
  const q = phoneSearch.value.toLowerCase()
  if (!q) return countries
  return countries.filter(c =>
    c.name.toLowerCase().includes(q) || c.dial.includes(q) || c.code.toLowerCase().includes(q)
  )
})

function selectCountry(c: Country) {
  selectedCountry.value = c
  phoneDropdownOpen.value = false
  phoneSearch.value = ''
}

function togglePhoneDropdown() {
  phoneDropdownOpen.value = !phoneDropdownOpen.value
  if (phoneDropdownOpen.value) {
    setTimeout(() => phoneSearchRef.value?.focus(), 50)
  }
}

function onClickOutside(e: MouseEvent) {
  if (phoneDropdownRef.value && !phoneDropdownRef.value.contains(e.target as Node)) {
    phoneDropdownOpen.value = false
    phoneSearch.value = ''
  }
}

onMounted(() => document.addEventListener('click', onClickOutside))
onUnmounted(() => document.removeEventListener('click', onClickOutside))

const phoneNumber = ref('')

function validatePhone(): boolean {
  const num = phoneNumber.value.trim()
  if (!num) {
    phoneError.value = ''
    return true
  }
  if (!/^[0-9]{6,15}$/.test(num.replace(/[\s\-]/g, ''))) {
    phoneError.value = 'Numéro invalide. Saisissez uniquement les chiffres sans l\'indicatif.'
    return false
  }
  phoneError.value = ''
  return true
}

function onPhoneInput(e: Event) {
  const input = e.target as HTMLInputElement
  phoneNumber.value = input.value.replace(/[^\d\s\-]/g, '')
  validatePhone()
}

const fullPhone = computed(() => {
  const num = phoneNumber.value.replace(/[\s\-]/g, '')
  if (!num) return ''
  return `${selectedCountry.value.dial}${num}`
})

const cguAccepted = ref(false)

/* ── Registration form ── */
const registerForm = ref({
  first_name: '',
  last_name: '',
  email: '',
  sex: '' as 'M' | 'F' | '',
  date_of_birth: '',
  password: '',
  password_confirm: '',
})

const benefits = [
  { icon: Users, title: 'Participez à la révolution', text: 'Engagez-vous considérablement dans la lutte pour la décolonisation, la souveraineté, l\'indépendance, le progrès et le développement de la Côte d\'Ivoire.' },
  { icon: CalendarDays, title: 'Accès aux événements', text: 'Participez à nos conférences, séminaires et rencontres exclusives.' },
  { icon: Megaphone, title: 'Rejoindre la communauté', text: 'Intégrez un réseau de citoyens engagés sur tout le territoire.' },
  { icon: BookOpen, title: 'Rester informé', text: 'Recevez nos publications, analyses et notes de positionnement en avant-première.' },
]

async function handleRegister() {
  if (phoneNumber.value && !validatePhone()) {
    toast.error('Erreur', phoneError.value)
    return
  }
  if (registerForm.value.password !== registerForm.value.password_confirm) {
    toast.error('Erreur', 'Les mots de passe ne correspondent pas.')
    return
  }
  submitting.value = true
  try {
    await authStore.register({
      first_name: registerForm.value.first_name,
      last_name: registerForm.value.last_name,
      email: registerForm.value.email,
      phone: fullPhone.value || undefined,
      sex: registerForm.value.sex as 'M' | 'F',
      date_of_birth: registerForm.value.date_of_birth,
      password: registerForm.value.password,
      password_confirm: registerForm.value.password_confirm,
      cgu_accepted: cguAccepted.value,
    })
    step.value = 'success'
    toast.success('Inscription réussie', 'Vérifiez votre email pour activer votre compte. Pensez à regarder dans les spams.')
  } catch (err: any) {
    const msg = err?.response?.data?.detail || err?.response?.data?.email?.[0] || 'Erreur lors de l\'inscription.'
    toast.error('Erreur', msg)
  } finally {
    submitting.value = false
  }
}

const pdfDownloading = ref<'registration' | 'membership' | null>(null)

async function downloadPdf(type: 'registration' | 'membership') {
  pdfDownloading.value = type
  const endpoint = type === 'registration'
    ? '/public/registration-form/pdf/'
    : '/public/membership-form/pdf/'
  const filename = type === 'registration'
    ? 'Fiche-Inscription-FPP.pdf'
    : 'Formulaire-Adhesion-FPP.pdf'
  try {
    const { default: api } = await import('@/api')
    const response = await api.get(endpoint, { responseType: 'blob' })
    const url = URL.createObjectURL(response.data)
    const a = document.createElement('a')
    a.href = url
    a.download = filename
    a.click()
    URL.revokeObjectURL(url)
  } catch {
    toast.error('Erreur', 'Le téléchargement du formulaire a échoué. Réessayez plus tard.')
  } finally {
    pdfDownloading.value = null
  }
}
</script>

<template>
  <div>
    <!-- ════════════════════ HERO ════════════════════ -->
    <section class="relative bg-[var(--color-primary)] py-20 md:py-28 overflow-hidden">
      <div class="absolute inset-0 bg-[radial-gradient(ellipse_at_top_right,rgba(22,163,74,0.12),transparent_60%)]" />
      <div class="relative mx-auto max-w-[var(--container-xl)] px-6 text-center">
        <p class="font-heading text-xs font-bold uppercase tracking-[0.15em] text-[var(--color-accent)] mb-4">
          Rejoignez le Parti
        </p>
        <h1 class="font-heading text-4xl md:text-5xl font-extrabold text-white leading-tight mb-5">
          Devenez membre du <span class="text-[var(--color-accent)]">FPP</span>
        </h1>
        <p class="text-lg text-white/60 max-w-xl mx-auto">
          Rejoignez les milliers de camarades engagés pour bâtir une Côte d'Ivoire décolonisée, souveraine, indépendante, prospère, développée et résolument tournée vers l'avenir.
        </p>
      </div>
    </section>

    <!-- ════════════════════ POURQUOI ADHERER ════════════════════ -->
    <section class="bg-white py-16 md:py-20 border-b border-[var(--color-border)]">
      <div class="mx-auto max-w-[var(--container-xl)] px-6">
        <h2 class="font-heading text-2xl md:text-3xl font-extrabold text-[var(--color-primary)] text-center mb-12">
          Pourquoi adhérer ?
        </h2>
        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
          <div
            v-for="(benefit, i) in benefits"
            :key="i"
            class="text-center p-6 bg-[var(--color-surface)] rounded-xl"
          >
            <div class="w-12 h-12 rounded-full bg-[var(--color-accent-light)] flex items-center justify-center mx-auto mb-4">
              <component :is="benefit.icon" :size="22" class="text-[var(--color-accent)]" />
            </div>
            <h3 class="font-heading text-sm font-bold text-[var(--color-primary)] mb-2">
              {{ benefit.title }}
            </h3>
            <p class="text-xs text-[var(--color-muted)] leading-relaxed">
              {{ benefit.text }}
            </p>
          </div>
        </div>
      </div>
    </section>

    <!-- ════════════════════ FORMULAIRE ════════════════════ -->
    <section class="bg-[var(--color-surface)] py-16 md:py-20">
      <div class="mx-auto max-w-[var(--container-md)] px-6">

        <!-- ── STEP: REGISTER ── -->
        <div v-if="step === 'register'">
          <div class="bg-white border border-[var(--color-border)] rounded-xl p-8 md:p-10">
            <div class="text-center mb-8">
              <h2 class="font-heading text-2xl font-extrabold text-[var(--color-primary)] mb-2">
                Créez votre compte
              </h2>
              <p class="text-sm text-[var(--color-muted)]">
                Déjà un compte ?
                <RouterLink to="/login" class="text-[var(--color-accent)] font-semibold no-underline hover:underline">
                  Connectez-vous
                </RouterLink>
              </p>
              <div class="flex items-center gap-3 mt-5 mb-2">
                <div class="flex-1 h-px bg-[var(--color-border)]" />
                <span class="text-xs font-semibold uppercase tracking-wide text-[var(--color-muted)]">ou téléchargez les fiches</span>
                <div class="flex-1 h-px bg-[var(--color-border)]" />
              </div>
              <div class="flex flex-col sm:flex-row items-center justify-center gap-2">
                <button
                  type="button"
                  @click="downloadPdf('registration')"
                  :disabled="!!pdfDownloading"
                  class="inline-flex items-center gap-1.5 text-sm text-[var(--color-accent)] font-semibold hover:underline cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <Loader2 v-if="pdfDownloading === 'registration'" :size="14" class="animate-spin" />
                  <FileDown v-else :size="14" />
                  Fiche d'inscription (PDF)
                </button>
                <span class="hidden sm:inline text-[var(--color-muted)]">•</span>
                <button
                  type="button"
                  @click="downloadPdf('membership')"
                  :disabled="!!pdfDownloading"
                  class="inline-flex items-center gap-1.5 text-sm text-[var(--color-accent)] font-semibold hover:underline cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <Loader2 v-if="pdfDownloading === 'membership'" :size="14" class="animate-spin" />
                  <FileDown v-else :size="14" />
                  Formulaire d'adhésion (PDF)
                </button>
              </div>
            </div>

            <form @submit.prevent="handleRegister" class="space-y-5">
              <div class="grid grid-cols-1 sm:grid-cols-2 gap-5">
                <div>
                  <label class="block font-heading text-xs font-bold uppercase tracking-[0.06em] text-[var(--color-muted)] mb-1.5">Prénom *</label>
                  <input v-model="registerForm.first_name" required type="text" class="w-full px-4 py-3 border border-[var(--color-border)] rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-[var(--color-accent)] transition">
                </div>
                <div>
                  <label class="block font-heading text-xs font-bold uppercase tracking-[0.06em] text-[var(--color-muted)] mb-1.5">Nom *</label>
                  <input v-model="registerForm.last_name" required type="text" class="w-full px-4 py-3 border border-[var(--color-border)] rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-[var(--color-accent)] transition">
                </div>
              </div>

              <div>
                <label class="block font-heading text-xs font-bold uppercase tracking-[0.06em] text-[var(--color-muted)] mb-1.5">Email *</label>
                <input v-model="registerForm.email" required type="email" class="w-full px-4 py-3 border border-[var(--color-border)] rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-[var(--color-accent)] transition">
              </div>

              <div class="grid grid-cols-1 sm:grid-cols-2 gap-5">
                <div>
                  <label class="block font-heading text-xs font-bold uppercase tracking-[0.06em] text-[var(--color-muted)] mb-1.5">Téléphone</label>
                  <div ref="phoneDropdownRef" class="relative">
                    <div
                      class="flex border rounded-lg overflow-hidden transition"
                      :class="phoneError ? 'border-red-400 ring-1 ring-red-300' : 'border-[var(--color-border)] focus-within:ring-2 focus-within:ring-[var(--color-accent)] focus-within:border-[var(--color-accent)]'"
                    >
                      <button
                        type="button"
                        @click.stop="togglePhoneDropdown"
                        class="flex items-center gap-1 px-3 py-3 bg-[var(--color-surface)] border-r border-[var(--color-border)] hover:bg-gray-100 transition-colors cursor-pointer shrink-0"
                      >
                        <span class="text-base leading-none">{{ selectedCountry.flag }}</span>
                        <span class="text-xs font-semibold text-[var(--color-primary)] whitespace-nowrap">{{ selectedCountry.dial }}</span>
                        <ChevronDown :size="14" class="text-[var(--color-muted)] transition-transform" :class="{ 'rotate-180': phoneDropdownOpen }" />
                      </button>
                      <input
                        :value="phoneNumber"
                        @input="onPhoneInput"
                        type="tel"
                        inputmode="tel"
                        placeholder="07 01 02 03 04"
                        class="flex-1 min-w-0 px-3 py-3 text-sm focus:outline-none bg-transparent"
                      >
                    </div>

                    <Transition
                      enter-active-class="transition duration-150 ease-out"
                      enter-from-class="opacity-0 -translate-y-1 scale-95"
                      enter-to-class="opacity-100 translate-y-0 scale-100"
                      leave-active-class="transition duration-100 ease-in"
                      leave-from-class="opacity-100 translate-y-0 scale-100"
                      leave-to-class="opacity-0 -translate-y-1 scale-95"
                    >
                      <div
                        v-if="phoneDropdownOpen"
                        class="absolute z-50 left-0 right-0 mt-1 bg-white border border-[var(--color-border)] rounded-lg shadow-lg overflow-hidden"
                      >
                        <div class="p-2 border-b border-[var(--color-border)]">
                          <div class="relative">
                            <Search :size="14" class="absolute left-2.5 top-1/2 -translate-y-1/2 text-[var(--color-muted)]" />
                            <input
                              ref="phoneSearchRef"
                              v-model="phoneSearch"
                              type="text"
                              placeholder="Rechercher un pays…"
                              class="w-full pl-8 pr-3 py-2 text-xs border border-[var(--color-border)] rounded-md focus:outline-none focus:ring-1 focus:ring-[var(--color-accent)]"
                            >
                          </div>
                        </div>
                        <ul class="max-h-48 overflow-y-auto">
                          <li
                            v-for="c in filteredCountries"
                            :key="c.code"
                            @click="selectCountry(c)"
                            class="flex items-center gap-2.5 px-3 py-2 text-sm cursor-pointer transition-colors"
                            :class="c.code === selectedCountry.code ? 'bg-[var(--color-accent-light)] text-[var(--color-accent)] font-semibold' : 'hover:bg-[var(--color-surface)]'"
                          >
                            <span class="text-base leading-none">{{ c.flag }}</span>
                            <span class="flex-1 truncate">{{ c.name }}</span>
                            <span class="text-xs text-[var(--color-muted)] font-mono">{{ c.dial }}</span>
                          </li>
                          <li v-if="filteredCountries.length === 0" class="px-3 py-3 text-xs text-center text-[var(--color-muted)]">
                            Aucun résultat
                          </li>
                        </ul>
                      </div>
                    </Transition>
                  </div>
                  <p v-if="phoneError" class="mt-1 text-xs text-red-500">{{ phoneError }}</p>
                </div>
                <div>
                  <label class="block font-heading text-xs font-bold uppercase tracking-[0.06em] text-[var(--color-muted)] mb-1.5">Sexe *</label>
                  <select v-model="registerForm.sex" required class="w-full px-4 py-3 border border-[var(--color-border)] rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-[var(--color-accent)] transition bg-white">
                    <option value="" disabled>Choisir</option>
                    <option value="M">Homme</option>
                    <option value="F">Femme</option>
                  </select>
                </div>
              </div>

              <div>
                <label class="block font-heading text-xs font-bold uppercase tracking-[0.06em] text-[var(--color-muted)] mb-1.5">Date de naissance *</label>
                <input v-model="registerForm.date_of_birth" required type="date" class="w-full px-4 py-3 border border-[var(--color-border)] rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-[var(--color-accent)] transition">
              </div>

              <div class="grid grid-cols-1 sm:grid-cols-2 gap-5">
                <div>
                  <label class="block font-heading text-xs font-bold uppercase tracking-[0.06em] text-[var(--color-muted)] mb-1.5">Mot de passe *</label>
                  <div class="relative">
                    <input v-model="registerForm.password" required :type="showPwd ? 'text' : 'password'" minlength="8" class="w-full px-4 py-3 pr-11 border border-[var(--color-border)] rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-[var(--color-accent)] transition">
                    <button type="button" @click="showPwd = !showPwd" class="absolute right-3 top-1/2 -translate-y-1/2 text-[var(--color-muted)] hover:text-[var(--color-primary)] cursor-pointer transition-colors" tabindex="-1">
                      <Eye v-if="!showPwd" :size="18" />
                      <EyeOff v-else :size="18" />
                    </button>
                  </div>
                </div>
                <div>
                  <label class="block font-heading text-xs font-bold uppercase tracking-[0.06em] text-[var(--color-muted)] mb-1.5">Confirmation *</label>
                  <div class="relative">
                    <input v-model="registerForm.password_confirm" required :type="showConfirm ? 'text' : 'password'" minlength="8" class="w-full px-4 py-3 pr-11 border border-[var(--color-border)] rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-[var(--color-accent)] transition">
                    <button type="button" @click="showConfirm = !showConfirm" class="absolute right-3 top-1/2 -translate-y-1/2 text-[var(--color-muted)] hover:text-[var(--color-primary)] cursor-pointer transition-colors" tabindex="-1">
                      <Eye v-if="!showConfirm" :size="18" />
                      <EyeOff v-else :size="18" />
                    </button>
                  </div>
                </div>
              </div>

              <div class="flex items-start gap-3">
                <input
                  id="cgu-checkbox"
                  v-model="cguAccepted"
                  type="checkbox"
                  class="mt-0.5 h-4 w-4 rounded border-gray-300 text-[var(--color-accent)] focus:ring-[var(--color-accent)] cursor-pointer shrink-0"
                >
                <label for="cgu-checkbox" class="text-xs text-[var(--color-muted)] leading-relaxed cursor-pointer select-none">
                  J'ai lu et j'accepte les
                  <RouterLink to="/cgu" target="_blank" class="text-[var(--color-accent)] font-semibold no-underline hover:underline">Conditions Générales d'Utilisation</RouterLink>
                  et la
                  <RouterLink to="/politique-confidentialite" target="_blank" class="text-[var(--color-accent)] font-semibold no-underline hover:underline">Politique de Confidentialité</RouterLink>
                  conformément à la Loi n° 2013-450 du 19 juin 2013 relative à la protection des données à caractère personnel.
                </label>
              </div>

              <button
                type="submit"
                :disabled="submitting || !cguAccepted"
                class="w-full flex items-center justify-center gap-2 px-6 py-3.5 font-heading text-sm font-bold uppercase tracking-[0.04em] bg-[var(--color-accent)] text-white rounded-lg transition-all hover:bg-[var(--color-accent-hover)] cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <Loader2 v-if="submitting" :size="18" class="animate-spin" />
                <template v-else>
                  Créer mon compte
                  <ArrowRight :size="18" />
                </template>
              </button>
            </form>
          </div>
        </div>

        <!-- ── STEP: SUCCESS (post-registration) ── -->
        <div v-else-if="step === 'success'">
          <div class="bg-white border border-[var(--color-border)] rounded-xl p-8 md:p-10 text-center">
            <div class="w-16 h-16 rounded-full bg-emerald-50 flex items-center justify-center mx-auto mb-5">
              <CheckCircle2 :size="32" class="text-emerald-500" />
            </div>
            <h2 class="font-heading text-2xl font-extrabold text-[var(--color-primary)] mb-3">
              Inscription réussie !
            </h2>
            <p class="text-[var(--color-muted)] max-w-md mx-auto mb-4">
              Un email de vérification a été envoyé à votre adresse. Cliquez sur le lien qu'il contient pour activer votre compte, puis connectez-vous pour compléter votre adhésion.
            </p>
            <div class="bg-amber-50 border border-amber-200 rounded-lg p-4 max-w-md mx-auto mb-6">
              <p class="text-xs text-amber-800 leading-relaxed">
                <strong>Vous ne trouvez pas l'email ?</strong> Pensez à vérifier votre dossier <strong>Spam</strong> ou <strong>Courrier indésirable</strong>. L'email provient de <em>FPP - Front Patriotique Panafricain</em>.
              </p>
            </div>
            <RouterLink
              to="/login"
              class="inline-flex items-center gap-2 px-6 py-3 font-heading text-sm font-bold uppercase tracking-[0.04em] bg-[var(--color-accent)] text-white no-underline rounded-sm transition-all hover:bg-[var(--color-accent-hover)] cursor-pointer"
            >
              Se connecter
              <ArrowRight :size="16" />
            </RouterLink>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>
