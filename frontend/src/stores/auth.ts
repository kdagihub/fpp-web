import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '@/api'
import type { User, LoginPayload, RegisterPayload } from '@/types'
import router from '@/router'

export const useAuthStore = defineStore('auth', () => {
  const user = ref<User | null>(null)
  const loading = ref(false)
  const initialized = ref(false)

  const isAuthenticated = computed(() => !!user.value)
  const isAdmin = computed(() => !!user.value?.is_staff)
  const fullName = computed(() =>
    user.value ? `${user.value.first_name} ${user.value.last_name}` : '',
  )
  const permissions = computed(() => user.value?.permissions ?? [])

  function hasPermission(perm: string): boolean {
    if (user.value?.is_staff) return true
    return permissions.value.includes(perm)
  }

  async function fetchUser() {
    try {
      const { data } = await api.get<User>('/auth/me/')
      user.value = data
    } catch {
      user.value = null
    }
  }

  async function init() {
    if (initialized.value) return
    loading.value = true
    try {
      await fetchUser()
    } finally {
      loading.value = false
      initialized.value = true
    }
  }

  async function login(payload: LoginPayload) {
    const { data } = await api.post('/auth/login/', payload)
    await fetchUser()
    return data
  }

  async function register(payload: RegisterPayload) {
    const { data } = await api.post('/auth/register/', payload)
    return data
  }

  async function logout() {
    try {
      await api.post('/auth/logout/')
    } finally {
      user.value = null
      router.push('/login')
    }
  }

  function handleSessionExpired() {
    user.value = null
    router.push({ path: '/login', query: { expired: '1' } })
  }

  async function changePassword(oldPassword: string, newPassword: string, newPasswordConfirm: string) {
    const res = await api.post('/auth/password/change/', {
      old_password: oldPassword,
      new_password: newPassword,
      new_password_confirm: newPasswordConfirm,
    })
    user.value = null
    return res
  }

  return {
    user,
    loading,
    initialized,
    isAuthenticated,
    isAdmin,
    fullName,
    permissions,
    hasPermission,
    fetchUser,
    init,
    login,
    register,
    logout,
    handleSessionExpired,
    changePassword,
  }
})
