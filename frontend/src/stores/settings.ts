import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '@/api'
import type { SiteSettings } from '@/types'

export const useSettingsStore = defineStore('settings', () => {
  const settings = ref<SiteSettings | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)

  async function fetchSettings() {
    if (settings.value) return

    loading.value = true
    error.value = null
    try {
      const { data } = await api.get<SiteSettings>('/public/settings/')
      settings.value = data
    } catch {
      error.value = 'Impossible de charger les paramètres du site.'
    } finally {
      loading.value = false
    }
  }

  async function updateSettings(payload: Partial<SiteSettings>) {
    const { data } = await api.patch<SiteSettings>('/admin/settings/', payload)
    settings.value = data
    return data
  }

  return {
    settings,
    loading,
    error,
    fetchSettings,
    updateSettings,
  }
})
