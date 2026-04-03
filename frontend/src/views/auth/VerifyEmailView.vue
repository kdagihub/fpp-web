<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { RouterLink, useRoute } from 'vue-router'
import api from '@/api'
import { CheckCircle2, XCircle, Loader2 } from 'lucide-vue-next'
import logoFpp from '@/assets/img/fpplogsf.png'

const route = useRoute()
const status = ref<'loading' | 'success' | 'error'>('loading')
const message = ref('')

onMounted(async () => {
  const uid = route.query.uid as string
  const token = route.query.token as string

  if (!uid || !token) {
    status.value = 'error'
    message.value = 'Lien de vérification invalide. Paramètres manquants.'
    return
  }

  try {
    await api.post('/auth/verify-email/', { uid, token })
    status.value = 'success'
    message.value = 'Votre adresse email a été vérifiée avec succès. Vous pouvez maintenant vous connecter.'
  } catch (err: any) {
    status.value = 'error'
    message.value = err?.response?.data?.detail || 'Le lien de vérification est invalide ou a expiré.'
  }
})
</script>

<template>
  <div class="min-h-screen flex items-center justify-center bg-[var(--color-surface)] px-4">
    <div class="w-full max-w-md">
      <div class="text-center mb-8">
        <RouterLink to="/" class="inline-block no-underline">
          <img :src="logoFpp" alt="FPP" class="h-14 mx-auto mb-3">
        </RouterLink>
      </div>

      <div class="bg-white rounded-xl border border-[var(--color-border)] p-8 shadow-[var(--shadow-sm)] text-center">
        <!-- Loading -->
        <div v-if="status === 'loading'" class="py-8">
          <Loader2 :size="40" class="animate-spin text-[var(--color-accent)] mx-auto mb-4" />
          <p class="font-heading text-lg font-bold text-[var(--color-primary)]">Vérification en cours...</p>
        </div>

        <!-- Success -->
        <div v-else-if="status === 'success'" class="py-4">
          <div class="w-16 h-16 rounded-full bg-emerald-50 flex items-center justify-center mx-auto mb-5">
            <CheckCircle2 :size="32" class="text-emerald-500" />
          </div>
          <h1 class="font-heading text-2xl font-extrabold text-[var(--color-primary)] mb-3">
            Email vérifié !
          </h1>
          <p class="text-sm text-[var(--color-muted)] mb-6">
            {{ message }}
          </p>
          <RouterLink
            to="/login"
            class="inline-flex items-center gap-2 px-6 py-3 font-heading text-sm font-bold uppercase tracking-[0.04em] bg-[var(--color-accent)] text-white no-underline rounded-sm transition-all hover:bg-[var(--color-accent-hover)] cursor-pointer"
          >
            Se connecter
          </RouterLink>
        </div>

        <!-- Error -->
        <div v-else class="py-4">
          <div class="w-16 h-16 rounded-full bg-red-50 flex items-center justify-center mx-auto mb-5">
            <XCircle :size="32" class="text-red-500" />
          </div>
          <h1 class="font-heading text-2xl font-extrabold text-[var(--color-primary)] mb-3">
            Erreur de vérification
          </h1>
          <p class="text-sm text-[var(--color-muted)] mb-6">
            {{ message }}
          </p>
          <RouterLink
            to="/"
            class="inline-flex items-center gap-2 px-6 py-3 font-heading text-sm font-bold uppercase tracking-[0.04em] text-[var(--color-primary)] no-underline border-2 border-[var(--color-primary)] rounded-sm transition-all hover:bg-[var(--color-primary)] hover:text-white cursor-pointer"
          >
            Retour à l'accueil
          </RouterLink>
        </div>
      </div>
    </div>
  </div>
</template>
