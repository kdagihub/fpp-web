<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { RouterLink } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { getMediaUrl } from '@/utils/media'
import api from '@/api'
import type { ArticleListItem, EventListItem, PaginatedResponse } from '@/types'
import {
  CreditCard,
  Calendar,
  Newspaper,
  BookOpen,
  Settings,
  MapPin,
  Clock,
  ChevronRight,
  Wallet,
  Lock,
  UserPlus,
  Tv,
} from 'lucide-vue-next'
import dayjs from 'dayjs'
import 'dayjs/locale/fr'

dayjs.locale('fr')

const authStore = useAuthStore()
const user = computed(() => authStore.user)
const membership = computed(() => user.value?.membership)

const isMember = computed(() => membership.value?.status === 'validated')
const isPending = computed(() => membership.value?.status === 'pending')

const latestArticles = ref<ArticleListItem[]>([])
const upcomingEvents = ref<EventListItem[]>([])

onMounted(async () => {
  try {
    const [articlesRes, eventsRes] = await Promise.all([
      api.get<PaginatedResponse<ArticleListItem>>('/public/articles/', { params: { page_size: 3 } }),
      api.get<PaginatedResponse<EventListItem>>('/public/events/', { params: { page_size: 3, ordering: 'start_date' } }),
    ])
    latestArticles.value = articlesRes.data.results ?? []
    upcomingEvents.value = eventsRes.data.results ?? []
  } catch {
    // silent — cards will show empty states
  }
})

const greeting = computed(() => {
  const hour = new Date().getHours()
  if (hour < 12) return 'Bonjour'
  if (hour < 18) return 'Bon après-midi'
  return 'Bonsoir'
})
</script>

<template>
  <div>
    <!-- ════ GREETING ════ -->
    <div class="mb-8">
      <h1 class="text-2xl sm:text-3xl font-extrabold text-gray-900 tracking-tight">
        {{ greeting }}, {{ user?.first_name }}
      </h1>
      <p class="text-sm text-gray-600 mt-1">
        <template v-if="isMember">
          Membre depuis {{ dayjs(membership?.membership_validated_at).format('MMMM YYYY') }}
        </template>
        <template v-else-if="isPending">
          Votre demande d'adhésion est en cours de traitement
        </template>
        <template v-else>
          Bienvenue dans votre espace personnel
        </template>
      </p>
    </div>

    <!-- ════ CARDS GRID (iCloud style) ════ -->
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5 lg:gap-6">

      <!-- ─── PROFIL CARD ─── -->
      <RouterLink
        to="/mon-espace/profil"
        class="group relative bg-white rounded-2xl border border-gray-300/80 p-4 sm:p-6 shadow-sm hover:shadow-lg hover:border-gray-400 transition-all duration-200 no-underline overflow-hidden"
      >
        <div class="absolute top-0 right-0 w-24 h-24 bg-gradient-to-bl from-green-100/60 to-transparent rounded-bl-[3rem]" />
        <div class="relative flex items-start gap-3 sm:gap-4">
          <div class="w-11 h-11 sm:w-14 sm:h-14 rounded-xl sm:rounded-2xl bg-gradient-to-br from-green-500 to-green-700 flex items-center justify-center text-white text-sm sm:text-lg font-bold shrink-0 overflow-hidden shadow-md">
            <img
              v-if="user?.avatar"
              :src="getMediaUrl(user.avatar)"
              class="w-full h-full object-cover"
              alt=""
            >
            <span v-else>{{ user?.first_name?.charAt(0) }}{{ user?.last_name?.charAt(0) }}</span>
          </div>
          <div class="min-w-0 flex-1">
            <h3 class="text-sm sm:text-base font-bold text-gray-900 truncate">{{ user?.first_name }} {{ user?.last_name }}</h3>
            <p v-if="membership?.matricule" class="text-[11px] sm:text-xs font-mono text-green-600 mt-0.5 whitespace-nowrap">{{ membership.matricule }}</p>
            <div class="flex items-center gap-1 mt-1.5 sm:mt-2 text-[11px] sm:text-xs text-gray-600">
              <MapPin :size="12" class="shrink-0" />
              <span class="truncate">{{ membership?.city || 'Non renseigné' }}{{ membership?.commune ? `, ${membership.commune}` : '' }}</span>
            </div>
          </div>
        </div>
        <div class="mt-3 sm:mt-4 flex items-center justify-between">
          <span
            class="inline-flex items-center gap-1.5 text-[10px] sm:text-[11px] font-semibold uppercase tracking-wide px-2 sm:px-2.5 py-1 rounded-full"
            :class="{
              'bg-green-100 text-green-800': isMember,
              'bg-amber-100 text-amber-800': isPending,
              'bg-gray-200 text-gray-700': !isMember && !isPending,
            }"
          >
            <span class="w-1.5 h-1.5 rounded-full" :class="{
              'bg-green-600': isMember,
              'bg-amber-500': isPending,
              'bg-gray-500': !isMember && !isPending,
            }" />
            {{ isMember ? 'Membre actif' : isPending ? 'En attente' : 'Partisan sympathisant' }}
          </span>
          <ChevronRight :size="16" class="text-gray-400 group-hover:text-gray-700 transition-colors" />
        </div>
      </RouterLink>

      <!-- ─── CARTE DE MEMBRE CARD (si membre validé) ─── -->
      <RouterLink
        v-if="isMember"
        to="/mon-espace/carte"
        class="group relative bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 rounded-2xl p-6 shadow-md hover:shadow-xl transition-all duration-200 no-underline overflow-hidden sm:col-span-2 lg:col-span-2"
      >
        <div class="absolute inset-0 bg-[radial-gradient(ellipse_at_30%_20%,rgba(0,166,81,0.15),transparent_50%)]" />
        <div class="absolute inset-0 bg-[radial-gradient(ellipse_at_70%_80%,rgba(255,255,255,0.05),transparent_50%)]" />
        <div class="absolute top-3 right-4 opacity-10">
          <CreditCard :size="48" class="text-white" />
        </div>

        <div class="relative flex items-start justify-between">
          <div>
            <p class="text-[10px] font-semibold uppercase tracking-[0.15em] text-green-400 mb-3">Carte de membre</p>
            <h3 class="text-lg font-bold text-white">{{ user?.first_name }} {{ user?.last_name }}</h3>
            <p class="text-xs font-mono text-gray-400 mt-1 tracking-wider">{{ membership?.matricule }}</p>
          </div>
          <div class="w-12 h-12 rounded-xl bg-white/10 flex items-center justify-center overflow-hidden">
            <img
              v-if="user?.avatar"
              :src="getMediaUrl(user.avatar)"
              class="w-full h-full object-cover"
              alt=""
            >
            <span v-else class="text-white text-sm font-bold">{{ user?.first_name?.charAt(0) }}{{ user?.last_name?.charAt(0) }}</span>
          </div>
        </div>

        <div class="relative mt-6 flex items-end justify-between">
          <div class="flex gap-6">
            <div>
              <p class="text-[10px] text-gray-500 uppercase tracking-wide">Depuis</p>
              <p class="text-xs text-gray-300 font-medium">{{ dayjs(membership?.membership_validated_at).format('MMM YYYY') }}</p>
            </div>
            <div>
              <p class="text-[10px] text-gray-500 uppercase tracking-wide">Ville</p>
              <p class="text-xs text-gray-300 font-medium">{{ membership?.city }}</p>
            </div>
          </div>
          <span class="inline-flex items-center gap-1 text-xs text-green-400 font-medium group-hover:translate-x-0.5 transition-transform">
            Voir ma carte
            <ChevronRight :size="14" />
          </span>
        </div>
      </RouterLink>

      <!-- ─── DEMANDER MA CARTE (si partisan / non-membre) ─── -->
      <RouterLink
        v-else
        to="/mon-espace/adhesion"
        class="group relative bg-gradient-to-br from-gray-800 to-gray-900 rounded-2xl p-6 shadow-md hover:shadow-xl transition-all duration-200 no-underline overflow-hidden sm:col-span-2 lg:col-span-2"
      >
        <div class="absolute inset-0 bg-[radial-gradient(ellipse_at_50%_50%,rgba(0,166,81,0.08),transparent_60%)]" />
        <div class="absolute top-3 right-4 opacity-10">
          <CreditCard :size="48" class="text-white" />
        </div>
        <div class="relative text-center py-4">
          <div class="w-14 h-14 rounded-2xl bg-green-500/15 flex items-center justify-center mx-auto mb-4">
            <UserPlus :size="24" class="text-green-400" />
          </div>
          <h3 class="text-base font-bold text-white mb-2">Obtenez votre carte de membre</h3>
          <p class="text-xs text-gray-400 max-w-xs mx-auto mb-4">
            {{ isPending ? 'Votre demande est en cours d\'examen. Vous recevrez votre carte une fois validé.' : 'Complétez votre demande d\'adhésion pour recevoir votre carte de membre officielle du FPP.' }}
          </p>
          <span
            v-if="!isPending"
            class="inline-flex items-center gap-1.5 px-5 py-2 text-xs font-semibold text-white bg-green-600 rounded-lg group-hover:bg-green-500 transition-colors"
          >
            Demander ma carte
            <ChevronRight :size="14" />
          </span>
          <span v-else class="inline-flex items-center gap-1.5 px-4 py-2 text-xs font-semibold text-amber-300 bg-amber-500/10 rounded-lg">
            <Clock :size="14" />
            Demande en cours
          </span>
        </div>
      </RouterLink>

      <!-- ─── COTISATIONS CARD (grisée) ─── -->
      <div class="relative bg-white rounded-2xl border border-gray-300/80 p-6 shadow-sm overflow-hidden opacity-60 cursor-not-allowed">
        <div class="absolute inset-0 bg-gray-50/50 backdrop-blur-[1px] z-10 flex flex-col items-center justify-center">
          <Lock :size="20" class="text-gray-400 mb-2" />
          <span class="text-xs font-semibold text-gray-500 uppercase tracking-wide">Bientôt disponible</span>
        </div>
        <div class="flex items-center gap-3 mb-4">
          <div class="w-10 h-10 rounded-xl bg-amber-50 flex items-center justify-center">
            <Wallet :size="20" class="text-amber-500" />
          </div>
          <div>
            <h3 class="text-sm font-bold text-gray-900">Cotisations</h3>
            <p class="text-xs text-gray-500">Statut & historique</p>
          </div>
        </div>
        <div class="space-y-2">
          <div class="h-3 bg-gray-200 rounded w-3/4"></div>
          <div class="h-3 bg-gray-200 rounded w-1/2"></div>
        </div>
      </div>

      <!-- ─── ÉVÉNEMENTS CARD ─── -->
      <RouterLink
        to="/mon-espace/agenda"
        class="group bg-white rounded-2xl border border-gray-300/80 p-6 shadow-sm hover:shadow-lg hover:border-gray-400 transition-all duration-200 no-underline overflow-hidden"
      >
        <div class="flex items-center justify-between mb-4">
          <div class="flex items-center gap-3">
            <div class="w-10 h-10 rounded-xl bg-blue-50 flex items-center justify-center">
              <Calendar :size="20" class="text-blue-500" />
            </div>
            <div>
              <h3 class="text-sm font-bold text-gray-900">Événements</h3>
              <p class="text-xs text-gray-500">À venir</p>
            </div>
          </div>
          <ChevronRight :size="16" class="text-gray-300 group-hover:text-gray-500 transition-colors" />
        </div>
        <ul class="space-y-3">
          <li
            v-for="event in upcomingEvents.slice(0, 3)"
            :key="event.id"
            class="flex items-start gap-3"
          >
            <div class="w-9 h-9 rounded-lg bg-blue-50 flex flex-col items-center justify-center shrink-0">
              <span class="text-[10px] font-bold text-blue-600 uppercase leading-none">{{ dayjs(event.start_date).format('MMM') }}</span>
              <span class="text-xs font-bold text-blue-800 leading-none">{{ dayjs(event.start_date).format('DD') }}</span>
            </div>
            <div class="min-w-0">
              <p class="text-xs font-semibold text-gray-800 truncate">{{ event.title }}</p>
              <p class="text-[11px] text-gray-500 truncate">{{ event.city || event.location }}</p>
            </div>
          </li>
          <li v-if="!upcomingEvents.length" class="text-xs text-gray-400 text-center py-3">
            Aucun événement à venir
          </li>
        </ul>
      </RouterLink>

      <!-- ─── ACTUALITÉS CARD ─── -->
      <RouterLink
        to="/mon-espace/actualites"
        class="group bg-white rounded-2xl border border-gray-300/80 p-6 shadow-sm hover:shadow-lg hover:border-gray-400 transition-all duration-200 no-underline overflow-hidden"
      >
        <div class="flex items-center justify-between mb-4">
          <div class="flex items-center gap-3">
            <div class="w-10 h-10 rounded-xl bg-purple-50 flex items-center justify-center">
              <Newspaper :size="20" class="text-purple-500" />
            </div>
            <div>
              <h3 class="text-sm font-bold text-gray-900">Actualités</h3>
              <p class="text-xs text-gray-500">Dernières nouvelles</p>
            </div>
          </div>
          <ChevronRight :size="16" class="text-gray-300 group-hover:text-gray-500 transition-colors" />
        </div>
        <ul class="space-y-3">
          <li
            v-for="article in latestArticles.slice(0, 3)"
            :key="article.id"
            class="flex items-start gap-3"
          >
            <div class="w-9 h-9 rounded-lg bg-gray-100 overflow-hidden shrink-0">
              <img
                v-if="article.cover_image"
                :src="getMediaUrl(article.cover_image)"
                class="w-full h-full object-cover"
                alt=""
              >
            </div>
            <div class="min-w-0">
              <p class="text-xs font-semibold text-gray-800 truncate">{{ article.title }}</p>
              <p class="text-[11px] text-gray-500">{{ dayjs(article.published_at).format('D MMM YYYY') }}</p>
            </div>
          </li>
          <li v-if="!latestArticles.length" class="text-xs text-gray-400 text-center py-3">
            Aucun article récent
          </li>
        </ul>
      </RouterLink>

      <!-- ─── PROGRAMME CARD ─── -->
      <RouterLink
        to="/mon-espace/programme"
        class="group bg-white rounded-2xl border border-gray-300/80 p-6 shadow-sm hover:shadow-lg hover:border-gray-400 transition-all duration-200 no-underline overflow-hidden"
      >
        <div class="flex items-center gap-3 mb-3">
          <div class="w-10 h-10 rounded-xl bg-green-50 flex items-center justify-center">
            <BookOpen :size="20" class="text-green-600" />
          </div>
          <div>
            <h3 class="text-sm font-bold text-gray-900">Programme</h3>
            <p class="text-xs text-gray-500">Notre vision</p>
          </div>
        </div>
        <p class="text-xs text-gray-600 leading-relaxed line-clamp-2">
          Découvrez les axes du programme politique du Front Patriotique Panafricain pour la Côte d'Ivoire.
        </p>
        <div class="mt-3 flex items-center gap-1 text-xs text-green-600 font-medium group-hover:translate-x-0.5 transition-transform">
          Consulter
          <ChevronRight :size="14" />
        </div>
      </RouterLink>

      <!-- ─── FPP-TV CARD ─── -->
      <RouterLink
        to="/mon-espace/fpp-tv"
        class="group bg-white rounded-2xl border border-gray-300/80 p-6 shadow-sm hover:shadow-lg hover:border-gray-400 transition-all duration-200 no-underline overflow-hidden"
      >
        <div class="flex items-center gap-3 mb-3">
          <div class="w-10 h-10 rounded-xl bg-red-50 flex items-center justify-center">
            <Tv :size="20" class="text-red-500" />
          </div>
          <div>
            <h3 class="text-sm font-bold text-gray-900">FPP-TV</h3>
            <p class="text-xs text-gray-500">Vidéos & médias</p>
          </div>
        </div>
        <p class="text-xs text-gray-600 leading-relaxed line-clamp-2">
          Retrouvez les vidéos, interviews et prises de parole du Front Patriotique Panafricain.
        </p>
        <div class="mt-3 flex items-center gap-1 text-xs text-red-500 font-medium group-hover:translate-x-0.5 transition-transform">
          Regarder
          <ChevronRight :size="14" />
        </div>
      </RouterLink>

      <!-- ─── PARAMÈTRES CARD ─── -->
      <RouterLink
        to="/mon-espace/parametres"
        class="group bg-white rounded-2xl border border-gray-300/80 p-6 shadow-sm hover:shadow-lg hover:border-gray-400 transition-all duration-200 no-underline overflow-hidden"
      >
        <div class="flex items-center gap-3 mb-3">
          <div class="w-10 h-10 rounded-xl bg-gray-100 flex items-center justify-center">
            <Settings :size="20" class="text-gray-600" />
          </div>
          <div>
            <h3 class="text-sm font-bold text-gray-900">Paramètres</h3>
            <p class="text-xs text-gray-500">Compte & sécurité</p>
          </div>
        </div>
        <ul class="space-y-1.5 text-xs text-gray-600">
          <li>Modifier mon profil</li>
          <li>Changer mon mot de passe</li>
        </ul>
        <div class="mt-3 flex items-center gap-1 text-xs text-gray-500 font-medium group-hover:text-gray-700 group-hover:translate-x-0.5 transition-all">
          Gérer
          <ChevronRight :size="14" />
        </div>
      </RouterLink>
    </div>
  </div>
</template>
