<script setup lang="ts">
import { ref } from 'vue'
import { RouterLink } from 'vue-router'
import api from '@/api'
import { Mail, ArrowRight, Loader2, ArrowLeft } from 'lucide-vue-next'
import logoFpp from '@/assets/img/fpplogsf.png'

const email = ref('')
const submitting = ref(false)
const submitted = ref(false)

async function handleSubmit() {
  submitting.value = true
  try {
    await api.post('/auth/password/reset/', { email: email.value })
  } catch {
    // Silent : même réponse que l'email existe ou non (anti-enumeration)
  } finally {
    submitting.value = false
    submitted.value = true
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

        <template v-if="!submitted">
          <div class="mb-7">
            <div class="w-12 h-12 rounded-full bg-[var(--color-accent-light)] flex items-center justify-center mx-auto mb-4">
              <Mail :size="22" class="text-[var(--color-accent)]" />
            </div>
            <h1 class="font-heading text-2xl font-extrabold text-[var(--color-primary)] mb-1 text-center">
              Mot de passe oublié
            </h1>
            <p class="text-sm text-[var(--color-muted)] mx-auto text-center">
              Entrez votre email, nous vous enverrons un lien de réinitialisation.
            </p>
          </div>

          <form @submit.prevent="handleSubmit" class="space-y-5">
            <div>
              <label class="block font-heading text-xs font-bold uppercase tracking-[0.06em] text-[var(--color-muted)] mb-1.5">Email</label>
              <input
                v-model="email"
                required
                type="email"
                autocomplete="email"
                class="w-full px-4 py-3 border border-[var(--color-border)] rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-[var(--color-accent)] transition"
                placeholder="votre@email.com"
              >
            </div>

            <button
              type="submit"
              :disabled="submitting"
              class="w-full flex items-center justify-center gap-2 px-6 py-3.5 font-heading text-sm font-bold uppercase tracking-[0.04em] bg-[var(--color-accent)] text-white rounded-lg transition-all hover:bg-[var(--color-accent-hover)] cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <Loader2 v-if="submitting" :size="18" class="animate-spin" />
              <template v-else>
                Envoyer le lien
                <ArrowRight :size="18" />
              </template>
            </button>
          </form>
        </template>

        <template v-else>
          <div class="py-4">
            <div class="w-14 h-14 rounded-full bg-emerald-50 flex items-center justify-center mx-auto mb-5">
              <Mail :size="28" class="text-emerald-500" />
            </div>
            <h2 class="font-heading text-xl font-extrabold text-[var(--color-primary)] mb-3 text-center">
              Vérifiez votre boîte mail
            </h2>
            <p class="text-sm text-[var(--color-muted)] mb-4 text-center mx-auto">
              Si un compte est associé à <strong>{{ email }}</strong>, vous recevrez un email avec les instructions de réinitialisation.
            </p>
            <div class="bg-amber-50 border border-amber-200 rounded-lg p-3 mb-6 text-center">
              <p class="text-xs text-amber-800 leading-relaxed mx-auto">
                <strong>Vous ne trouvez pas l'email ?</strong> Vérifiez votre dossier <strong>Spam</strong> ou <strong>Courrier indésirable</strong>.
              </p>
            </div>
          </div>
        </template>

        <div class="mt-6 flex justify-center">
          <RouterLink
            to="/login"
            class="inline-flex items-center gap-1 text-xs text-[var(--color-muted)] no-underline hover:text-[var(--color-primary)] transition-colors"
          >
            <ArrowLeft :size="14" />
            Retour à la connexion
          </RouterLink>
        </div>
      </div>
    </div>
  </div>
</template>
