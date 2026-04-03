import { ref } from 'vue'

export type ShareNetwork = 'facebook' | 'x' | 'whatsapp' | 'telegram' | 'copy'

interface ShareData {
  title: string
  description?: string
  url?: string
  ogUrl?: string
  image?: string
}

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api'

export function buildShareOgUrl(type: 'article' | 'event' | 'programme', slug: string): string {
  return `${API_BASE}/share/${type}/${slug}/`
}

export function useShare() {
  const showDialog = ref(false)
  const shareData = ref<ShareData>({ title: '' })
  const copied = ref(false)

  function openShare(data: ShareData) {
    shareData.value = {
      ...data,
      url: data.url ?? window.location.href,
    }
    showDialog.value = true
    copied.value = false
  }

  function closeShare() {
    showDialog.value = false
  }

  function shareOn(network: ShareNetwork) {
    const pageUrl = shareData.value.url ?? window.location.href
    const ogUrl = shareData.value.ogUrl ?? pageUrl
    const title = shareData.value.title
    const desc = shareData.value.description ?? ''
    const fullText = `*${title}*${desc ? '\n' + desc : ''}`

    if (network === 'copy') {
      navigator.clipboard.writeText(pageUrl)
      copied.value = true
      setTimeout(() => { copied.value = false }, 2500)
      return
    }

    let targetUrl = ''

    switch (network) {
      case 'whatsapp':
        targetUrl = `https://api.whatsapp.com/send?text=${encodeURIComponent(fullText + '\n\n' + ogUrl)}`
        break
      case 'facebook':
        targetUrl = `https://www.facebook.com/sharer.php?u=${encodeURIComponent(ogUrl)}`
        break
      case 'x':
        targetUrl = `https://twitter.com/intent/tweet?text=${encodeURIComponent(title)}&url=${encodeURIComponent(ogUrl)}`
        break
      case 'telegram':
        targetUrl = `https://t.me/share/url?url=${encodeURIComponent(ogUrl)}&text=${encodeURIComponent(fullText)}`
        break
    }

    window.open(targetUrl, '_blank')
  }

  return {
    showDialog,
    shareData,
    copied,
    openShare,
    closeShare,
    shareOn,
  }
}
