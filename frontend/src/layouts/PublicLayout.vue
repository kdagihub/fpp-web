<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { RouterLink, RouterView, useRoute } from 'vue-router'
import { useSettingsStore } from '@/stores/settings'
import { useAuthStore } from '@/stores/auth'
import {
  Menu,
  X,
  ArrowRight,
  LogIn,
  Mail,
  Phone,
  MapPin,
  Facebook,
  Twitter,
  Instagram,
  Youtube,
  ChevronDown,
} from 'lucide-vue-next'
import logoFpp from '@/assets/img/fpplogsf.png'

const settingsStore = useSettingsStore()
const authStore = useAuthStore()
const route = useRoute()
const mobileMenuOpen = ref(false)
const partiDropdownOpen = ref(false)
let dropdownTimeout: ReturnType<typeof setTimeout> | null = null

const navLinks = [
  { to: '/', label: 'Accueil', name: 'home' },
  { to: '/programme', label: 'Programme', name: 'programme' },
  { to: '/actualites', label: 'Actualités', name: 'news' },
  { to: '/agenda', label: 'Agenda', name: 'agenda' },
  { to: '/fpp-tv', label: 'FPP-TV', name: 'fpp-tv' },
  { to: '/contact', label: 'Contact', name: 'contact' },
]

const partiSubLinks = [
  { to: '/a-propos', label: 'Présentation', name: 'about' },
  { to: '/documents', label: 'Documents & Ressources', name: 'documents' },
]

function isActive(name: string): boolean {
  return route.name === name || (name === 'news' && route.name === 'news-detail')
}

function isPartiActive(): boolean {
  return partiSubLinks.some(l => route.name === l.name)
}

function openPartiDropdown() {
  if (dropdownTimeout) clearTimeout(dropdownTimeout)
  partiDropdownOpen.value = true
}

function closePartiDropdown() {
  dropdownTimeout = setTimeout(() => { partiDropdownOpen.value = false }, 150)
}

function closeMobileMenu() {
  mobileMenuOpen.value = false
}

onMounted(() => {
  settingsStore.fetchSettings()
})
</script>

<template>
  <div class="min-h-screen flex flex-col bg-[var(--color-background)]">
    <!-- ────── NAVBAR ────── -->
    <nav class="sticky top-0 z-50 bg-white border-b border-[var(--color-border)]">
      <div class="mx-auto max-w-[var(--container-xl)] h-16 px-6 flex items-center">
        <!-- Logo + brand -->
        <RouterLink
          to="/"
          class="flex items-center gap-2.5 no-underline group shrink-0"
          @click="closeMobileMenu"
        >
          <img
            :src="logoFpp"
            alt="FPP"
            class="h-10 w-auto"
          >
          <div class="flex flex-col leading-none">
            <span class="font-heading text-xl font-extrabold tracking-tight text-[var(--color-primary)]">
              FPP
            </span>
            <span class="font-heading text-[8px] font-semibold uppercase tracking-[0.12em] text-[var(--color-muted)]">
              Front Patriotique Panafricain
            </span>
          </div>
        </RouterLink>

        <!-- Desktop nav links (left, after logo) -->
        <div class="hidden lg:flex items-center ml-8 xl:ml-10">
          <!-- Accueil -->
          <RouterLink
            to="/"
            class="relative px-3 xl:px-4 py-2 font-heading text-[12px] xl:text-[13px] font-bold uppercase tracking-[0.04em] no-underline transition-colors whitespace-nowrap"
            :class="isActive('home') ? 'text-[var(--color-primary)]' : 'text-[var(--color-muted)] hover:text-[var(--color-primary)]'"
          >
            Accueil
            <span v-if="isActive('home')" class="absolute bottom-0 left-3 right-3 h-[2.5px] bg-[var(--color-accent)] rounded-full" />
          </RouterLink>

          <!-- Le Parti — dropdown -->
          <div class="relative" @mouseenter="openPartiDropdown" @mouseleave="closePartiDropdown">
            <button
              class="relative px-3 xl:px-4 py-2 font-heading text-[12px] xl:text-[13px] font-bold uppercase tracking-[0.04em] transition-colors whitespace-nowrap inline-flex items-center gap-1 cursor-pointer"
              :class="isPartiActive() ? 'text-[var(--color-primary)]' : 'text-[var(--color-muted)] hover:text-[var(--color-primary)]'"
            >
              Le Parti
              <ChevronDown :size="13" class="transition-transform" :class="partiDropdownOpen ? 'rotate-180' : ''" />
              <span v-if="isPartiActive()" class="absolute bottom-0 left-3 right-3 h-[2.5px] bg-[var(--color-accent)] rounded-full" />
            </button>
            <Transition
              enter-active-class="transition-all duration-150 ease-out"
              enter-from-class="opacity-0 -translate-y-1 scale-95"
              enter-to-class="opacity-100 translate-y-0 scale-100"
              leave-active-class="transition-all duration-100 ease-in"
              leave-from-class="opacity-100 translate-y-0 scale-100"
              leave-to-class="opacity-0 -translate-y-1 scale-95"
            >
              <div v-if="partiDropdownOpen" class="absolute top-full left-0 mt-1 w-56 bg-white rounded-xl shadow-lg border border-[var(--color-border)] py-2 z-50">
                <RouterLink
                  v-for="sub in partiSubLinks"
                  :key="sub.name"
                  :to="sub.to"
                  class="block px-4 py-2.5 text-sm font-medium no-underline transition-colors"
                  :class="isActive(sub.name) ? 'text-[var(--color-accent)] bg-[var(--color-accent-light)]' : 'text-[var(--color-primary)] hover:bg-[var(--color-surface)] hover:text-[var(--color-accent)]'"
                  @click="partiDropdownOpen = false"
                >
                  {{ sub.label }}
                </RouterLink>
              </div>
            </Transition>
          </div>

          <!-- Remaining links -->
          <RouterLink
            v-for="link in navLinks.slice(1)"
            :key="link.name"
            :to="link.to"
            class="relative px-3 xl:px-4 py-2 font-heading text-[12px] xl:text-[13px] font-bold uppercase tracking-[0.04em] no-underline transition-colors whitespace-nowrap"
            :class="[
              isActive(link.name)
                ? 'text-[var(--color-primary)]'
                : 'text-[var(--color-muted)] hover:text-[var(--color-primary)]'
            ]"
          >
            {{ link.label }}
            <span
              v-if="isActive(link.name)"
              class="absolute bottom-0 left-3 right-3 h-[2.5px] bg-[var(--color-accent)] rounded-full"
            />
          </RouterLink>
        </div>

        <!-- Desktop CTA (pushed far right) -->
        <div class="hidden lg:flex items-center gap-2.5 ml-auto shrink-0">
          <template v-if="authStore.isAuthenticated && authStore.isAdmin">
            <RouterLink
              to="/admin/dashboard"
              class="inline-flex items-center gap-1.5 px-3.5 py-2 font-heading text-[12px] font-bold uppercase tracking-[0.04em] text-[var(--color-primary)] no-underline border-2 border-[var(--color-primary)] rounded-sm transition-all hover:bg-[var(--color-primary)] hover:text-white cursor-pointer whitespace-nowrap"
            >
              Administration
            </RouterLink>
          </template>
          <template v-else>
            <RouterLink
              to="/login"
              class="inline-flex items-center gap-1.5 px-3.5 py-2 font-heading text-[12px] font-bold uppercase tracking-[0.04em] text-[var(--color-muted)] no-underline border border-[var(--color-border)] rounded-sm transition-all hover:border-[var(--color-primary)] hover:text-[var(--color-primary)] cursor-pointer whitespace-nowrap"
            >
              <LogIn :size="14" />
              Connexion
            </RouterLink>
            <RouterLink
              to="/adherer"
              class="group inline-flex items-center gap-1.5 px-5 py-2.5 font-heading text-[12px] xl:text-[13px] font-bold uppercase tracking-[0.04em] bg-[var(--color-accent)] text-white no-underline rounded-sm transition-all hover:bg-[var(--color-accent-hover)] cursor-pointer whitespace-nowrap"
            >
              Adhérer
              <ArrowRight :size="15" class="transition-transform group-hover:translate-x-0.5" />
            </RouterLink>
          </template>
        </div>

        <!-- Mobile hamburger -->
        <button
          class="lg:hidden ml-auto p-2 cursor-pointer text-[var(--color-primary)]"
          @click="mobileMenuOpen = !mobileMenuOpen"
          :aria-label="mobileMenuOpen ? 'Fermer le menu' : 'Ouvrir le menu'"
        >
          <X v-if="mobileMenuOpen" :size="24" />
          <Menu v-else :size="24" />
        </button>
      </div>

      <!-- Mobile menu -->
      <Transition
        enter-active-class="transition-all duration-200 ease-out"
        enter-from-class="opacity-0 -translate-y-2"
        enter-to-class="opacity-100 translate-y-0"
        leave-active-class="transition-all duration-150 ease-in"
        leave-from-class="opacity-100 translate-y-0"
        leave-to-class="opacity-0 -translate-y-2"
      >
        <div
          v-if="mobileMenuOpen"
          class="lg:hidden bg-white border-b border-[var(--color-border)] px-6 pb-5"
        >
          <!-- Accueil -->
          <RouterLink
            to="/"
            class="block py-3 font-heading text-sm font-bold uppercase tracking-[0.04em] no-underline border-b border-[var(--color-border)]"
            :class="isActive('home') ? 'text-[var(--color-primary)]' : 'text-[var(--color-muted)]'"
            @click="closeMobileMenu"
          >
            <span class="flex items-center justify-between">
              Accueil
              <span v-if="isActive('home')" class="w-2 h-2 rounded-full bg-[var(--color-accent)]" />
            </span>
          </RouterLink>
          <!-- Le Parti section -->
          <div class="border-b border-[var(--color-border)]">
            <div class="py-3 font-heading text-sm font-bold uppercase tracking-[0.04em] text-[var(--color-muted)]" :class="{ 'text-[var(--color-primary)]': isPartiActive() }">
              Le Parti
            </div>
            <RouterLink
              v-for="sub in partiSubLinks"
              :key="sub.name"
              :to="sub.to"
              class="block py-2.5 pl-4 font-heading text-[13px] font-medium no-underline"
              :class="isActive(sub.name) ? 'text-[var(--color-accent)]' : 'text-[var(--color-muted)]'"
              @click="closeMobileMenu"
            >
              <span class="flex items-center justify-between">
                {{ sub.label }}
                <span v-if="isActive(sub.name)" class="w-2 h-2 rounded-full bg-[var(--color-accent)]" />
              </span>
            </RouterLink>
          </div>
          <!-- Remaining links -->
          <RouterLink
            v-for="link in navLinks.slice(1)"
            :key="link.name"
            :to="link.to"
            class="block py-3 font-heading text-sm font-bold uppercase tracking-[0.04em] no-underline border-b border-[var(--color-border)] last:border-b-0"
            :class="[
              isActive(link.name)
                ? 'text-[var(--color-primary)]'
                : 'text-[var(--color-muted)]'
            ]"
            @click="closeMobileMenu"
          >
            <span class="flex items-center justify-between">
              {{ link.label }}
              <span
                v-if="isActive(link.name)"
                class="w-2 h-2 rounded-full bg-[var(--color-accent)]"
              />
            </span>
          </RouterLink>
          <div class="mt-4 flex flex-col gap-2.5">
            <template v-if="authStore.isAuthenticated && authStore.isAdmin">
              <RouterLink
                to="/admin/dashboard"
                class="flex items-center justify-center gap-2 w-full px-5 py-3 font-heading text-[13px] font-bold uppercase tracking-[0.04em] text-[var(--color-primary)] no-underline border-2 border-[var(--color-primary)] rounded-sm cursor-pointer"
                @click="closeMobileMenu"
              >
                Administration
              </RouterLink>
            </template>
            <template v-else>
              <RouterLink
                to="/login"
                class="flex items-center justify-center gap-2 w-full px-5 py-3 font-heading text-[13px] font-bold uppercase tracking-[0.04em] text-[var(--color-primary)] no-underline border-2 border-[var(--color-border)] rounded-sm cursor-pointer"
                @click="closeMobileMenu"
              >
                <LogIn :size="15" />
                Connexion
              </RouterLink>
              <RouterLink
                to="/adherer"
                class="flex items-center justify-center gap-2 w-full px-5 py-3 font-heading text-[13px] font-bold uppercase tracking-[0.04em] bg-[var(--color-accent)] text-white no-underline rounded-sm cursor-pointer"
                @click="closeMobileMenu"
              >
                Adhérer
                <ArrowRight :size="16" />
              </RouterLink>
            </template>
          </div>
        </div>
      </Transition>
    </nav>

    <!-- ────── MAIN CONTENT ────── -->
    <main class="flex-1">
      <RouterView />
    </main>

    <!-- ────── FOOTER ────── -->
    <footer class="bg-[var(--color-primary)] text-white">
      <div class="mx-auto max-w-[var(--container-xl)] px-6 py-16">
        <div class="grid grid-cols-1 md:grid-cols-12 gap-10">
          <!-- Col 1: Brand (spans 4) -->
          <div class="md:col-span-4">
            <div class="flex items-center gap-3 mb-5">
              <img
                :src="logoFpp"
                alt="FPP"
                class="h-12 w-auto invert"
              >
              <div>
                <p class="font-heading text-lg font-extrabold tracking-tight leading-tight">
                  FPP
                </p>
                <p class="font-heading text-xs font-medium text-white/60 uppercase tracking-[0.08em]">
                  Front Patriotique Panafricain
                </p>
              </div>
            </div>
            <p class="text-sm text-white/50 leading-relaxed max-w-xs">
              {{ settingsStore.settings?.slogan ?? 'Ensemble, construisons l\'avenir de la Côte d\'Ivoire.' }}
            </p>
          </div>

          <!-- Col 2: Navigation (spans 3) -->
          <div class="md:col-span-3">
            <h4 class="font-heading text-xs font-bold uppercase tracking-[0.1em] text-white/40 mb-5">
              Navigation
            </h4>
            <ul class="space-y-3">
              <li>
                <RouterLink to="/" class="text-sm text-white/70 no-underline hover:text-white transition-colors font-medium">Accueil</RouterLink>
              </li>
              <li v-for="sub in partiSubLinks" :key="sub.name">
                <RouterLink :to="sub.to" class="text-sm text-white/70 no-underline hover:text-white transition-colors font-medium">{{ sub.label }}</RouterLink>
              </li>
              <li v-for="link in navLinks.slice(1)" :key="link.name">
                <RouterLink :to="link.to" class="text-sm text-white/70 no-underline hover:text-white transition-colors font-medium">{{ link.label }}</RouterLink>
              </li>
              <li>
                <RouterLink to="/adherer" class="text-sm text-white/70 no-underline hover:text-white transition-colors font-medium">Adhérer</RouterLink>
              </li>
            </ul>
          </div>

          <!-- Col 3: Contact (spans 3) -->
          <div class="md:col-span-3">
            <h4 class="font-heading text-xs font-bold uppercase tracking-[0.1em] text-white/40 mb-5">
              Contact
            </h4>
            <ul class="space-y-3.5 text-sm text-white/70">
              <li v-if="settingsStore.settings?.contact_email">
                <a
                  :href="`mailto:${settingsStore.settings.contact_email}`"
                  class="inline-flex items-center gap-2.5 no-underline text-white/70 hover:text-white transition-colors font-medium group"
                >
                  <span class="flex items-center justify-center w-8 h-8 rounded-full bg-white/10 group-hover:bg-[var(--color-accent)] transition-colors shrink-0">
                    <Mail :size="15" />
                  </span>
                  {{ settingsStore.settings.contact_email }}
                </a>
              </li>
              <li v-if="settingsStore.settings?.whatsapp_number">
                <a
                  :href="`tel:${settingsStore.settings.whatsapp_number.startsWith('+') ? settingsStore.settings.whatsapp_number : '+225' + settingsStore.settings.whatsapp_number}`"
                  class="inline-flex items-center gap-2.5 no-underline text-white/70 hover:text-white transition-colors font-medium group"
                >
                  <span class="flex items-center justify-center w-8 h-8 rounded-full bg-white/10 group-hover:bg-[var(--color-accent)] transition-colors shrink-0">
                    <Phone :size="15" />
                  </span>
                  {{ settingsStore.settings.whatsapp_number.startsWith('+') ? settingsStore.settings.whatsapp_number : '+225 ' + settingsStore.settings.whatsapp_number }}
                </a>
              </li>
              <li v-if="settingsStore.settings?.address">
                <div class="inline-flex items-start gap-2.5">
                  <span class="flex items-center justify-center w-8 h-8 rounded-full bg-white/10 shrink-0 mt-0.5">
                    <MapPin :size="15" />
                  </span>
                  <span class="leading-relaxed">{{ settingsStore.settings.address }}</span>
                </div>
              </li>
            </ul>
          </div>

          <!-- Col 4: Social (spans 2) -->
          <div class="md:col-span-2">
            <h4 class="font-heading text-xs font-bold uppercase tracking-[0.1em] text-white/40 mb-5">
              Réseaux
            </h4>
            <div class="flex flex-wrap gap-2.5">
              <a
                v-if="settingsStore.settings?.facebook_url"
                :href="settingsStore.settings.facebook_url"
                target="_blank"
                rel="noopener"
                class="flex items-center justify-center w-10 h-10 rounded-full bg-white/10 text-white/70 no-underline hover:bg-[#1877F2] hover:text-white transition-all"
                title="Facebook"
              >
                <Facebook :size="18" />
              </a>
              <a
                v-if="settingsStore.settings?.twitter_url"
                :href="settingsStore.settings.twitter_url"
                target="_blank"
                rel="noopener"
                class="flex items-center justify-center w-10 h-10 rounded-full bg-white/10 text-white/70 no-underline hover:bg-black hover:text-white transition-all"
                title="X / Twitter"
              >
                <Twitter :size="18" />
              </a>
              <a
                v-if="settingsStore.settings?.instagram_url"
                :href="settingsStore.settings.instagram_url"
                target="_blank"
                rel="noopener"
                class="flex items-center justify-center w-10 h-10 rounded-full bg-white/10 text-white/70 no-underline hover:bg-gradient-to-br hover:from-[#f09433] hover:via-[#dc2743] hover:to-[#bc1888] hover:text-white transition-all"
                title="Instagram"
              >
                <Instagram :size="18" />
              </a>
              <a
                v-if="settingsStore.settings?.youtube_url"
                :href="settingsStore.settings.youtube_url"
                target="_blank"
                rel="noopener"
                class="flex items-center justify-center w-10 h-10 rounded-full bg-white/10 text-white/70 no-underline hover:bg-[#FF0000] hover:text-white transition-all"
                title="YouTube"
              >
                <Youtube :size="18" />
              </a>
            </div>
          </div>
        </div>

        <!-- Bottom bar -->
        <div class="mt-12 pt-6 border-t border-white/10 flex flex-col md:flex-row items-center justify-between gap-4">
          <p class="text-xs text-white/30 font-medium">
            &copy; {{ new Date().getFullYear() }} Front Patriotique Panafricain. Tous droits réservés.
          </p>
          <div class="flex items-center gap-4">
            <RouterLink to="/cgu" class="text-xs text-white/30 font-medium no-underline hover:text-white/60 transition-colors">
              CGU
            </RouterLink>
            <RouterLink to="/politique-confidentialite" class="text-xs text-white/30 font-medium no-underline hover:text-white/60 transition-colors">
              Confidentialité
            </RouterLink>
            <a
              href="https://kdagihub.github.io/coder-showcase-studio/"
              target="_blank"
              rel="noopener noreferrer"
              class="text-xs text-white/30 font-medium hover:text-green-400 transition-colors"
            >
              Développé par KDA - DEV
            </a>
          </div>
        </div>
      </div>
    </footer>
  </div>
</template>
