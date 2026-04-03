<script setup lang="ts">
import { ref, onMounted } from 'vue'
import Toast from 'primevue/toast'
import SplashScreen from '@/components/SplashScreen.vue'
import WelcomeModal from '@/components/WelcomeModal.vue'

const SPLASH_KEY = 'fpp_splash_seen'

const showSplash = ref(false)
const showWelcome = ref(false)
const appReady = ref(false)

onMounted(() => {
  if (!sessionStorage.getItem(SPLASH_KEY)) {
    showSplash.value = true
  } else {
    appReady.value = true
  }
})

function onSplashDone() {
  showSplash.value = false
  appReady.value = true
  sessionStorage.setItem(SPLASH_KEY, '1')
  showWelcome.value = true
}

function onWelcomeClose() {
  showWelcome.value = false
}
</script>

<template>
  <SplashScreen v-if="showSplash" @done="onSplashDone" />

  <template v-if="appReady">
    <Toast position="top-right" />
    <RouterView />
    <WelcomeModal v-if="showWelcome" @close="onWelcomeClose" />
  </template>
</template>
