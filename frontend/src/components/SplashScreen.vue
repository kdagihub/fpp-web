<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount } from 'vue'
import logoFpp from '@/assets/img/fpplogsf.png'
import splash0 from '@/assets/img/Cinematic_Pan_African_Movement_Logo_Animation.mp4'
import splash1 from '@/assets/img/splash2.mp4'
import splash2 from '@/assets/img/splash3.mp4'

const SPLASH_VIDEOS = [splash0, splash1, splash2] as const
const STORAGE_KEY = 'fpp_splash_idx'

function pickVideo(): string {
  const stored = sessionStorage.getItem(STORAGE_KEY)
  if (stored !== null) {
    const idx = Number(stored)
    if (idx >= 0 && idx < SPLASH_VIDEOS.length) return SPLASH_VIDEOS[idx]!
  }
  const lastIdx = Number(localStorage.getItem(STORAGE_KEY) ?? -1)
  let idx: number
  do { idx = Math.floor(Math.random() * SPLASH_VIDEOS.length) } while (idx === lastIdx && SPLASH_VIDEOS.length > 1)
  sessionStorage.setItem(STORAGE_KEY, String(idx))
  localStorage.setItem(STORAGE_KEY, String(idx))
  return SPLASH_VIDEOS[idx]!
}

const splashVideo = pickVideo()

const emit = defineEmits<{ done: [] }>()

const videoRef = ref<HTMLVideoElement | null>(null)
const phase = ref<'gate' | 'playing' | 'dissolving' | 'gone'>('gate')
const gateReady = ref(false)

const MAX_DURATION = 6000

let timeout: ReturnType<typeof setTimeout> | null = null

function dissolve() {
  if (phase.value === 'dissolving' || phase.value === 'gone') return
  phase.value = 'dissolving'
  setTimeout(() => {
    phase.value = 'gone'
    emit('done')
  }, 900)
}

function onVideoEnd() {
  if (timeout) clearTimeout(timeout)
  dissolve()
}

async function enterSite() {
  if (phase.value !== 'gate') return
  phase.value = 'playing'

  timeout = setTimeout(dissolve, MAX_DURATION)

  const video = videoRef.value
  if (!video) { dissolve(); return }

  video.muted = false
  try {
    await video.play()
  } catch {
    video.muted = true
    try { await video.play() } catch { dissolve() }
  }
}

onMounted(() => {
  requestAnimationFrame(() => { gateReady.value = true })
})

onBeforeUnmount(() => {
  if (timeout) clearTimeout(timeout)
})
</script>

<template>
  <Transition name="splash-exit">
    <div
      v-if="phase !== 'gone'"
      class="splash-overlay"
      :class="{ 'splash--dissolving': phase === 'dissolving' }"
    >
      <!-- ═══ Phase 1 : Gate — écran d'accueil cliquable ═══ -->
      <Transition name="gate-fade">
        <div
          v-if="phase === 'gate'"
          class="gate"
          @click="enterSite"
        >
          <div class="gate-bg">
            <div class="gate-radial" />
            <div class="gate-lines" />
          </div>

          <div class="gate-content" :class="{ 'gate-content--ready': gateReady }">
            <!-- Rings -->
            <div class="gate-rings">
              <div class="gate-ring gate-ring--outer" />
              <div class="gate-ring gate-ring--inner" />
            </div>

            <!-- Logo -->
            <div class="gate-logo-wrap">
              <img :src="logoFpp" alt="FPP" class="gate-logo" />
            </div>

            <!-- Text -->
            <div class="gate-text">
              <div class="gate-party">Front Patriotique Panafricain</div>
              <div class="gate-divider" />
              <div class="gate-motto">Allons o&ugrave; on va&nbsp;!</div>
              <div class="gate-slogan">Souverainet&eacute; &bull; Unit&eacute; &bull; Dignit&eacute;</div>
            </div>

            <!-- CTA -->
            <button class="gate-cta" @click.stop="enterSite">
              <span class="gate-cta-text">Entrer sur le site</span>
              <span class="gate-cta-icon">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14"/><path d="m12 5 7 7-7 7"/></svg>
              </span>
              <span class="gate-cta-glow" />
            </button>
          </div>

          <div class="gate-footer">
            <span class="gate-footer-icon">&#9679;</span>
            Appuyez n'importe o&ugrave; pour continuer
          </div>
        </div>
      </Transition>

      <!-- ═══ Phase 2 : Video ═══ -->
      <div v-show="phase === 'playing' || phase === 'dissolving'" class="splash-video-wrapper">
        <video
          ref="videoRef"
          :src="splashVideo"
          playsinline
          preload="auto"
          class="splash-video"
          @ended="onVideoEnd"
        />
      </div>

      <div v-if="phase === 'playing' || phase === 'dissolving'" class="splash-bottom-fade" />
      <div v-if="phase === 'playing' || phase === 'dissolving'" class="splash-top-fade" />
    </div>
  </Transition>
</template>

<style scoped>
/* ────────── Overlay ────────── */
.splash-overlay {
  position: fixed;
  inset: 0;
  z-index: 99999;
  background: #060606;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}

/* ────────── Gate ────────── */
.gate {
  position: absolute;
  inset: 0;
  z-index: 2;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  -webkit-tap-highlight-color: transparent;
}

.gate-bg {
  position: absolute;
  inset: 0;
  overflow: hidden;
}

.gate-radial {
  position: absolute;
  top: 50%;
  left: 50%;
  width: 1000px;
  height: 1000px;
  transform: translate(-50%, -55%);
  border-radius: 50%;
  background: radial-gradient(circle, rgba(0, 166, 81, 0.08) 0%, rgba(0, 166, 81, 0.02) 40%, transparent 70%);
  animation: gate-glow 4s ease-in-out infinite alternate;
}

.gate-lines {
  position: absolute;
  inset: 0;
  background-image:
    linear-gradient(0deg, transparent 49.5%, rgba(255,255,255,0.015) 49.5%, rgba(255,255,255,0.015) 50.5%, transparent 50.5%);
  background-size: 100% 4px;
  animation: gate-scan 8s linear infinite;
}

/* ── Gate content ── */
.gate-content {
  position: relative;
  z-index: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 32px;
  opacity: 0;
  transform: translateY(20px);
  transition: opacity 1s cubic-bezier(0.16, 1, 0.3, 1), transform 1s cubic-bezier(0.16, 1, 0.3, 1);
}

.gate-content--ready {
  opacity: 1;
  transform: translateY(0);
}

/* ── Rings ── */
.gate-rings {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -60%);
  pointer-events: none;
}

.gate-ring {
  position: absolute;
  border-radius: 50%;
  border: 1px solid rgba(0, 166, 81, 0.15);
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
}

.gate-ring--outer {
  width: 320px;
  height: 320px;
  animation: ring-breathe 3s ease-in-out infinite;
}

.gate-ring--inner {
  width: 250px;
  height: 250px;
  border-color: rgba(0, 166, 81, 0.25);
  animation: ring-breathe 3s ease-in-out infinite 1.5s;
}

/* ── Logo ── */
.gate-logo-wrap {
  width: 170px;
  height: 170px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: radial-gradient(circle, rgba(0, 166, 81, 0.12) 0%, transparent 70%);
  animation: logo-float 5s ease-in-out infinite;
}

.gate-logo {
  width: 140px;
  height: 140px;
  object-fit: contain;
  filter: drop-shadow(0 0 40px rgba(0, 166, 81, 0.35));
}

/* ── Text ── */
.gate-text {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
}

.gate-party {
  font-family: 'Inter', system-ui, sans-serif;
  font-size: 16px;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.85);
  letter-spacing: 5px;
  text-transform: uppercase;
  text-align: center;
}

.gate-divider {
  width: 64px;
  height: 2px;
  background: linear-gradient(90deg, transparent, #00A651, transparent);
  border-radius: 1px;
}

.gate-motto {
  font-family: 'Georgia', 'Times New Roman', serif;
  font-size: 22px;
  font-style: italic;
  font-weight: 400;
  color: #00A651;
  letter-spacing: 1.5px;
  opacity: 0.9;
}

.gate-slogan {
  font-family: 'Inter', system-ui, sans-serif;
  font-size: 12px;
  font-weight: 400;
  color: rgba(255, 255, 255, 0.4);
  letter-spacing: 3px;
  text-transform: uppercase;
}

/* ── CTA Button ── */
.gate-cta {
  position: relative;
  display: flex;
  align-items: center;
  gap: 10px;
  margin-top: 16px;
  padding: 16px 44px;
  border: 1px solid rgba(0, 166, 81, 0.35);
  border-radius: 999px;
  background: rgba(0, 166, 81, 0.08);
  color: #00A651;
  font-family: 'Inter', system-ui, sans-serif;
  font-size: 14px;
  font-weight: 600;
  letter-spacing: 1.5px;
  text-transform: uppercase;
  cursor: pointer;
  overflow: hidden;
  transition: all 300ms cubic-bezier(0.16, 1, 0.3, 1);
}

.gate-cta:hover {
  background: rgba(0, 166, 81, 0.15);
  border-color: rgba(0, 166, 81, 0.6);
  transform: scale(1.04);
  box-shadow: 0 0 40px rgba(0, 166, 81, 0.15);
}

.gate-cta:active {
  transform: scale(0.97);
}

.gate-cta-icon {
  display: flex;
  transition: transform 300ms ease;
}

.gate-cta:hover .gate-cta-icon {
  transform: translateX(3px);
}

.gate-cta-glow {
  position: absolute;
  inset: -1px;
  border-radius: inherit;
  background: linear-gradient(90deg, transparent 0%, rgba(0, 166, 81, 0.15) 50%, transparent 100%);
  animation: cta-shimmer 3s ease-in-out infinite;
  pointer-events: none;
}

.gate-cta-text {
  position: relative;
  z-index: 1;
}

/* ── Footer hint ── */
.gate-footer {
  position: absolute;
  bottom: 32px;
  left: 0;
  right: 0;
  text-align: center;
  font-family: 'Inter', system-ui, sans-serif;
  font-size: 11px;
  font-weight: 400;
  color: rgba(255, 255, 255, 0.2);
  letter-spacing: 0.5px;
  animation: footer-pulse 3s ease-in-out infinite;
}

.gate-footer-icon {
  color: rgba(0, 166, 81, 0.5);
  font-size: 6px;
  vertical-align: middle;
  margin-right: 6px;
}

/* ── Gate transition ── */
.gate-fade-leave-active {
  transition: opacity 500ms ease, transform 500ms cubic-bezier(0.16, 1, 0.3, 1);
}

.gate-fade-leave-to {
  opacity: 0;
  transform: scale(1.08);
}

/* ────────── Video ────────── */
.splash-video-wrapper {
  position: relative;
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}

.splash-video {
  width: 100%;
  height: 100%;
  object-fit: contain;
  object-position: center center;
}

.splash-bottom-fade {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 20%;
  pointer-events: none;
  background: linear-gradient(to top, #060606 0%, #060606 20%, transparent 100%);
}

.splash-top-fade {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 10%;
  pointer-events: none;
  background: linear-gradient(to bottom, #060606 0%, transparent 100%);
}

/* ────────── Dissolve ────────── */
.splash--dissolving {
  animation: splash-dissolve 900ms cubic-bezier(0.4, 0, 0.2, 1) forwards;
}

@keyframes splash-dissolve {
  0% { opacity: 1; filter: blur(0) brightness(1); transform: scale(1); }
  50% { opacity: 0.7; filter: blur(4px) brightness(1.5); transform: scale(1.04); }
  100% { opacity: 0; filter: blur(20px) brightness(2); transform: scale(1.1); }
}

/* ────────── Animations ────────── */
@keyframes gate-glow {
  0% { opacity: 0.6; transform: translate(-50%, -55%) scale(1); }
  100% { opacity: 1; transform: translate(-50%, -55%) scale(1.15); }
}

@keyframes gate-scan {
  0% { background-position: 0 0; }
  100% { background-position: 0 400px; }
}

@keyframes ring-breathe {
  0%, 100% { opacity: 0.3; transform: translate(-50%, -50%) scale(1); }
  50% { opacity: 0.7; transform: translate(-50%, -50%) scale(1.06); }
}

@keyframes logo-float {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-6px); }
}

@keyframes cta-shimmer {
  0%, 100% { transform: translateX(-100%); }
  50% { transform: translateX(100%); }
}

@keyframes footer-pulse {
  0%, 100% { opacity: 0.5; }
  50% { opacity: 1; }
}

/* ────────── Reduced motion ────────── */
@media (prefers-reduced-motion: reduce) {
  .gate-radial, .gate-ring, .gate-logo-wrap, .gate-cta-glow, .gate-lines { animation: none; }
  .gate-footer { animation: none; opacity: 0.7; }
  .splash--dissolving {
    animation: splash-fade-simple 400ms ease-out forwards;
  }
  @keyframes splash-fade-simple {
    to { opacity: 0; }
  }
}

/* ────────── Mobile ────────── */
@media (max-width: 480px) {
  .gate-party { font-size: 12px; letter-spacing: 3px; }
  .gate-motto { font-size: 17px; }
  .gate-slogan { font-size: 10px; letter-spacing: 2px; }
  .gate-logo-wrap { width: 130px; height: 130px; }
  .gate-logo { width: 105px; height: 105px; }
  .gate-ring--outer { width: 240px; height: 240px; }
  .gate-ring--inner { width: 190px; height: 190px; }
  .gate-cta { padding: 14px 34px; font-size: 12px; }
  .gate-footer { bottom: 20px; font-size: 10px; }
}
</style>
