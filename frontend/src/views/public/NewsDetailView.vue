<script setup lang="ts">
import { onMounted, computed, watch } from 'vue'
import { RouterLink } from 'vue-router'
import { useApiGet, usePaginatedApi } from '@/composables/useApi'
import { useSeoMeta } from '@/composables/useSeoMeta'
import { useShare, buildShareOgUrl } from '@/composables/useShare'
import ShareDialog from '@/components/ShareDialog.vue'
import type { ArticleDetail, ArticleListItem } from '@/types'
import {
  ArrowLeft,
  Calendar,
  User,
  Share2,
  Loader2,
  ChevronRight,
} from 'lucide-vue-next'
import logoFpp from '@/assets/img/fpplogsf.png'

const props = defineProps<{ slug: string }>()

const { data: article, loading, error, execute: fetchArticle } = useApiGet<ArticleDetail>(`/public/articles/${props.slug}/`)
const { data: relatedArticles, fetch: fetchRelated } = usePaginatedApi<ArticleListItem>('/public/articles/')
const { showDialog, shareData, copied, openShare, closeShare, shareOn } = useShare()

const articleTitle = computed(() => article.value?.title ?? 'Article')
const articleDescription = computed(() => article.value?.summary ?? '')
const articleImage = computed(() => article.value?.cover_image ?? undefined)

useSeoMeta({
  title: articleTitle,
  description: articleDescription,
  image: articleImage,
  type: 'article',
})

function formatDate(dateStr: string): string {
  return new Date(dateStr).toLocaleDateString('fr-FR', {
    day: 'numeric',
    month: 'long',
    year: 'numeric',
  })
}

function openShareDialog() {
  openShare({
    title: article.value?.title ?? '',
    description: article.value?.summary ?? '',
    url: window.location.href,
    ogUrl: buildShareOgUrl('article', props.slug),
    image: article.value?.cover_image ?? undefined,
  })
}

onMounted(async () => {
  await fetchArticle()
  fetchRelated({ page: 1, page_size: 4 })
})

const filteredRelated = computed(() =>
  (relatedArticles.value ?? []).filter((a) => a.slug !== props.slug).slice(0, 3),
)
</script>

<template>
  <div>
    <!-- Loading -->
    <div v-if="loading" class="flex items-center justify-center py-32">
      <Loader2 :size="32" class="animate-spin text-[var(--color-accent)]" />
    </div>

    <!-- Error -->
    <div v-else-if="error" class="py-32 text-center">
      <p class="text-[var(--color-error)] font-heading font-bold mb-4">{{ error }}</p>
      <RouterLink
        to="/actualites"
        class="inline-flex items-center gap-2 font-heading text-sm font-bold text-[var(--color-accent)] no-underline"
      >
        <ArrowLeft :size="16" />
        Retour aux actualités
      </RouterLink>
    </div>

    <!-- Article content -->
    <template v-else-if="article">
      <!-- Breadcrumb -->
      <section class="bg-white border-b border-[var(--color-border)]">
        <div class="mx-auto max-w-[var(--container-lg)] px-6 py-4">
          <nav class="flex items-center gap-2 text-xs text-[var(--color-muted)]">
            <RouterLink to="/" class="hover:text-[var(--color-primary)] no-underline transition-colors">
              Accueil
            </RouterLink>
            <ChevronRight :size="12" />
            <RouterLink to="/actualites" class="hover:text-[var(--color-primary)] no-underline transition-colors">
              Actualités
            </RouterLink>
            <ChevronRight :size="12" />
            <span class="text-[var(--color-primary)] font-medium truncate max-w-[200px]">
              {{ article.title }}
            </span>
          </nav>
        </div>
      </section>

      <!-- Article header -->
      <section class="bg-white py-10 md:py-14">
        <div class="mx-auto max-w-[var(--container-lg)] px-6">
          <span class="inline-block px-3 py-1 bg-[var(--color-accent-light)] text-[var(--color-accent)] font-heading text-xs font-bold uppercase tracking-[0.06em] rounded-sm mb-5">
            {{ article.category_name }}
          </span>
          <h1 class="font-heading text-3xl md:text-4xl lg:text-5xl font-extrabold text-[var(--color-primary)] leading-tight mb-6">
            {{ article.title }}
          </h1>
          <div class="flex flex-wrap items-center gap-5 text-sm text-[var(--color-muted)]">
            <span class="flex items-center gap-1.5">
              <User :size="16" />
              {{ article.author_name }}
            </span>
            <span class="flex items-center gap-1.5">
              <Calendar :size="16" />
              {{ formatDate(article.published_at) }}
            </span>
          </div>
        </div>
      </section>

      <!-- Cover image -->
      <section v-if="article.cover_image" class="bg-white pb-8">
        <div class="mx-auto max-w-[var(--container-lg)] px-6">
          <div class="aspect-[21/9] rounded-xl overflow-hidden">
            <img
              :src="article.cover_image"
              :alt="article.title"
              class="w-full h-full object-cover"
            >
          </div>
        </div>
      </section>

      <!-- Article body (HTML) -->
      <section class="bg-white pb-16">
        <div class="mx-auto max-w-[var(--container-md)] px-6">
          <div
            class="prose prose-lg max-w-none text-[var(--color-primary)] leading-relaxed
              [&_h2]:font-heading [&_h2]:text-2xl [&_h2]:font-extrabold [&_h2]:mt-10 [&_h2]:mb-4
              [&_h3]:font-heading [&_h3]:text-xl [&_h3]:font-bold [&_h3]:mt-8 [&_h3]:mb-3
              [&_p]:text-[var(--color-muted)] [&_p]:mb-5
              [&_ul]:pl-5 [&_ul]:space-y-2 [&_li]:text-[var(--color-muted)]
              [&_a]:text-[var(--color-accent)] [&_a]:underline
              [&_blockquote]:border-l-4 [&_blockquote]:border-[var(--color-accent)] [&_blockquote]:pl-5 [&_blockquote]:italic [&_blockquote]:text-[var(--color-muted)]
              [&_img]:rounded-xl [&_img]:my-6"
            v-html="article.content"
          />
        </div>
      </section>

      <!-- Share button -->
      <section class="bg-[var(--color-surface)] py-8 border-y border-[var(--color-border)]">
        <div class="mx-auto max-w-[var(--container-md)] px-6">
          <button
            class="inline-flex items-center gap-3 px-6 py-3 font-heading text-sm font-bold text-[var(--color-primary)] bg-white border border-[var(--color-border)] rounded-xl hover:border-[var(--color-accent)] hover:text-[var(--color-accent)] transition-all cursor-pointer"
            @click="openShareDialog"
          >
            <Share2 :size="18" />
            Partager cet article
          </button>
        </div>
      </section>

      <!-- Related articles -->
      <section v-if="filteredRelated.length > 0" class="bg-white py-16 md:py-20">
        <div class="mx-auto max-w-[var(--container-xl)] px-6">
          <div class="flex items-end justify-between mb-10">
            <h2 class="font-heading text-2xl md:text-3xl font-extrabold text-[var(--color-primary)]">
              Articles récents
            </h2>
            <RouterLink
              to="/actualites"
              class="inline-flex items-center gap-2 font-heading text-sm font-bold text-[var(--color-accent)] no-underline hover:text-[var(--color-accent-hover)] transition-colors"
            >
              Tout voir
              <ChevronRight :size="16" />
            </RouterLink>
          </div>

          <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
            <RouterLink
              v-for="related in filteredRelated"
              :key="related.id"
              :to="`/actualites/${related.slug}`"
              class="group bg-[var(--color-surface)] border border-[var(--color-border)] rounded-xl overflow-hidden no-underline transition-all hover:shadow-[var(--shadow-md)] hover:-translate-y-0.5 cursor-pointer"
            >
              <div class="aspect-[16/9] bg-[var(--color-border)] relative overflow-hidden">
                <img
                  v-if="related.cover_image"
                  :src="related.cover_image"
                  :alt="related.title"
                  class="w-full h-full object-cover transition-transform duration-300 group-hover:scale-105"
                >
                <div v-else class="absolute inset-0 flex items-center justify-center">
                  <img :src="logoFpp" alt="" class="w-16 opacity-10">
                </div>
              </div>
              <div class="p-5">
                <div class="flex items-center gap-2 text-xs text-[var(--color-muted)] mb-2">
                  <Calendar :size="12" />
                  {{ formatDate(related.published_at) }}
                </div>
                <h3 class="font-heading text-sm font-bold text-[var(--color-primary)] group-hover:text-[var(--color-accent)] transition-colors leading-snug">
                  {{ related.title }}
                </h3>
              </div>
            </RouterLink>
          </div>
        </div>
      </section>
    </template>

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
