<script setup lang="ts">
import { computed, ref, onMounted, nextTick } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useRouter } from 'vue-router'
import { getMediaUrl } from '@/utils/media'
import { Download, ArrowLeft, RotateCcw } from 'lucide-vue-next'
import { RouterLink } from 'vue-router'
import QRCode from 'qrcode'
import dayjs from 'dayjs'
import 'dayjs/locale/fr'
import logoFpp from '@/assets/img/fpplogsf.png'

dayjs.locale('fr')

const authStore = useAuthStore()
const router = useRouter()
const user = computed(() => authStore.user)
const membership = computed(() => user.value?.membership)

const qrDataUrl = ref('')
const cardRef = ref<HTMLElement | null>(null)
const flipped = ref(false)
const exporting = ref(false)

onMounted(async () => {
  if (membership.value?.status !== 'validated') {
    router.replace('/mon-espace')
    return
  }
  if (membership.value?.matricule) {
    const qrText = `FPP-MEMBER:${membership.value.matricule}|${user.value?.first_name} ${user.value?.last_name}|${user.value?.email}`
    qrDataUrl.value = await QRCode.toDataURL(qrText, {
      width: 200,
      margin: 1,
      color: { dark: '#111111', light: '#ffffff' },
      errorCorrectionLevel: 'M',
    })
  }
})

async function exportPdf() {
  if (!cardRef.value) return
  exporting.value = true
  const wasFlipped = flipped.value
  flipped.value = false
  await nextTick()

  try {
    const html2canvas = (await import('html2canvas-pro')).default
    const { jsPDF } = await import('jspdf')

    const canvas = await html2canvas(cardRef.value, {
      scale: 3,
      useCORS: true,
      backgroundColor: null,
    })

    const imgData = canvas.toDataURL('image/png')
    const pdf = new jsPDF({
      orientation: 'landscape',
      unit: 'mm',
      format: [85.6, 54],
    })
    pdf.addImage(imgData, 'PNG', 0, 0, 85.6, 54)
    pdf.save(`carte-membre-fpp-${membership.value?.matricule || 'draft'}.pdf`)
  } finally {
    flipped.value = wasFlipped
    exporting.value = false
  }
}
</script>

<template>
  <div>
    <!-- Breadcrumb -->
    <div class="flex items-center gap-2 mb-4">
      <RouterLink to="/mon-espace" class="w-8 h-8 rounded-lg bg-white border border-gray-200 flex items-center justify-center text-gray-500 hover:text-gray-900 hover:border-gray-300 transition-all no-underline shrink-0">
        <ArrowLeft :size="16" />
      </RouterLink>
      <h1 class="text-lg sm:text-xl font-bold text-gray-900">Ma carte de membre</h1>
    </div>

    <!-- Actions -->
    <div class="flex items-center gap-2 mb-6">
      <button
        @click="flipped = !flipped"
        class="inline-flex items-center gap-1.5 px-3 py-2 text-xs font-semibold text-gray-700 bg-white border border-gray-200 rounded-lg hover:bg-gray-50 transition-all cursor-pointer"
      >
        <RotateCcw :size="14" />
        Retourner
      </button>
      <button
        @click="exportPdf"
        :disabled="exporting"
        class="inline-flex items-center gap-1.5 px-3 py-2 text-xs font-semibold text-white bg-gray-900 rounded-lg hover:bg-gray-800 transition-all cursor-pointer disabled:opacity-50"
      >
        <Download :size="14" />
        {{ exporting ? 'Export...' : 'Télécharger PDF' }}
      </button>
    </div>

    <!-- Card container with perspective -->
    <div class="flex justify-center">
      <div class="w-full max-w-[430px]" style="perspective: 1200px;">
        <div
          class="relative w-full transition-transform duration-700 ease-in-out"
          :style="{ transformStyle: 'preserve-3d', transform: flipped ? 'rotateY(180deg)' : '' }"
          style="aspect-ratio: 85.6 / 54;"
        >
          <!-- ═══ RECTO ═══ -->
          <div
            ref="cardRef"
            class="absolute inset-0 rounded-2xl overflow-hidden shadow-2xl"
            style="backface-visibility: hidden;"
          >
            <div class="relative w-full h-full bg-gradient-to-br from-[#0a0a0a] via-[#1a1a1a] to-[#0d0d0d] p-5 flex flex-col justify-between">
              <!-- Holographic overlay -->
              <div class="absolute inset-0 bg-[radial-gradient(ellipse_at_20%_30%,rgba(0,166,81,0.12),transparent_50%)]" />
              <div class="absolute inset-0 bg-[radial-gradient(ellipse_at_80%_70%,rgba(255,255,255,0.04),transparent_50%)]" />
              <div class="absolute top-0 left-0 right-0 h-[3px] bg-gradient-to-r from-green-500 via-green-400 to-green-600" />

              <!-- Top row: Logo + Title -->
              <div class="relative flex items-center justify-between">
                <div class="flex items-center gap-2.5">
                  <img :src="logoFpp" alt="FPP" class="h-8 w-auto opacity-90">
                  <div>
                    <div class="text-[11px] font-bold text-white tracking-[0.15em] uppercase leading-none">FPP</div>
                    <div class="text-[6px] text-green-400 tracking-[0.08em] uppercase mt-0.5 leading-none">Front Patriotique Panafricain</div>
                  </div>
                </div>
                <div class="text-right">
                  <div class="text-[7px] text-gray-500 uppercase tracking-wider">Carte de membre</div>
                  <div class="text-[7px] text-gray-500 uppercase tracking-wider">Côte d'Ivoire</div>
                </div>
              </div>

              <!-- Middle: Photo + Info -->
              <div class="relative flex items-end gap-4">
                <div class="w-16 h-20 rounded-lg bg-gray-800 border border-gray-700 overflow-hidden shrink-0 shadow-inner">
                  <img
                    v-if="user?.avatar"
                    :src="getMediaUrl(user.avatar)"
                    class="w-full h-full object-cover"
                    alt=""
                  >
                  <div v-else class="w-full h-full flex items-center justify-center text-gray-600 text-lg font-bold">
                    {{ user?.first_name?.charAt(0) }}{{ user?.last_name?.charAt(0) }}
                  </div>
                </div>
                <div class="flex-1 min-w-0">
                  <p class="text-white text-sm font-bold truncate leading-tight">
                    {{ user?.last_name?.toUpperCase() }}
                  </p>
                  <p class="text-gray-300 text-xs font-medium truncate leading-tight">
                    {{ user?.first_name }}
                  </p>
                  <p class="text-green-400 text-[11px] font-mono tracking-widest mt-1.5">
                    {{ membership?.matricule || '—' }}
                  </p>
                </div>
              </div>

              <!-- Bottom row: Meta -->
              <div class="relative flex items-end justify-between">
                <div class="flex gap-5">
                  <div>
                    <p class="text-[7px] text-gray-500 uppercase tracking-wider">Membre depuis</p>
                    <p class="text-[10px] text-gray-300 font-medium">
                      {{ dayjs(membership?.membership_validated_at).format('DD/MM/YYYY') }}
                    </p>
                  </div>
                  <div>
                    <p class="text-[7px] text-gray-500 uppercase tracking-wider">Ville</p>
                    <p class="text-[10px] text-gray-300 font-medium">{{ membership?.city }}</p>
                  </div>
                </div>
                <div class="w-6 h-6 rounded-full bg-gradient-to-br from-green-400 to-green-600 opacity-80" />
              </div>
            </div>
          </div>

          <!-- ═══ VERSO ═══ -->
          <div
            class="absolute inset-0 rounded-2xl overflow-hidden shadow-2xl"
            style="backface-visibility: hidden; transform: rotateY(180deg);"
          >
            <div class="relative w-full h-full bg-gradient-to-br from-gray-50 to-white p-5 flex flex-col justify-between">
              <!-- Top -->
              <div class="flex items-center justify-between">
                <div>
                  <p class="text-[8px] text-gray-400 uppercase tracking-wider font-semibold">Front Patriotique Panafricain</p>
                  <p class="text-[7px] text-gray-400 mt-0.5">Parti politique — Côte d'Ivoire</p>
                </div>
                <img :src="logoFpp" alt="FPP" class="h-6 w-auto opacity-30">
              </div>

              <!-- QR Code center -->
              <div class="flex items-center justify-center">
                <div class="bg-white rounded-lg p-1.5 shadow-sm border border-gray-100">
                  <img v-if="qrDataUrl" :src="qrDataUrl" class="w-20 h-20" alt="QR Code">
                </div>
              </div>

              <!-- Bottom info -->
              <div class="text-center space-y-1">
                <p class="text-[8px] text-gray-500">
                  Cette carte est personnelle et incessible.
                </p>
                <p class="text-[7px] text-gray-400">
                  En cas de perte, contactez info@fpp-ci.online
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Instructions -->
    <p class="mt-6 text-center text-[11px] text-gray-400 leading-relaxed px-4">
      Cliquez « Retourner » pour le verso (QR code).<br class="sm:hidden">
      Le PDF est au format carte de crédit (85,6 × 54 mm).
    </p>
  </div>
</template>
