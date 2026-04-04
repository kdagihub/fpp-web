<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { RouterLink } from 'vue-router'
import { useSettingsStore } from '@/stores/settings'
import api from '@/api'
import { getMediaUrl } from '@/utils/media'
import {
  ArrowRight,
  Eye,
  Heart,
  Globe,
  Users,
  Flag,
  MapPin,
  Loader2,
} from 'lucide-vue-next'
import logoFppFallback from '@/assets/img/fpplogsf.png'
import heroAboutImgFallback from '@/assets/img/parti2.png'

const settingsStore = useSettingsStore()

function heroImage() {
  const url = settingsStore.settings?.hero_image
  return url ? getMediaUrl(url) : heroAboutImgFallback
}
function logoImage() {
  const url = settingsStore.settings?.logo
  return url ? getMediaUrl(url) : logoFppFallback
}

interface BureauMemberPublic {
  id: string
  full_name: string
  title: string
  photo: string | null
  order: number
}

const bureauMembers = ref<BureauMemberPublic[]>([])
const bureauLoading = ref(true)

onMounted(async () => {
  try {
    const { data } = await api.get<BureauMemberPublic[]>('/public/bureau/')
    bureauMembers.value = data
  } catch {
    // silently fallback to empty
  } finally {
    bureauLoading.value = false
  }
})

const values = [
  {
    icon: Eye,
    title: 'Transparence',
    text: 'Une gouvernance claire et ouverte, des comptes rendus publics et une communication honnête avec les citoyens.',
    color: 'bg-emerald-50 text-emerald-600',
  },
  {
    icon: Heart,
    title: 'Solidarité',
    text: 'Renforcer les liens entre tous les Ivoiriens, soutenir les plus vulnérables et construire une société plus juste.',
    color: 'bg-rose-50 text-rose-600',
  },
  {
    icon: Globe,
    title: 'Panafricanisme',
    text: 'Promouvoir l\'unité africaine, la coopération entre les peuples et la souveraineté du continent.',
    color: 'bg-amber-50 text-amber-600',
  },
  {
    icon: Users,
    title: 'Engagement',
    text: 'Impliquer les populations dans la processus révolutionnaire de transformation radicale de notre société à travers la décolonisation et valoriser la participation active à notre projet commun.',
    color: 'bg-sky-50 text-sky-600',
  },
]

const timeline = [
  { year: '2020', title: 'Genèse du projet', description: 'Premiers échanges autour d\'une vision politique panafricaine et révolutionnaire pour la Côte d\'Ivoire.' },
  { year: '2021', title: 'Création officielle du FPP', description: '20 novembre 2021 — Le Front Patriotique Panafricain est officiellement créé et enregistré.' },
  { year: '2022', title: 'Inclusion politique des jeunes', description: 'Lutte pour une plus large inclusion politique des jeunes : être candidat à 18 ans à toutes les élections en Côte d\'Ivoire.' },
  { year: '2023', title: 'Première apparition télévisée', description: 'Mardi 23 janvier 2023 — Première apparition sur un plateau télévisé du Président du FPP.' },
  { year: '2024', title: 'Implantation nationale', description: 'Début d\'implantation du parti sur l\'étendue du territoire national.' },
  { year: '2025', title: 'Meeting historique & candidature présidentielle', description: '12 juillet 2025 — Premier meeting historique du FPP. 12 août 2025 — Dépôt de candidature du Président du parti à l\'élection présidentielle de Côte d\'Ivoire.' },
  { year: '2026', title: 'Publication & vision', description: 'Premier livre du Président du parti sur l\'engagement politique des jeunes en Côte d\'Ivoire ainsi que la vision du FPP pour la Côte d\'Ivoire et l\'Afrique.' },
]

const regions = [
  { name: 'Bouaké' },
  { name: 'Gagnoa' },
  { name: 'Korhogo' },
  { name: 'San-Pédro' },
  { name: 'Bonoua' },
]
</script>

<template>
  <div>
    <!-- ════════════════════ HERO ════════════════════ -->
    <section class="relative bg-[var(--color-primary)] py-24 md:py-32 overflow-hidden">
      <img :src="heroImage()" alt="" class="absolute inset-0 w-full h-full object-cover object-[center_25%] opacity-40" />
      <div class="absolute inset-0 bg-gradient-to-r from-[var(--color-primary)]/70 via-[var(--color-primary)]/40 to-transparent" />
      <div class="relative mx-auto max-w-[var(--container-xl)] px-6">
        <div class="max-w-2xl">
          <p class="font-heading text-xs font-bold uppercase tracking-[0.15em] text-[var(--color-accent)] mb-4">
            Qui sommes-nous
          </p>
          <h1 class="font-heading text-4xl md:text-5xl lg:text-6xl font-extrabold text-white leading-[1.05] mb-6">
            Le FPP, un parti<br>
            <span class="text-[var(--color-accent)]">citoyen</span>
          </h1>
          <p class="text-lg text-white/60 leading-relaxed max-w-lg">
            {{ settingsStore.settings?.about_text || 'Fondé en 2021, le Front Patriotique Panafricain rassemble des hommes et des femmes de tous horizons, unis par une même conviction : la Côte d\'Ivoire peut faire mieux, ensemble.' }}
          </p>
        </div>
      </div>
    </section>

    <!-- ════════════════════ NOTRE MISSION ════════════════════ -->
    <section class="bg-white py-20 md:py-28">
      <div class="mx-auto max-w-[var(--container-xl)] px-6">
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-12 lg:gap-20 items-center">
          <div>
            <p class="font-heading text-xs font-bold uppercase tracking-[0.15em] text-[var(--color-accent)] mb-3">
              Notre mission
            </p>
            <h2 class="font-heading text-3xl md:text-4xl font-extrabold text-[var(--color-primary)] mb-6">
              Dignité, souveraineté, unité : pour les États-Unis d’Afrique.
            </h2>
            <div class="space-y-4 text-[var(--color-muted)] leading-relaxed">
              <p>
                {{ settingsStore.settings?.vision_text || 'Unir chaque Ivoirien et chaque Ivoirienne autour de la lutte pour la décolonisation effective de la Côte d’Ivoire, comme fondement de notre développement, de notre souveraineté et de notre progrès.' }}
              </p>
              <p>
                Nous défendons l’unité, la dignité et l’intégrité.
                <br>
                Nous agissons avec transparence et responsabilité.
                <br>
                Nous promouvons la justice, l’équité et la solidarité, dans le respect des droits et libertés de tous.
              </p>
            </div>
            <div class="mt-8 grid grid-cols-3 gap-6">
              <div>
                <p class="font-heading text-3xl font-extrabold text-[var(--color-primary)]">5000+</p>
                <p class="font-heading text-xs font-semibold uppercase tracking-[0.08em] text-[var(--color-muted)] mt-1">Adhérents</p>
              </div>
              <div>
                <p class="font-heading text-3xl font-extrabold text-[var(--color-primary)]">1</p>
                <p class="font-heading text-xs font-semibold uppercase tracking-[0.08em] text-[var(--color-muted)] mt-1">Présidentielle</p>
              </div>
              <div>
                <p class="font-heading text-3xl font-extrabold text-[var(--color-primary)]">5</p>
                <p class="font-heading text-xs font-semibold uppercase tracking-[0.08em] text-[var(--color-muted)] mt-1">Régions couvertes</p>
              </div>
            </div>
          </div>

          <div class="flex flex-col items-center">
            <div class="bg-[var(--color-surface)] rounded-2xl p-12 w-full flex flex-col items-center">
              <img :src="logoImage()" alt="FPP" class="w-44 md:w-56 mb-6">
              <p class="font-heading text-sm font-bold uppercase tracking-[0.08em] text-[var(--color-muted)] text-center">
                Front Patriotique Panafricain
              </p>
              <div class="mt-6 flex items-center gap-3">
                <Flag :size="20" class="text-[var(--color-accent)]" />
                <span class="font-heading text-sm font-semibold text-[var(--color-primary)]">Depuis 2021</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- ════════════════════ NOS VALEURS ════════════════════ -->
    <section class="bg-[var(--color-surface)] py-20 md:py-28">
      <div class="mx-auto max-w-[var(--container-xl)] px-6">
        <div class="text-center mb-14">
          <p class="font-heading text-xs font-bold uppercase tracking-[0.15em] text-[var(--color-accent)] mb-3">
            Ce qui nous guide
          </p>
          <h2 class="font-heading text-3xl md:text-4xl font-extrabold text-[var(--color-primary)] mb-4">
            Nos valeurs
          </h2>
          <p class="text-[var(--color-muted)] max-w-xl mx-auto">
            {{ settingsStore.settings?.values_text || 'Quatre piliers qui guident notre action quotidienne et notre vision pour la Côte d\'Ivoire de demain.' }}
          </p>
        </div>

        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
          <div
            v-for="(val, i) in values"
            :key="i"
            class="group bg-white border border-[var(--color-border)] rounded-xl p-7 text-center transition-all hover:shadow-[var(--shadow-md)] hover:-translate-y-0.5"
          >
            <div
              class="w-14 h-14 rounded-full flex items-center justify-center mx-auto mb-5 transition-colors"
              :class="val.color"
            >
              <component :is="val.icon" :size="24" />
            </div>
            <h3 class="font-heading text-base font-bold text-[var(--color-primary)] mb-2">
              {{ val.title }}
            </h3>
            <p class="text-sm text-[var(--color-muted)] leading-relaxed">
              {{ val.text }}
            </p>
          </div>
        </div>
      </div>
    </section>

    <!-- ════════════════════ TIMELINE ════════════════════ -->
    <section class="bg-white py-20 md:py-28">
      <div class="mx-auto max-w-[var(--container-xl)] px-6">
        <div class="text-center mb-14">
          <p class="font-heading text-xs font-bold uppercase tracking-[0.15em] text-[var(--color-accent)] mb-3">
            Notre parcours
          </p>
          <h2 class="font-heading text-3xl md:text-4xl font-extrabold text-[var(--color-primary)]">
            L'histoire du FPP
          </h2>
        </div>

        <div class="relative max-w-3xl mx-auto">
          <div class="absolute left-6 md:left-1/2 top-0 bottom-0 w-0.5 bg-[var(--color-border)] -translate-x-1/2" />

          <div
            v-for="(item, i) in timeline"
            :key="i"
            class="relative flex items-start mb-12 last:mb-0"
            :class="[i % 2 === 0 ? 'md:flex-row' : 'md:flex-row-reverse']"
          >
            <div class="absolute left-6 md:left-1/2 w-4 h-4 rounded-full bg-[var(--color-accent)] border-4 border-white -translate-x-1/2 z-10 shadow-[var(--shadow-sm)]" />

            <div
              class="ml-14 md:ml-0 md:w-1/2"
              :class="[i % 2 === 0 ? 'md:pr-12 md:text-right' : 'md:pl-12']"
            >
              <span class="inline-block px-3 py-1 bg-[var(--color-accent-light)] text-[var(--color-accent)] font-heading text-xs font-bold rounded-full mb-2">
                {{ item.year }}
              </span>
              <h3 class="font-heading text-lg font-bold text-[var(--color-primary)] mb-1">
                {{ item.title }}
              </h3>
              <p class="text-sm text-[var(--color-muted)] leading-relaxed">
                {{ item.description }}
              </p>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- ════════════════════ BUREAU NATIONAL ════════════════════ -->
    <section class="bg-[var(--color-surface)] py-20 md:py-28">
      <div class="mx-auto max-w-[var(--container-xl)] px-6">
        <div class="text-center mb-14">
          <p class="font-heading text-xs font-bold uppercase tracking-[0.15em] text-[var(--color-accent)] mb-3">
            Direction
          </p>
          <h2 class="font-heading text-3xl md:text-4xl font-extrabold text-[var(--color-primary)]">
            Le Bureau National
          </h2>
        </div>

        <!-- Loading state -->
        <div v-if="bureauLoading" class="flex justify-center py-12">
          <Loader2 :size="32" class="animate-spin text-[var(--color-accent)]" />
        </div>

        <!-- Empty state -->
        <p v-else-if="bureauMembers.length === 0" class="text-center text-[var(--color-muted)] py-8">
          Aucun membre du bureau renseigné pour le moment.
        </p>

        <!-- Members grid -->
        <div v-else class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
          <div
            v-for="member in bureauMembers"
            :key="member.id"
            class="bg-white border border-[var(--color-border)] rounded-xl overflow-hidden transition-all hover:shadow-[var(--shadow-md)]"
          >
            <div class="aspect-[4/3] bg-[var(--color-border)] relative overflow-hidden">
              <img
                v-if="member.photo"
                :src="getMediaUrl(member.photo)"
                :alt="member.full_name"
                class="w-full h-full object-cover object-top"
              >
              <div v-else class="absolute inset-0 flex items-center justify-center">
                <Users :size="48" class="text-[var(--color-muted)] opacity-20" />
              </div>
            </div>
            <div class="p-5 text-center">
              <h3 class="font-heading text-base font-bold text-[var(--color-primary)] mb-1">
                {{ member.full_name }}
              </h3>
              <p class="font-heading text-xs font-semibold uppercase tracking-[0.06em] text-[var(--color-accent)]">
                {{ member.title }}
              </p>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- ════════════════════ IMPLANTATION ════════════════════ -->
    <section class="bg-white py-20 md:py-28">
      <div class="mx-auto max-w-[var(--container-xl)] px-6">
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-12 lg:gap-16 items-center">
          <div>
            <p class="font-heading text-xs font-bold uppercase tracking-[0.15em] text-[var(--color-accent)] mb-3">
              Présence nationale
            </p>
            <h2 class="font-heading text-3xl md:text-4xl font-extrabold text-[var(--color-primary)] mb-6">
              Le FPP sur le terrain
            </h2>
            <p class="text-[var(--color-muted)] leading-relaxed mb-8">
              Avec des Coordinations Régionales dans 5 régions, le Front Patriotique Panafricain s'étend progressivement sur toute l'étendue du territoire national, au plus près des préoccupations des Ivoiriens.
            </p>
            <div class="grid grid-cols-2 sm:grid-cols-3 gap-3">
              <div
                v-for="(region, i) in regions"
                :key="i"
                class="flex items-center gap-3 p-3 bg-[var(--color-surface)] rounded-lg"
              >
                <MapPin :size="16" class="text-[var(--color-accent)] shrink-0" />
                <p class="font-heading text-sm font-bold text-[var(--color-primary)]">{{ region.name }}</p>
              </div>
            </div>
          </div>

          <div class="bg-[var(--color-surface)] rounded-2xl p-10 text-center">
            <div class="grid grid-cols-2 gap-8">
              <div>
                <p class="font-heading text-4xl font-extrabold text-[var(--color-primary)]">5</p>
                <p class="font-heading text-xs font-semibold uppercase tracking-[0.08em] text-[var(--color-muted)] mt-1">Régions</p>
              </div>
              <div>
                <p class="font-heading text-4xl font-extrabold text-[var(--color-primary)]">0</p>
                <p class="font-heading text-xs font-semibold uppercase tracking-[0.08em] text-[var(--color-muted)] mt-1">Élus locaux</p>
              </div>
              <div>
                <p class="font-heading text-4xl font-extrabold text-[var(--color-primary)]">5</p>
                <p class="font-heading text-xs font-semibold uppercase tracking-[0.08em] text-[var(--color-muted)] mt-1">Coordinations Régionales</p>
              </div>
              <div>
                <p class="font-heading text-4xl font-extrabold text-[var(--color-primary)]">5000+</p>
                <p class="font-heading text-xs font-semibold uppercase tracking-[0.08em] text-[var(--color-muted)] mt-1">Adhérents actifs</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- ════════════════════ CTA ════════════════════ -->
    <section class="bg-[var(--color-primary)] py-20 md:py-28">
      <div class="mx-auto max-w-[var(--container-lg)] px-6 text-center">
        <h2 class="font-heading text-3xl md:text-4xl lg:text-5xl font-extrabold text-white leading-tight mb-6">
          Rejoignez le <span class="text-[var(--color-accent)]">Parti</span>
        </h2>
        <p class="text-lg text-white/60 max-w-xl mx-auto mb-10">
          Le FPP est ouvert à tous les citoyens qui partagent notre vision d'une Côte d'Ivoire plus juste et plus prospère.
        </p>
        <div class="flex flex-wrap justify-center gap-4">
          <RouterLink
            to="/adherer"
            class="group inline-flex items-center gap-2 px-8 py-4 font-heading text-sm font-bold uppercase tracking-[0.04em] bg-[var(--color-accent)] text-white no-underline rounded-sm transition-all hover:bg-[var(--color-accent-hover)] cursor-pointer"
          >
            Devenir membre
            <ArrowRight :size="18" class="transition-transform group-hover:translate-x-1" />
          </RouterLink>
          <RouterLink
            to="/contact"
            class="inline-flex items-center gap-2 px-8 py-4 font-heading text-sm font-bold uppercase tracking-[0.04em] text-white no-underline border-2 border-white/30 rounded-sm transition-all hover:border-white hover:bg-white/10 cursor-pointer"
          >
            Nous contacter
          </RouterLink>
        </div>
      </div>
    </section>
  </div>
</template>
