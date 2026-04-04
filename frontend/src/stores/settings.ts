import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '@/api'
import type { SiteSettings } from '@/types'

export const useSettingsStore = defineStore('settings', () => {
  const settings = ref<SiteSettings | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)
  let lastFetchedAt = 0

  async function fetchSettings(force = false) {
    const now = Date.now()
    const staleAfter = 5 * 60 * 1000 // 5 min
    if (!force && settings.value && now - lastFetchedAt < staleAfter) return

    loading.value = true
    error.value = null
    try {
      const { data } = await api.get<SiteSettings>('/public/settings/')
      settings.value = data
      lastFetchedAt = now
    } catch {
      error.value = 'Impossible de charger les paramètres du site.'
    } finally {
      loading.value = false
    }
  }

  async function fetchAdminSettings() {
    loading.value = true
    error.value = null
    try {
      const { data } = await api.get<SiteSettings>('/admin/settings/')
      settings.value = data
      lastFetchedAt = Date.now()
    } catch {
      error.value = 'Impossible de charger les paramètres.'
    } finally {
      loading.value = false
    }
  }

  async function updateSettings(payload: Partial<SiteSettings>) {
    const { data } = await api.patch<SiteSettings>('/admin/settings/', payload)
    settings.value = data
    lastFetchedAt = Date.now()
    return data
  }

  async function updateSettingsWithFiles(payload: FormData) {
    const { data } = await api.patch<SiteSettings>('/admin/settings/', payload, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
    settings.value = data
    lastFetchedAt = Date.now()
    return data
  }

  return {
    settings,
    loading,
    error,
    fetchSettings,
    fetchAdminSettings,
    updateSettings,
    updateSettingsWithFiles,
  }
})
