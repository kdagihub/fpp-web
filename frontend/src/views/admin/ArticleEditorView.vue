<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useAppToast } from '@/composables/useToast'
import api from '@/api'
import { getMediaUrl } from '@/utils/media'
import type { AdminArticleDetail, AdminCategory } from '@/types'

import { useShare, buildShareOgUrl } from '@/composables/useShare'
import ShareDialog from '@/components/ShareDialog.vue'

import { useEditor, EditorContent } from '@tiptap/vue-3'
import StarterKit from '@tiptap/starter-kit'
import Link from '@tiptap/extension-link'
import Image from '@tiptap/extension-image'
import Placeholder from '@tiptap/extension-placeholder'
import Underline from '@tiptap/extension-underline'
import TextAlign from '@tiptap/extension-text-align'

import {
  ArrowLeft,
  Save,
  Send,
  Loader2,
  ImagePlus,
  X,
  Bold,
  Italic,
  Underline as UnderlineIcon,
  Strikethrough,
  Heading2,
  Heading3,
  List,
  ListOrdered,
  Quote,
  Code,
  Link as LinkIcon,
  Image as ImageIcon,
  Minus,
  Undo2,
  Redo2,
  AlignLeft,
  AlignCenter,
  AlignRight,
  Eye,
  Trash2,
  Share2,
} from 'lucide-vue-next'

const props = defineProps<{ id?: string }>()

const router = useRouter()
const toast = useAppToast()
const isEditing = computed(() => !!props.id)

/* ── State ── */
const loading = ref(false)
const saving = ref(false)
const categories = ref<AdminCategory[]>([])
const article = ref<AdminArticleDetail | null>(null)

const form = ref({
  title: '',
  summary: '',
  content: '',
  category: '' as string | null,
  status: 'draft' as 'draft' | 'published' | 'archived',
  is_featured: false,
})

const coverFile = ref<File | null>(null)
const coverPreview = ref<string | null>(null)
const existingCover = ref<string | null>(null)
const removeCover = ref(false)

/* ── TipTap Editor ── */
const editor = useEditor({
  extensions: [
    StarterKit.configure({
      heading: { levels: [2, 3, 4] },
    }),
    Link.configure({
      openOnClick: false,
      HTMLAttributes: { class: 'text-[var(--color-accent)] underline' },
    }),
    Image.configure({
      inline: false,
      HTMLAttributes: { class: 'rounded-lg max-w-full' },
    }),
    Placeholder.configure({
      placeholder: 'Rédigez le contenu de votre article ici...',
    }),
    Underline,
    TextAlign.configure({
      types: ['heading', 'paragraph'],
    }),
  ],
  editorProps: {
    attributes: {
      class: 'prose prose-sm sm:prose max-w-none focus:outline-none min-h-[20rem] p-4 sm:p-5',
    },
  },
  onUpdate: ({ editor: e }) => {
    form.value.content = e.getHTML()
  },
})

/* ── Load data ── */
async function loadArticle() {
  if (!props.id) return
  loading.value = true
  try {
    const { data } = await api.get<AdminArticleDetail>(`/admin/articles/${props.id}/`)
    article.value = data
    form.value = {
      title: data.title,
      summary: data.summary,
      content: data.content,
      category: data.category,
      status: data.status,
      is_featured: data.is_featured,
    }
    existingCover.value = data.cover_image
    editor.value?.commands.setContent(data.content || '')
  } catch {
    toast.error('Erreur', 'Article introuvable.')
    router.push('/admin/articles')
  } finally {
    loading.value = false
  }
}

async function loadCategories() {
  try {
    const { data } = await api.get<AdminCategory[]>('/admin/categories/')
    categories.value = data
  } catch { /* silent */ }
}

onMounted(() => {
  loadCategories()
  if (props.id) loadArticle()
})

/* ── Cover image ── */
function onCoverChange(e: Event) {
  const file = (e.target as HTMLInputElement).files?.[0]
  if (!file) return
  const allowed = ['image/jpeg', 'image/png', 'image/webp']
  if (!allowed.includes(file.type)) {
    toast.error('Format invalide', 'Seuls JPG, PNG et WebP sont acceptés.')
    return
  }
  if (file.size > 5 * 1024 * 1024) {
    toast.error('Fichier trop volumineux', 'La taille maximale est de 5 Mo.')
    return
  }
  coverFile.value = file
  coverPreview.value = URL.createObjectURL(file)
  removeCover.value = false
}

function clearCover() {
  if (coverPreview.value) URL.revokeObjectURL(coverPreview.value)
  coverFile.value = null
  coverPreview.value = null
  if (existingCover.value) removeCover.value = true
}

onUnmounted(() => {
  if (coverPreview.value) URL.revokeObjectURL(coverPreview.value)
  editor.value?.destroy()
})

/* ── Save ── */
async function save(publishNow = false) {
  if (!form.value.title.trim()) {
    toast.error('Titre requis', 'Veuillez saisir un titre pour l\'article.')
    return
  }
  if (!form.value.summary.trim()) {
    toast.error('Résumé requis', 'Veuillez saisir un résumé.')
    return
  }

  saving.value = true
  const status = publishNow ? 'published' : form.value.status

  try {
    const fd = new FormData()
    fd.append('title', form.value.title)
    fd.append('summary', form.value.summary)
    fd.append('content', form.value.content)
    fd.append('status', status)
    fd.append('is_featured', String(form.value.is_featured))
    if (form.value.category) fd.append('category', form.value.category)

    if (coverFile.value) {
      fd.append('cover_image', coverFile.value)
    } else if (removeCover.value) {
      fd.append('cover_image', '')
    }

    let result: AdminArticleDetail

    if (isEditing.value) {
      const { data } = await api.patch<AdminArticleDetail>(
        `/admin/articles/${props.id}/`,
        fd,
        { headers: { 'Content-Type': 'multipart/form-data' } },
      )
      result = data
      toast.success('Enregistré', publishNow ? 'Article publié avec succès.' : 'Modifications enregistrées.')
    } else {
      const { data } = await api.post<AdminArticleDetail>(
        '/admin/articles/create/',
        fd,
        { headers: { 'Content-Type': 'multipart/form-data' } },
      )
      result = data
      toast.success('Créé', publishNow ? 'Article créé et publié.' : 'Article créé en brouillon.')
      router.replace(`/admin/articles/${result.id}/edit`)
    }

    article.value = result
    form.value.status = result.status
    existingCover.value = result.cover_image
    coverFile.value = null
    if (coverPreview.value) {
      URL.revokeObjectURL(coverPreview.value)
      coverPreview.value = null
    }
    removeCover.value = false
  } catch (err: any) {
    const detail = err?.response?.data?.detail
      || err?.response?.data?.is_featured?.[0]
      || err?.response?.data?.cover_image?.[0]
      || 'Une erreur est survenue.'
    toast.error('Erreur', detail)
  } finally {
    saving.value = false
  }
}

/* ── TipTap toolbar actions ── */
function setLink() {
  const prev = editor.value?.getAttributes('link').href || ''
  const url = window.prompt('URL du lien :', prev)
  if (url === null) return
  if (url === '') {
    editor.value?.chain().focus().extendMarkRange('link').unsetLink().run()
  } else {
    editor.value?.chain().focus().extendMarkRange('link').setLink({ href: url }).run()
  }
}

function addImage() {
  const url = window.prompt('URL de l\'image :')
  if (url) {
    editor.value?.chain().focus().setImage({ src: url }).run()
  }
}

const displayCover = computed(() => {
  if (coverPreview.value) return coverPreview.value
  if (existingCover.value && !removeCover.value) return getMediaUrl(existingCover.value)
  return null
})

/* ── Share ── */
const { showDialog: shareOpen, shareData, copied, openShare, closeShare, shareOn } = useShare()

function openShareDialog() {
  if (!article.value) return
  const publicUrl = `${window.location.origin}/actualites/${article.value.slug}`
  openShare({
    title: article.value.title,
    description: article.value.summary,
    url: publicUrl,
    ogUrl: buildShareOgUrl('article', article.value.slug),
    image: article.value.cover_image ? getMediaUrl(article.value.cover_image) : undefined,
  })
}
</script>

<template>
  <div class="max-w-5xl">
    <!-- Header -->
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-5 sm:mb-6">
      <div class="flex items-center gap-3">
        <button
          @click="router.push('/admin/articles')"
          class="p-2 rounded-lg hover:bg-gray-100 text-gray-500 hover:text-gray-700 transition-colors cursor-pointer bg-transparent border-none shrink-0"
        >
          <ArrowLeft :size="18" />
        </button>
        <div>
          <h2 class="font-heading text-lg sm:text-xl font-bold text-[var(--color-primary)]">
            {{ isEditing ? 'Modifier l\'article' : 'Nouvel article' }}
          </h2>
          <p v-if="article" class="text-[11px] text-gray-400 mt-0.5">
            Slug : {{ article.slug }}
          </p>
        </div>
      </div>

      <div class="flex items-center gap-2 self-end sm:self-auto">
        <button
          @click="save(false)"
          :disabled="saving"
          class="inline-flex items-center gap-2 px-4 py-2.5 text-sm font-semibold rounded-lg border border-gray-200 bg-white text-gray-700 hover:bg-gray-50 transition-colors cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <Loader2 v-if="saving" :size="14" class="animate-spin" />
          <Save v-else :size="14" />
          <span class="hidden sm:inline">Enregistrer</span>
        </button>
        <button
          v-if="form.status !== 'published'"
          @click="save(true)"
          :disabled="saving"
          class="inline-flex items-center gap-2 px-4 py-2.5 text-sm font-semibold text-white bg-[var(--color-accent)] rounded-lg hover:bg-[var(--color-accent-hover)] transition-colors cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <Send :size="14" />
          <span class="hidden sm:inline">Publier</span>
        </button>
        <a
          v-if="article?.status === 'published'"
          :href="`/actualites/${article.slug}`"
          target="_blank"
          class="inline-flex items-center gap-2 px-3 py-2.5 text-sm font-medium rounded-lg border border-gray-200 text-gray-500 hover:text-green-600 hover:border-green-200 transition-all no-underline"
          title="Voir sur le site"
        >
          <Eye :size="14" />
        </a>
        <button
          v-if="article?.status === 'published'"
          @click="openShareDialog"
          class="inline-flex items-center gap-2 px-3 py-2.5 text-sm font-medium rounded-lg border border-gray-200 text-gray-500 hover:text-indigo-600 hover:border-indigo-200 transition-all cursor-pointer bg-transparent"
          title="Partager"
        >
          <Share2 :size="14" />
        </button>
      </div>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="space-y-4 animate-pulse">
      <div class="h-12 bg-gray-100 rounded-lg w-full" />
      <div class="h-10 bg-gray-100 rounded-lg w-full" />
      <div class="h-64 bg-gray-100 rounded-lg w-full" />
    </div>

    <template v-else>
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-4 sm:gap-6">
        <!-- ═══ Main content (2/3) ═══ -->
        <div class="lg:col-span-2 space-y-4">
          <!-- Title -->
          <div class="bg-white rounded-xl border border-gray-200 p-4 sm:p-5">
            <input
              v-model="form.title"
              type="text"
              placeholder="Titre de l'article"
              class="w-full text-xl sm:text-2xl font-heading font-bold text-gray-900 placeholder:text-gray-300 outline-none bg-transparent border-none p-0"
            />
          </div>

          <!-- Summary -->
          <div class="bg-white rounded-xl border border-gray-200 p-4 sm:p-5">
            <label class="block text-[11px] font-semibold text-gray-400 uppercase tracking-wide mb-2">Résumé</label>
            <textarea
              v-model="form.summary"
              rows="2"
              maxlength="500"
              placeholder="Résumé court de l'article (affiché dans les listes)..."
              class="w-full text-sm text-gray-700 placeholder:text-gray-400 outline-none bg-transparent border-none p-0 resize-none leading-relaxed"
            />
            <p class="text-[10px] text-gray-300 text-right mt-1">{{ form.summary.length }}/500</p>
          </div>

          <!-- TipTap Editor -->
          <div class="bg-white rounded-xl border border-gray-200 overflow-hidden">
            <label class="block text-[11px] font-semibold text-gray-400 uppercase tracking-wide px-4 sm:px-5 pt-4 sm:pt-5 mb-2">Contenu</label>

            <!-- Toolbar -->
            <div v-if="editor" class="border-b border-gray-200 px-2 sm:px-3 py-2 flex flex-wrap items-center gap-0.5">
              <button
                @click="editor.chain().focus().toggleBold().run()"
                :class="{ 'bg-gray-200 text-gray-900': editor.isActive('bold') }"
                class="p-2 rounded-lg text-gray-500 hover:bg-gray-100 hover:text-gray-700 transition-colors cursor-pointer bg-transparent border-none"
                title="Gras"
              >
                <Bold :size="15" />
              </button>
              <button
                @click="editor.chain().focus().toggleItalic().run()"
                :class="{ 'bg-gray-200 text-gray-900': editor.isActive('italic') }"
                class="p-2 rounded-lg text-gray-500 hover:bg-gray-100 hover:text-gray-700 transition-colors cursor-pointer bg-transparent border-none"
                title="Italique"
              >
                <Italic :size="15" />
              </button>
              <button
                @click="editor.chain().focus().toggleUnderline().run()"
                :class="{ 'bg-gray-200 text-gray-900': editor.isActive('underline') }"
                class="p-2 rounded-lg text-gray-500 hover:bg-gray-100 hover:text-gray-700 transition-colors cursor-pointer bg-transparent border-none"
                title="Souligné"
              >
                <UnderlineIcon :size="15" />
              </button>
              <button
                @click="editor.chain().focus().toggleStrike().run()"
                :class="{ 'bg-gray-200 text-gray-900': editor.isActive('strike') }"
                class="p-2 rounded-lg text-gray-500 hover:bg-gray-100 hover:text-gray-700 transition-colors cursor-pointer bg-transparent border-none"
                title="Barré"
              >
                <Strikethrough :size="15" />
              </button>

              <div class="w-px h-5 bg-gray-200 mx-1" />

              <button
                @click="editor.chain().focus().toggleHeading({ level: 2 }).run()"
                :class="{ 'bg-gray-200 text-gray-900': editor.isActive('heading', { level: 2 }) }"
                class="p-2 rounded-lg text-gray-500 hover:bg-gray-100 hover:text-gray-700 transition-colors cursor-pointer bg-transparent border-none"
                title="Titre H2"
              >
                <Heading2 :size="15" />
              </button>
              <button
                @click="editor.chain().focus().toggleHeading({ level: 3 }).run()"
                :class="{ 'bg-gray-200 text-gray-900': editor.isActive('heading', { level: 3 }) }"
                class="p-2 rounded-lg text-gray-500 hover:bg-gray-100 hover:text-gray-700 transition-colors cursor-pointer bg-transparent border-none"
                title="Titre H3"
              >
                <Heading3 :size="15" />
              </button>

              <div class="w-px h-5 bg-gray-200 mx-1" />

              <button
                @click="editor.chain().focus().toggleBulletList().run()"
                :class="{ 'bg-gray-200 text-gray-900': editor.isActive('bulletList') }"
                class="p-2 rounded-lg text-gray-500 hover:bg-gray-100 hover:text-gray-700 transition-colors cursor-pointer bg-transparent border-none"
                title="Liste à puces"
              >
                <List :size="15" />
              </button>
              <button
                @click="editor.chain().focus().toggleOrderedList().run()"
                :class="{ 'bg-gray-200 text-gray-900': editor.isActive('orderedList') }"
                class="p-2 rounded-lg text-gray-500 hover:bg-gray-100 hover:text-gray-700 transition-colors cursor-pointer bg-transparent border-none"
                title="Liste numérotée"
              >
                <ListOrdered :size="15" />
              </button>
              <button
                @click="editor.chain().focus().toggleBlockquote().run()"
                :class="{ 'bg-gray-200 text-gray-900': editor.isActive('blockquote') }"
                class="p-2 rounded-lg text-gray-500 hover:bg-gray-100 hover:text-gray-700 transition-colors cursor-pointer bg-transparent border-none"
                title="Citation"
              >
                <Quote :size="15" />
              </button>
              <button
                @click="editor.chain().focus().toggleCodeBlock().run()"
                :class="{ 'bg-gray-200 text-gray-900': editor.isActive('codeBlock') }"
                class="p-2 rounded-lg text-gray-500 hover:bg-gray-100 hover:text-gray-700 transition-colors cursor-pointer bg-transparent border-none"
                title="Bloc de code"
              >
                <Code :size="15" />
              </button>

              <div class="w-px h-5 bg-gray-200 mx-1 hidden sm:block" />

              <button
                @click="editor.chain().focus().setTextAlign('left').run()"
                :class="{ 'bg-gray-200 text-gray-900': editor.isActive({ textAlign: 'left' }) }"
                class="p-2 rounded-lg text-gray-500 hover:bg-gray-100 hover:text-gray-700 transition-colors cursor-pointer bg-transparent border-none hidden sm:block"
                title="Aligner à gauche"
              >
                <AlignLeft :size="15" />
              </button>
              <button
                @click="editor.chain().focus().setTextAlign('center').run()"
                :class="{ 'bg-gray-200 text-gray-900': editor.isActive({ textAlign: 'center' }) }"
                class="p-2 rounded-lg text-gray-500 hover:bg-gray-100 hover:text-gray-700 transition-colors cursor-pointer bg-transparent border-none hidden sm:block"
                title="Centrer"
              >
                <AlignCenter :size="15" />
              </button>
              <button
                @click="editor.chain().focus().setTextAlign('right').run()"
                :class="{ 'bg-gray-200 text-gray-900': editor.isActive({ textAlign: 'right' }) }"
                class="p-2 rounded-lg text-gray-500 hover:bg-gray-100 hover:text-gray-700 transition-colors cursor-pointer bg-transparent border-none hidden sm:block"
                title="Aligner à droite"
              >
                <AlignRight :size="15" />
              </button>

              <div class="w-px h-5 bg-gray-200 mx-1" />

              <button
                @click="setLink"
                :class="{ 'bg-gray-200 text-gray-900': editor.isActive('link') }"
                class="p-2 rounded-lg text-gray-500 hover:bg-gray-100 hover:text-gray-700 transition-colors cursor-pointer bg-transparent border-none"
                title="Lien"
              >
                <LinkIcon :size="15" />
              </button>
              <button
                @click="addImage"
                class="p-2 rounded-lg text-gray-500 hover:bg-gray-100 hover:text-gray-700 transition-colors cursor-pointer bg-transparent border-none"
                title="Image (URL)"
              >
                <ImageIcon :size="15" />
              </button>
              <button
                @click="editor.chain().focus().setHorizontalRule().run()"
                class="p-2 rounded-lg text-gray-500 hover:bg-gray-100 hover:text-gray-700 transition-colors cursor-pointer bg-transparent border-none"
                title="Ligne horizontale"
              >
                <Minus :size="15" />
              </button>

              <div class="flex-1" />

              <button
                @click="editor.chain().focus().undo().run()"
                :disabled="!editor.can().undo()"
                class="p-2 rounded-lg text-gray-500 hover:bg-gray-100 hover:text-gray-700 transition-colors cursor-pointer bg-transparent border-none disabled:opacity-30 disabled:cursor-not-allowed"
                title="Annuler"
              >
                <Undo2 :size="15" />
              </button>
              <button
                @click="editor.chain().focus().redo().run()"
                :disabled="!editor.can().redo()"
                class="p-2 rounded-lg text-gray-500 hover:bg-gray-100 hover:text-gray-700 transition-colors cursor-pointer bg-transparent border-none disabled:opacity-30 disabled:cursor-not-allowed"
                title="Rétablir"
              >
                <Redo2 :size="15" />
              </button>
            </div>

            <!-- Editor content -->
            <EditorContent :editor="editor" />
          </div>
        </div>

        <!-- ═══ Sidebar (1/3) ═══ -->
        <div class="space-y-4">
          <!-- Status -->
          <div class="bg-white rounded-xl border border-gray-200 p-4 sm:p-5">
            <label class="block text-[11px] font-semibold text-gray-400 uppercase tracking-wide mb-3">Statut</label>
            <div class="grid grid-cols-3 gap-2">
              <button
                v-for="opt in [
                  { value: 'draft', label: 'Brouillon', color: 'border-amber-300 bg-amber-50 text-amber-700' },
                  { value: 'published', label: 'Publié', color: 'border-green-300 bg-green-50 text-green-700' },
                  { value: 'archived', label: 'Archivé', color: 'border-gray-300 bg-gray-50 text-gray-600' },
                ]"
                :key="opt.value"
                @click="form.status = opt.value as any"
                class="px-2 py-2 rounded-lg text-xs font-semibold border-2 transition-all cursor-pointer text-center"
                :class="form.status === opt.value ? opt.color : 'border-gray-200 bg-white text-gray-400 hover:border-gray-300'"
              >
                {{ opt.label }}
              </button>
            </div>
          </div>

          <!-- Category -->
          <div class="bg-white rounded-xl border border-gray-200 p-4 sm:p-5">
            <label class="block text-[11px] font-semibold text-gray-400 uppercase tracking-wide mb-2">Catégorie</label>
            <select
              v-model="form.category"
              class="w-full px-3 py-2.5 text-sm border border-gray-200 rounded-lg bg-gray-50 focus:bg-white focus:ring-2 focus:ring-[var(--color-accent)]/20 focus:border-[var(--color-accent)] outline-none transition-all cursor-pointer appearance-none"
            >
              <option :value="null">Aucune catégorie</option>
              <option v-for="cat in categories" :key="cat.id" :value="cat.id">
                {{ cat.name }}
              </option>
            </select>
          </div>

          <!-- Cover image -->
          <div class="bg-white rounded-xl border border-gray-200 p-4 sm:p-5">
            <label class="block text-[11px] font-semibold text-gray-400 uppercase tracking-wide mb-3">Image de couverture</label>

            <div v-if="displayCover" class="relative mb-3">
              <img
                :src="displayCover"
                alt="Couverture"
                class="w-full h-40 object-cover rounded-lg"
              />
              <button
                @click="clearCover"
                class="absolute top-2 right-2 p-1.5 bg-black/50 hover:bg-black/70 rounded-lg text-white transition-colors cursor-pointer"
              >
                <Trash2 :size="14" />
              </button>
            </div>

            <label
              class="flex flex-col items-center gap-2 p-6 border-2 border-dashed border-gray-200 rounded-lg hover:border-[var(--color-accent)]/40 hover:bg-[var(--color-accent-light)]/30 transition-all cursor-pointer"
            >
              <ImagePlus :size="24" class="text-gray-400" />
              <span class="text-xs text-gray-500 font-medium text-center">
                {{ displayCover ? 'Changer l\'image' : 'Choisir une image' }}
              </span>
              <span class="text-[10px] text-gray-400">JPG, PNG ou WebP — max 5 Mo</span>
              <input
                type="file"
                accept="image/jpeg,image/png,image/webp"
                class="hidden"
                @change="onCoverChange"
              />
            </label>
          </div>

          <!-- Featured -->
          <div class="bg-white rounded-xl border border-gray-200 p-4 sm:p-5">
            <label class="flex items-center gap-3 cursor-pointer">
              <input
                v-model="form.is_featured"
                type="checkbox"
                class="w-4 h-4 rounded accent-[var(--color-accent)]"
              />
              <div>
                <span class="text-sm font-medium text-gray-700">Mettre à la une</span>
                <p class="text-[10px] text-gray-400 mt-0.5">Affiché en priorité sur la page d'accueil (max 3)</p>
              </div>
            </label>
          </div>

          <!-- Meta info (edit mode only) -->
          <div v-if="article" class="bg-gray-50 rounded-xl border border-gray-200 p-4 text-xs text-gray-400 space-y-1.5">
            <p><span class="font-semibold text-gray-500">Auteur :</span> {{ article.author_name || '—' }}</p>
            <p><span class="font-semibold text-gray-500">Créé le :</span> {{ article.created_at ? new Date(article.created_at).toLocaleDateString('fr-FR') : '—' }}</p>
            <p v-if="article.published_at"><span class="font-semibold text-gray-500">Publié le :</span> {{ new Date(article.published_at).toLocaleDateString('fr-FR') }}</p>
            <p><span class="font-semibold text-gray-500">Modifié le :</span> {{ article.updated_at ? new Date(article.updated_at).toLocaleDateString('fr-FR') : '—' }}</p>
          </div>
        </div>
      </div>

      <!-- ═══ Mobile sticky save bar ═══ -->
      <div class="lg:hidden fixed bottom-0 left-0 right-0 bg-white border-t border-gray-200 p-3 flex items-center gap-2 z-30 safe-area-bottom">
        <button
          @click="save(false)"
          :disabled="saving"
          class="flex-1 inline-flex items-center justify-center gap-2 py-3 text-sm font-semibold rounded-lg border border-gray-200 bg-white text-gray-700 cursor-pointer disabled:opacity-50"
        >
          <Save :size="14" />
          Enregistrer
        </button>
        <button
          v-if="form.status !== 'published'"
          @click="save(true)"
          :disabled="saving"
          class="flex-1 inline-flex items-center justify-center gap-2 py-3 text-sm font-semibold text-white bg-[var(--color-accent)] rounded-lg cursor-pointer disabled:opacity-50"
        >
          <Send :size="14" />
          Publier
        </button>
      </div>
      <div class="lg:hidden h-20" />
    </template>

    <!-- ═══ Share Dialog ═══ -->
    <ShareDialog
      :show="shareOpen"
      :title="shareData.title"
      :description="shareData.description"
      :image="shareData.image"
      :copied="copied"
      @close="closeShare"
      @share="shareOn"
    />
  </div>
</template>

<style>
.tiptap p.is-editor-empty:first-child::before {
  content: attr(data-placeholder);
  float: left;
  color: #adb5bd;
  pointer-events: none;
  height: 0;
}

.tiptap {
  min-height: 20rem;
}

.tiptap h2 {
  font-size: 1.5rem;
  font-weight: 700;
  margin-top: 1.5rem;
  margin-bottom: 0.75rem;
  color: #1a1a1a;
}

.tiptap h3 {
  font-size: 1.25rem;
  font-weight: 600;
  margin-top: 1.25rem;
  margin-bottom: 0.5rem;
  color: #1a1a1a;
}

.tiptap p {
  margin-bottom: 0.75rem;
  line-height: 1.7;
}

.tiptap ul,
.tiptap ol {
  padding-left: 1.5rem;
  margin-bottom: 0.75rem;
}

.tiptap ul {
  list-style-type: disc;
}

.tiptap ol {
  list-style-type: decimal;
}

.tiptap li {
  margin-bottom: 0.25rem;
}

.tiptap blockquote {
  border-left: 3px solid #16A34A;
  padding-left: 1rem;
  margin: 1rem 0;
  color: #555;
  font-style: italic;
}

.tiptap code {
  background: #f1f5f9;
  border-radius: 4px;
  padding: 0.15rem 0.4rem;
  font-size: 0.875em;
}

.tiptap pre {
  background: #1e293b;
  color: #e2e8f0;
  border-radius: 8px;
  padding: 1rem;
  overflow-x: auto;
  margin: 1rem 0;
}

.tiptap pre code {
  background: none;
  padding: 0;
  color: inherit;
}

.tiptap hr {
  border: none;
  border-top: 2px solid #e5e7eb;
  margin: 1.5rem 0;
}

.tiptap img {
  max-width: 100%;
  border-radius: 8px;
  margin: 1rem 0;
}

.tiptap a {
  color: #16A34A;
  text-decoration: underline;
}

.safe-area-bottom {
  padding-bottom: max(0.75rem, env(safe-area-inset-bottom));
}
</style>
