<script setup lang="ts">
import { ref, onMounted, computed, watch } from 'vue'
import { RouterLink } from 'vue-router'
import { useApiGet } from '@/composables/useApi'
import { useSeoMeta } from '@/composables/useSeoMeta'
import { useShare, buildShareOgUrl } from '@/composables/useShare'
import ShareDialog from '@/components/ShareDialog.vue'
import type { ProgramSectionListItem, ProgramSectionDetail } from '@/types'
import {
  ArrowRight,
  Download,
  ChevronRight,
  CheckCircle2,
  Clock,
  Share2,
  Loader2,
  GraduationCap,
  HeartPulse,
  Briefcase,
  Wheat,
  Landmark,
  Globe,
  Lightbulb,
  Shield,
  Zap,
  Users,
  Building2,
  Scale,
} from 'lucide-vue-next'

useSeoMeta({
  title: 'Programme du FPP',
  description: 'Découvrez les mesures concrètes du Front Patriotique Panafricain pour la transformation de la Côte d\'Ivoire.',
})

const { showDialog, shareData, copied, openShare, closeShare, shareOn } = useShare()

const iconMap: Record<string, any> = {
  'graduation-cap': GraduationCap,
  'heart-pulse': HeartPulse,
  briefcase: Briefcase,
  wheat: Wheat,
  landmark: Landmark,
  globe: Globe,
  lightbulb: Lightbulb,
  shield: Shield,
  zap: Zap,
  users: Users,
  building2: Building2,
  scale: Scale,
}

const { data: sections, loading: loadingSections, execute: fetchSections } = useApiGet<ProgramSectionListItem[]>('/public/programme/')
const activeSlug = ref<string | null>(null)
const { data: activeSection, loading: loadingDetail, execute: fetchDetail } = useApiGet<ProgramSectionDetail>('')

const FALLBACK_SECTIONS: ProgramSectionListItem[] = [
  { id: '1', title: 'Éducation et Formation', slug: 'education-et-formation', description: 'Garantir une éducation de qualité accessible à tous les citoyens.', icon: 'graduation-cap', cover_image: null, order: 1, item_count: 3 },
  { id: '2', title: 'Santé et Protection Sociale', slug: 'sante-et-protection-sociale', description: 'Mettre en place un système de santé universel.', icon: 'heart-pulse', cover_image: null, order: 2, item_count: 2 },
  { id: '3', title: 'Économie et Emploi', slug: 'economie-et-emploi', description: 'Relancer l\'économie nationale et créer des emplois durables.', icon: 'briefcase', cover_image: null, order: 3, item_count: 2 },
  { id: '4', title: 'Agriculture et Souveraineté Alimentaire', slug: 'agriculture-et-souverainete-alimentaire', description: 'Moderniser l\'agriculture et garantir l\'autosuffisance alimentaire.', icon: 'wheat', cover_image: null, order: 4, item_count: 2 },
  { id: '5', title: 'Gouvernance et Institutions', slug: 'gouvernance-et-institutions', description: 'Renforcer la démocratie et lutter contre la corruption.', icon: 'landmark', cover_image: null, order: 5, item_count: 2 },
]

const displaySections = computed(() =>
  sections.value && sections.value.length > 0 ? sections.value : FALLBACK_SECTIONS,
)

const totalMeasures = computed(() =>
  displaySections.value.reduce((sum, s) => sum + s.item_count, 0),
)

const activeIndex = computed(() => {
  if (!activeSlug.value) return 0
  const idx = displaySections.value.findIndex((s) => s.slug === activeSlug.value)
  return idx >= 0 ? idx : 0
})

const currentSection = computed(() => displaySections.value[activeIndex.value])

async function selectSection(slug: string) {
  activeSlug.value = slug
  try {
    await fetchDetail(undefined)
  } catch {
    // Silently ignore — will show section card without items
  }
}

watch(activeSlug, async (slug) => {
  if (!slug) return
  const url = `/public/programme/${slug}/`
  try {
    const res = await import('@/api').then((m) => m.default.get<ProgramSectionDetail>(url))
    activeSection.value = res.data
  } catch {
    activeSection.value = null
  }
})

const stats = computed(() => [
  { value: String(totalMeasures.value || '50+'), label: 'Mesures concrètes' },
  { value: String(displaySections.value.length), label: 'Axes prioritaires' },
  { value: '5 ans', label: "Plan d'action" },
  { value: '100%', label: 'Financement identifié' },
])

const roadmap = [
  {
    period: '100 premiers jours',
    title: "Mesures d'urgence",
    items: ['Audit général des finances publiques', 'Gel des recrutements clientélistes', "Lancement du plan d'urgence santé", 'Baisse immédiate des prix des produits de première nécessité'],
  },
  {
    period: 'Année 1',
    title: 'Fondations',
    items: ['Réforme de la commission électorale', "Lancement du programme Éducation pour Tous", 'Création du Fonds PME/PMI', "Début des grands travaux d'infrastructure"],
  },
  {
    period: 'Années 2-3',
    title: 'Transformation',
    items: ['Couverture santé universelle opérationnelle', 'Électrification totale du territoire', '100 000 emplois créés', 'Décentralisation effective'],
  },
  {
    period: 'Années 4-5',
    title: 'Consolidation',
    items: ['200 000 emplois créés', 'Transformation locale de 70% des matières premières', "Côte d'Ivoire parmi les 5 économies africaines les plus dynamiques", 'Bilan et préparation de la suite'],
  },
]

const sectionColors = [
  'bg-blue-50 text-blue-600',
  'bg-rose-50 text-rose-600',
  'bg-emerald-50 text-emerald-600',
  'bg-amber-50 text-amber-600',
  'bg-purple-50 text-purple-600',
  'bg-sky-50 text-sky-600',
  'bg-teal-50 text-teal-600',
  'bg-orange-50 text-orange-600',
]

function getColor(index: number) {
  return sectionColors[index % sectionColors.length]
}

function shareSection(section: ProgramSectionListItem) {
  openShare({
    title: `${section.title} — Programme du FPP`,
    description: section.description,
    url: `${window.location.origin}/programme#${section.slug}`,
    ogUrl: buildShareOgUrl('programme', section.slug),
  })
}

function shareProgramme() {
  openShare({
    title: 'Programme du FPP — Front Patriotique Panafricain',
    description: `${totalMeasures.value} mesures concrètes pour transformer la Côte d'Ivoire en 5 ans.`,
    url: `${window.location.origin}/programme`,
    ogUrl: buildShareOgUrl('programme', displaySections.value[0]?.slug ?? 'programme'),
  })
}

onMounted(async () => {
  try {
    await fetchSections()
    if (displaySections.value.length > 0) {
      activeSlug.value = displaySections.value[0].slug
    }
  } catch {
    activeSlug.value = FALLBACK_SECTIONS[0].slug
  }
})
</script>

<template>
  <div>
    <!-- ═══════ HERO ═══════ -->
    <section class="relative bg-[var(--color-primary)] py-24 md:py-32 overflow-hidden">
      <div class="absolute inset-0 bg-[radial-gradient(ellipse_at_bottom_left,rgba(22,163,74,0.12),transparent_60%)]" />
      <div class="relative mx-auto max-w-[var(--container-xl)] px-6">
        <div class="max-w-2xl">
          <p class="font-heading text-xs font-bold uppercase tracking-[0.15em] text-[var(--color-accent)] mb-4">
            Notre projet pour la Côte d'Ivoire
          </p>
          <h1 class="font-heading text-4xl md:text-5xl lg:text-6xl font-extrabold text-white leading-[1.05] mb-6">
            Programme du <span class="text-[var(--color-accent)]">FPP</span>
          </h1>
          <p class="text-lg text-white/60 leading-relaxed max-w-lg mb-10">
            {{ totalMeasures }} mesures concrètes, chiffrées et financées pour transformer la Côte d'Ivoire en 5 ans.
          </p>
          <div class="flex flex-wrap gap-3">
            <a
              href="#"
              class="group inline-flex items-center gap-2 px-7 py-3.5 font-heading text-sm font-bold uppercase tracking-[0.04em] bg-[var(--color-accent)] text-white no-underline rounded-sm transition-all hover:bg-[var(--color-accent-hover)] cursor-pointer"
            >
              <Download :size="18" />
              Télécharger le PDF
            </a>
            <button
              class="inline-flex items-center gap-2 px-6 py-3.5 font-heading text-sm font-bold uppercase tracking-[0.04em] text-white border border-white/30 rounded-sm transition-all hover:border-white hover:bg-white/10 cursor-pointer"
              @click="shareProgramme"
            >
              <Share2 :size="18" />
              Partager
            </button>
          </div>
        </div>
      </div>
    </section>

    <!-- ═══════ STATS BAR ═══════ -->
    <section class="bg-white border-b border-[var(--color-border)]">
      <div class="mx-auto max-w-[var(--container-xl)] px-6">
        <div class="grid grid-cols-2 md:grid-cols-4 divide-x divide-[var(--color-border)]">
          <div v-for="(stat, i) in stats" :key="i" class="py-8 md:py-10 text-center">
            <p class="font-heading text-3xl md:text-4xl font-extrabold text-[var(--color-primary)] mb-1">
              {{ stat.value }}
            </p>
            <p class="font-heading text-xs font-semibold uppercase tracking-[0.1em] text-[var(--color-muted)]">
              {{ stat.label }}
            </p>
          </div>
        </div>
      </div>
    </section>

    <!-- ═══════ LOADING ═══════ -->
    <div v-if="loadingSections" class="flex items-center justify-center py-32">
      <Loader2 :size="32" class="animate-spin text-[var(--color-accent)]" />
    </div>

    <template v-else>
      <!-- ═══════ AXES PRIORITAIRES (TABS) ═══════ -->
      <section id="axes-section" class="bg-[var(--color-surface)] py-20 md:py-28">
        <div class="mx-auto max-w-[var(--container-xl)] px-6">
          <div class="text-center mb-14">
            <p class="font-heading text-xs font-bold uppercase tracking-[0.15em] text-[var(--color-accent)] mb-3">
              {{ displaySections.length }} axes prioritaires
            </p>
            <h2 class="font-heading text-3xl md:text-4xl font-extrabold text-[var(--color-primary)]">
              Nos engagements
            </h2>
          </div>

          <!-- Tab pills -->
          <div class="flex flex-wrap justify-center gap-2 mb-12">
            <button
              v-for="(s, i) in displaySections"
              :key="s.id"
              class="flex items-center gap-2 px-5 py-2.5 font-heading text-xs font-bold uppercase tracking-[0.04em] rounded-full border transition-all cursor-pointer"
              :class="[
                activeIndex === i
                  ? 'bg-[var(--color-primary)] text-white border-[var(--color-primary)]'
                  : 'bg-white text-[var(--color-muted)] border-[var(--color-border)] hover:border-[var(--color-primary)] hover:text-[var(--color-primary)]'
              ]"
              @click="activeSlug = s.slug"
            >
              <component :is="iconMap[s.icon] ?? Lightbulb" :size="16" />
              <span class="hidden sm:inline">{{ s.title.split(' ')[0] }}</span>
            </button>
          </div>

          <!-- Active section content -->
          <div class="bg-white border border-[var(--color-border)] rounded-xl p-8 md:p-12">
            <div class="grid grid-cols-1 lg:grid-cols-2 gap-10">
              <div>
                <div
                  class="w-14 h-14 rounded-xl flex items-center justify-center mb-5"
                  :class="getColor(activeIndex)"
                >
                  <component :is="iconMap[currentSection.icon] ?? Lightbulb" :size="28" />
                </div>
                <h3 class="font-heading text-2xl font-extrabold text-[var(--color-primary)] mb-3">
                  {{ currentSection.title }}
                </h3>
                <p class="text-[var(--color-muted)] leading-relaxed mb-5">
                  {{ currentSection.description }}
                </p>
                <button
                  class="inline-flex items-center gap-2 text-sm font-heading font-bold text-[var(--color-accent)] hover:text-[var(--color-accent-hover)] transition-colors cursor-pointer"
                  @click="shareSection(currentSection)"
                >
                  <Share2 :size="14" />
                  Partager cette section
                </button>
              </div>
              <div>
                <h4 class="font-heading text-sm font-bold uppercase tracking-[0.08em] text-[var(--color-muted)] mb-5">
                  Mesures phares
                </h4>
                <div v-if="loadingDetail" class="flex items-center justify-center py-10">
                  <Loader2 :size="20" class="animate-spin text-[var(--color-accent)]" />
                </div>
                <ul v-else-if="activeSection?.items?.length" class="space-y-3">
                  <li
                    v-for="item in activeSection.items"
                    :key="item.id"
                    class="flex items-start gap-3"
                  >
                    <CheckCircle2 :size="18" class="text-[var(--color-accent)] shrink-0 mt-0.5" />
                    <div>
                      <span class="text-sm font-semibold text-[var(--color-primary)] leading-relaxed">{{ item.title }}</span>
                      <p class="text-xs text-[var(--color-muted)] mt-0.5 leading-relaxed">{{ item.description }}</p>
                    </div>
                  </li>
                </ul>
                <p v-else class="text-sm text-[var(--color-muted)] italic">
                  {{ currentSection.item_count }} mesures dans cette section.
                </p>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- ═══════ VUE D'ENSEMBLE (CARDS) ═══════ -->
      <section class="bg-white py-20 md:py-28">
        <div class="mx-auto max-w-[var(--container-xl)] px-6">
          <div class="text-center mb-14">
            <p class="font-heading text-xs font-bold uppercase tracking-[0.15em] text-[var(--color-accent)] mb-3">
              Vue d'ensemble
            </p>
            <h2 class="font-heading text-3xl md:text-4xl font-extrabold text-[var(--color-primary)]">
              Les piliers de notre programme
            </h2>
          </div>

          <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
            <button
              v-for="(s, i) in displaySections"
              :key="s.id"
              class="text-left bg-[var(--color-surface)] border border-[var(--color-border)] rounded-xl p-7 transition-all hover:shadow-[var(--shadow-md)] hover:-translate-y-0.5 cursor-pointer"
              @click="activeSlug = s.slug; document.getElementById('axes-section')?.scrollIntoView({ behavior: 'smooth' })"
            >
              <div class="w-12 h-12 rounded-lg flex items-center justify-center mb-4" :class="getColor(i)">
                <component :is="iconMap[s.icon] ?? Lightbulb" :size="24" />
              </div>
              <h3 class="font-heading text-base font-bold text-[var(--color-primary)] mb-2">
                {{ s.title }}
              </h3>
              <p class="text-sm text-[var(--color-muted)] leading-relaxed line-clamp-2">
                {{ s.description }}
              </p>
              <span class="inline-flex items-center gap-1 mt-4 font-heading text-xs font-bold text-[var(--color-accent)] uppercase tracking-[0.04em]">
                {{ s.item_count }} mesures
                <ChevronRight :size="14" />
              </span>
            </button>
          </div>
        </div>
      </section>
    </template>

    <!-- ═══════ CALENDRIER DE MISE EN ŒUVRE ═══════ -->
    <section class="bg-[var(--color-surface)] py-20 md:py-28">
      <div class="mx-auto max-w-[var(--container-xl)] px-6">
        <div class="text-center mb-14">
          <p class="font-heading text-xs font-bold uppercase tracking-[0.15em] text-[var(--color-accent)] mb-3">
            Calendrier
          </p>
          <h2 class="font-heading text-3xl md:text-4xl font-extrabold text-[var(--color-primary)]">
            Plan de mise en œuvre
          </h2>
        </div>

        <div class="max-w-3xl mx-auto space-y-6">
          <div
            v-for="(phase, i) in roadmap"
            :key="i"
            class="bg-white border border-[var(--color-border)] rounded-xl p-7 md:p-8"
          >
            <div class="flex items-center gap-4 mb-5">
              <div class="w-10 h-10 rounded-full bg-[var(--color-accent)] text-white flex items-center justify-center font-heading text-sm font-bold shrink-0">
                {{ i + 1 }}
              </div>
              <div>
                <span class="font-heading text-xs font-bold uppercase tracking-[0.08em] text-[var(--color-accent)]">
                  {{ phase.period }}
                </span>
                <h3 class="font-heading text-lg font-bold text-[var(--color-primary)]">
                  {{ phase.title }}
                </h3>
              </div>
            </div>
            <ul class="space-y-2 ml-14">
              <li
                v-for="(item, j) in phase.items"
                :key="j"
                class="flex items-start gap-3 text-sm text-[var(--color-muted)]"
              >
                <Clock :size="14" class="text-[var(--color-accent)] shrink-0 mt-0.5" />
                {{ item }}
              </li>
            </ul>
          </div>
        </div>
      </div>
    </section>

    <!-- ═══════ CTA ═══════ -->
    <section class="bg-[var(--color-primary)] py-20 md:py-28">
      <div class="mx-auto max-w-[var(--container-lg)] px-6 text-center">
        <h2 class="font-heading text-3xl md:text-4xl lg:text-5xl font-extrabold text-white leading-tight mb-6">
          Participez à la construction de <span class="text-[var(--color-accent)]">notre programme</span>
        </h2>
        <p class="text-lg text-white/60 max-w-xl mx-auto mb-10">
          Votre avis compte. Soumettez vos idées et contribuez à façonner le futur de la Côte d'Ivoire.
        </p>
        <div class="flex flex-wrap justify-center gap-4">
          <RouterLink
            to="/adherer"
            class="group inline-flex items-center gap-2 px-8 py-4 font-heading text-sm font-bold uppercase tracking-[0.04em] bg-[var(--color-accent)] text-white no-underline rounded-sm transition-all hover:bg-[var(--color-accent-hover)] cursor-pointer"
          >
            Rejoindre le FPP
            <ArrowRight :size="18" class="transition-transform group-hover:translate-x-1" />
          </RouterLink>
          <RouterLink
            to="/contact"
            class="inline-flex items-center gap-2 px-8 py-4 font-heading text-sm font-bold uppercase tracking-[0.04em] text-white no-underline border-2 border-white/30 rounded-sm transition-all hover:border-white hover:bg-white/10 cursor-pointer"
          >
            Soumettre une idée
          </RouterLink>
        </div>
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
