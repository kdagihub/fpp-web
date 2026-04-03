<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { RouterLink } from 'vue-router'
import { usePaginatedApi } from '@/composables/useApi'
import { useSeoMeta } from '@/composables/useSeoMeta'
import { useShare, buildShareOgUrl } from '@/composables/useShare'
import ShareDialog from '@/components/ShareDialog.vue'
import type { EventListItem } from '@/types'
import {
  CalendarDays,
  MapPin,
  Clock,
  ArrowRight,
  Share2,
  Loader2,
  Filter,
  ChevronLeft,
  ChevronRight,
} from 'lucide-vue-next'

useSeoMeta({
  title: 'Agenda du FPP',
  description: 'Retrouvez nos prochains événements, congrès, formations et rencontres du Front Patriotique Panafricain.',
})

const { showDialog, shareData, copied, openShare, closeShare, shareOn } = useShare()
const { data: events, loading, totalCount, currentPage, hasNext, hasPrevious, fetch: fetchEvents, goToPage } = usePaginatedApi<EventListItem>('/public/events/')

const activeFilter = ref<string>('all')
const FALLBACK_EVENTS: EventListItem[] = [
  {
    id: '1', title: 'Congrès fondateur du FPP', slug: 'congres-fondateur-du-fpp',
    short_description: 'Premier congrès historique du FPP à Abidjan.',
    cover_image: null, event_type: 'conference', status: 'upcoming', computed_status: 'upcoming',
    start_date: '2026-05-02T09:00:00Z', end_date: '2026-05-04T18:00:00Z',
    location: 'Palais de la Culture', city: 'Abidjan', is_featured: true, published_at: '2026-04-02T00:00:00Z',
  },
  {
    id: '2', title: 'Caravane de sensibilisation — Grand Nord', slug: 'caravane-grand-nord',
    short_description: 'Tournée dans les régions du nord pour présenter le programme.',
    cover_image: null, event_type: 'campaign', status: 'upcoming', computed_status: 'upcoming',
    start_date: '2026-05-17T07:00:00Z', end_date: '2026-05-24T19:00:00Z',
    location: 'Korhogo, Bouaké, Odienné', city: 'Korhogo', is_featured: true, published_at: '2026-04-02T00:00:00Z',
  },
  {
    id: '3', title: 'Formation des cadres régionaux', slug: 'formation-cadres-regionaux',
    short_description: 'Formation des responsables régionaux du Parti.',
    cover_image: null, event_type: 'workshop', status: 'upcoming', computed_status: 'upcoming',
    start_date: '2026-04-17T10:00:00Z', end_date: '2026-04-18T17:00:00Z',
    location: 'Hôtel Ivoire', city: 'Abidjan', is_featured: false, published_at: '2026-04-02T00:00:00Z',
  },
]

const displayEvents = computed(() =>
  events.value && events.value.length > 0 ? events.value : FALLBACK_EVENTS,
)

const upcomingEvents = computed(() =>
  displayEvents.value.filter((e) => e.computed_status === 'upcoming' || e.computed_status === 'ongoing'),
)
const pastEvents = computed(() =>
  displayEvents.value.filter((e) => e.computed_status === 'completed'),
)

const typeLabels: Record<string, string> = {
  meeting: 'Réunion',
  rally: 'Rassemblement',
  conference: 'Conférence',
  workshop: 'Atelier',
  ceremony: 'Cérémonie',
  campaign: 'Campagne',
  other: 'Autre',
}

const typeColors: Record<string, string> = {
  meeting: 'bg-blue-100 text-blue-700',
  rally: 'bg-purple-100 text-purple-700',
  conference: 'bg-rose-100 text-rose-700',
  workshop: 'bg-sky-100 text-sky-700',
  ceremony: 'bg-amber-100 text-amber-700',
  campaign: 'bg-emerald-100 text-emerald-700',
  other: 'bg-gray-100 text-gray-700',
}

const filterTypes = computed(() => {
  const types = new Set(displayEvents.value.map((e) => e.event_type))
  return [
    { id: 'all', label: 'Tous' },
    ...Array.from(types).map((t) => ({ id: t, label: typeLabels[t] ?? t })),
  ]
})

const filteredUpcoming = computed(() =>
  activeFilter.value === 'all'
    ? upcomingEvents.value
    : upcomingEvents.value.filter((e) => e.event_type === activeFilter.value),
)

const filteredPast = computed(() =>
  activeFilter.value === 'all'
    ? pastEvents.value
    : pastEvents.value.filter((e) => e.event_type === activeFilter.value),
)

function formatDate(dateStr: string): string {
  return new Date(dateStr).toLocaleDateString('fr-FR', {
    weekday: 'long',
    day: 'numeric',
    month: 'long',
    year: 'numeric',
  })
}

function formatShortDate(dateStr: string): { day: string; month: string } {
  const d = new Date(dateStr)
  return {
    day: d.getDate().toString().padStart(2, '0'),
    month: d.toLocaleDateString('fr-FR', { month: 'short' }).toUpperCase(),
  }
}

function formatTime(dateStr: string): string {
  return new Date(dateStr).toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' })
}

function shareEvent(event: EventListItem) {
  openShare({
    title: event.title,
    description: event.short_description || `${formatDate(event.start_date)} — ${event.location}`,
    url: `${window.location.origin}/agenda#${event.slug}`,
    ogUrl: buildShareOgUrl('event', event.slug),
    image: event.cover_image ?? undefined,
  })
}

onMounted(async () => {
  try {
    await fetchEvents({ page_size: 20 })
  } catch {
    // Fallback silencieux
  }
})
</script>

<template>
  <div>
    <!-- ═══════ HERO ═══════ -->
    <section class="bg-[var(--color-primary)] py-16 md:py-20">
      <div class="mx-auto max-w-[var(--container-xl)] px-6">
        <p class="font-heading text-xs font-bold uppercase tracking-[0.15em] text-[var(--color-accent)] mb-3">
          Calendrier
        </p>
        <h1 class="font-heading text-3xl md:text-4xl lg:text-5xl font-extrabold text-white leading-tight mb-4">
          Agenda du FPP
        </h1>
        <p class="text-white/60 max-w-xl">
          Retrouvez nos prochains événements, congrès, formations et rencontres sur tout le territoire.
        </p>
      </div>
    </section>

    <!-- ═══════ FILTERS ═══════ -->
    <section class="bg-white border-b border-[var(--color-border)] sticky top-0 z-10">
      <div class="mx-auto max-w-[var(--container-xl)] px-6 py-4">
        <div class="flex items-center gap-3 overflow-x-auto scrollbar-none">
          <Filter :size="16" class="text-[var(--color-muted)] shrink-0" />
          <button
            v-for="ft in filterTypes"
            :key="ft.id"
            class="whitespace-nowrap px-4 py-2 font-heading text-xs font-bold uppercase tracking-[0.04em] rounded-full border transition-all cursor-pointer"
            :class="[
              activeFilter === ft.id
                ? 'bg-[var(--color-primary)] text-white border-[var(--color-primary)]'
                : 'bg-white text-[var(--color-muted)] border-[var(--color-border)] hover:border-[var(--color-primary)] hover:text-[var(--color-primary)]'
            ]"
            @click="activeFilter = ft.id"
          >
            {{ ft.label }}
          </button>
        </div>
      </div>
    </section>

    <!-- ═══════ LOADING ═══════ -->
    <div v-if="loading" class="flex items-center justify-center py-32">
      <Loader2 :size="32" class="animate-spin text-[var(--color-accent)]" />
    </div>

    <template v-else>
      <!-- ═══════ UPCOMING EVENTS ═══════ -->
      <section v-if="filteredUpcoming.length > 0" class="bg-white py-16 md:py-20">
        <div class="mx-auto max-w-[var(--container-xl)] px-6">
          <div class="flex items-center gap-3 mb-10">
            <div class="w-3 h-3 rounded-full bg-[var(--color-accent)] animate-pulse" />
            <h2 class="font-heading text-2xl md:text-3xl font-extrabold text-[var(--color-primary)]">
              Événements à venir
            </h2>
          </div>

          <div class="space-y-5">
            <div
              v-for="event in filteredUpcoming"
              :key="event.id"
              :id="event.slug"
              class="group bg-[var(--color-surface)] border border-[var(--color-border)] rounded-xl overflow-hidden transition-all hover:shadow-[var(--shadow-md)]"
            >
              <div class="flex flex-col md:flex-row">
                <!-- Date block -->
                <div class="md:w-28 bg-[var(--color-primary)] text-white flex flex-col items-center justify-center py-5 md:py-0 shrink-0">
                  <span class="font-heading text-3xl font-extrabold leading-none">
                    {{ formatShortDate(event.start_date).day }}
                  </span>
                  <span class="font-heading text-xs font-bold uppercase tracking-[0.1em] text-white/60 mt-1">
                    {{ formatShortDate(event.start_date).month }}
                  </span>
                </div>

                <!-- Content -->
                <div class="flex-1 p-6 md:p-7">
                  <div class="flex flex-wrap items-center gap-3 mb-3">
                    <span
                      class="px-3 py-1 font-heading text-xs font-bold uppercase tracking-[0.04em] rounded-full"
                      :class="typeColors[event.event_type] ?? 'bg-gray-100 text-gray-700'"
                    >
                      {{ typeLabels[event.event_type] ?? event.event_type }}
                    </span>
                    <span v-if="event.is_featured" class="px-3 py-1 font-heading text-xs font-bold uppercase tracking-[0.04em] rounded-full bg-[var(--color-accent-light)] text-[var(--color-accent)]">
                      À la une
                    </span>
                  </div>
                  <h3 class="font-heading text-lg font-bold text-[var(--color-primary)] mb-2">
                    {{ event.title }}
                  </h3>
                  <p class="text-sm text-[var(--color-muted)] leading-relaxed mb-4 max-w-2xl">
                    {{ event.short_description }}
                  </p>
                  <div class="flex flex-wrap items-center gap-5 text-xs text-[var(--color-muted)]">
                    <span class="flex items-center gap-1.5">
                      <CalendarDays :size="14" class="text-[var(--color-accent)]" />
                      {{ formatDate(event.start_date) }}
                    </span>
                    <span class="flex items-center gap-1.5">
                      <Clock :size="14" class="text-[var(--color-accent)]" />
                      {{ formatTime(event.start_date) }}
                      <template v-if="event.end_date"> — {{ formatTime(event.end_date) }}</template>
                    </span>
                    <span class="flex items-center gap-1.5">
                      <MapPin :size="14" class="text-[var(--color-accent)]" />
                      {{ event.location }}<template v-if="event.city">, {{ event.city }}</template>
                    </span>
                  </div>
                </div>

                <!-- Share button -->
                <div class="hidden md:flex items-center pr-6">
                  <button
                    class="w-10 h-10 rounded-full border border-[var(--color-border)] flex items-center justify-center text-[var(--color-muted)] hover:text-[var(--color-accent)] hover:border-[var(--color-accent)] transition-colors cursor-pointer"
                    title="Partager cet événement"
                    @click="shareEvent(event)"
                  >
                    <Share2 :size="16" />
                  </button>
                </div>
              </div>

              <!-- Mobile share -->
              <div class="md:hidden px-6 pb-4">
                <button
                  class="inline-flex items-center gap-2 text-xs font-heading font-bold text-[var(--color-accent)] cursor-pointer"
                  @click="shareEvent(event)"
                >
                  <Share2 :size="14" />
                  Partager
                </button>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- ═══════ PAST EVENTS ═══════ -->
      <section v-if="filteredPast.length > 0" class="bg-[var(--color-surface)] py-16 md:py-20">
        <div class="mx-auto max-w-[var(--container-xl)] px-6">
          <h2 class="font-heading text-2xl md:text-3xl font-extrabold text-[var(--color-primary)] mb-10">
            Événements passés
          </h2>

          <div class="space-y-4">
            <div
              v-for="event in filteredPast"
              :key="event.id"
              :id="event.slug"
              class="bg-white border border-[var(--color-border)] rounded-xl p-5 md:p-6 flex flex-col md:flex-row md:items-center gap-4"
            >
              <div class="flex items-center gap-4 flex-1">
                <div class="w-14 h-14 rounded-lg bg-[var(--color-surface)] flex flex-col items-center justify-center shrink-0">
                  <span class="font-heading text-lg font-extrabold text-[var(--color-primary)] leading-none">
                    {{ formatShortDate(event.start_date).day }}
                  </span>
                  <span class="font-heading text-[9px] font-bold uppercase tracking-[0.08em] text-[var(--color-muted)]">
                    {{ formatShortDate(event.start_date).month }}
                  </span>
                </div>
                <div>
                  <div class="flex items-center gap-2 mb-1">
                    <span
                      class="px-2 py-0.5 font-heading text-[10px] font-bold uppercase tracking-[0.04em] rounded-full"
                      :class="typeColors[event.event_type] ?? 'bg-gray-100 text-gray-700'"
                    >
                      {{ typeLabels[event.event_type] ?? event.event_type }}
                    </span>
                  </div>
                  <h3 class="font-heading text-sm font-bold text-[var(--color-primary)]">
                    {{ event.title }}
                  </h3>
                </div>
              </div>
              <div class="flex items-center gap-4 text-xs text-[var(--color-muted)]">
                <span class="flex items-center gap-1">
                  <MapPin :size="12" />
                  {{ event.location }}
                </span>
                <button
                  class="w-8 h-8 rounded-full border border-[var(--color-border)] flex items-center justify-center text-[var(--color-muted)] hover:text-[var(--color-accent)] hover:border-[var(--color-accent)] transition-colors cursor-pointer shrink-0"
                  @click="shareEvent(event)"
                >
                  <Share2 :size="14" />
                </button>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- ═══════ EMPTY STATE ═══════ -->
      <section v-if="filteredUpcoming.length === 0 && filteredPast.length === 0" class="bg-white py-20">
        <div class="text-center">
          <CalendarDays :size="48" class="text-[var(--color-border)] mx-auto mb-4" />
          <p class="font-heading text-lg font-bold text-[var(--color-primary)] mb-2">Aucun événement trouvé</p>
          <p class="text-sm text-[var(--color-muted)]">Essayez un autre filtre ou revenez bientôt.</p>
        </div>
      </section>

      <!-- ═══════ PAGINATION ═══════ -->
      <section v-if="totalCount > 20" class="bg-white py-8 border-t border-[var(--color-border)]">
        <div class="mx-auto max-w-[var(--container-xl)] px-6 flex items-center justify-center gap-4">
          <button
            :disabled="!hasPrevious"
            class="inline-flex items-center gap-1 px-4 py-2 font-heading text-xs font-bold border border-[var(--color-border)] rounded-lg transition-colors cursor-pointer disabled:opacity-40 disabled:cursor-not-allowed hover:border-[var(--color-primary)]"
            @click="goToPage(currentPage - 1, { page_size: 20 })"
          >
            <ChevronLeft :size="14" />
            Précédent
          </button>
          <span class="font-heading text-sm text-[var(--color-muted)]">
            Page {{ currentPage }}
          </span>
          <button
            :disabled="!hasNext"
            class="inline-flex items-center gap-1 px-4 py-2 font-heading text-xs font-bold border border-[var(--color-border)] rounded-lg transition-colors cursor-pointer disabled:opacity-40 disabled:cursor-not-allowed hover:border-[var(--color-primary)]"
            @click="goToPage(currentPage + 1, { page_size: 20 })"
          >
            Suivant
            <ChevronRight :size="14" />
          </button>
        </div>
      </section>
    </template>

    <!-- ═══════ CTA ═══════ -->
    <section class="bg-[var(--color-primary)] py-16 md:py-20">
      <div class="mx-auto max-w-[var(--container-lg)] px-6 text-center">
        <h2 class="font-heading text-2xl md:text-3xl font-extrabold text-white mb-4">
          Ne manquez aucun événement
        </h2>
        <p class="text-white/60 max-w-lg mx-auto mb-8">
          Devenez membre du FPP pour recevoir les invitations et participer à nos rencontres sur tout le territoire.
        </p>
        <RouterLink
          to="/adherer"
          class="group inline-flex items-center gap-2 px-8 py-4 font-heading text-sm font-bold uppercase tracking-[0.04em] bg-[var(--color-accent)] text-white no-underline rounded-sm transition-all hover:bg-[var(--color-accent-hover)] cursor-pointer"
        >
          Rejoindre le FPP
          <ArrowRight :size="18" class="transition-transform group-hover:translate-x-1" />
        </RouterLink>
      </div>
    </section>

    <!-- Share Dialog -->
    <ShareDialog
      :show="showDialog"
      :title="shareData.title"
      :description="shareData.description"
      :image="shareData.image"
      :copied="copied"
      @close="closeShare"
      @share="shareOn"
    />
  </div>
</template>
