<script setup lang="ts">
import { ref, computed } from 'vue'
import { RouterLink, RouterView, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import {
  LayoutDashboard,
  Users,
  FileText,
  Mail,
  Settings,
  Shield,
  LogOut,
  Menu,
  X,
  ChevronLeft,
} from 'lucide-vue-next'

const authStore = useAuthStore()
const route = useRoute()
const sidebarOpen = ref(false)

const sidebarItems = computed(() => {
  const items = [
    { to: '/admin/dashboard', label: 'Tableau de bord', icon: LayoutDashboard, permission: 'can_view_dashboard' },
    { to: '/admin/membres', label: 'Membres', icon: Users, permission: 'can_view_members' },
    { to: '/admin/articles', label: 'Articles', icon: FileText, permission: 'can_create_article' },
    { to: '/admin/contacts', label: 'Contacts', icon: Mail, permission: 'can_manage_contacts' },
    { to: '/admin/parametres', label: 'Paramètres', icon: Settings, permission: 'can_manage_settings' },
    { to: '/admin/audit', label: 'Journal d\'audit', icon: Shield, permission: 'can_view_audit_log' },
  ]
  return items.filter((item) => authStore.hasPermission(item.permission))
})

function isActive(path: string): boolean {
  return route.path.startsWith(path)
}

async function handleLogout() {
  await authStore.logout()
}
</script>

<template>
  <div class="min-h-screen flex bg-[var(--color-surface)]">
    <!-- Sidebar (desktop) -->
    <aside
      class="hidden lg:flex flex-col w-64 bg-white border-r border-[var(--color-border)] fixed inset-y-0 left-0 z-40"
    >
      <!-- Logo -->
      <div class="h-16 flex items-center px-6 border-b border-[var(--color-border)]">
        <RouterLink to="/admin/dashboard" class="flex items-center gap-2 no-underline">
          <span class="font-heading font-bold text-lg text-[var(--color-primary)]">FPP Admin</span>
        </RouterLink>
      </div>

      <!-- Nav items -->
      <nav class="flex-1 py-4 px-3 space-y-1 overflow-y-auto">
        <RouterLink
          v-for="item in sidebarItems"
          :key="item.to"
          :to="item.to"
          class="flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium no-underline transition-all"
          :class="[
            isActive(item.to)
              ? 'bg-[var(--color-accent-light)] text-[var(--color-accent)]'
              : 'text-[var(--color-muted)] hover:bg-[var(--color-surface)] hover:text-[var(--color-primary)]'
          ]"
        >
          <component :is="item.icon" :size="20" />
          {{ item.label }}
        </RouterLink>
      </nav>

      <!-- Bottom section -->
      <div class="p-4 border-t border-[var(--color-border)]">
        <RouterLink
          to="/"
          class="flex items-center gap-2 px-3 py-2 text-sm text-[var(--color-muted)] no-underline hover:text-[var(--color-primary)] transition-colors"
        >
          <ChevronLeft :size="18" />
          Retour au site
        </RouterLink>
        <button
          @click="handleLogout"
          class="flex items-center gap-2 w-full px-3 py-2 text-sm text-[var(--color-error)] hover:bg-red-50 rounded-lg transition-colors cursor-pointer mt-1"
        >
          <LogOut :size="18" />
          Déconnexion
        </button>
      </div>
    </aside>

    <!-- Mobile sidebar overlay -->
    <Transition
      enter-active-class="transition-opacity duration-200"
      enter-from-class="opacity-0"
      enter-to-class="opacity-100"
      leave-active-class="transition-opacity duration-150"
      leave-from-class="opacity-100"
      leave-to-class="opacity-0"
    >
      <div
        v-if="sidebarOpen"
        class="lg:hidden fixed inset-0 bg-black/30 z-40"
        @click="sidebarOpen = false"
      />
    </Transition>

    <Transition
      enter-active-class="transition-transform duration-200 ease-out"
      enter-from-class="-translate-x-full"
      enter-to-class="translate-x-0"
      leave-active-class="transition-transform duration-150 ease-in"
      leave-from-class="translate-x-0"
      leave-to-class="-translate-x-full"
    >
      <aside
        v-if="sidebarOpen"
        class="lg:hidden fixed inset-y-0 left-0 w-64 bg-white border-r border-[var(--color-border)] z-50 flex flex-col"
      >
        <div class="h-16 flex items-center justify-between px-6 border-b border-[var(--color-border)]">
          <span class="font-heading font-bold text-lg text-[var(--color-primary)]">FPP Admin</span>
          <button @click="sidebarOpen = false" class="p-1 cursor-pointer">
            <X :size="20" />
          </button>
        </div>
        <nav class="flex-1 py-4 px-3 space-y-1 overflow-y-auto">
          <RouterLink
            v-for="item in sidebarItems"
            :key="item.to"
            :to="item.to"
            class="flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium no-underline transition-all"
            :class="[
              isActive(item.to)
                ? 'bg-[var(--color-accent-light)] text-[var(--color-accent)]'
                : 'text-[var(--color-muted)] hover:bg-[var(--color-surface)] hover:text-[var(--color-primary)]'
            ]"
            @click="sidebarOpen = false"
          >
            <component :is="item.icon" :size="20" />
            {{ item.label }}
          </RouterLink>
        </nav>
        <div class="p-4 border-t border-[var(--color-border)]">
          <button
            @click="handleLogout"
            class="flex items-center gap-2 w-full px-3 py-2 text-sm text-[var(--color-error)] hover:bg-red-50 rounded-lg transition-colors cursor-pointer"
          >
            <LogOut :size="18" />
            Déconnexion
          </button>
        </div>
      </aside>
    </Transition>

    <!-- Main content area -->
    <div class="flex-1 lg:ml-64 flex flex-col min-h-screen">
      <!-- Topbar -->
      <header class="h-16 bg-white border-b border-[var(--color-border)] flex items-center justify-between px-6 sticky top-0 z-30">
        <div class="flex items-center gap-4">
          <button
            class="lg:hidden p-2 cursor-pointer"
            @click="sidebarOpen = true"
            aria-label="Ouvrir le menu"
          >
            <Menu :size="22" />
          </button>
          <h1 class="font-heading text-lg font-semibold text-[var(--color-primary)]">
            <slot name="title" />
          </h1>
        </div>
        <div class="flex items-center gap-3">
          <span class="text-sm text-[var(--color-muted)]">
            {{ authStore.fullName }}
          </span>
          <div class="w-8 h-8 rounded-full bg-[var(--color-accent-light)] flex items-center justify-center text-sm font-semibold text-[var(--color-accent)]">
            {{ authStore.user?.first_name?.charAt(0) }}{{ authStore.user?.last_name?.charAt(0) }}
          </div>
        </div>
      </header>

      <!-- Page content -->
      <main class="flex-1 p-6">
        <RouterView />
      </main>
    </div>
  </div>
</template>
