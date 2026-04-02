import { ref, type Ref } from 'vue'
import api from '@/api'
import type { PaginatedResponse } from '@/types'
import type { AxiosError } from 'axios'

interface UseApiOptions {
  immediate?: boolean
}

export function useApiGet<T>(url: string, options: UseApiOptions = {}) {
  const data = ref<T | null>(null) as Ref<T | null>
  const loading = ref(false)
  const error = ref<string | null>(null)

  async function execute(params?: Record<string, unknown>) {
    loading.value = true
    error.value = null
    try {
      const response = await api.get<T>(url, { params })
      data.value = response.data
      return response.data
    } catch (err) {
      const axiosErr = err as AxiosError<{ detail?: string }>
      error.value = axiosErr.response?.data?.detail ?? 'Une erreur est survenue.'
      throw err
    } finally {
      loading.value = false
    }
  }

  if (options.immediate) {
    execute()
  }

  return { data, loading, error, execute }
}

export function usePaginatedApi<T>(baseUrl: string) {
  const data = ref<T[]>([]) as Ref<T[]>
  const loading = ref(false)
  const error = ref<string | null>(null)
  const totalCount = ref(0)
  const currentPage = ref(1)
  const hasNext = ref(false)
  const hasPrevious = ref(false)

  async function fetch(params?: Record<string, unknown>) {
    loading.value = true
    error.value = null
    try {
      const response = await api.get<PaginatedResponse<T>>(baseUrl, { params })
      data.value = response.data.results
      totalCount.value = response.data.count
      hasNext.value = !!response.data.next
      hasPrevious.value = !!response.data.previous
      return response.data
    } catch (err) {
      const axiosErr = err as AxiosError<{ detail?: string }>
      error.value = axiosErr.response?.data?.detail ?? 'Une erreur est survenue.'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function goToPage(page: number, extraParams?: Record<string, unknown>) {
    currentPage.value = page
    return fetch({ page, ...extraParams })
  }

  return {
    data,
    loading,
    error,
    totalCount,
    currentPage,
    hasNext,
    hasPrevious,
    fetch,
    goToPage,
  }
}
