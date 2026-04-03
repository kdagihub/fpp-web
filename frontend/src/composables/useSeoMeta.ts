import { watchEffect, onUnmounted, type Ref, isRef } from 'vue'

interface SeoMetaOptions {
  title: string | Ref<string>
  description: string | Ref<string>
  image?: string | Ref<string | undefined | null>
  url?: string | Ref<string>
  type?: 'website' | 'article'
  siteName?: string
}

function resolve<T>(val: T | Ref<T>): T {
  return isRef(val) ? val.value : val
}

function setMeta(property: string, content: string, attr = 'property') {
  let el = document.querySelector(`meta[${attr}="${property}"]`) as HTMLMetaElement | null
  if (!el) {
    el = document.createElement('meta')
    el.setAttribute(attr, property)
    document.head.appendChild(el)
  }
  el.setAttribute('content', content)
}

export function useSeoMeta(options: SeoMetaOptions) {
  const originalTitle = document.title

  const stop = watchEffect(() => {
    const title = resolve(options.title)
    const description = resolve(options.description)
    const image = resolve(options.image) ?? ''
    const url = resolve(options.url) ?? window.location.href
    const type = options.type ?? 'website'
    const siteName = options.siteName ?? 'FPP — Front Patriotique Panafricain'

    document.title = `${title} — FPP`

    setMeta('description', description, 'name')

    setMeta('og:title', title)
    setMeta('og:description', description)
    setMeta('og:type', type)
    setMeta('og:url', url)
    setMeta('og:site_name', siteName)
    if (image) setMeta('og:image', image)

    setMeta('twitter:card', image ? 'summary_large_image' : 'summary', 'name')
    setMeta('twitter:title', title, 'name')
    setMeta('twitter:description', description, 'name')
    if (image) setMeta('twitter:image', image, 'name')
  })

  onUnmounted(() => {
    stop()
    document.title = originalTitle
  })
}
