<script setup lang="ts">
const props = defineProps<{ id?: string }>()
const isEditing = !!props.id
</script>

<template>
  <div>
    <h2 class="font-heading text-2xl font-bold text-[var(--color-primary)] mb-6">
      {{ isEditing ? 'Modifier l\'article' : 'Nouvel article' }}
    </h2>
    <p class="text-[var(--color-muted)]">Éditeur d'article TipTap — à compléter.</p>
  </div>
</template>
