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

const memberPhoto = computed(() => {
  if (membership.value?.photo) return getMediaUrl(membership.value.photo)
  if (user.value?.avatar) return getMediaUrl(user.value.avatar)
  return null
})

const sexLabel = computed(() => user.value?.sex === 'F' ? 'F' : 'M')

const affiliationLabel = computed(() =>
  user.value?.sex === 'F' ? 'MILITANTE' : 'MILITANT'
)

const formattedDob = computed(() => {
  if (!user.value?.date_of_birth) return '—'
  return dayjs(user.value.date_of_birth).format('DD/MM/YYYY')
})

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
      <div class="w-full max-w-[560px]" style="perspective: 1200px;">
        <div
          class="relative w-full transition-transform duration-700 ease-in-out"
          :style="{ transformStyle: 'preserve-3d', transform: flipped ? 'rotateY(180deg)' : '' }"
          style="aspect-ratio: 85.6 / 54;"
        >
          <!-- ═══ RECTO ═══ -->
          <div
            ref="cardRef"
            class="absolute inset-0 rounded-xl overflow-hidden shadow-2xl border border-gray-200"
            style="backface-visibility: hidden;"
          >
            <div class="relative w-full h-full bg-white flex flex-col">

              <!-- Top bar -->
              <div class="bg-[#111] px-3 py-[6px] sm:py-2 flex items-center justify-center shrink-0">
                <span class="text-white text-[9px] sm:text-[12px] font-extrabold tracking-[0.3em] sm:tracking-[0.35em] uppercase">
                  Front Patriotique Panafricain
                </span>
              </div>

              <!-- Body -->
              <div class="flex-1 flex min-h-0 relative overflow-hidden">

                <!-- FPP watermark -->
                <div class="absolute inset-0 flex items-center justify-center pointer-events-none select-none overflow-hidden">
                  <span class="text-[60px] sm:text-[80px] font-extrabold text-gray-100 tracking-wide leading-none">FPP</span>
                </div>

                <!-- Photo -->
                <div class="w-[36%] shrink-0 p-2 sm:p-2.5 flex items-stretch relative z-10">
                  <div class="w-full bg-sky-100 border border-gray-300 overflow-hidden">
                    <img
                      v-if="memberPhoto"
                      :src="memberPhoto"
                      class="w-full h-full object-cover"
                      alt="Photo membre"
                      crossorigin="anonymous"
                    >
                    <div v-else class="w-full h-full flex items-center justify-center bg-gray-100 text-gray-400 text-lg font-bold">
                      {{ user?.first_name?.charAt(0) }}{{ user?.last_name?.charAt(0) }}
                    </div>
                  </div>
                </div>

                <!-- Info fields -->
                <div class="flex-1 py-1.5 sm:py-2 pr-2 sm:pr-3 relative z-10 min-w-0">
                  <div class="space-y-[2px] sm:space-y-1">

                    <!-- Nom + Sexe -->
                    <div class="flex items-start gap-1">
                      <div class="flex-1 min-w-0">
                        <p class="text-[6px] sm:text-[8px] text-gray-400 italic leading-none">Nom :</p>
                        <p class="text-[9px] sm:text-[13px] font-extrabold text-[#111] uppercase leading-tight truncate">{{ user?.last_name }}</p>
                      </div>
                      <div class="text-right shrink-0">
                        <p class="text-[6px] sm:text-[8px] text-gray-400 italic leading-none">Sexe :</p>
                        <p class="text-[9px] sm:text-[13px] font-extrabold text-[#111] leading-tight">{{ sexLabel }}</p>
                      </div>
                    </div>

                    <!-- Prénom(s) -->
                    <div>
                      <p class="text-[6px] sm:text-[8px] text-gray-400 italic leading-none">Prénom(s) :</p>
                      <p class="text-[9px] sm:text-[12px] font-bold text-[#111] uppercase leading-tight truncate">{{ user?.first_name }}</p>
                    </div>

                    <!-- Date de naissance -->
                    <div>
                      <p class="text-[6px] sm:text-[8px] text-gray-400 italic leading-none">Date de naissance :</p>
                      <p class="text-[8px] sm:text-[11px] font-bold text-[#111] leading-tight">{{ formattedDob }}</p>
                    </div>

                    <!-- Lieu de naissance -->
                    <div>
                      <p class="text-[6px] sm:text-[8px] text-gray-400 italic leading-none">Lieu de naissance :</p>
                      <p class="text-[8px] sm:text-[11px] font-bold text-[#111] uppercase leading-tight truncate">{{ membership?.commune || '—' }}</p>
                    </div>

                    <!-- Lieu de résidence -->
                    <div>
                      <p class="text-[6px] sm:text-[8px] text-gray-400 italic leading-none">Lieu de résidence :</p>
                      <p class="text-[8px] sm:text-[11px] font-bold text-[#111] uppercase leading-tight truncate">{{ membership?.city || '—' }}</p>
                    </div>

                    <!-- Fonction -->
                    <div>
                      <p class="text-[6px] sm:text-[8px] text-gray-400 italic leading-none">Fonction :</p>
                      <p class="text-[8px] sm:text-[11px] font-bold text-[#111] uppercase leading-tight truncate">{{ membership?.profession || '—' }}</p>
                    </div>

                    <!-- Affiliation -->
                    <div>
                      <p class="text-[6px] sm:text-[8px] text-gray-400 italic leading-none">Affiliation :</p>
                      <p class="text-[8px] sm:text-[11px] font-extrabold text-[#111] uppercase leading-tight">{{ affiliationLabel }}</p>
                    </div>

                    <!-- Matricule + QR -->
                    <div class="flex items-end justify-between gap-1 pt-1 sm:pt-2">
                      <div class="min-w-0">
                        <p class="text-[6px] sm:text-[8px] text-gray-400 italic leading-none">Matricule :</p>
                        <p class="text-[8px] sm:text-[11px] font-mono font-bold text-[#111] leading-tight truncate">{{ membership?.matricule || '—' }}</p>
                      </div>
                      <div v-if="qrDataUrl" class="shrink-0 flex flex-col items-center">
                        <p class="text-[5px] sm:text-[6px] text-gray-300 italic leading-none mb-0.5">Front Patriotique Panafricain</p>
                        <img :src="qrDataUrl" class="w-10 h-10 sm:w-13 sm:h-13" alt="QR Code">
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Bottom bar -->
              <div class="bg-[#111] px-3 py-[6px] sm:py-2 flex items-center justify-center shrink-0">
                <span class="text-white text-[9px] sm:text-[13px] font-extrabold tracking-[0.25em] sm:tracking-[0.3em] uppercase">
                  Unité – Dignité – Intégrité
                </span>
              </div>
            </div>
          </div>

          <!-- ═══ VERSO ═══ -->
          <div
            class="absolute inset-0 rounded-xl overflow-hidden shadow-2xl border border-gray-200"
            style="backface-visibility: hidden; transform: rotateY(180deg);"
          >
            <div class="relative w-full h-full bg-white flex flex-col items-center justify-between py-4 sm:py-5 px-5 sm:px-8">

              <!-- Slogan top -->
              <p class="text-[11px] sm:text-[15px] font-extrabold text-[#111] text-center uppercase leading-snug tracking-wide">
                Un peuple debout est un peuple<br>qui gagne toujours.
              </p>

              <!-- Logo center -->
              <div class="flex items-center gap-3 sm:gap-4">
                <img :src="logoFpp" alt="FPP" class="h-14 sm:h-20 w-auto">
                <div>
                  <p class="text-2xl sm:text-4xl font-black text-[#111] leading-none tracking-tight">FPP</p>
                  <p class="text-[7px] sm:text-[10px] text-gray-600 font-medium mt-0.5">Front Patriotique Panafricain</p>
                </div>
              </div>

              <!-- Slogan bottom -->
              <p class="text-[13px] sm:text-[18px] font-black text-[#111] text-center uppercase tracking-wide">
                Allons où on va !
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Instructions -->
    <p class="mt-6 text-center text-[11px] text-gray-400 leading-relaxed px-4">
      Cliquez « Retourner » pour voir le verso.<br class="sm:hidden">
      Le PDF est au format carte de crédit (85,6 × 54 mm).
    </p>
  </div>
</template>
