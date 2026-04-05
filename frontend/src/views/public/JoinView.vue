<script setup lang="ts">
import { ref } from 'vue'
import { RouterLink } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useSettingsStore } from '@/stores/settings'
import { useAppToast } from '@/composables/useToast'
import { VueTelInput } from 'vue-tel-input'
import 'vue-tel-input/vue-tel-input.css'
import tutoSpamImg from '@/assets/img/tuto_spam.png'
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
  MailSearch,
  ShieldAlert,
  Headset,
  Phone,
  ImageIcon,
} from 'lucide-vue-next'

const authStore = useAuthStore()
const settingsStore = useSettingsStore()
const toast = useAppToast()
const showTutoImage = ref(false)

const step = ref<'register' | 'success'>('register')
const submitting = ref(false)
const showPwd = ref(false)
const showConfirm = ref(false)

const phone = ref('')
const phoneValid = ref(false)
const phoneTouched = ref(false)

function onPhoneValidate(validation: any) {
  phoneValid.value = !!validation.valid
}

const cguAccepted = ref(false)

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
  phoneTouched.value = true
  if (!phone.value || !phoneValid.value) {
    toast.error('Erreur', !phone.value ? 'Le numéro de téléphone est obligatoire.' : 'Numéro de téléphone invalide.')
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
      phone: phone.value,
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
                <div class="sm:col-span-2 md:col-span-1">
                  <label class="block font-heading text-xs font-bold uppercase tracking-[0.06em] text-[var(--color-muted)] mb-1.5">Téléphone *</label>
                  <vue-tel-input
                    v-model="phone"
                    mode="international"
                    default-country="CI"
                    :dropdown-options="{ showDialCodeInSelection: true, showFlags: true, showSearchBox: true }"
                    :input-options="{ placeholder: '07 01 02 03 04', styleClasses: 'text-sm' }"
                    :class="['vue-tel-input--custom', { 'vue-tel-input--error': phoneTouched && (!phone || !phoneValid) }]"
                    @validate="onPhoneValidate"
                    @blur="phoneTouched = true"
                  />
                  <p v-if="phoneTouched && !phone" class="mt-1 text-xs text-red-500">Le numéro de téléphone est obligatoire.</p>
                  <p v-else-if="phoneTouched && phone && !phoneValid" class="mt-1 text-xs text-red-500">Numéro de téléphone invalide.</p>
                </div>
                <div class="sm:col-span-2 md:col-span-1">
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
        <div v-else-if="step === 'success'" class="max-w-2xl mx-auto space-y-6">

          <!-- Confirmation -->
          <div class="bg-white border border-[var(--color-border)] rounded-xl p-8 md:p-10 text-center">
            <div class="w-16 h-16 rounded-full bg-emerald-50 flex items-center justify-center mx-auto mb-5">
              <CheckCircle2 :size="32" class="text-emerald-500" />
            </div>
            <h2 class="font-heading text-2xl font-extrabold text-[var(--color-primary)] mb-3">
              Inscription réussie !
            </h2>
            <p class="text-[var(--color-muted)] max-w-lg mx-auto mb-6">
              Un email de vérification a été envoyé à votre adresse. <strong class="text-[var(--color-primary)]">Ouvrez votre boîte mail</strong> et cliquez sur le lien qu'il contient pour activer votre compte.
            </p>
            <RouterLink
              to="/login"
              class="inline-flex items-center gap-2 px-6 py-3 font-heading text-sm font-bold uppercase tracking-[0.04em] bg-[var(--color-accent)] text-white no-underline rounded-lg transition-all hover:bg-[var(--color-accent-hover)] cursor-pointer"
            >
              J'ai confirmé, me connecter
              <ArrowRight :size="16" />
            </RouterLink>
          </div>

          <!-- Guide spam -->
          <div class="bg-amber-50 border border-amber-300 rounded-xl p-6 md:p-8">
            <div class="flex items-center gap-3 mb-4">
              <div class="w-10 h-10 rounded-full bg-amber-100 flex items-center justify-center shrink-0">
                <ShieldAlert :size="20" class="text-amber-600" />
              </div>
              <h3 class="font-heading text-base font-bold text-amber-900">
                Vous ne trouvez pas l'email ?
              </h3>
            </div>

            <p class="text-sm text-amber-800 leading-relaxed mb-5">
              Il arrive souvent que l'email arrive dans le dossier <strong>« Spam »</strong> ou <strong>« Courrier indésirable »</strong> de votre boîte mail. C'est normal, voici comment le retrouver :
            </p>

            <div class="space-y-3 mb-5">
              <div class="flex items-start gap-3">
                <span class="flex items-center justify-center w-6 h-6 rounded-full bg-amber-200 text-amber-800 font-heading text-xs font-bold shrink-0 mt-0.5">1</span>
                <p class="text-sm text-amber-800">Ouvrez votre application mail (Gmail, Yahoo, Outlook...)</p>
              </div>
              <div class="flex items-start gap-3">
                <span class="flex items-center justify-center w-6 h-6 rounded-full bg-amber-200 text-amber-800 font-heading text-xs font-bold shrink-0 mt-0.5">2</span>
                <p class="text-sm text-amber-800">Dans le menu à gauche, cherchez <strong>« Spam »</strong>, <strong>« Courrier indésirable »</strong> ou <strong>« Junk »</strong>. Sur Gmail, cliquez d'abord sur <strong>« Plus »</strong> pour le voir.</p>
              </div>
              <div class="flex items-start gap-3">
                <span class="flex items-center justify-center w-6 h-6 rounded-full bg-amber-200 text-amber-800 font-heading text-xs font-bold shrink-0 mt-0.5">3</span>
                <p class="text-sm text-amber-800">Cherchez un email de <strong>« FPP - Front Patriotique Panafricain »</strong> et ouvrez-le</p>
              </div>
              <div class="flex items-start gap-3">
                <span class="flex items-center justify-center w-6 h-6 rounded-full bg-amber-200 text-amber-800 font-heading text-xs font-bold shrink-0 mt-0.5">4</span>
                <p class="text-sm text-amber-800">Cliquez sur le bouton <strong>« Confirmer mon adresse email »</strong> dans le message</p>
              </div>
            </div>

            <!-- Tuto image -->
            <div class="bg-white rounded-lg border border-amber-200 overflow-hidden">
              <button
                type="button"
                @click="showTutoImage = !showTutoImage"
                class="w-full flex items-center justify-between px-4 py-3 cursor-pointer hover:bg-amber-50/50 transition-colors"
              >
                <span class="flex items-center gap-2 text-sm font-semibold text-amber-800">
                  <ImageIcon :size="16" />
                  Voir comment trouver le dossier Spam sur Gmail
                </span>
                <ArrowRight :size="16" class="text-amber-600 transition-transform" :class="{ 'rotate-90': showTutoImage }" />
              </button>
              <div v-if="showTutoImage" class="px-4 pb-4">
                <img
                  :src="tutoSpamImg"
                  alt="Tutoriel : comment trouver le dossier Spam dans Gmail"
                  class="w-full max-w-md mx-auto rounded-lg border border-amber-200"
                />
                <p class="text-xs text-amber-700 text-center mt-2">
                  Sur Gmail : cliquez sur <strong>« Plus »</strong> (1), puis sur <strong>« Spam »</strong> (2)
                </p>
              </div>
            </div>
          </div>

          <!-- Contact secrétariat -->
          <div v-if="settingsStore.settings?.whatsapp_number" class="bg-white border border-[var(--color-border)] rounded-xl p-6 md:p-8">
            <div class="flex items-start gap-4">
              <div class="w-10 h-10 rounded-lg bg-[var(--color-accent-light)] flex items-center justify-center shrink-0">
                <Headset :size="20" class="text-[var(--color-accent)]" />
              </div>
              <div class="flex-1">
                <h3 class="font-heading text-sm font-bold text-[var(--color-primary)] mb-1">Besoin d'aide ? Appelez le secrétariat</h3>
                <p class="text-xs text-[var(--color-muted)] leading-relaxed mb-3">
                  Notre secrétariat est disponible <strong>24h/24, 7j/7</strong> pour vous accompagner dans votre inscription.
                </p>
                <div class="flex flex-col sm:flex-row gap-2">
                  <a
                    :href="`tel:${settingsStore.settings.whatsapp_number}`"
                    class="inline-flex items-center justify-center gap-2 px-4 py-2.5 bg-[var(--color-accent)] text-white text-sm font-semibold rounded-lg no-underline hover:bg-[var(--color-accent-hover)] transition-colors"
                  >
                    <Phone :size="16" />
                    Appeler : {{ settingsStore.settings.whatsapp_number }}
                  </a>
                  <a
                    :href="`https://wa.me/${settingsStore.settings.whatsapp_number.replace(/[^0-9+]/g, '')}`"
                    target="_blank"
                    rel="noopener"
                    class="inline-flex items-center justify-center gap-2 px-4 py-2.5 border-2 border-[var(--color-accent)] text-[var(--color-accent)] text-sm font-semibold rounded-lg no-underline hover:bg-[var(--color-accent)] hover:text-white transition-all"
                  >
                    <MailSearch :size="16" />
                    Écrire sur WhatsApp
                  </a>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>
