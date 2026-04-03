<script setup lang="ts">
import { RouterLink } from 'vue-router'
import {
  ArrowRight,
  Eye,
  Heart,
  Globe,
  Users,
  Target,
  Rocket,
  Shield,
  ChevronRight,
  Calendar,
} from 'lucide-vue-next'
import heroImg from '@/assets/img/hero-meeting.png'
import logoFpp from '@/assets/img/fpplogsf.png'
import presidentImg from '@/assets/img/president.png'

const stats = [
  { value: '5000+', label: 'Adhérents' },
  { value: '1', label: 'Candidature à la présidence' },
  { value: '5+', label: 'Régions' },
  { value: '5+', label: 'Ans d\'engagement' },
]

const pillars = [
  {
    icon: Target,
    title: 'Notre vision',
    text: 'Unis chaque ivoirien et Ivoirienne au tour de la lutte pour la décolonisation de la Côte d’Ivoire, gage de notre developpement et notre progrès.',
  },
  {
    icon: Rocket,
    title: 'Notre mission',
    text: 'D’une part, assurez la sécurité des populations sur tous les plans, promouvoir le progrès économique, le developpement, l’intégrité, l’emplois pour tous. D’autre part promouvoir le panafricanisme dans l’optique de mener avec les autres peuples d’Afriques, le combat pour l’indépendance politique, économique, militaire, éducative, culturelle, spirituelle etc. Mais aussi et surtout mener le combat des États Unis d’Afrique.',
  },
  {
    icon: Shield,
    title: 'Nos valeurs',
    text: 'Nous valorisons l’unité, la dignité, l’intégrité, la transparence, la responsabilité. Nous promouvons la justice, l’équité, la solidarité, et respectons les droits et libertés de tous les citoyens.',
  },
]

const values = [
  {
    icon: Eye,
    title: 'Transparence',
    text: 'Une gouvernance claire et ouverte, des comptes rendus publics et une communication honnête avec les citoyens.',
  },
  {
    icon: Heart,
    title: 'Solidarité',
    text: 'Renforcer les liens entre tous les Ivoiriens, soutenir les plus vulnérables et construire une société plus juste.',
  },
  {
    icon: Globe,
    title: 'Panafricanisme',
    text: 'Promouvoir l\'unité africaine, la coopération entre les peuples et la souveraineté du continent.',
  },
  {
    icon: Users,
    title: 'Engagement',
    text: 'Impliquer les populations dans la processus révolutionnaire de transformation radicale de notre société à travers la décolonisation et valoriser la participation active à notre projet commun.',
  },
]

const articles = [
  {
    slug: 'congres-national-2026',
    title: 'Congrès National 2026 : Les grandes orientations',
    summary: 'Retour sur les moments forts de notre congrès annuel et les décisions prises pour l\'avenir du parti.',
    category: 'Événement',
    date: '15 mars 2026',
    image: null,
  },
  {
    slug: 'developpement-economique',
    title: 'Développement économique : Notre vision',
    summary: 'Découvrez notre analyse complète et nos propositions pour une économie ivoirienne forte et inclusive.',
    category: 'Politique',
    date: '12 mars 2026',
    image: null,
  },
  {
    slug: 'education-10-mesures',
    title: 'Éducation : 10 mesures concrètes',
    summary: 'Notre plan détaillé pour une éducation de qualité accessible à tous les enfants ivoiriens.',
    category: 'Programme',
    date: '8 mars 2026',
    image: null,
  },
]
</script>

<template>
  <div>
    <!-- ════════════════════ HERO ════════════════════ -->
    <section class="relative overflow-hidden bg-[var(--color-primary)]">
      <img
        :src="heroImg"
        alt="Meeting FPP — Yopougon 2025"
        class="absolute inset-0 w-full h-full object-cover opacity-40"
      >
      <div class="absolute inset-0 bg-gradient-to-r from-[var(--color-primary)] via-[var(--color-primary)]/80 to-transparent" />
      <div class="relative mx-auto max-w-[var(--container-xl)] px-6 py-24 md:py-36 lg:py-44">
        <div class="max-w-2xl">
          <p class="font-heading text-xs font-bold uppercase tracking-[0.15em] text-[var(--color-accent)] mb-4">
            Ensemble pour la Côte d'Ivoire
          </p>
          <h1 class="font-heading text-4xl md:text-5xl lg:text-6xl font-extrabold text-white leading-[1.05] mb-6">
            Construisons<br>
            <span class="text-[var(--color-accent)]">l'avenir</span> ensemble
          </h1>
          <p class="text-lg text-white/70 leading-relaxed mb-10 max-w-lg">
            Le Front Patriotique Panafricain rassemble des citoyens engagés pour bâtir une Côte d’Ivoire décolonisée, souveraine, prospère et développée. Rejoignez notre parti politique.
          </p>
          <div class="flex flex-wrap gap-4">
            <RouterLink
              to="/adherer"
              class="group inline-flex items-center gap-2 px-7 py-3.5 font-heading text-sm font-bold uppercase tracking-[0.04em] bg-[var(--color-accent)] text-white no-underline rounded-sm transition-all hover:bg-[var(--color-accent-hover)] cursor-pointer"
            >
              Rejoindre le Parti
              <ArrowRight :size="18" class="transition-transform group-hover:translate-x-1" />
            </RouterLink>
            <RouterLink
              to="/a-propos"
              class="inline-flex items-center gap-2 px-7 py-3.5 font-heading text-sm font-bold uppercase tracking-[0.04em] text-white no-underline border-2 border-white/30 rounded-sm transition-all hover:border-white hover:bg-white/10 cursor-pointer"
            >
              Découvrir notre programme
            </RouterLink>
          </div>
        </div>
      </div>
    </section>

    <!-- ════════════════════ STATS BAR ════════════════════ -->
    <section class="bg-white border-b border-[var(--color-border)]">
      <div class="mx-auto max-w-[var(--container-xl)] px-6">
        <div class="grid grid-cols-2 md:grid-cols-4 divide-x divide-[var(--color-border)]">
          <div
            v-for="(stat, i) in stats"
            :key="i"
            class="py-8 md:py-10 text-center"
          >
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

    <!-- ════════════════════ VISION / MISSION / VALEURS ════════════════════ -->
    <section class="bg-[var(--color-surface)] py-20 md:py-28">
      <div class="mx-auto max-w-[var(--container-xl)] px-6">
        <div class="text-center mb-14">
          <p class="font-heading text-xs font-bold uppercase tracking-[0.15em] text-[var(--color-accent)] mb-3">
            Ce que nous portons
          </p>
          <h2 class="font-heading text-3xl md:text-4xl font-extrabold text-[var(--color-primary)]">
            Notre engagement pour la Côte d'Ivoire
          </h2>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div
            v-for="(pillar, i) in pillars"
            :key="i"
            class="bg-white border border-[var(--color-border)] rounded-xl p-8 transition-all hover:shadow-[var(--shadow-md)] hover:-translate-y-0.5"
          >
            <div class="w-12 h-12 rounded-lg bg-[var(--color-accent-light)] flex items-center justify-center mb-5">
              <component :is="pillar.icon" :size="24" class="text-[var(--color-accent)]" />
            </div>
            <h3 class="font-heading text-lg font-bold text-[var(--color-primary)] mb-3">
              {{ pillar.title }}
            </h3>
            <p class="text-sm text-[var(--color-muted)] leading-relaxed">
              {{ pillar.text }}
            </p>
          </div>
        </div>
      </div>
    </section>

    <!-- ════════════════════ NOS FONDAMENTAUX ════════════════════ -->
    <section class="bg-white py-20 md:py-28">
      <div class="mx-auto max-w-[var(--container-xl)] px-6">
        <div class="text-center mb-14">
          <p class="font-heading text-xs font-bold uppercase tracking-[0.15em] text-[var(--color-accent)] mb-3">
            Nos fondamentaux
          </p>
          <h2 class="font-heading text-3xl md:text-4xl font-extrabold text-[var(--color-primary)] mb-4">
            Nos Valeurs
          </h2>
          <p class="text-[var(--color-muted)] max-w-xl mx-auto">
            Quatre piliers qui guident notre action quotidienne et notre vision pour la Côte d'Ivoire de demain.
          </p>
        </div>

        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
          <div
            v-for="(val, i) in values"
            :key="i"
            class="group border border-[var(--color-border)] rounded-xl p-7 text-center transition-all hover:shadow-[var(--shadow-md)] hover:-translate-y-0.5"
          >
            <div class="w-14 h-14 rounded-full bg-[var(--color-accent-light)] flex items-center justify-center mx-auto mb-5 transition-colors group-hover:bg-[var(--color-accent)] group-hover:text-white">
              <component :is="val.icon" :size="24" class="text-[var(--color-accent)] group-hover:text-white transition-colors" />
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

    <!-- ════════════════════ LE PRÉSIDENT ════════════════════ -->
    <section class="bg-[var(--color-surface)] py-20 md:py-28">
      <div class="mx-auto max-w-[var(--container-xl)] px-6">
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-12 lg:gap-16 items-center">
          <!-- Photo président -->
          <div class="relative">
            <div class="aspect-[3/4] rounded-2xl overflow-hidden shadow-[var(--shadow-lg)]">
              <img
                :src="presidentImg"
                alt="Le Président du FPP"
                class="w-full h-full object-cover"
              >
            </div>
            <div class="absolute -bottom-4 -right-4 bg-[var(--color-accent)] text-white px-6 py-3 rounded-xl shadow-[var(--shadow-md)]">
              <p class="font-heading text-xs font-bold uppercase tracking-[0.08em]">
                Le Président du Parti
              </p>
            </div>
          </div>

          <!-- Bio -->
          <div>
            <p class="font-heading text-xs font-bold uppercase tracking-[0.15em] text-[var(--color-accent)] mb-3">
              Le Président du Parti
            </p>
            <h2 class="font-heading text-3xl md:text-4xl font-extrabold text-[var(--color-primary)] mb-2">
              Dabé Nogbo Wanaminou
            </h2>
            <p class="text-[var(--color-accent)] font-heading font-semibold text-sm italic mb-6">
              Pour une Côte d’Ivoire décolonisée, souveraine, indépendante, développée et résolument tournée vers l’avenir.
            </p>
            <div class="space-y-4 text-[var(--color-muted)] leading-relaxed text-[15px]">
              <p>
                Un homme dont le parcours est aussi captivant qu'engagé. Juriste de formation, acteur politique indépendant et révolutionnaire passionné, il est un véritable architecte du changement en Côte d'Ivoire.
              </p>
              <p>
                Depuis la création du FPP, il porte un Parti politique dont le slogan est «Allons Où On Va!» un slogan qui met en avance l’importance de la décolonisation de la Côte d’Ivoire, gage de son décollage vers son véritable progrès et developpement.
              </p>
              <p>
                Avec une détermination inflexible et un cœur tourné vers les autres, il continue d'écrire son histoire, et celle de la Côte d'Ivoire, une page à la fois.
              </p>
            </div>
            <RouterLink
              to="/a-propos"
              class="inline-flex items-center gap-2 mt-8 font-heading text-sm font-bold text-[var(--color-accent)] no-underline hover:text-[var(--color-accent-hover)] transition-colors cursor-pointer"
            >
              Lire la biographie complète
              <ChevronRight :size="18" />
            </RouterLink>
          </div>
        </div>
      </div>
    </section>

    <!-- ════════════════════ LE FPP C'EST QUI ════════════════════ -->
    <section class="bg-white py-20 md:py-28">
      <div class="mx-auto max-w-[var(--container-xl)] px-6">
        <div class="grid grid-cols-1 lg:grid-cols-12 gap-12 lg:gap-16 items-center">
          <!-- Text -->
          <div class="lg:col-span-7">
            <p class="font-heading text-xs font-bold uppercase tracking-[0.15em] text-[var(--color-accent)] mb-3">
              À propos
            </p>
            <h2 class="font-heading text-3xl md:text-4xl font-extrabold text-[var(--color-primary)] mb-6">
              Le FPP, c'est qui ?
            </h2>
            <div class="space-y-4 text-[var(--color-muted)] leading-relaxed">
              <p>
                Fondé en 2021, le Front Patriotique Panafricain rassemble des hommes et des femmes de tous horizons, unis par une même conviction : la Côte d'Ivoire peut faire mieux, ensemble.
              </p>
              <p>
                Notre Parti se distingue par son approche pragmatique et inclusive. Nous croyons en une politique fondée sur l'écoute, le dialogue et l'action concrète.
              </p>
              <p>
                Avec plus de 5000 adhérents répartis dans 5 régions, nous sommes présents sur tout le territoire, au plus près des préoccupations des Ivoiriens.
              </p>
            </div>
            <RouterLink
              to="/a-propos"
              class="group inline-flex items-center gap-2 mt-8 px-6 py-3 font-heading text-sm font-bold uppercase tracking-[0.04em] text-[var(--color-primary)] no-underline border-2 border-[var(--color-primary)] rounded-sm transition-all hover:bg-[var(--color-primary)] hover:text-white cursor-pointer"
            >
              En savoir plus sur notre histoire
              <ArrowRight :size="16" class="transition-transform group-hover:translate-x-0.5" />
            </RouterLink>
          </div>

          <!-- Logo + stat -->
          <div class="lg:col-span-5 flex flex-col items-center">
            <div class="bg-[var(--color-surface)] rounded-2xl p-12 flex flex-col items-center w-full">
              <img
                :src="logoFpp"
                alt="FPP — Front Patriotique Panafricain"
                class="w-40 md:w-52 mb-8"
              >
              <div class="text-center">
                <p class="font-heading text-5xl font-extrabold text-[var(--color-primary)]">8</p>
                <p class="font-heading text-xs font-bold uppercase tracking-[0.1em] text-[var(--color-muted)] mt-1">
                  ans d'engagement
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- ════════════════════ ACTUALITÉS RÉCENTES ════════════════════ -->
    <section class="bg-[var(--color-surface)] py-20 md:py-28">
      <div class="mx-auto max-w-[var(--container-xl)] px-6">
        <div class="flex flex-col md:flex-row md:items-end justify-between mb-12 gap-4">
          <div>
            <p class="font-heading text-xs font-bold uppercase tracking-[0.15em] text-[var(--color-accent)] mb-3">
              Restez informés
            </p>
            <h2 class="font-heading text-3xl md:text-4xl font-extrabold text-[var(--color-primary)]">
              Actualités
            </h2>
          </div>
          <RouterLink
            to="/actualites"
            class="inline-flex items-center gap-2 font-heading text-sm font-bold text-[var(--color-accent)] no-underline hover:text-[var(--color-accent-hover)] transition-colors cursor-pointer"
          >
            Toutes les actualités
            <ArrowRight :size="16" />
          </RouterLink>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
          <RouterLink
            v-for="article in articles"
            :key="article.slug"
            :to="`/actualites/${article.slug}`"
            class="group bg-white border border-[var(--color-border)] rounded-xl overflow-hidden no-underline transition-all hover:shadow-[var(--shadow-md)] hover:-translate-y-0.5 cursor-pointer"
          >
            <!-- Image placeholder -->
            <div class="aspect-[16/9] bg-[var(--color-border)] relative overflow-hidden">
              <div class="absolute inset-0 flex items-center justify-center">
                <img :src="logoFpp" alt="" class="w-16 opacity-10">
              </div>
              <span class="absolute top-3 left-3 px-3 py-1 bg-[var(--color-accent)] text-white text-xs font-heading font-bold uppercase tracking-[0.06em] rounded-sm">
                {{ article.category }}
              </span>
            </div>
            <div class="p-6">
              <div class="flex items-center gap-2 text-xs text-[var(--color-muted)] mb-3">
                <Calendar :size="14" />
                {{ article.date }}
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
      </div>
    </section>

    <!-- ════════════════════ CTA FINAL ════════════════════ -->
    <section class="bg-[var(--color-primary)] py-20 md:py-28">
      <div class="mx-auto max-w-[var(--container-lg)] px-6 text-center">
        <h2 class="font-heading text-3xl md:text-4xl lg:text-5xl font-extrabold text-white leading-tight mb-6">
          Prêt à vous engager pour<br>
          <span class="text-[var(--color-accent)]">la Côte d'Ivoire</span> ?
        </h2>
        <p class="text-lg text-white/60 max-w-xl mx-auto mb-10">
          Rejoignez les milliers de citoyens qui ont choisi de s'impliquer. Ensemble, nous pouvons faire la différence.
        </p>
        <div class="flex flex-wrap justify-center gap-4">
          <RouterLink
            to="/adherer"
            class="group inline-flex items-center gap-2 px-8 py-4 font-heading text-sm font-bold uppercase tracking-[0.04em] bg-[var(--color-accent)] text-white no-underline rounded-sm transition-all hover:bg-[var(--color-accent-hover)] cursor-pointer"
          >
            Adhérer maintenant
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
