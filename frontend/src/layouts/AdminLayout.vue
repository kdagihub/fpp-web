<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
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
  ChevronsLeft,
  ChevronsRight,
  AlertTriangle,
  BadgeCheck,
  Crown,
} from 'lucide-vue-next'
import { getMediaUrl } from '@/utils/media'
import logoImg from '@/assets/img/fpplogsf.png'

const COLLAPSE_KEY = 'fpp_sidebar_collapsed'

const authStore = useAuthStore()
const route = useRoute()
const sidebarOpen = ref(false)
const sidebarCollapsed = ref(false)

onMounted(() => {
  sidebarCollapsed.value = localStorage.getItem(COLLAPSE_KEY) === '1'
})

function toggleCollapse() {
  sidebarCollapsed.value = !sidebarCollapsed.value
  localStorage.setItem(COLLAPSE_KEY, sidebarCollapsed.value ? '1' : '0')
}

const sidebarItems = computed(() => {
  const items = [
    { to: '/admin/dashboard', label: 'Tableau de bord', icon: LayoutDashboard, permission: 'can_view_dashboard' },
    { to: '/admin/membres', label: 'Membres', icon: Users, permission: 'can_view_members' },
    { to: '/admin/verification-matricule', label: 'Vérifier matricule', icon: BadgeCheck, permission: 'can_view_members' },
    { to: '/admin/articles', label: 'Articles', icon: FileText, permission: 'can_create_article' },
    { to: '/admin/contacts', label: 'Contacts', icon: Mail, permission: 'can_manage_contacts' },
    { to: '/admin/bureau', label: 'Bureau National', icon: Crown, permission: 'can_manage_settings' },
    { to: '/admin/parametres', label: 'Paramètres', icon: Settings, permission: 'can_manage_settings' },
    { to: '/admin/audit', label: "Journal d'audit", icon: Shield, permission: 'can_view_audit_log' },
  ]
  return items.filter((item) => authStore.hasPermission(item.permission))
})

const isEmergencyUser = computed(() => !!authStore.user?.is_emergency_user)

function isActive(path: string): boolean {
  return route.path.startsWith(path)
}

async function handleLogout() {
  await authStore.logout()
}
</script>

<template>
  <div class="min-h-screen flex bg-[var(--color-surface)] overflow-x-hidden">
    <!-- ═══ Desktop Sidebar ═══ -->
    <aside
      class="hidden lg:flex flex-col bg-white border-r border-[var(--color-border)] fixed inset-y-0 left-0 z-40 transition-all duration-200"
      :class="sidebarCollapsed ? 'w-[68px]' : 'w-64'"
    >
      <!-- Logo -->
      <div class="h-16 flex items-center border-b border-[var(--color-border)] overflow-hidden"
        :class="sidebarCollapsed ? 'justify-center px-2' : 'px-6'"
      >
        <RouterLink to="/admin/dashboard" class="flex items-center gap-2 no-underline shrink-0">
          <img :src="logoImg" alt="FPP" class="h-9 w-9 object-contain shrink-0" />
          <span v-if="!sidebarCollapsed" class="font-heading font-bold text-lg text-[var(--color-primary)]">FPP Admin</span>
        </RouterLink>
      </div>

      <!-- Collapse toggle -->
      <button
        @click="toggleCollapse"
        class="mx-auto mt-2 mb-1 flex items-center justify-center w-8 h-8 rounded-lg text-[var(--color-muted)] hover:bg-[var(--color-surface)] hover:text-[var(--color-primary)] transition-colors cursor-pointer"
        :title="sidebarCollapsed ? 'Déplier le menu' : 'Replier le menu'"
      >
        <ChevronsRight v-if="sidebarCollapsed" :size="18" />
        <ChevronsLeft v-else :size="18" />
      </button>

      <!-- Nav items -->
      <nav class="flex-1 py-2 overflow-y-auto" :class="sidebarCollapsed ? 'px-2' : 'px-3'">
        <RouterLink
          v-for="item in sidebarItems"
          :key="item.to"
          :to="item.to"
          class="flex items-center rounded-lg font-medium no-underline transition-all mb-0.5"
          :class="[
            sidebarCollapsed ? 'justify-center px-0 py-2.5' : 'gap-3 px-3 py-2.5 text-sm',
            isActive(item.to)
              ? 'bg-[var(--color-accent-light)] text-[var(--color-accent)]'
              : 'text-[var(--color-muted)] hover:bg-[var(--color-surface)] hover:text-[var(--color-primary)]'
          ]"
          :title="sidebarCollapsed ? item.label : undefined"
        >
          <component :is="item.icon" :size="20" class="shrink-0" />
          <span v-if="!sidebarCollapsed" class="truncate">{{ item.label }}</span>
        </RouterLink>
      </nav>

      <!-- Bottom section -->
      <div class="border-t border-[var(--color-border)]" :class="sidebarCollapsed ? 'p-2' : 'p-4'">
        <RouterLink
          v-if="isEmergencyUser"
          to="/admin/urgence"
          class="flex items-center rounded-lg font-medium no-underline transition-all mb-1"
          :class="[
            sidebarCollapsed ? 'justify-center px-0 py-2 text-xs' : 'gap-2 px-3 py-2 text-sm',
            isActive('/admin/urgence')
              ? 'bg-red-100 text-red-700'
              : 'text-red-500 hover:bg-red-50 hover:text-red-700'
          ]"
          :title="sidebarCollapsed ? 'Urgence' : undefined"
        >
          <AlertTriangle :size="18" class="shrink-0" />
          <span v-if="!sidebarCollapsed">Urgence</span>
        </RouterLink>
        <RouterLink
          to="/mon-espace"
          class="flex items-center text-sm text-[var(--color-muted)] no-underline hover:text-[var(--color-primary)] transition-colors"
          :class="sidebarCollapsed ? 'justify-center py-2' : 'gap-2 px-3 py-2'"
          :title="sidebarCollapsed ? 'Mon espace' : undefined"
        >
          <ChevronLeft :size="18" class="shrink-0" />
          <span v-if="!sidebarCollapsed">Mon espace</span>
        </RouterLink>
        <button
          @click="handleLogout"
          class="flex items-center w-full text-sm text-[var(--color-error)] hover:bg-red-50 rounded-lg transition-colors cursor-pointer mt-1"
          :class="sidebarCollapsed ? 'justify-center py-2' : 'gap-2 px-3 py-2'"
          :title="sidebarCollapsed ? 'Déconnexion' : undefined"
        >
          <LogOut :size="18" class="shrink-0" />
          <span v-if="!sidebarCollapsed">Déconnexion</span>
        </button>
      </div>
    </aside>

    <!-- ═══ Mobile sidebar overlay ═══ -->
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
          <div class="flex items-center gap-2">
            <img :src="logoImg" alt="FPP" class="h-9 w-9 object-contain" />
            <span class="font-heading font-bold text-lg text-[var(--color-primary)]">FPP Admin</span>
          </div>
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
          <RouterLink
            v-if="isEmergencyUser"
            to="/admin/urgence"
            class="flex items-center gap-2 px-3 py-2 text-sm font-medium no-underline rounded-lg transition-all mb-1"
            :class="[
              isActive('/admin/urgence')
                ? 'bg-red-100 text-red-700'
                : 'text-red-500 hover:bg-red-50 hover:text-red-700'
            ]"
            @click="sidebarOpen = false"
          >
            <AlertTriangle :size="18" />
            Urgence
          </RouterLink>
          <RouterLink
            to="/mon-espace"
            class="flex items-center gap-2 px-3 py-2 text-sm text-[var(--color-muted)] no-underline hover:text-[var(--color-primary)] transition-colors"
            @click="sidebarOpen = false"
          >
            <ChevronLeft :size="18" />
            Mon espace
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
    </Transition>

    <!-- ═══ Main content area ═══ -->
    <div class="flex-1 min-w-0 flex flex-col min-h-screen transition-all duration-200"
      :class="sidebarCollapsed ? 'lg:ml-[68px]' : 'lg:ml-64'"
    >
      <!-- Topbar -->
      <header class="h-14 sm:h-16 bg-white border-b border-[var(--color-border)] flex items-center justify-between px-3 sm:px-6 sticky top-0 z-30 min-w-0">
        <div class="flex items-center gap-2 sm:gap-4 min-w-0">
          <button
            class="lg:hidden p-1.5 cursor-pointer shrink-0"
            @click="sidebarOpen = true"
            aria-label="Ouvrir le menu"
          >
            <Menu :size="20" />
          </button>
          <h1 class="font-heading text-base sm:text-lg font-semibold text-[var(--color-primary)] truncate">
            <slot name="title" />
          </h1>
        </div>
        <div class="flex items-center gap-2 sm:gap-3 shrink-0">
          <span class="text-sm text-[var(--color-muted)] hidden sm:inline truncate max-w-[140px]">
            {{ authStore.fullName }}
          </span>
          <div class="w-8 h-8 rounded-full bg-[var(--color-accent-light)] flex items-center justify-center text-sm font-semibold text-[var(--color-accent)] overflow-hidden shrink-0">
            <img
              v-if="authStore.user?.avatar"
              :src="getMediaUrl(authStore.user.avatar)"
              alt=""
              class="w-full h-full object-cover"
            >
            <template v-else>
              {{ authStore.user?.first_name?.charAt(0) }}{{ authStore.user?.last_name?.charAt(0) }}
            </template>
          </div>
        </div>
      </header>

      <!-- Page content -->
      <main class="flex-1 p-3 sm:p-6 min-w-0 overflow-x-hidden">
        <RouterView />
      </main>
    </div>
  </div>
</template>
