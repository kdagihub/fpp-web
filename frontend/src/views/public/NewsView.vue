<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue'
import { RouterLink } from 'vue-router'
import { usePaginatedApi, useApiGet } from '@/composables/useApi'
import type { ArticleListItem, Category, MediaContent, MediaPlatform } from '@/types'
import {
  Search,
  Calendar,
  ChevronRight,
  ArrowRight,
  Loader2,
  X,
  Facebook,
  Youtube,
  Tv,
  ExternalLink,
} from 'lucide-vue-next'
import logoFpp from '@/assets/img/fpplogsf.png'

const PAGE_SIZE = 9

const {
  data: articles,
  loading,
  error,
  totalCount,
  currentPage,
  fetch: fetchArticles,
  goToPage,
} = usePaginatedApi<ArticleListItem>('/public/articles/')

const { data: categories, execute: fetchCategories } = useApiGet<Category[]>('/public/categories/')

const DEMO_MEDIA: MediaContent[] = [
  {
    id: 'm1',
    title: 'Meeting Historique du FPP — Yopougon 2025',
    description: 'Retour en images sur le meeting historique du Front Patriotique Panafricain.',
    platform: 'facebook',
    embed_type: 'video',
    source_url: 'https://www.facebook.com/reel/946502157963600/',
    published_at: '2025-07-12',
    category: 'Meeting',
    is_featured: true,
  },
  {
    id: 'm2',
    title: 'Le FPP en action — Publication officielle',
    description: 'Publication officielle du Front Patriotique Panafricain.',
    platform: 'facebook',
    embed_type: 'post',
    source_url: 'https://www.facebook.com/leaderfpp/posts/pfbid0tXjRcZNQ6cqN7unxwBhm8DPAg8CiRdnEfRZ94Nt6y5xTnRKK3wbqzoKPkgddvYyWl',
    published_at: '2025-07-10',
    category: 'Communiqué',
    is_featured: false,
  },
  {
    id: 'm3',
    title: 'Reel FPP — Moments forts sur le terrain',
    description: 'Les temps forts des actions du FPP sur le terrain.',
    platform: 'facebook',
    embed_type: 'video',
    source_url: 'https://www.facebook.com/reel/953100833749265/',
    published_at: '2025-06-28',
    category: 'Terrain',
    is_featured: false,
  },
]

const {
  data: apiRecentMedia,
  fetch: fetchRecentMedia,
} = usePaginatedApi<MediaContent>('/public/media/')

const useMediaApi = ref(false)
const recentMedia = computed(() => useMediaApi.value ? apiRecentMedia.value : DEMO_MEDIA)

async function loadRecentMedia() {
  try {
    await fetchRecentMedia({ page: 1, page_size: 3 })
    if (apiRecentMedia.value.length > 0) {
      useMediaApi.value = true
    }
  } catch {
    useMediaApi.value = false
  }
}

function getEmbedUrl(media: MediaContent): string {
  if (media.platform === 'facebook') {
    const encodedUrl = encodeURIComponent(media.source_url)
    return `https://www.facebook.com/plugins/video.php?height=399&href=${encodedUrl}&show_text=false&width=560&t=0`
  }
  return `https://www.youtube.com/embed/${media.source_url}`
}

function isEmbeddable(media: MediaContent): boolean {
  return media.embed_type === 'video'
}

const selectedCategory = ref<string | null>(null)
const searchQuery = ref('')
const searchDebounced = ref('')

let searchTimeout: ReturnType<typeof setTimeout>
watch(searchQuery, (val) => {
  clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => {
    searchDebounced.value = val
  }, 400)
})

watch([selectedCategory, searchDebounced], () => {
  loadArticles(1)
})

const featuredArticle = computed(() =>
  articles.value.find((a) => a.is_featured) ?? articles.value[0] ?? null,
)

const gridArticles = computed(() => {
  if (!featuredArticle.value) return articles.value
  return articles.value.filter((a) => a.id !== featuredArticle.value?.id)
})

const totalPages = computed(() => Math.ceil(totalCount.value / PAGE_SIZE))

function buildParams(page: number): Record<string, unknown> {
  const params: Record<string, unknown> = { page }
  if (selectedCategory.value) params.category = selectedCategory.value
  if (searchDebounced.value.trim()) params.search = searchDebounced.value.trim()
  return params
}

async function loadArticles(page: number) {
  try {
    await goToPage(page, buildParams(page))
  } catch {
    // error is handled by the composable
  }
}

function clearFilters() {
  selectedCategory.value = null
  searchQuery.value = ''
  searchDebounced.value = ''
}

function formatDate(dateStr: string): string {
  return new Date(dateStr).toLocaleDateString('fr-FR', {
    day: 'numeric',
    month: 'long',
    year: 'numeric',
  })
}

onMounted(() => {
  fetchCategories()
  loadArticles(1)
  loadRecentMedia()
})
</script>

<template>
  <div>
    <!-- ════════════════════ HERO ════════════════════ -->
    <section class="bg-[var(--color-primary)] py-16 md:py-20">
      <div class="mx-auto max-w-[var(--container-xl)] px-6">
        <p class="font-heading text-xs font-bold uppercase tracking-[0.15em] text-[var(--color-accent)] mb-3">
          Restez informés
        </p>
        <h1 class="font-heading text-3xl md:text-4xl lg:text-5xl font-extrabold text-white leading-tight mb-4">
          Actualités
        </h1>
        <p class="text-white/60 max-w-xl">
          Suivez les dernières nouvelles, événements et prises de position du Front Patriotique Panafricain.
        </p>
      </div>
    </section>

    <!-- ════════════════════ FEATURED ARTICLE ════════════════════ -->
    <section
      v-if="featuredArticle && !selectedCategory && !searchDebounced"
      class="bg-white border-b border-[var(--color-border)]"
    >
      <div class="mx-auto max-w-[var(--container-xl)] px-6 py-12">
        <RouterLink
          :to="`/actualites/${featuredArticle.slug}`"
          class="group grid grid-cols-1 lg:grid-cols-2 gap-8 no-underline"
        >
          <div class="aspect-[16/9] bg-[var(--color-surface)] rounded-xl overflow-hidden relative">
            <img
              v-if="featuredArticle.cover_image"
              :src="featuredArticle.cover_image"
              :alt="featuredArticle.title"
              class="w-full h-full object-cover transition-transform duration-300 group-hover:scale-105"
            >
            <div v-else class="absolute inset-0 flex items-center justify-center">
              <img :src="logoFpp" alt="" class="w-20 opacity-10">
            </div>
            <span class="absolute top-4 left-4 px-3 py-1 bg-[var(--color-accent)] text-white text-xs font-heading font-bold uppercase tracking-[0.06em] rounded-sm">
              À la une
            </span>
          </div>
          <div class="flex flex-col justify-center">
            <span class="inline-block px-3 py-1 bg-[var(--color-accent-light)] text-[var(--color-accent)] font-heading text-xs font-bold uppercase tracking-[0.06em] rounded-sm w-fit mb-4">
              {{ featuredArticle.category_name }}
            </span>
            <h2 class="font-heading text-2xl md:text-3xl font-extrabold text-[var(--color-primary)] mb-3 group-hover:text-[var(--color-accent)] transition-colors leading-tight">
              {{ featuredArticle.title }}
            </h2>
            <p class="text-[var(--color-muted)] leading-relaxed mb-4 line-clamp-3">
              {{ featuredArticle.summary }}
            </p>
            <div class="flex items-center gap-4 text-xs text-[var(--color-muted)]">
              <span class="flex items-center gap-1.5">
                <Calendar :size="14" />
                {{ formatDate(featuredArticle.published_at) }}
              </span>
              <span>{{ featuredArticle.author_name }}</span>
            </div>
            <span class="inline-flex items-center gap-1 mt-6 font-heading text-sm font-bold text-[var(--color-accent)] uppercase tracking-[0.04em]">
              Lire l'article
              <ArrowRight :size="16" class="transition-transform group-hover:translate-x-1" />
            </span>
          </div>
        </RouterLink>
      </div>
    </section>

    <!-- ════════════════════ FILTERS ════════════════════ -->
    <section class="bg-white sticky top-16 z-30 border-b border-[var(--color-border)]">
      <div class="mx-auto max-w-[var(--container-xl)] px-6 py-4">
        <div class="flex flex-col md:flex-row md:items-center gap-4">
          <!-- Category pills -->
          <div class="flex flex-wrap gap-2 flex-1">
            <button
              class="px-4 py-2 font-heading text-xs font-bold uppercase tracking-[0.04em] rounded-full border transition-all cursor-pointer"
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
              v-for="cat in (categories ?? [])"
              :key="cat.id"
              class="px-4 py-2 font-heading text-xs font-bold uppercase tracking-[0.04em] rounded-full border transition-all cursor-pointer"
              :class="[
                selectedCategory === cat.slug
                  ? 'bg-[var(--color-primary)] text-white border-[var(--color-primary)]'
                  : 'bg-white text-[var(--color-muted)] border-[var(--color-border)] hover:border-[var(--color-primary)]'
              ]"
              @click="selectedCategory = cat.slug"
            >
              {{ cat.name }}
            </button>
          </div>

          <!-- Search -->
          <div class="relative w-full md:w-72">
            <Search :size="16" class="absolute left-3 top-1/2 -translate-y-1/2 text-[var(--color-muted)]" />
            <input
              v-model="searchQuery"
              type="text"
              placeholder="Rechercher..."
              class="w-full pl-10 pr-9 py-2.5 text-sm border border-[var(--color-border)] rounded-lg bg-[var(--color-surface)] focus:outline-none focus:ring-2 focus:ring-[var(--color-accent)] focus:border-transparent transition"
            >
            <button
              v-if="searchQuery"
              class="absolute right-3 top-1/2 -translate-y-1/2 text-[var(--color-muted)] hover:text-[var(--color-primary)] cursor-pointer"
              @click="searchQuery = ''"
            >
              <X :size="14" />
            </button>
          </div>
        </div>
      </div>
    </section>

    <!-- ════════════════════ ARTICLES GRID ════════════════════ -->
    <section class="bg-[var(--color-surface)] py-12 md:py-16">
      <div class="mx-auto max-w-[var(--container-xl)] px-6">
        <!-- Loading -->
        <div v-if="loading" class="flex items-center justify-center py-20">
          <Loader2 :size="32" class="animate-spin text-[var(--color-accent)]" />
        </div>

        <!-- Error -->
        <div v-else-if="error" class="text-center py-20">
          <p class="text-[var(--color-error)] font-heading font-bold mb-4">{{ error }}</p>
          <button
            class="px-6 py-2.5 font-heading text-sm font-bold bg-[var(--color-primary)] text-white rounded-sm cursor-pointer"
            @click="loadArticles(currentPage)"
          >
            Réessayer
          </button>
        </div>

        <!-- Empty state -->
        <div v-else-if="articles.length === 0" class="text-center py-20">
          <p class="text-[var(--color-muted)] text-lg mb-2">Aucun article trouvé.</p>
          <button
            v-if="selectedCategory || searchDebounced"
            class="mt-4 px-6 py-2.5 font-heading text-sm font-bold text-[var(--color-accent)] border-2 border-[var(--color-accent)] rounded-sm cursor-pointer hover:bg-[var(--color-accent)] hover:text-white transition-all"
            @click="clearFilters"
          >
            Réinitialiser les filtres
          </button>
        </div>

        <!-- Grid -->
        <div v-else>
          <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            <RouterLink
              v-for="article in (selectedCategory || searchDebounced ? articles : gridArticles)"
              :key="article.id"
              :to="`/actualites/${article.slug}`"
              class="group bg-white border border-[var(--color-border)] rounded-xl overflow-hidden no-underline transition-all hover:shadow-[var(--shadow-md)] hover:-translate-y-0.5 cursor-pointer"
            >
              <div class="aspect-[16/9] bg-[var(--color-border)] relative overflow-hidden">
                <img
                  v-if="article.cover_image"
                  :src="article.cover_image"
                  :alt="article.title"
                  class="w-full h-full object-cover transition-transform duration-300 group-hover:scale-105"
                >
                <div v-else class="absolute inset-0 flex items-center justify-center">
                  <img :src="logoFpp" alt="" class="w-16 opacity-10">
                </div>
                <span class="absolute top-3 left-3 px-3 py-1 bg-[var(--color-accent)] text-white text-xs font-heading font-bold uppercase tracking-[0.06em] rounded-sm">
                  {{ article.category_name }}
                </span>
              </div>
              <div class="p-6">
                <div class="flex items-center gap-2 text-xs text-[var(--color-muted)] mb-3">
                  <Calendar :size="14" />
                  {{ formatDate(article.published_at) }}
                </div>
                <h3 class="font-heading text-base font-bold text-[var(--color-primary)] mb-2 group-hover:text-[var(--color-accent)] transition-colors leading-snug">
                  {{ article.title }}
                </h3>
                <p class="text-sm text-[var(--color-muted)] leading-relaxed line-clamp-2">
                  {{ article.summary }}
                </p>
                <span class="inline-flex items-center gap-1 mt-4 font-heading text-xs font-bold text-[var(--color-accent)] uppercase tracking-[0.04em]">
                  Lire la suite
                  <ChevronRight :size="14" class="transition-transform group-hover:translate-x-0.5" />
                </span>
              </div>
            </RouterLink>
          </div>

          <!-- Pagination -->
          <div v-if="totalPages > 1" class="flex items-center justify-center gap-2 mt-12">
            <button
              v-for="page in totalPages"
              :key="page"
              class="w-10 h-10 rounded-lg font-heading text-sm font-bold transition-all cursor-pointer"
              :class="[
                currentPage === page
                  ? 'bg-[var(--color-primary)] text-white'
                  : 'bg-white text-[var(--color-muted)] border border-[var(--color-border)] hover:border-[var(--color-primary)]'
              ]"
              @click="loadArticles(page)"
            >
              {{ page }}
            </button>
          </div>
        </div>
      </div>
    </section>

    <!-- ════════════════════ RECENT MEDIA ════════════════════ -->
    <section v-if="recentMedia.length > 0" class="bg-white border-t border-[var(--color-border)] py-12 md:py-16">
      <div class="mx-auto max-w-[var(--container-xl)] px-6">
        <div class="flex items-center justify-between mb-8">
          <div class="flex items-center gap-3">
            <Tv :size="20" class="text-[var(--color-accent)]" />
            <h2 class="font-heading text-xl md:text-2xl font-extrabold text-[var(--color-primary)]">
              Derniers médias
            </h2>
          </div>
          <RouterLink
            to="/fpp-tv"
            class="inline-flex items-center gap-1.5 font-heading text-sm font-bold text-[var(--color-accent)] uppercase tracking-[0.04em] no-underline hover:gap-2.5 transition-all"
          >
            Voir tout
            <ArrowRight :size="16" />
          </RouterLink>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <div
            v-for="media in recentMedia"
            :key="media.id"
            class="group bg-[var(--color-surface)] border border-[var(--color-border)] rounded-xl overflow-hidden transition-all hover:shadow-[var(--shadow-md)]"
          >
            <!-- Video embed -->
            <div v-if="isEmbeddable(media)" class="relative bg-black aspect-video">
              <iframe
                :src="getEmbedUrl(media)"
                class="w-full h-full border-none overflow-hidden"
                scrolling="no"
                frameborder="0"
                allow="autoplay; clipboard-write; encrypted-media; picture-in-picture"
                allowfullscreen
                :title="media.title"
              />
            </div>
            <!-- Post card -->
            <a
              v-else
              :href="media.source_url"
              target="_blank"
              rel="noopener noreferrer"
              class="block aspect-video bg-gradient-to-br from-[#1877F2] to-[#0C5CBF] relative group/post no-underline"
            >
              <div class="absolute inset-0 flex flex-col items-center justify-center text-white p-6 text-center">
                <Facebook :size="32" class="mb-3 opacity-70" />
                <p class="font-heading text-sm font-bold leading-snug mb-3 line-clamp-2 max-w-[220px]">
                  {{ media.title }}
                </p>
                <span class="inline-flex items-center gap-1.5 px-4 py-2 bg-white text-[#1877F2] rounded-full font-heading text-xs font-bold transition-transform group-hover/post:scale-105">
                  <ExternalLink :size="13" />
                  Voir sur Facebook
                </span>
              </div>
            </a>
            <div class="p-5">
              <div class="flex items-center gap-2 mb-2 flex-wrap">
                <span
                  class="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-bold"
                  :class="media.platform === 'facebook' ? 'bg-[#1877F2]/10 text-[#1877F2]' : 'bg-red-50 text-red-600'"
                >
                  <Facebook v-if="media.platform === 'facebook'" :size="10" />
                  <Youtube v-else :size="10" />
                  {{ media.platform === 'facebook' ? 'Facebook' : 'YouTube' }}
                </span>
                <span class="flex items-center gap-1 text-xs text-[var(--color-muted)]">
                  <Calendar :size="12" />
                  {{ formatDate(media.published_at) }}
                </span>
              </div>
              <h3 class="font-heading text-sm font-bold text-[var(--color-primary)] leading-snug line-clamp-2">
                {{ media.title }}
              </h3>
            </div>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>
