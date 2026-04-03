<script setup lang="ts">
import { ref, reactive } from 'vue'
import { RouterLink, useRoute, useRouter } from 'vue-router'
import { useAppToast } from '@/composables/useToast'
import api from '@/api'
import { Lock, ArrowRight, Loader2, CheckCircle2, XCircle, Eye, EyeOff } from 'lucide-vue-next'
import logoFpp from '@/assets/img/fpplogsf.png'

const route = useRoute()
const router = useRouter()
const toast = useAppToast()

const uid = route.query.uid as string
const token = route.query.token as string
const valid = !!(uid && token)

const form = ref({ password: '', password_confirm: '' })
const submitting = ref(false)
const success = ref(false)
const showPwd = ref(false)
const showConfirm = ref(false)
const errors = reactive<Record<string, string>>({})

function clearErrors() {
  Object.keys(errors).forEach(k => delete errors[k])
}

function validateLocally(): boolean {
  clearErrors()
  if (form.value.password.length < 8) {
    errors.password = 'Le mot de passe doit contenir au moins 8 caractères.'
    return false
  }
  if (form.value.password !== form.value.password_confirm) {
    errors.password_confirm = 'Les mots de passe ne correspondent pas.'
    return false
  }
  return true
}

function parseApiErrors(data: any) {
  clearErrors()
  if (data?.new_password) {
    errors.password = Array.isArray(data.new_password) ? data.new_password.join(' ') : data.new_password
  }
  if (data?.new_password_confirm) {
    errors.password_confirm = Array.isArray(data.new_password_confirm) ? data.new_password_confirm.join(' ') : data.new_password_confirm
  }
  if (data?.uid || data?.token) {
    errors.global = 'Ce lien de réinitialisation est invalide ou a expiré.'
  }
  if (data?.non_field_errors) {
    errors.global = Array.isArray(data.non_field_errors) ? data.non_field_errors.join(' ') : data.non_field_errors
  }
  if (!errors.password && !errors.password_confirm && !errors.global) {
    errors.global = data?.detail || 'Une erreur est survenue. Veuillez réessayer.'
  }
}

async function handleSubmit() {
  if (!validateLocally()) return

  submitting.value = true
  clearErrors()
  try {
    await api.post('/auth/password/reset/confirm/', {
      uid,
      token,
      new_password: form.value.password,
      new_password_confirm: form.value.password_confirm,
    })
    success.value = true
    toast.success('Mot de passe modifié', 'Vous pouvez maintenant vous connecter.')
    setTimeout(() => router.push('/login'), 3000)
  } catch (err: any) {
    parseApiErrors(err?.response?.data)
  } finally {
    submitting.value = false
  }
}
</script>

<template>
  <div class="min-h-screen flex items-center justify-center bg-[var(--color-surface)] px-4">
    <div class="w-full max-w-md">
      <div class="text-center mb-8">
        <RouterLink to="/" class="inline-block no-underline">
          <img :src="logoFpp" alt="FPP" class="h-14 mx-auto mb-3">
        </RouterLink>
      </div>

      <div class="bg-white rounded-xl border border-[var(--color-border)] p-8 shadow-[var(--shadow-sm)]">
        <!-- Invalid link -->
        <div v-if="!valid" class="py-4">
          <div class="w-16 h-16 rounded-full bg-red-50 flex items-center justify-center mx-auto mb-5">
            <XCircle :size="32" class="text-red-500" />
          </div>
          <h1 class="font-heading text-2xl font-extrabold text-[var(--color-primary)] mb-3 text-center">
            Lien invalide
          </h1>
          <p class="text-sm text-[var(--color-muted)] mb-6 text-center mx-auto">
            Ce lien de réinitialisation est invalide. Veuillez demander un nouveau lien.
          </p>
          <div class="flex justify-center">
            <RouterLink
              to="/password-reset"
              class="inline-flex items-center gap-2 px-6 py-3 font-heading text-sm font-bold text-[var(--color-accent)] no-underline border-2 border-[var(--color-accent)] rounded-sm cursor-pointer hover:bg-[var(--color-accent)] hover:text-white transition-all"
            >
              Nouveau lien
            </RouterLink>
          </div>
        </div>

        <!-- Success -->
        <div v-else-if="success" class="py-4">
          <div class="w-16 h-16 rounded-full bg-emerald-50 flex items-center justify-center mx-auto mb-5">
            <CheckCircle2 :size="32" class="text-emerald-500" />
          </div>
          <h1 class="font-heading text-2xl font-extrabold text-[var(--color-primary)] mb-3 text-center">
            Mot de passe modifié
          </h1>
          <p class="text-sm text-[var(--color-muted)] mb-6 text-center mx-auto">
            Redirection vers la page de connexion...
          </p>
        </div>

        <!-- Form -->
        <template v-else>
          <div class="mb-7">
            <div class="w-12 h-12 rounded-full bg-[var(--color-accent-light)] flex items-center justify-center mx-auto mb-4">
              <Lock :size="22" class="text-[var(--color-accent)]" />
            </div>
            <h1 class="font-heading text-2xl font-extrabold text-[var(--color-primary)] mb-1 text-center">
              Nouveau mot de passe
            </h1>
            <p class="text-sm text-[var(--color-muted)] text-center mx-auto">
              Choisissez un nouveau mot de passe sécurisé.
            </p>
          </div>

          <form @submit.prevent="handleSubmit" class="space-y-5">
            <!-- Erreur globale (lien expiré, etc.) -->
            <div v-if="errors.global" class="bg-red-50 border border-red-200 rounded-lg p-3">
              <p class="text-xs text-red-700 text-center mx-auto">{{ errors.global }}</p>
            </div>

            <div>
              <label class="block font-heading text-xs font-bold uppercase tracking-[0.06em] text-[var(--color-muted)] mb-1.5">Nouveau mot de passe</label>
              <div class="relative">
                <input
                  v-model="form.password"
                  required
                  :type="showPwd ? 'text' : 'password'"
                  minlength="8"
                  autocomplete="new-password"
                  class="w-full px-4 py-3 pr-11 border rounded-lg text-sm focus:outline-none focus:ring-2 transition"
                  :class="errors.password ? 'border-red-400 focus:ring-red-300' : 'border-[var(--color-border)] focus:ring-[var(--color-accent)]'"
                  placeholder="••••••••"
                >
                <button
                  type="button"
                  @click="showPwd = !showPwd"
                  class="absolute right-3 top-1/2 -translate-y-1/2 text-[var(--color-muted)] hover:text-[var(--color-primary)] cursor-pointer transition-colors"
                  tabindex="-1"
                >
                  <Eye v-if="!showPwd" :size="18" />
                  <EyeOff v-else :size="18" />
                </button>
              </div>
              <p v-if="errors.password" class="text-xs text-red-600 mt-1.5">{{ errors.password }}</p>
              <p v-else class="text-[11px] text-[var(--color-muted)] mt-1.5">Minimum 8 caractères, avec lettres et chiffres.</p>
            </div>
            <div>
              <label class="block font-heading text-xs font-bold uppercase tracking-[0.06em] text-[var(--color-muted)] mb-1.5">Confirmation</label>
              <div class="relative">
                <input
                  v-model="form.password_confirm"
                  required
                  :type="showConfirm ? 'text' : 'password'"
                  minlength="8"
                  autocomplete="new-password"
                  class="w-full px-4 py-3 pr-11 border rounded-lg text-sm focus:outline-none focus:ring-2 transition"
                  :class="errors.password_confirm ? 'border-red-400 focus:ring-red-300' : 'border-[var(--color-border)] focus:ring-[var(--color-accent)]'"
                  placeholder="••••••••"
                >
                <button
                  type="button"
                  @click="showConfirm = !showConfirm"
                  class="absolute right-3 top-1/2 -translate-y-1/2 text-[var(--color-muted)] hover:text-[var(--color-primary)] cursor-pointer transition-colors"
                  tabindex="-1"
                >
                  <Eye v-if="!showConfirm" :size="18" />
                  <EyeOff v-else :size="18" />
                </button>
              </div>
              <p v-if="errors.password_confirm" class="text-xs text-red-600 mt-1.5">{{ errors.password_confirm }}</p>
              <p v-else class="text-[11px] text-[var(--color-muted)] mt-1.5">Saisissez à nouveau votre mot de passe.</p>
            </div>

            <button
              type="submit"
              :disabled="submitting"
              class="w-full flex items-center justify-center gap-2 px-6 py-3.5 font-heading text-sm font-bold uppercase tracking-[0.04em] bg-[var(--color-accent)] text-white rounded-lg transition-all hover:bg-[var(--color-accent-hover)] cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <Loader2 v-if="submitting" :size="18" class="animate-spin" />
              <template v-else>
                Valider
                <ArrowRight :size="18" />
              </template>
            </button>
          </form>
        </template>

        <div class="mt-6 flex justify-center">
          <RouterLink
            to="/login"
            class="text-xs text-[var(--color-muted)] no-underline hover:text-[var(--color-primary)] transition-colors"
          >
            ← Retour à la connexion
          </RouterLink>
        </div>
      </div>
    </div>
  </div>
</template>
