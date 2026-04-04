<script setup lang="ts">
import { ref, onMounted, computed, watch } from 'vue'
import { useRoute } from 'vue-router'
import Toast from 'primevue/toast'
import SplashScreen from '@/components/SplashScreen.vue'
import WelcomeModal from '@/components/WelcomeModal.vue'

const route = useRoute()

const SPLASH_KEY = 'fpp_splash_seen'
const SKIP_SPLASH_ROUTES = new Set(['cgu', 'privacy-policy'])

const isLegalPage = computed(() => SKIP_SPLASH_ROUTES.has(route.name as string))

const showSplash = ref(false)
const showWelcome = ref(false)
const appReady = ref(false)

watch(isLegalPage, (legal) => {
  if (legal && !appReady.value) {
    showSplash.value = false
    appReady.value = true
  }
})

onMounted(() => {
  if (isLegalPage.value || sessionStorage.getItem(SPLASH_KEY)) {
    appReady.value = true
  } else {
    showSplash.value = true
  }
})

function onSplashDone() {
  showSplash.value = false
  appReady.value = true
  sessionStorage.setItem(SPLASH_KEY, '1')
  if (!isLegalPage.value) {
    showWelcome.value = true
  }
}

function onWelcomeClose() {
  showWelcome.value = false
}
</script>

<template>
  <SplashScreen v-if="showSplash && !isLegalPage" @done="onSplashDone" />

  <template v-if="appReady">
    <Toast position="top-right" />
    <RouterView />
    <WelcomeModal v-if="showWelcome && !isLegalPage" @close="onWelcomeClose" />
  </template>
</template>
