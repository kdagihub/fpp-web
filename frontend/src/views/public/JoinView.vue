<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { RouterLink } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useAppToast } from '@/composables/useToast'
import api from '@/api'
import type { RegisterPayload, MembershipRequestPayload } from '@/types'
import {
  ArrowRight,
  Users,
  CalendarDays,
  Megaphone,
  BookOpen,
  Upload,
  CheckCircle2,
  Clock,
  XCircle,
  Loader2,
  Eye,
  EyeOff,
} from 'lucide-vue-next'

const authStore = useAuthStore()
const toast = useAppToast()

const step = ref<'register' | 'membership' | 'status' | 'success'>('register')
const submitting = ref(false)
const showPwd = ref(false)
const showConfirm = ref(false)

/* ── Registration form ── */
const registerForm = ref({
  first_name: '',
  last_name: '',
  email: '',
  phone: '',
  sex: '' as 'M' | 'F' | '',
  date_of_birth: '',
  password: '',
  password_confirm: '',
})

/* ── Membership form ── */
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

/* ── Membership status ── */
const membershipStatus = ref<string | null>(null)

const benefits = [
  { icon: Users, title: 'Participez à la révolution', text: 'Engagez-vous considérablement dans la lutte pour la décolonisation, la souveraineté, l\'indépendance, le progrès et le développement de la Côte d\'Ivoire.' },
  { icon: CalendarDays, title: 'Accès aux événements', text: 'Participez à nos conférences, séminaires et rencontres exclusives.' },
  { icon: Megaphone, title: 'Rejoindre la communauté', text: 'Intégrez un réseau de citoyens engagés sur tout le territoire.' },
  { icon: BookOpen, title: 'Rester informé', text: 'Recevez nos publications, analyses et notes de positionnement en avant-première.' },
]

const documentTypes = [
  { value: 'cni', label: 'Carte Nationale d\'Identité' },
  { value: 'passport', label: 'Passeport' },
  { value: 'permis', label: 'Permis de conduire' },
  { value: 'attestation', label: 'Attestation d\'identité' },
]

function determineStep() {
  if (!authStore.isAuthenticated) {
    step.value = 'register'
    return
  }
  const membership = authStore.user?.membership
  if (!membership) {
    step.value = 'membership'
  } else {
    membershipStatus.value = membership.status
    step.value = 'status'
  }
}

async function handleRegister() {
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
      phone: registerForm.value.phone || undefined,
      sex: registerForm.value.sex as 'M' | 'F',
      date_of_birth: registerForm.value.date_of_birth,
      password: registerForm.value.password,
      password_confirm: registerForm.value.password_confirm,
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

async function handleMembership() {
  if (!photoFile.value || !idScanFile.value) {
    toast.error('Erreur', 'Veuillez ajouter votre photo et le scan de votre pièce d\'identité.')
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
    toast.success('Demande envoyée', 'Votre demande d\'adhésion a bien été soumise.')
    await authStore.fetchUser()
    determineStep()
  } catch (err: any) {
    const msg = err?.response?.data?.detail || 'Erreur lors de l\'envoi de la demande.'
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
  determineStep()
})
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
              <span class="inline-block px-3 py-1 bg-[var(--color-accent-light)] text-[var(--color-accent)] font-heading text-xs font-bold uppercase tracking-[0.06em] rounded-full mb-3">
                Étape 1/2
              </span>
              <h2 class="font-heading text-2xl font-extrabold text-[var(--color-primary)] mb-2">
                Créez votre compte
              </h2>
              <p class="text-sm text-[var(--color-muted)]">
                Déjà un compte ?
                <RouterLink to="/login" class="text-[var(--color-accent)] font-semibold no-underline hover:underline">
                  Connectez-vous
                </RouterLink>
              </p>
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
                  <input v-model="registerForm.phone" type="tel" class="w-full px-4 py-3 border border-[var(--color-border)] rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-[var(--color-accent)] transition">
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

              <button
                type="submit"
                :disabled="submitting"
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

        <!-- ── STEP: MEMBERSHIP ── -->
        <div v-else-if="step === 'membership'">
          <div class="bg-white border border-[var(--color-border)] rounded-xl p-8 md:p-10">
            <div class="text-center mb-8">
              <span class="inline-block px-3 py-1 bg-[var(--color-accent-light)] text-[var(--color-accent)] font-heading text-xs font-bold uppercase tracking-[0.06em] rounded-full mb-3">
                Étape 2/2
              </span>
              <h2 class="font-heading text-2xl font-extrabold text-[var(--color-primary)] mb-2">
                Demande d'adhésion
              </h2>
              <p class="text-sm text-[var(--color-muted)]">
                Complétez votre dossier pour devenir membre officiel du FPP.
              </p>
            </div>

            <form @submit.prevent="handleMembership" class="space-y-5">
              <div class="grid grid-cols-1 sm:grid-cols-2 gap-5">
                <div>
                  <label class="block font-heading text-xs font-bold uppercase tracking-[0.06em] text-[var(--color-muted)] mb-1.5">Type de pièce *</label>
                  <select v-model="membershipForm.id_document_type" required class="w-full px-4 py-3 border border-[var(--color-border)] rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-[var(--color-accent)] transition bg-white">
                    <option v-for="doc in documentTypes" :key="doc.value" :value="doc.value">{{ doc.label }}</option>
                  </select>
                </div>
                <div>
                  <label class="block font-heading text-xs font-bold uppercase tracking-[0.06em] text-[var(--color-muted)] mb-1.5">N° du document *</label>
                  <input v-model="membershipForm.id_document_number" required type="text" class="w-full px-4 py-3 border border-[var(--color-border)] rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-[var(--color-accent)] transition">
                </div>
              </div>

              <div class="grid grid-cols-1 sm:grid-cols-2 gap-5">
                <div>
                  <label class="block font-heading text-xs font-bold uppercase tracking-[0.06em] text-[var(--color-muted)] mb-1.5">Photo d'identité *</label>
                  <label class="flex items-center gap-3 px-4 py-3 border border-dashed border-[var(--color-border)] rounded-lg cursor-pointer hover:border-[var(--color-accent)] transition">
                    <Upload :size="18" class="text-[var(--color-muted)]" />
                    <span class="text-sm text-[var(--color-muted)]">{{ photoFile?.name ?? 'Choisir un fichier' }}</span>
                    <input type="file" accept="image/*" class="hidden" @change="onFileChange('photo', $event)">
                  </label>
                </div>
                <div>
                  <label class="block font-heading text-xs font-bold uppercase tracking-[0.06em] text-[var(--color-muted)] mb-1.5">Scan de la pièce *</label>
                  <label class="flex items-center gap-3 px-4 py-3 border border-dashed border-[var(--color-border)] rounded-lg cursor-pointer hover:border-[var(--color-accent)] transition">
                    <Upload :size="18" class="text-[var(--color-muted)]" />
                    <span class="text-sm text-[var(--color-muted)]">{{ idScanFile?.name ?? 'Choisir un fichier' }}</span>
                    <input type="file" accept="image/jpeg,image/png,image/webp" class="hidden" @change="onFileChange('scan', $event)">
                  </label>
                </div>
              </div>

              <div class="grid grid-cols-1 sm:grid-cols-2 gap-5">
                <div>
                  <label class="block font-heading text-xs font-bold uppercase tracking-[0.06em] text-[var(--color-muted)] mb-1.5">Ville *</label>
                  <input v-model="membershipForm.city" required type="text" class="w-full px-4 py-3 border border-[var(--color-border)] rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-[var(--color-accent)] transition">
                </div>
                <div>
                  <label class="block font-heading text-xs font-bold uppercase tracking-[0.06em] text-[var(--color-muted)] mb-1.5">Commune *</label>
                  <input v-model="membershipForm.commune" required type="text" class="w-full px-4 py-3 border border-[var(--color-border)] rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-[var(--color-accent)] transition">
                </div>
              </div>

              <div class="grid grid-cols-1 sm:grid-cols-2 gap-5">
                <div>
                  <label class="block font-heading text-xs font-bold uppercase tracking-[0.06em] text-[var(--color-muted)] mb-1.5">Région</label>
                  <input v-model="membershipForm.region" type="text" class="w-full px-4 py-3 border border-[var(--color-border)] rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-[var(--color-accent)] transition">
                </div>
                <div>
                  <label class="block font-heading text-xs font-bold uppercase tracking-[0.06em] text-[var(--color-muted)] mb-1.5">Quartier</label>
                  <input v-model="membershipForm.neighborhood" type="text" class="w-full px-4 py-3 border border-[var(--color-border)] rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-[var(--color-accent)] transition">
                </div>
              </div>

              <div>
                <label class="block font-heading text-xs font-bold uppercase tracking-[0.06em] text-[var(--color-muted)] mb-1.5">Profession</label>
                <input v-model="membershipForm.profession" type="text" class="w-full px-4 py-3 border border-[var(--color-border)] rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-[var(--color-accent)] transition">
              </div>

              <div>
                <label class="block font-heading text-xs font-bold uppercase tracking-[0.06em] text-[var(--color-muted)] mb-1.5">Motivation</label>
                <textarea v-model="membershipForm.motivation" rows="3" class="w-full px-4 py-3 border border-[var(--color-border)] rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-[var(--color-accent)] transition resize-none" placeholder="Pourquoi souhaitez-vous rejoindre le FPP ?"></textarea>
              </div>

              <button
                type="submit"
                :disabled="submitting"
                class="w-full flex items-center justify-center gap-2 px-6 py-3.5 font-heading text-sm font-bold uppercase tracking-[0.04em] bg-[var(--color-accent)] text-white rounded-lg transition-all hover:bg-[var(--color-accent-hover)] cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
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

        <!-- ── STEP: STATUS ── -->
        <div v-else-if="step === 'status'">
          <div class="bg-white border border-[var(--color-border)] rounded-xl p-8 md:p-10 text-center">
            <div v-if="membershipStatus === 'pending'" class="space-y-4">
              <div class="w-16 h-16 rounded-full bg-amber-50 flex items-center justify-center mx-auto">
                <Clock :size="32" class="text-amber-500" />
              </div>
              <h2 class="font-heading text-2xl font-extrabold text-[var(--color-primary)]">Demande en cours de traitement</h2>
              <p class="text-[var(--color-muted)] max-w-md mx-auto">
                Votre demande d'adhésion a bien été reçue. Notre équipe l'examine actuellement. Vous serez notifié par email dès qu'une décision sera prise.
              </p>
            </div>
            <div v-else-if="membershipStatus === 'validated'" class="space-y-4">
              <div class="w-16 h-16 rounded-full bg-emerald-50 flex items-center justify-center mx-auto">
                <CheckCircle2 :size="32" class="text-emerald-500" />
              </div>
              <h2 class="font-heading text-2xl font-extrabold text-[var(--color-primary)]">Bienvenue au FPP !</h2>
              <p class="text-[var(--color-muted)] max-w-md mx-auto">
                Votre adhésion a été validée. Vous êtes désormais membre officiel du Front Patriotique Panafricain.
              </p>
              <p v-if="authStore.user?.membership?.matricule" class="font-heading text-lg font-bold text-[var(--color-accent)]">
                Matricule : {{ authStore.user.membership.matricule }}
              </p>
            </div>
            <div v-else-if="membershipStatus === 'rejected'" class="space-y-4">
              <div class="w-16 h-16 rounded-full bg-red-50 flex items-center justify-center mx-auto">
                <XCircle :size="32" class="text-red-500" />
              </div>
              <h2 class="font-heading text-2xl font-extrabold text-[var(--color-primary)]">Demande refusée</h2>
              <p class="text-[var(--color-muted)] max-w-md mx-auto">
                Votre demande d'adhésion n'a pas été acceptée. Vous pouvez nous contacter pour plus d'informations.
              </p>
              <RouterLink
                to="/contact"
                class="inline-flex items-center gap-2 mt-4 px-6 py-3 font-heading text-sm font-bold text-white bg-[var(--color-primary)] no-underline rounded-sm cursor-pointer"
              >
                Nous contacter
              </RouterLink>
            </div>
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
