<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { usePaginatedApi } from '@/composables/useApi'
import type { MediaContent, MediaPlatform, MediaEmbedType } from '@/types'
import {
  Tv,
  Calendar,
  Facebook,
  Youtube,
  Loader2,
  ExternalLink,
} from 'lucide-vue-next'

const DEMO_MEDIA: MediaContent[] = [
  {
    id: '1',
    title: 'Meeting Historique du FPP — Yopougon 2025',
    description: 'Retour en images sur le meeting historique du Front Patriotique Panafricain à Yopougon, 12 juillet 2025.',
    platform: 'facebook',
    embed_type: 'video',
    source_url: 'https://www.facebook.com/reel/946502157963600/',
    published_at: '2025-07-12',
    category: 'Meeting',
    is_featured: true,
  },
  {
    id: '2',
    title: 'Le FPP en action — Publication officielle',
    description: 'Publication officielle du Front Patriotique Panafricain sur les activités récentes du Parti.',
    platform: 'facebook',
    embed_type: 'post',
    source_url: 'https://www.facebook.com/leaderfpp/posts/pfbid0tXjRcZNQ6cqN7unxwBhm8DPAg8CiRdnEfRZ94Nt6y5xTnRKK3wbqzoKPkgddvYyWl',
    published_at: '2025-07-10',
    category: 'Communiqué',
    is_featured: false,
  },
  {
    id: '3',
    title: 'Mobilisation citoyenne — Communiqué du Parti',
    description: 'Le FPP appelle à la mobilisation citoyenne pour une Côte d\'Ivoire plus juste.',
    platform: 'facebook',
    embed_type: 'post',
    source_url: 'https://www.facebook.com/leaderfpp/posts/pfbid0t5rCTHriEPvLyH1v2fNJVkVjk8buey3hFs6mQkGTApn4HDnvvEMQtwkBMaAzEVvul',
    published_at: '2025-07-08',
    category: 'Communiqué',
    is_featured: false,
  },
  {
    id: '4',
    title: 'Activités du Parti — Bilan et perspectives',
    description: 'Bilan des activités récentes du FPP et perspectives pour les prochains mois.',
    platform: 'facebook',
    embed_type: 'post',
    source_url: 'https://www.facebook.com/leaderfpp/posts/pfbid02EBtJfBAQS7Fqojf9A4EVtVsuyofgR248VtWTgY6QKcENkBv3n9JpjCUYep9BrKyWl',
    published_at: '2025-07-05',
    category: 'Communiqué',
    is_featured: false,
  },
  {
    id: '5',
    title: 'Reel FPP — Moments forts sur le terrain',
    description: 'Les temps forts des actions du FPP sur le terrain, captés en vidéo.',
    platform: 'facebook',
    embed_type: 'video',
    source_url: 'https://www.facebook.com/reel/953100833749265/',
    published_at: '2025-06-28',
    category: 'Terrain',
    is_featured: false,
  },
  {
    id: '6',
    title: 'Vidéo du Président — Message aux militants',
    description: 'Le Président Dabé Nogbo Wanaminou s\'adresse aux militants et sympathisants du FPP.',
    platform: 'facebook',
    embed_type: 'video',
    source_url: 'https://www.facebook.com/leaderfpp/videos/934848615614460/',
    published_at: '2025-06-20',
    category: 'Interview',
    is_featured: false,
  },
  {
    id: '7',
    title: 'Sensibilisation citoyenne — Reel',
    description: 'Campagne de sensibilisation citoyenne du Front Patriotique Panafricain.',
    platform: 'facebook',
    embed_type: 'video',
    source_url: 'https://www.facebook.com/reel/973591361670445/',
    published_at: '2025-06-15',
    category: 'Terrain',
    is_featured: false,
  },
  {
    id: '8',
    title: 'Déclaration officielle du FPP',
    description: 'Déclaration officielle du Front Patriotique Panafricain sur l\'actualité nationale.',
    platform: 'facebook',
    embed_type: 'post',
    source_url: 'https://www.facebook.com/leaderfpp/posts/pfbid0258NE3B1zxbQ7jDAMMtQS5SeYY2poDfcv4bWor4qfTbYSNhKv9ejvRuhSTHZ11Hwul',
    published_at: '2025-06-10',
    category: 'Communiqué',
    is_featured: false,
  },
]

function isFacebookEmbeddable(url: string): boolean {
  const lower = url.toLowerCase()
  return (
    lower.includes('/reel/') ||
    lower.includes('/videos/') ||
    lower.includes('/watch') ||
    lower.includes('plugins/video.php')
  )
}

function getEmbedUrl(media: MediaContent): string {
  if (media.platform === 'facebook') {
    if (!isFacebookEmbeddable(media.source_url)) {
      return ''
    }
    const encodedUrl = encodeURIComponent(media.source_url)
    return `https://www.facebook.com/plugins/video.php?height=399&href=${encodedUrl}&show_text=false&width=560&t=0`
  }
  return `https://www.youtube.com/embed/${media.source_url}`
}

function getFacebookPostUrl(media: MediaContent): string {
  return media.source_url
}

function isEmbeddable(media: MediaContent): boolean {
  if (media.embed_type !== 'video') return false
  if (media.platform === 'facebook') return isFacebookEmbeddable(media.source_url)
  return true
}

const platformLabel: Record<MediaPlatform, string> = {
  youtube: 'YouTube',
  facebook: 'Facebook',
}

const {
  data: apiMedia,
  loading,
  totalCount,
  currentPage,
  goToPage,
} = usePaginatedApi<MediaContent>('/public/media/')

const useApi = ref(false)
const videos = computed(() => useApi.value ? apiMedia.value : DEMO_MEDIA)

async function loadMedia(page: number) {
  const params: Record<string, unknown> = { page, page_size: 50 }
  if (selectedPlatform.value) params.platform = selectedPlatform.value
  if (selectedCategory.value) params.category = selectedCategory.value
  try {
    await goToPage(page, params)
    useApi.value = true
  } catch {
    useApi.value = false
  }
}

const selectedCategory = ref<string | null>(null)
const selectedPlatform = ref<MediaPlatform | null>(null)
const featuredVideo = computed(() => videos.value[0] ?? null)

const categories = computed(() => {
  const cats = new Set(videos.value.map((v) => v.category).filter(Boolean))
  return Array.from(cats)
})

const filteredVideos = computed(() => {
  let rest = videos.value.slice(1)
  if (selectedCategory.value) {
    rest = rest.filter((v) => v.category === selectedCategory.value)
  }
  if (selectedPlatform.value) {
    rest = rest.filter((v) => v.platform === selectedPlatform.value)
  }
  return rest
})

function formatDate(dateStr: string): string {
  return new Date(dateStr).toLocaleDateString('fr-FR', {
    day: 'numeric',
    month: 'long',
    year: 'numeric',
  })
}

const categoryColors: Record<string, string> = {
  Meeting: 'bg-emerald-100 text-emerald-700',
  Congrès: 'bg-purple-100 text-purple-700',
  Communiqué: 'bg-indigo-100 text-indigo-700',
  Événement: 'bg-amber-100 text-amber-700',
  Terrain: 'bg-sky-100 text-sky-700',
  Interview: 'bg-rose-100 text-rose-700',
  Formation: 'bg-blue-100 text-blue-700',
}

onMounted(() => {
  loadMedia(1)
})
</script>

<template>
  <div>
    <!-- ════════════════════ HERO ════════════════════ -->
    <section class="bg-[var(--color-primary)] py-16 md:py-20">
      <div class="mx-auto max-w-[var(--container-xl)] px-6">
        <div class="flex items-center gap-3 mb-3">
          <Tv :size="20" class="text-[var(--color-accent)]" />
          <p class="font-heading text-xs font-bold uppercase tracking-[0.15em] text-[var(--color-accent)]">
            Vidéothèque
          </p>
        </div>
        <h1 class="font-heading text-3xl md:text-4xl lg:text-5xl font-extrabold text-white leading-tight mb-4">
          FPP-TV
        </h1>
        <p class="text-white/60 max-w-xl">
          Retrouvez nos discours, reportages, interviews et publications vidéo sur Facebook et YouTube. Le FPP en images et en action.
        </p>
      </div>
    </section>

    <!-- ════════════════════ FEATURED VIDEO ════════════════════ -->
    <section v-if="featuredVideo" class="bg-white py-12 md:py-16 border-b border-[var(--color-border)]">
      <div class="mx-auto max-w-[var(--container-xl)] px-6">
        <div class="grid grid-cols-1 lg:grid-cols-12 gap-8">
          <div class="lg:col-span-8">
            <!-- Video embed -->
            <div v-if="isEmbeddable(featuredVideo)" class="aspect-video rounded-xl overflow-hidden bg-black shadow-[var(--shadow-lg)]">
              <iframe
                :src="getEmbedUrl(featuredVideo)"
                class="w-full h-full border-none overflow-hidden"
                scrolling="no"
                frameborder="0"
                allow="autoplay; clipboard-write; encrypted-media; picture-in-picture"
                allowfullscreen
                title="Vidéo à la une"
              />
            </div>
            <!-- Post card (non-embeddable) -->
            <a
              v-else
              :href="getFacebookPostUrl(featuredVideo)"
              target="_blank"
              rel="noopener noreferrer"
              class="block aspect-video rounded-xl overflow-hidden bg-gradient-to-br from-[#1877F2] to-[#0C5CBF] shadow-[var(--shadow-lg)] relative group no-underline"
            >
              <div class="absolute inset-0 flex flex-col items-center justify-center text-white p-8 text-center">
                <Facebook :size="48" class="mb-4 opacity-80" />
                <p class="font-heading text-lg md:text-xl font-bold leading-snug mb-3 max-w-md">
                  {{ featuredVideo.title }}
                </p>
                <span class="inline-flex items-center gap-2 px-5 py-2.5 bg-white text-[#1877F2] rounded-full font-heading text-sm font-bold transition-transform group-hover:scale-105">
                  <ExternalLink :size="15" />
                  Voir sur Facebook
                </span>
              </div>
            </a>
          </div>
          <div class="lg:col-span-4 flex flex-col justify-center">
            <span class="inline-block px-3 py-1 bg-[var(--color-accent)] text-white font-heading text-xs font-bold uppercase tracking-[0.06em] rounded-sm w-fit mb-4">
              À la une
            </span>
            <div class="flex items-center gap-2 mb-3 flex-wrap">
              <span
                class="inline-flex items-center gap-1.5 px-3 py-1 font-heading text-xs font-bold uppercase tracking-[0.04em] rounded-full"
                :class="categoryColors[featuredVideo.category] ?? 'bg-gray-100 text-gray-700'"
              >
                {{ featuredVideo.category }}
              </span>
              <span class="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-bold"
                :class="featuredVideo.platform === 'facebook' ? 'bg-[#1877F2]/10 text-[#1877F2]' : 'bg-red-50 text-red-600'"
              >
                <Facebook v-if="featuredVideo.platform === 'facebook'" :size="12" />
                <Youtube v-else :size="12" />
                {{ platformLabel[featuredVideo.platform] }}
              </span>
            </div>
            <h2 class="font-heading text-xl md:text-2xl font-extrabold text-[var(--color-primary)] mb-3 leading-tight">
              {{ featuredVideo.title }}
            </h2>
            <p class="text-sm text-[var(--color-muted)] leading-relaxed mb-4">
              {{ featuredVideo.description }}
            </p>
            <div class="flex items-center gap-2 text-xs text-[var(--color-muted)]">
              <Calendar :size="14" />
              {{ formatDate(featuredVideo.published_at) }}
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- ════════════════════ FILTERS ════════════════════ -->
    <section class="bg-white sticky top-16 z-30 border-b border-[var(--color-border)]">
      <div class="mx-auto max-w-[var(--container-xl)] px-6 py-4">
        <!-- Plateforme -->
        <div class="flex items-center gap-2 mb-3">
          <span class="text-[10px] font-heading font-bold uppercase tracking-[0.08em] text-[var(--color-muted)] mr-1 hidden sm:inline">Plateforme</span>
          <button
            class="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full border text-xs font-bold transition-all cursor-pointer"
            :class="[
              !selectedPlatform
                ? 'bg-[var(--color-primary)] text-white border-[var(--color-primary)]'
                : 'bg-white text-[var(--color-muted)] border-[var(--color-border)] hover:border-[var(--color-primary)]'
            ]"
            @click="selectedPlatform = null"
          >
            Tout
          </button>
          <button
            class="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full border text-xs font-bold transition-all cursor-pointer"
            :class="[
              selectedPlatform === 'facebook'
                ? 'bg-[#1877F2] text-white border-[#1877F2]'
                : 'bg-white text-[var(--color-muted)] border-[var(--color-border)] hover:border-[#1877F2] hover:text-[#1877F2]'
            ]"
            @click="selectedPlatform = selectedPlatform === 'facebook' ? null : 'facebook'"
          >
            <Facebook :size="13" />
            Facebook
          </button>
          <button
            class="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full border text-xs font-bold transition-all cursor-pointer"
            :class="[
              selectedPlatform === 'youtube'
                ? 'bg-red-600 text-white border-red-600'
                : 'bg-white text-[var(--color-muted)] border-[var(--color-border)] hover:border-red-600 hover:text-red-600'
            ]"
            @click="selectedPlatform = selectedPlatform === 'youtube' ? null : 'youtube'"
          >
            <Youtube :size="13" />
            YouTube
          </button>
        </div>

        <!-- Catégories (scroll horizontal mobile) -->
        <div class="flex items-center gap-2 overflow-x-auto pb-1 -mx-1 px-1 scrollbar-none">
          <button
            class="shrink-0 px-3.5 py-1.5 font-heading text-xs font-bold uppercase tracking-[0.04em] rounded-full border transition-all cursor-pointer"
            :class="[
              !selectedCategory
                ? 'bg-[var(--color-primary)] text-white border-[var(--color-primary)]'
                : 'bg-white text-[var(--color-muted)] border-[var(--color-border)] hover:border-[var(--color-primary)]'
            ]"
            @click="selectedCategory = null"
          >
            Toutes
          </button>
          <button
            v-for="cat in categories"
            :key="cat"
            class="shrink-0 px-3.5 py-1.5 font-heading text-xs font-bold uppercase tracking-[0.04em] rounded-full border transition-all cursor-pointer whitespace-nowrap"
            :class="[
              selectedCategory === cat
                ? 'bg-[var(--color-primary)] text-white border-[var(--color-primary)]'
                : 'bg-white text-[var(--color-muted)] border-[var(--color-border)] hover:border-[var(--color-primary)]'
            ]"
            @click="selectedCategory = cat"
          >
            {{ cat }}
          </button>
        </div>
      </div>
    </section>

    <!-- ════════════════════ VIDEO GRID ════════════════════ -->
    <section class="bg-[var(--color-surface)] py-12 md:py-16">
      <div class="mx-auto max-w-[var(--container-xl)] px-6">
        <div v-if="loading && videos.length === 0" class="flex items-center justify-center py-20">
          <Loader2 :size="32" class="animate-spin text-[var(--color-accent)]" />
        </div>

        <div v-else-if="filteredVideos.length === 0" class="text-center py-16">
          <p class="text-[var(--color-muted)] text-lg">Aucune vidéo dans cette sélection.</p>
        </div>

        <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <div
            v-for="video in filteredVideos"
            :key="video.id"
            class="group bg-white border border-[var(--color-border)] rounded-xl overflow-hidden transition-all hover:shadow-[var(--shadow-md)]"
          >
            <!-- Video embed -->
            <div v-if="isEmbeddable(video)" class="relative bg-black aspect-video">
              <iframe
                :src="getEmbedUrl(video)"
                class="w-full h-full border-none overflow-hidden"
                scrolling="no"
                frameborder="0"
                allow="autoplay; clipboard-write; encrypted-media; picture-in-picture"
                allowfullscreen
                :title="video.title"
              />
            </div>
            <!-- Post card -->
            <a
              v-else
              :href="getFacebookPostUrl(video)"
              target="_blank"
              rel="noopener noreferrer"
              class="block aspect-video bg-gradient-to-br from-[#1877F2] to-[#0C5CBF] relative group/post no-underline"
            >
              <div class="absolute inset-0 flex flex-col items-center justify-center text-white p-6 text-center">
                <Facebook :size="32" class="mb-3 opacity-70" />
                <p class="font-heading text-sm font-bold leading-snug mb-3 line-clamp-2 max-w-[220px]">
                  {{ video.title }}
                </p>
                <span class="inline-flex items-center gap-1.5 px-4 py-2 bg-white text-[#1877F2] rounded-full font-heading text-xs font-bold transition-transform group-hover/post:scale-105">
                  <ExternalLink :size="13" />
                  Voir sur Facebook
                </span>
              </div>
            </a>
            <div class="p-5">
              <div class="flex items-center gap-2 mb-3 flex-wrap">
                <span
                  class="px-2 py-0.5 font-heading text-[10px] font-bold uppercase tracking-[0.04em] rounded-full"
                  :class="categoryColors[video.category] ?? 'bg-gray-100 text-gray-700'"
                >
                  {{ video.category }}
                </span>
                <span
                  class="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-bold"
                  :class="video.platform === 'facebook' ? 'bg-[#1877F2]/10 text-[#1877F2]' : 'bg-red-50 text-red-600'"
                >
                  <Facebook v-if="video.platform === 'facebook'" :size="10" />
                  <Youtube v-else :size="10" />
                  {{ platformLabel[video.platform] }}
                </span>
                <span class="flex items-center gap-1 text-xs text-[var(--color-muted)]">
                  <Calendar :size="12" />
                  {{ formatDate(video.published_at) }}
                </span>
              </div>
              <h3 class="font-heading text-sm font-bold text-[var(--color-primary)] mb-1.5 leading-snug">
                {{ video.title }}
              </h3>
              <p class="text-xs text-[var(--color-muted)] leading-relaxed line-clamp-2">
                {{ video.description }}
              </p>
            </div>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>
