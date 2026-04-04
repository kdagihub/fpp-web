import axios from 'axios'
import type { AxiosError, InternalAxiosRequestConfig } from 'axios'

interface RetryableConfig extends InternalAxiosRequestConfig {
  _retry?: boolean
}

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL,
  withCredentials: true,
  headers: {
    'Content-Type': 'application/json',
  },
})

let isRefreshing = false
let failedQueue: Array<{
  resolve: (value?: unknown) => void
  reject: (reason?: unknown) => void
}> = []

function processQueue(error: AxiosError | null) {
  failedQueue.forEach((p) => {
    if (error) {
      p.reject(error)
    } else {
      p.resolve()
    }
  })
  failedQueue = []
}

api.interceptors.request.use((config) => {
  if (config.data instanceof FormData) {
    config.headers.delete('Content-Type')
  }
  return config
})

api.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config as RetryableConfig | undefined

    const skipRefreshUrls = ['/auth/token/refresh/', '/auth/login/', '/auth/me/']
    const shouldSkip = skipRefreshUrls.some((u) => originalRequest?.url?.includes(u))

    if (
      error.response?.status === 401 &&
      originalRequest &&
      !originalRequest._retry &&
      !shouldSkip
    ) {
      if (isRefreshing) {
        return new Promise((resolve, reject) => {
          failedQueue.push({ resolve, reject })
        }).then(() => api(originalRequest))
      }

      originalRequest._retry = true
      isRefreshing = true

      try {
        await api.post('/auth/token/refresh/')
        processQueue(null)
        return api(originalRequest)
      } catch (refreshError) {
        processQueue(refreshError as AxiosError)

        const { useAuthStore } = await import('@/stores/auth')
        const authStore = useAuthStore()
        authStore.handleSessionExpired()

        return Promise.reject(refreshError)
      } finally {
        isRefreshing = false
      }
    }

    return Promise.reject(error)
  },
)

export default api
