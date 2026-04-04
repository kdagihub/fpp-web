<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { RouterLink } from 'vue-router'
import { useAppToast } from '@/composables/useToast'
import api from '@/api'
import type { DashboardData } from '@/types'

import Skeleton from 'primevue/skeleton'

import { Line, Doughnut, Bar } from 'vue-chartjs'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  Tooltip,
  Legend,
  Filler,
} from 'chart.js'

import {
  Users,
  UserCheck,
  Clock,
  FileText,
  Mail,
  MailOpen,
  TrendingUp,
  BadgeCheck,
  Settings,
  Shield,
} from 'lucide-vue-next'
import { useAuthStore } from '@/stores/auth'

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, BarElement, ArcElement, Tooltip, Legend, Filler)

const toast = useAppToast()
const authStore = useAuthStore()
const data = ref<DashboardData | null>(null)
const loading = ref(true)
const period = ref(30)

const periodOptions = [
  { label: '7j', value: 7 },
  { label: '30j', value: 30 },
  { label: '90j', value: 90 },
  { label: '1 an', value: 365 },
]

const shortcuts = computed(() => {
  const all = [
    { to: '/admin/membres', label: 'Membres', icon: Users, permission: 'can_view_members', color: 'text-green-600', bg: 'bg-green-50 hover:bg-green-100' },
    { to: '/admin/verification-matricule', label: 'Vérifier matricule', icon: BadgeCheck, permission: 'can_view_members', color: 'text-indigo-600', bg: 'bg-indigo-50 hover:bg-indigo-100' },
    { to: '/admin/articles', label: 'Articles', icon: FileText, permission: 'can_create_article', color: 'text-blue-600', bg: 'bg-blue-50 hover:bg-blue-100' },
    { to: '/admin/contacts', label: 'Contacts', icon: Mail, permission: 'can_manage_contacts', color: 'text-orange-600', bg: 'bg-orange-50 hover:bg-orange-100' },
    { to: '/admin/parametres', label: 'Paramètres', icon: Settings, permission: 'can_manage_settings', color: 'text-gray-600', bg: 'bg-gray-50 hover:bg-gray-100' },
    { to: '/admin/audit', label: 'Audit', icon: Shield, permission: 'can_view_audit_log', color: 'text-purple-600', bg: 'bg-purple-50 hover:bg-purple-100' },
  ]
  return all.filter(s => authStore.hasPermission(s.permission))
})

async function fetchDashboard() {
  loading.value = true
  try {
    const { data: resp } = await api.get<DashboardData>('/admin/dashboard/', {
      params: { period: period.value },
    })
    data.value = resp
  } catch {
    toast.error('Erreur', 'Impossible de charger le tableau de bord.')
  } finally {
    loading.value = false
  }
}

watch(period, () => fetchDashboard())
onMounted(fetchDashboard)

/* ── KPI cards ── */
const kpis = computed(() => {
  if (!data.value) return []
  return [
    {
      label: 'Membres validés',
      value: data.value.members.total_validated,
      icon: UserCheck,
      color: 'text-green-600',
      bg: 'bg-green-50',
    },
    {
      label: 'Demandes en attente',
      value: data.value.members.pending,
      icon: Clock,
      color: 'text-amber-600',
      bg: 'bg-amber-50',
    },
    {
      label: 'Articles publiés',
      value: data.value.articles.total_published,
      icon: FileText,
      color: 'text-blue-600',
      bg: 'bg-blue-50',
    },
    {
      label: 'Messages non lus',
      value: data.value.contacts.unread,
      icon: data.value.contacts.unread > 0 ? Mail : MailOpen,
      color: data.value.contacts.unread > 0 ? 'text-red-600' : 'text-gray-500',
      bg: data.value.contacts.unread > 0 ? 'bg-red-50' : 'bg-gray-50',
    },
  ]
})

/* ── Charts ── */
const accentGreen = '#16A34A'
const accentGreenLight = 'rgba(22, 163, 74, 0.1)'

const evolutionChartData = computed(() => {
  if (!data.value) return { labels: [], datasets: [] }
  const evo = data.value.members.evolution
  return {
    labels: evo.map((e) => {
      const d = new Date(e.date)
      return d.toLocaleDateString('fr-FR', { day: 'numeric', month: 'short' })
    }),
    datasets: [
      {
        label: 'Nouvelles adhésions',
        data: evo.map((e) => e.count),
        borderColor: accentGreen,
        backgroundColor: accentGreenLight,
        fill: true,
        tension: 0.4,
        pointRadius: 2,
        pointHoverRadius: 5,
      },
    ],
  }
})

const evolutionChartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: { display: false },
    tooltip: {
      backgroundColor: '#111',
      titleFont: { size: 11 },
      bodyFont: { size: 12 },
      padding: 10,
      cornerRadius: 8,
    },
  },
  scales: {
    x: {
      grid: { display: false },
      ticks: { font: { size: 10 }, color: '#999', maxTicksLimit: 12 },
    },
    y: {
      beginAtZero: true,
      grid: { color: '#f0f0f0' },
      ticks: { font: { size: 10 }, color: '#999', precision: 0 },
    },
  },
}

const statusColors: Record<string, string> = {
  validated: '#16A34A',
  pending: '#D97706',
  rejected: '#DC2626',
  suspended: '#6B7280',
}

const statusLabels: Record<string, string> = {
  validated: 'Validé',
  pending: 'En attente',
  rejected: 'Rejeté',
  suspended: 'Suspendu',
}

const statusChartData = computed(() => {
  if (!data.value) return { labels: [], datasets: [] }
  const items = data.value.members.by_status
  return {
    labels: items.map((s) => statusLabels[s.membership_status] || s.membership_status),
    datasets: [
      {
        data: items.map((s) => s.count),
        backgroundColor: items.map((s) => statusColors[s.membership_status] || '#ccc'),
        borderWidth: 0,
        hoverOffset: 8,
      },
    ],
  }
})

const sexChartData = computed(() => {
  if (!data.value) return { labels: [], datasets: [] }
  const items = data.value.members.by_sex
  const maleCount = items.find((s) => s.user__sex === 'M')?.count ?? 0
  const femaleCount = items.find((s) => s.user__sex === 'F')?.count ?? 0
  return {
    labels: ['Hommes', 'Femmes'],
    datasets: [
      {
        data: [maleCount, femaleCount],
        backgroundColor: ['#3B82F6', '#EC4899'],
        borderWidth: 0,
        hoverOffset: 8,
      },
    ],
  }
})

const doughnutOptions = {
  responsive: true,
  maintainAspectRatio: false,
  cutout: '65%',
  plugins: {
    legend: {
      position: 'bottom' as const,
      labels: { font: { size: 11 }, padding: 16, usePointStyle: true, pointStyleWidth: 8 },
    },
    tooltip: {
      backgroundColor: '#111',
      titleFont: { size: 11 },
      bodyFont: { size: 12 },
      padding: 10,
      cornerRadius: 8,
    },
  },
}

const cityChartData = computed(() => {
  if (!data.value) return { labels: [], datasets: [] }
  const cities = data.value.members.by_city.slice(0, 8)
  return {
    labels: cities.map((c) => c.city),
    datasets: [
      {
        label: 'Membres',
        data: cities.map((c) => c.count),
        backgroundColor: accentGreen,
        borderRadius: 6,
        barPercentage: 0.6,
      },
    ],
  }
})

const cityChartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  indexAxis: 'y' as const,
  plugins: {
    legend: { display: false },
    tooltip: {
      backgroundColor: '#111',
      titleFont: { size: 11 },
      bodyFont: { size: 12 },
      padding: 10,
      cornerRadius: 8,
    },
  },
  scales: {
    x: {
      beginAtZero: true,
      grid: { color: '#f0f0f0' },
      ticks: { font: { size: 10 }, color: '#999', precision: 0 },
    },
    y: {
      grid: { display: false },
      ticks: { font: { size: 11 }, color: '#555' },
    },
  },
}
</script>

<template>
  <div>
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3 sm:gap-4 mb-5 sm:mb-6">
      <h2 class="font-heading text-xl sm:text-2xl font-bold text-[var(--color-primary)]">
        Tableau de bord
      </h2>
      <div class="flex items-center bg-white border border-gray-200 rounded-lg p-1 gap-0.5 self-start sm:self-auto">
        <button
          v-for="opt in periodOptions"
          :key="opt.value"
          @click="period = opt.value"
          class="px-3 py-1.5 text-xs font-semibold rounded-md transition-all cursor-pointer"
          :class="period === opt.value
            ? 'bg-[var(--color-accent)] text-white shadow-sm'
            : 'text-gray-500 hover:text-gray-800 hover:bg-gray-50'"
        >
          {{ opt.label }}
        </button>
      </div>
    </div>

    <!-- KPIs -->
    <div class="grid grid-cols-2 lg:grid-cols-4 gap-3 sm:gap-4 mb-5 sm:mb-8">
      <template v-if="loading">
        <div v-for="i in 4" :key="i" class="bg-white rounded-xl border border-gray-200 p-3 sm:p-5">
          <Skeleton height="1rem" width="60%" class="mb-3" />
          <Skeleton height="2rem" width="40%" />
        </div>
      </template>
      <template v-else>
        <div
          v-for="(kpi, i) in kpis"
          :key="i"
          class="bg-white rounded-xl border border-gray-200 p-3 sm:p-4 lg:p-5"
        >
          <div class="flex items-center gap-2 sm:gap-3 mb-1.5 sm:mb-2">
            <div class="w-8 h-8 sm:w-9 sm:h-9 rounded-lg flex items-center justify-center shrink-0" :class="kpi.bg">
              <component :is="kpi.icon" :size="16" :class="kpi.color" />
            </div>
            <span class="text-[10px] sm:text-xs font-semibold text-gray-500 uppercase tracking-wide leading-tight">{{ kpi.label }}</span>
          </div>
          <p class="text-xl sm:text-2xl lg:text-3xl font-bold text-gray-900">{{ kpi.value.toLocaleString('fr-FR') }}</p>
        </div>
      </template>
    </div>

    <!-- Charts Row 1: Evolution + Status -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-4 sm:gap-6 mb-4 sm:mb-6">
      <!-- Evolution line chart -->
      <div class="lg:col-span-2 bg-white rounded-xl border border-gray-200 p-4 sm:p-5">
        <div class="flex items-center gap-2 mb-3 sm:mb-4">
          <TrendingUp :size="16" class="text-[var(--color-accent)]" />
          <h3 class="text-sm font-bold text-gray-900">Évolution des adhésions</h3>
        </div>
        <div v-if="loading" class="h-48 sm:h-64 flex items-center justify-center">
          <Skeleton height="100%" width="100%" />
        </div>
        <div v-else class="h-48 sm:h-64">
          <Line :data="evolutionChartData" :options="evolutionChartOptions" />
        </div>
      </div>

      <!-- Status doughnut -->
      <div class="bg-white rounded-xl border border-gray-200 p-4 sm:p-5">
        <h3 class="text-sm font-bold text-gray-900 mb-3 sm:mb-4">Répartition par statut</h3>
        <div v-if="loading" class="h-44 sm:h-52 flex items-center justify-center">
          <Skeleton shape="circle" size="8rem" />
        </div>
        <div v-else class="h-44 sm:h-52">
          <Doughnut :data="statusChartData" :options="doughnutOptions" />
        </div>
      </div>
    </div>

    <!-- Charts Row 2: Cities + Sex (compact) -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-4 sm:gap-6 mb-4 sm:mb-6">
      <!-- Top cities -->
      <div class="lg:col-span-2 bg-white rounded-xl border border-gray-200 p-4 sm:p-5">
        <h3 class="text-sm font-bold text-gray-900 mb-3">Top villes</h3>
        <div v-if="loading" class="h-36 sm:h-44 flex items-center justify-center">
          <Skeleton height="100%" width="100%" />
        </div>
        <div v-else class="h-36 sm:h-44">
          <Bar :data="cityChartData" :options="cityChartOptions" />
        </div>
      </div>

      <!-- Sex doughnut -->
      <div class="bg-white rounded-xl border border-gray-200 p-4 sm:p-5">
        <h3 class="text-sm font-bold text-gray-900 mb-3">Répartition H / F</h3>
        <div v-if="loading" class="h-36 sm:h-44 flex items-center justify-center">
          <Skeleton shape="circle" size="7rem" />
        </div>
        <div v-else class="h-36 sm:h-44">
          <Doughnut :data="sexChartData" :options="doughnutOptions" />
        </div>
      </div>
    </div>

    <!-- Quick access shortcuts -->
    <div>
      <h3 class="text-xs font-bold text-gray-400 uppercase tracking-wide mb-3">Accès rapide</h3>
      <div class="grid grid-cols-3 sm:grid-cols-3 lg:grid-cols-6 gap-2 sm:gap-3">
        <RouterLink
          v-for="s in shortcuts"
          :key="s.to"
          :to="s.to"
          class="group flex flex-col items-center gap-1.5 sm:gap-2 p-3 sm:p-4 rounded-xl border border-gray-200 no-underline transition-all"
          :class="s.bg"
        >
          <div class="w-8 h-8 sm:w-10 sm:h-10 rounded-lg flex items-center justify-center bg-white shadow-sm">
            <component :is="s.icon" :size="18" :class="s.color" />
          </div>
          <span class="text-[10px] sm:text-xs font-semibold text-gray-700 text-center leading-tight">{{ s.label }}</span>
        </RouterLink>
      </div>
    </div>
  </div>
</template>
