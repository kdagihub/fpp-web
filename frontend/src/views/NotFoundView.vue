<script setup lang="ts">
import { RouterLink } from 'vue-router'
</script>

<template>
  <div class="min-h-screen flex items-center justify-center bg-[var(--color-surface)]">
    <div class="text-center px-6">
      <p class="font-heading text-6xl font-bold text-[var(--color-accent)] mb-4">404</p>
      <h1 class="font-heading text-2xl font-bold text-[var(--color-primary)] mb-2">
        Page introuvable
      </h1>
      <p class="text-[var(--color-muted)] mb-8">
        La page que vous cherchez n'existe pas ou a été déplacée.
      </p>
      <RouterLink
        to="/"
        class="inline-flex items-center px-6 py-3 rounded-lg text-sm font-heading font-semibold bg-[var(--color-accent)] text-white no-underline transition-all hover:bg-[var(--color-accent-hover)] cursor-pointer"
      >
        Retour à l'accueil
      </RouterLink>
    </div>
  </div>
</template>
