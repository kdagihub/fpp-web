const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api'
const BACKEND_ORIGIN = API_BASE.replace(/\/api\/?$/, '')

/**
 * Résout une URL de média retournée par l'API vers une URL accessible par le navigateur.
 * Gère les cas : chemins relatifs (/media/...), URLs Docker internes, production.
 */
export function getMediaUrl(url: string | null | undefined): string {
  if (!url) return ''

  if (url.includes('host.docker.internal')) {
    const isDev = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
    if (isDev) {
      return url.replace(/http:\/\/host\.docker\.internal:\d+/, 'http://localhost:8000')
    }
    return url.replace(/http:\/\/host\.docker\.internal:\d+/, BACKEND_ORIGIN)
  }

  if (url.includes('backend:8000')) {
    return url.replace('http://backend:8000', BACKEND_ORIGIN)
  }

  if (url.startsWith('/media/') || url.startsWith('/static/')) {
    return `${BACKEND_ORIGIN}${url}`
  }

  if (url.startsWith('http://') || url.startsWith('https://')) {
    return url
  }

  return `${BACKEND_ORIGIN}/${url}`
}
