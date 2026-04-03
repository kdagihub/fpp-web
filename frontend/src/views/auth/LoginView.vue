<script setup lang="ts">
import { ref } from 'vue'
import { RouterLink, useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useAppToast } from '@/composables/useToast'
import { ArrowRight, Loader2, LogIn, Eye, EyeOff } from 'lucide-vue-next'
import logoFpp from '@/assets/img/fpplogsf.png'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()
const toast = useAppToast()

const form = ref({ email: '', password: '' })
const submitting = ref(false)
const showPwd = ref(false)

if (route.query.expired === '1') {
  toast.warn('Session expirée', 'Veuillez vous reconnecter.')
}

async function handleLogin() {
  submitting.value = true
  try {
    await authStore.login({
      email: form.value.email,
      password: form.value.password,
    })
    toast.success('Bienvenue !', `Connecté en tant que ${authStore.fullName}`)
    const redirect = (route.query.redirect as string) || '/mon-espace'
    router.push(redirect)
  } catch (err: any) {
    const msg = err?.response?.data?.detail || 'Email ou mot de passe incorrect.'
    toast.error('Erreur de connexion', msg)
  } finally {
    submitting.value = false
  }
}
</script>

<template>
  <div class="min-h-screen flex items-center justify-center bg-[var(--color-surface)] px-4">
    <div class="w-full max-w-md">
      <!-- Logo -->
      <div class="text-center mb-8">
        <RouterLink to="/" class="inline-block no-underline">
          <img :src="logoFpp" alt="FPP" class="h-14 mx-auto mb-3">
          <p class="font-heading text-xs font-bold uppercase tracking-[0.1em] text-[var(--color-muted)] mx-auto text-center">
            Front Patriotique Panafricain
          </p>
        </RouterLink>
      </div>

      <!-- Form card -->
      <div class="bg-white rounded-xl border border-[var(--color-border)] p-8 shadow-[var(--shadow-sm)]">
        <div class="mb-7">
          <div class="w-12 h-12 rounded-full bg-[var(--color-accent-light)] flex items-center justify-center mx-auto mb-4">
            <LogIn :size="22" class="text-[var(--color-accent)]" />
          </div>
          <h1 class="font-heading text-2xl font-extrabold text-[var(--color-primary)] mb-1 text-center">
            Connexion
          </h1>
          <p class="text-sm text-[var(--color-muted)] text-center mx-auto">
            Accédez à votre espace membre
          </p>
        </div>

        <form @submit.prevent="handleLogin" class="space-y-5">
          <div>
            <label class="block font-heading text-xs font-bold uppercase tracking-[0.06em] text-[var(--color-muted)] mb-1.5">Email</label>
            <input
              v-model="form.email"
              required
              type="email"
              autocomplete="email"
              class="w-full px-4 py-3 border border-[var(--color-border)] rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-[var(--color-accent)] transition"
              placeholder="votre@email.com"
            >
          </div>
          <div>
            <div class="flex items-center justify-between mb-1.5">
              <label class="font-heading text-xs font-bold uppercase tracking-[0.06em] text-[var(--color-muted)]">Mot de passe</label>
              <RouterLink to="/password-reset" class="text-xs text-[var(--color-accent)] no-underline hover:underline font-medium">
                Mot de passe Oublié ?
              </RouterLink>
            </div>
            <div class="relative">
              <input
                v-model="form.password"
                required
                :type="showPwd ? 'text' : 'password'"
                autocomplete="current-password"
                class="w-full px-4 py-3 pr-11 border border-[var(--color-border)] rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-[var(--color-accent)] transition"
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
          </div>

          <button
            type="submit"
            :disabled="submitting"
            class="w-full flex items-center justify-center gap-2 px-6 py-3.5 font-heading text-sm font-bold uppercase tracking-[0.04em] bg-[var(--color-accent)] text-white rounded-lg transition-all hover:bg-[var(--color-accent-hover)] cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <Loader2 v-if="submitting" :size="18" class="animate-spin" />
            <template v-else>
              Se connecter
              <ArrowRight :size="18" />
            </template>
          </button>
        </form>

        <div class="mt-6">
          <p class="text-sm text-[var(--color-muted)] text-center mx-auto">
            Pas encore de compte ?
            <RouterLink to="/adherer" class="text-[var(--color-accent)] font-semibold no-underline hover:underline">
              Créer un compte
            </RouterLink>
          </p>
        </div>
      </div>

      <!-- Back to home -->
      <div class="mt-6 flex justify-center">
        <RouterLink to="/" class="text-xs text-[var(--color-muted)] no-underline hover:text-[var(--color-primary)] transition-colors">
          ← Retour au site
        </RouterLink>
      </div>
    </div>
  </div>
</template>
