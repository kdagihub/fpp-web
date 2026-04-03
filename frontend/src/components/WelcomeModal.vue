<script setup lang="ts">
import { ref } from 'vue'
import { X } from 'lucide-vue-next'
import logoFpp from '@/assets/img/fpplogsf.png'

const emit = defineEmits<{ close: [] }>()

const visible = ref(true)

function dismiss() {
  visible.value = false
  setTimeout(() => emit('close'), 400)
}
</script>

<template>
  <Teleport to="body">
    <Transition name="welcome">
      <div v-if="visible" class="welcome-backdrop" @click.self="dismiss">
        <div class="welcome-card">
          <!-- Close -->
          <button
            @click="dismiss"
            class="absolute top-4 right-4 w-8 h-8 rounded-full flex items-center justify-center text-gray-400 hover:text-gray-700 hover:bg-gray-100 transition-all cursor-pointer"
          >
            <X :size="18" />
          </button>

          <!-- Green accent top bar -->
          <div class="h-1 bg-gradient-to-r from-[var(--color-accent)] via-emerald-400 to-[var(--color-accent)] rounded-t-2xl" />

          <div class="px-8 pt-7 pb-8 text-center">
            <!-- Logo -->
            <div class="relative mx-auto mb-5 w-20 h-20">
              <div class="absolute inset-0 rounded-full bg-[var(--color-accent)]/10 animate-pulse" />
              <img :src="logoFpp" alt="FPP" class="relative w-full h-full object-contain drop-shadow-lg">
            </div>

            <!-- Title -->
            <h2 class="font-heading text-xl sm:text-2xl font-extrabold text-[var(--color-primary)] mb-1 tracking-tight">
              Bienvenue sur <span class="text-[var(--color-accent)]">FPP</span>
            </h2>

            <p class="font-heading text-[10px] sm:text-xs font-bold uppercase tracking-[0.12em] text-[var(--color-muted)] mb-5">
              Front Patriotique Panafricain
            </p>

            <!-- Message -->
            <p class="text-sm leading-relaxed text-[var(--color-muted)] mb-6 mx-auto">
              Ensemble, construisons une Côte d'Ivoire souveraine, prospère et unie. 
              Rejoignez le mouvement pour un avenir panafricain.
            </p>

            <!-- CTA -->
            <div class="flex flex-col sm:flex-row items-center justify-center gap-3">
              <button
                @click="dismiss"
                class="w-full sm:w-auto inline-flex items-center justify-center gap-2 px-7 py-3 font-heading text-sm font-bold uppercase tracking-[0.04em] bg-[var(--color-accent)] text-white rounded-lg transition-all hover:bg-[var(--color-accent-hover)] hover:shadow-lg cursor-pointer"
              >
                Découvrir
              </button>
              <button
                @click="dismiss"
                class="w-full sm:w-auto inline-flex items-center justify-center gap-2 px-7 py-3 font-heading text-sm font-bold uppercase tracking-[0.04em] text-[var(--color-muted)] border border-[var(--color-border)] rounded-lg transition-all hover:border-[var(--color-primary)] hover:text-[var(--color-primary)] cursor-pointer"
              >
                Fermer
              </button>
            </div>
          </div>

          <!-- Bottom decorative line -->
          <div class="flex gap-0">
            <div class="h-0.5 flex-1 bg-black" />
            <div class="h-0.5 flex-1 bg-[var(--color-accent)]" />
            <div class="h-0.5 flex-1 bg-black" />
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<style scoped>
.welcome-backdrop {
  position: fixed;
  inset: 0;
  z-index: 50000;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1rem;
  background: rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
}

.welcome-card {
  position: relative;
  width: 100%;
  max-width: 420px;
  background: white;
  border-radius: 1rem;
  overflow: hidden;
  box-shadow:
    0 25px 50px -12px rgba(0, 0, 0, 0.25),
    0 0 0 1px rgba(0, 0, 0, 0.05);
  animation: card-entrance 500ms cubic-bezier(0.16, 1, 0.3, 1) both;
}

@keyframes card-entrance {
  from {
    opacity: 0;
    transform: translateY(24px) scale(0.96);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

/* Transition leave */
.welcome-leave-active {
  transition: opacity 350ms ease, transform 350ms ease;
}
.welcome-leave-to {
  opacity: 0;
  transform: scale(0.95);
}

.welcome-leave-active .welcome-card {
  transition: transform 350ms ease;
}
.welcome-leave-to .welcome-card {
  transform: translateY(16px) scale(0.96);
}

@media (prefers-reduced-motion: reduce) {
  .welcome-card { animation: none; }
}
</style>
