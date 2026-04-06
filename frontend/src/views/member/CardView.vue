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

let touchStartX = 0
let touchStartY = 0

function onTouchStart(e: TouchEvent) {
  touchStartX = e.touches[0].clientX
  touchStartY = e.touches[0].clientY
}

function onTouchEnd(e: TouchEvent) {
  const dx = e.changedTouches[0].clientX - touchStartX
  const dy = e.changedTouches[0].clientY - touchStartY
  if (Math.abs(dx) > 40 && Math.abs(dx) > Math.abs(dy)) {
    flipped.value = !flipped.value
  }
}

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
          class="card-flip relative w-full transition-transform duration-700 ease-in-out cursor-pointer"
          style="aspect-ratio: 85.6 / 54;"
          :style="{ transformStyle: 'preserve-3d', transform: flipped ? 'rotateY(180deg)' : '' }"
          @click="flipped = !flipped"
          @touchstart.passive="onTouchStart"
          @touchend.passive="onTouchEnd"
        >
          <!-- ═══ RECTO ═══ -->
          <div
            ref="cardRef"
            class="card-face absolute inset-0 rounded-xl overflow-hidden shadow-2xl border border-gray-200"
            style="backface-visibility: hidden;"
          >
            <div class="relative w-full h-full bg-white flex flex-col">

              <!-- Top bar -->
              <div class="card-bar bg-[#111] flex items-center justify-center shrink-0">
                <span class="card-bar-text text-white font-extrabold uppercase whitespace-nowrap">
                  Front Patriotique Panafricain
                </span>
              </div>

              <!-- Body -->
              <div class="flex-1 flex min-h-0 relative overflow-hidden">

                <!-- FPP watermark -->
                <div class="absolute inset-0 flex items-center justify-center pointer-events-none select-none overflow-hidden">
                  <span class="text-[40px] sm:text-[80px] font-extrabold text-gray-100 tracking-wide leading-none">FPP</span>
                </div>

                <!-- Photo -->
                <div class="card-photo shrink-0 flex items-stretch relative z-10">
                  <div class="card-photo-inner w-full bg-sky-100 border border-gray-300 overflow-hidden">
                    <img
                      v-if="memberPhoto"
                      :src="memberPhoto"
                      class="w-full h-full object-cover"
                      alt="Photo membre"
                      crossorigin="anonymous"
                    >
                    <div v-else class="w-full h-full flex items-center justify-center bg-gray-100 text-gray-400 text-sm sm:text-lg font-bold">
                      {{ user?.first_name?.charAt(0) }}{{ user?.last_name?.charAt(0) }}
                    </div>
                  </div>
                </div>

                <!-- Info fields -->
                <div class="card-info flex-1 relative z-10 min-w-0">
                  <div class="card-fields">

                    <!-- Nom + Sexe -->
                    <div class="flex items-start">
                      <div class="flex-1 min-w-0">
                        <p class="card-label text-gray-400 italic leading-none">Nom :</p>
                        <p class="card-value-lg font-extrabold text-[#111] uppercase leading-tight truncate">{{ user?.last_name }}</p>
                      </div>
                      <div class="text-right shrink-0">
                        <p class="card-label text-gray-400 italic leading-none">Sexe :</p>
                        <p class="card-value-lg font-extrabold text-[#111] leading-tight">{{ sexLabel }}</p>
                      </div>
                    </div>

                    <!-- Prénom(s) -->
                    <div>
                      <p class="card-label text-gray-400 italic leading-none">Prénom(s) :</p>
                      <p class="card-value-lg font-bold text-[#111] uppercase leading-tight truncate">{{ user?.first_name }}</p>
                    </div>

                    <!-- Date de naissance -->
                    <div>
                      <p class="card-label text-gray-400 italic leading-none">Né(e) le :</p>
                      <p class="card-value font-bold text-[#111] leading-tight">{{ formattedDob }}</p>
                    </div>

                    <!-- Lieu de naissance -->
                    <div>
                      <p class="card-label text-gray-400 italic leading-none">Lieu naiss. :</p>
                      <p class="card-value font-bold text-[#111] uppercase leading-tight truncate">{{ membership?.commune || '—' }}</p>
                    </div>

                    <!-- Lieu de résidence -->
                    <div>
                      <p class="card-label text-gray-400 italic leading-none">Résidence :</p>
                      <p class="card-value font-bold text-[#111] uppercase leading-tight truncate">{{ membership?.city || '—' }}</p>
                    </div>

                    <!-- Fonction -->
                    <div>
                      <p class="card-label text-gray-400 italic leading-none">Fonction :</p>
                      <p class="card-value font-bold text-[#111] uppercase leading-tight truncate">{{ membership?.profession || '—' }}</p>
                    </div>

                    <!-- Affiliation -->
                    <div>
                      <p class="card-label text-gray-400 italic leading-none">Affiliation :</p>
                      <p class="card-value font-extrabold text-[#111] uppercase leading-tight">{{ affiliationLabel }}</p>
                    </div>

                    <!-- Matricule + QR -->
                    <div class="card-qr-row flex items-end justify-between">
                      <div class="min-w-0">
                        <p class="card-label text-gray-400 italic leading-none">Matricule :</p>
                        <p class="card-value font-mono font-bold text-[#111] leading-tight truncate">{{ membership?.matricule || '—' }}</p>
                      </div>
                      <div v-if="qrDataUrl" class="shrink-0 flex flex-col items-center">
                        <p class="card-qr-caption text-gray-300 italic leading-none">Front Patriotique Panafricain</p>
                        <img :src="qrDataUrl" class="card-qr-img" alt="QR Code">
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Bottom bar -->
              <div class="card-bar bg-[#111] flex items-center justify-center shrink-0">
                <span class="card-bar-text text-white font-extrabold uppercase whitespace-nowrap">
                  Unité – Dignité – Intégrité
                </span>
              </div>
            </div>
          </div>

          <!-- ═══ VERSO ═══ -->
          <div
            class="card-face absolute inset-0 rounded-xl overflow-hidden shadow-2xl border border-gray-200"
            style="backface-visibility: hidden; transform: rotateY(180deg);"
          >
            <div class="card-verso relative w-full h-full bg-white flex flex-col items-center justify-between">

              <!-- Slogan top -->
              <p class="card-verso-slogan text-[#111] text-center uppercase leading-snug" style="font-family: Georgia, 'Times New Roman', serif; font-style: italic; font-weight: 900;">
                Un peuple debout est un peuple<br>qui gagne toujours.
              </p>

              <!-- Logo center -->
              <div class="card-verso-logo flex items-center">
                <img :src="logoFpp" alt="FPP" class="card-verso-logo-img w-auto">
                <div>
                  <p class="card-verso-fpp font-black text-[#111] leading-none tracking-tight">FPP</p>
                  <p class="card-verso-sub text-gray-600 font-medium">Front Patriotique Panafricain</p>
                </div>
              </div>

              <!-- Slogan bottom -->
              <p class="card-verso-cta font-black text-[#111] text-center uppercase tracking-wide">
                Allons où on va !
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Instructions -->
    <p class="mt-6 text-center text-[11px] text-gray-400 leading-relaxed px-4">
      <span class="sm:hidden">Cliquez ou swipez pour retourner la carte.</span>
      <span class="hidden sm:inline">Cliquez sur la carte ou sur « Retourner » pour voir le verso.</span>
      <br>
      Le PDF est au format carte de crédit (85,6 × 54 mm).
    </p>
  </div>
</template>

<style scoped>
/* ─── Aspect ratio (fiable inline + CSS backup) ─── */
.card-flip {
  aspect-ratio: 85.6 / 54;
  -webkit-text-size-adjust: 100%;
  text-size-adjust: 100%;
}

/* ═══════════════════════════════════════════════════
   MOBILE (< 640px) — CSS pur avec !important
   Bypass complet de Tailwind pour fiabilité totale
   ═══════════════════════════════════════════════════ */
@media (max-width: 639px) {
  /* Barres noires top/bottom */
  .card-bar {
    padding: 4px 8px !important;
  }
  .card-bar-text {
    font-size: 7px !important;
    letter-spacing: 0.15em !important;
  }

  /* Photo */
  .card-photo {
    width: 30% !important;
    padding: 5px !important;
  }

  /* Colonne info — prend toute la hauteur */
  .card-info {
    padding: 4px 8px 4px 0 !important;
    display: flex !important;
    flex-direction: column !important;
    height: 100% !important;
  }

  /* Container champs — distribue sur toute la hauteur */
  .card-fields {
    display: flex !important;
    flex-direction: column !important;
    justify-content: space-between !important;
    flex: 1 !important;
  }

  /* Labels (italic gris) */
  .card-label {
    font-size: 5px !important;
    line-height: 1 !important;
    margin: 0 !important;
  }

  /* Valeurs principales (Nom, Prénom) */
  .card-value-lg {
    font-size: 10px !important;
    line-height: 1.15 !important;
    margin: 0 !important;
  }

  /* Valeurs normales */
  .card-value {
    font-size: 8px !important;
    line-height: 1.15 !important;
    margin: 0 !important;
  }

  /* Ligne Matricule + QR */
  .card-qr-row {
    gap: 3px !important;
    padding-top: 0 !important;
  }

  /* QR Code */
  .card-qr-img {
    width: 34px !important;
    height: 34px !important;
  }

  /* Texte au-dessus du QR */
  .card-qr-caption {
    display: none !important;
  }

  /* ─── VERSO mobile ─── */
  .card-verso {
    padding: 10px 14px !important;
  }
  .card-verso-slogan {
    font-size: 11px !important;
    line-height: 1.4 !important;
  }
  .card-verso-logo {
    gap: 8px !important;
  }
  .card-verso-logo-img {
    height: 48px !important;
  }
  .card-verso-fpp {
    font-size: 24px !important;
  }
  .card-verso-sub {
    font-size: 7px !important;
    margin-top: 1px !important;
  }
  .card-verso-cta {
    font-size: 13px !important;
  }
}

/* ═══════════════════════════════════════════════════
   DESKTOP (≥ 640px) — tailles originales
   ═══════════════════════════════════════════════════ */
@media (min-width: 640px) {
  .card-bar {
    padding: 8px 12px;
  }
  .card-bar-text {
    font-size: 12px;
    letter-spacing: 0.35em;
  }
  .card-photo {
    width: 36%;
    padding: 10px;
  }
  .card-info {
    padding: 8px 12px 8px 0;
  }
  .card-fields {
    display: flex;
    flex-direction: column;
    gap: 4px;
  }
  .card-label {
    font-size: 8px;
    line-height: 1;
  }
  .card-value-lg {
    font-size: 13px;
    line-height: 1.25;
  }
  .card-value {
    font-size: 11px;
    line-height: 1.25;
  }
  .card-qr-row {
    gap: 4px;
    padding-top: 8px;
  }
  .card-qr-img {
    width: 52px;
    height: 52px;
  }
  .card-qr-caption {
    font-size: 6px;
    margin-bottom: 2px;
  }

  /* VERSO desktop */
  .card-verso {
    padding: 20px 32px;
  }
  .card-verso-slogan {
    font-size: 18px;
    line-height: 1.5;
  }
  .card-verso-logo {
    gap: 16px;
  }
  .card-verso-logo-img {
    height: 80px;
  }
  .card-verso-fpp {
    font-size: 36px;
  }
  .card-verso-sub {
    font-size: 10px;
    margin-top: 2px;
  }
  .card-verso-cta {
    font-size: 18px;
  }
}
</style>
