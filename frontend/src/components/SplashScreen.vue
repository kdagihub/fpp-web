<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount } from 'vue'
import { Volume2, VolumeX } from 'lucide-vue-next'
import splashVideo from '@/assets/img/Cinematic_Pan_African_Movement_Logo_Animation.mp4'

const emit = defineEmits<{ done: [] }>()

const videoRef = ref<HTMLVideoElement | null>(null)
const phase = ref<'playing' | 'dissolving' | 'gone'>('playing')
const isMuted = ref(false)
const showSoundHint = ref(false)

const MAX_DURATION = 6000

let timeout: ReturnType<typeof setTimeout> | null = null

function dissolve() {
  if (phase.value !== 'playing') return
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

function toggleMute() {
  if (!videoRef.value) return
  videoRef.value.muted = !videoRef.value.muted
  isMuted.value = videoRef.value.muted
}

onMounted(async () => {
  timeout = setTimeout(dissolve, MAX_DURATION)
  const video = videoRef.value
  if (!video) return

  // Try with sound first
  video.muted = false
  try {
    await video.play()
    isMuted.value = false
  } catch {
    // Browser blocked audio autoplay — fallback to muted
    video.muted = true
    isMuted.value = true
    showSoundHint.value = true
    try {
      await video.play()
    } catch {
      dissolve()
    }
  }
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
      <div class="splash-video-wrapper">
        <video
          ref="videoRef"
          :src="splashVideo"
          playsinline
          preload="auto"
          class="splash-video"
          @ended="onVideoEnd"
        />
      </div>

      <div class="splash-bottom-fade" />
      <div class="splash-top-fade" />

      <!-- Sound toggle -->
      <button
        v-if="phase === 'playing'"
        @click="toggleMute"
        class="splash-sound-btn"
        :class="{ 'splash-sound-btn--hint': showSoundHint && isMuted }"
      >
        <VolumeX v-if="isMuted" :size="18" />
        <Volume2 v-else :size="18" />
        <span v-if="showSoundHint && isMuted" class="splash-sound-label">Activer le son</span>
      </button>
    </div>
  </Transition>
</template>

<style scoped>
.splash-overlay {
  position: fixed;
  inset: 0;
  z-index: 99999;
  background: #0a0a0a;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}

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
  background: linear-gradient(to top, #0a0a0a 0%, #0a0a0a 20%, transparent 100%);
}

.splash-top-fade {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 10%;
  pointer-events: none;
  background: linear-gradient(to bottom, #0a0a0a 0%, transparent 100%);
}

.splash-sound-btn {
  position: absolute;
  bottom: 24px;
  right: 24px;
  z-index: 10;
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 14px;
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.08);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  color: rgba(255, 255, 255, 0.7);
  font-size: 12px;
  font-weight: 600;
  letter-spacing: 0.03em;
  cursor: pointer;
  transition: all 200ms ease;
}

.splash-sound-btn:hover {
  background: rgba(255, 255, 255, 0.15);
  color: #fff;
  border-color: rgba(255, 255, 255, 0.35);
}

.splash-sound-btn--hint {
  animation: sound-pulse 2s ease-in-out infinite;
}

.splash-sound-label {
  white-space: nowrap;
}

@keyframes sound-pulse {
  0%, 100% { border-color: rgba(255, 255, 255, 0.2); }
  50% { border-color: rgba(255, 255, 255, 0.5); }
}

.splash--dissolving {
  animation: splash-dissolve 900ms cubic-bezier(0.4, 0, 0.2, 1) forwards;
}

@keyframes splash-dissolve {
  0% {
    opacity: 1;
    filter: blur(0) brightness(1);
    transform: scale(1);
  }
  50% {
    opacity: 0.7;
    filter: blur(4px) brightness(1.5);
    transform: scale(1.04);
  }
  100% {
    opacity: 0;
    filter: blur(20px) brightness(2);
    transform: scale(1.1);
  }
}

@media (prefers-reduced-motion: reduce) {
  .splash--dissolving {
    animation: splash-fade-simple 400ms ease-out forwards;
  }
  @keyframes splash-fade-simple {
    to { opacity: 0; }
  }
}
</style>
