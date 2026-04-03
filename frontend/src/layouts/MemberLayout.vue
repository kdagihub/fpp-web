<script setup lang="ts">
import { RouterLink, RouterView, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { LogOut, ChevronDown, ArrowLeft } from 'lucide-vue-next'
import { ref, computed } from 'vue'
import { getMediaUrl } from '@/utils/media'
import logoFpp from '@/assets/img/fpplogsf.png'

const route = useRoute()
const authStore = useAuthStore()
const dropdownOpen = ref(false)

const isDashboard = computed(() => route.path === '/mon-espace' || route.path === '/mon-espace/')

const pageTitle = computed(() => {
  const map: Record<string, string> = {
    'member-news': 'Actualités',
    'member-news-detail': 'Actualités',
    'member-agenda': 'Agenda',
    'member-programme': 'Programme',
    'member-fpp-tv': 'FPP-TV',
    'member-profile': 'Mon profil',
    'member-card': 'Carte de membre',
    'member-settings': 'Paramètres',
    'member-join': 'Demande d\'adhésion',
  }
  return map[route.name as string] || ''
})

async function handleLogout() {
  dropdownOpen.value = false
  await authStore.logout()
}
</script>

<template>
  <div class="min-h-screen bg-gradient-to-br from-gray-100 via-gray-50 to-gray-100">
    <!-- ────── HEADER LÉGER ────── -->
    <header class="sticky top-0 z-50 backdrop-blur-xl bg-white/90 border-b border-gray-300/60 shadow-sm">
      <div class="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        <!-- Logo + Titre -->
        <RouterLink to="/mon-espace" class="flex items-center gap-3 no-underline shrink-0">
          <img :src="logoFpp" alt="FPP" class="h-9 w-auto">
          <div class="hidden sm:block">
            <span class="font-heading text-sm font-bold text-gray-900 tracking-tight">Mon espace</span>
          </div>
        </RouterLink>

        <!-- Profil dropdown -->
        <div class="relative">
          <button
            @click="dropdownOpen = !dropdownOpen"
            class="flex items-center gap-2 px-2 py-1.5 rounded-full hover:bg-gray-100 transition-all cursor-pointer"
          >
            <div class="w-8 h-8 rounded-full bg-gradient-to-br from-green-400 to-green-600 flex items-center justify-center text-white text-xs font-bold overflow-hidden">
              <img
                v-if="authStore.user?.avatar"
                :src="getMediaUrl(authStore.user.avatar)"
                class="w-full h-full object-cover"
                alt=""
              >
              <span v-else>{{ authStore.user?.first_name?.charAt(0) }}{{ authStore.user?.last_name?.charAt(0) }}</span>
            </div>
            <span class="hidden sm:block text-sm font-medium text-gray-700 max-w-[120px] truncate">
              {{ authStore.user?.first_name }}
            </span>
            <ChevronDown :size="14" class="text-gray-400" />
          </button>

          <!-- Dropdown menu -->
          <Transition
            enter-active-class="transition duration-150 ease-out"
            enter-from-class="opacity-0 scale-95 -translate-y-1"
            enter-to-class="opacity-100 scale-100 translate-y-0"
            leave-active-class="transition duration-100 ease-in"
            leave-from-class="opacity-100 scale-100 translate-y-0"
            leave-to-class="opacity-0 scale-95 -translate-y-1"
          >
            <div
              v-if="dropdownOpen"
              class="absolute right-0 mt-2 w-56 bg-white rounded-xl shadow-lg border border-gray-200/80 py-1.5 z-50"
            >
              <div class="px-4 py-3 border-b border-gray-100">
                <p class="text-sm font-semibold text-gray-900 truncate">{{ authStore.fullName }}</p>
                <p class="text-xs text-gray-500 truncate">{{ authStore.user?.email }}</p>
              </div>
              <RouterLink
                to="/mon-espace"
                class="flex items-center gap-2 px-4 py-2.5 text-sm text-gray-700 hover:bg-gray-50 no-underline transition-colors"
                @click="dropdownOpen = false"
              >
                Tableau de bord
              </RouterLink>
              <RouterLink
                to="/mon-espace/profil"
                class="flex items-center gap-2 px-4 py-2.5 text-sm text-gray-700 hover:bg-gray-50 no-underline transition-colors"
                @click="dropdownOpen = false"
              >
                Mon profil
              </RouterLink>
              <div class="border-t border-gray-100 mt-1.5 pt-1.5">
                <button
                  @click="handleLogout"
                  class="flex items-center gap-2 w-full px-4 py-2.5 text-sm text-red-600 hover:bg-red-50 cursor-pointer transition-colors"
                >
                  <LogOut :size="14" />
                  Déconnexion
                </button>
              </div>
            </div>
          </Transition>
        </div>
      </div>
    </header>

    <!-- Click outside to close dropdown -->
    <div v-if="dropdownOpen" class="fixed inset-0 z-40" @click="dropdownOpen = false" />

    <!-- ────── BREADCRUMB / RETOUR ────── -->
    <div v-if="!isDashboard" class="border-b border-gray-200/60 bg-white/50 backdrop-blur-sm">
      <div class="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 h-11 flex items-center">
        <RouterLink
          to="/mon-espace"
          class="inline-flex items-center gap-1.5 text-xs font-semibold text-gray-500 hover:text-gray-900 no-underline transition-colors"
        >
          <ArrowLeft :size="14" />
          Tableau de bord
        </RouterLink>
        <span v-if="pageTitle" class="mx-2 text-gray-300">/</span>
        <span v-if="pageTitle" class="text-xs font-semibold text-gray-800">{{ pageTitle }}</span>
      </div>
    </div>

    <!-- ────── MAIN CONTENT ────── -->
    <main class="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-8">
      <RouterView />
    </main>
  </div>
</template>
