<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useAppToast } from '@/composables/useToast'
import api from '@/api'
import type { AdminDocument, DocumentCategory } from '@/types'
import dayjs from 'dayjs'
import 'dayjs/locale/fr'

import Tag from 'primevue/tag'

import {
  FolderDown,
  Plus,
  Search,
  SlidersHorizontal,
  X,
  Edit3,
  Trash2,
  Download,
  Eye,
  EyeOff,
  Loader2,
  FileText,
  FileSpreadsheet,
  FileImage,
  File,
  Globe,
  Lock,
  ExternalLink,
  FileArchive,
  FileType,
} from 'lucide-vue-next'

dayjs.locale('fr')

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api'
const toast = useAppToast()

const items = ref<AdminDocument[]>([])
const loading = ref(true)
const filterCategory = ref<string | null>(null)
const filterVisibility = ref<string | null>(null)
const searchQuery = ref('')
const showFilters = ref(false)

const categoryOptions: { value: DocumentCategory; label: string }[] = [
  { value: 'statuts', label: 'Statuts & Règlements' },
  { value: 'rapport', label: 'Rapports' },
  { value: 'communique', label: 'Communiqués' },
  { value: 'formulaire', label: 'Formulaires' },
  { value: 'autre', label: 'Autre' },
]

const categoryLabel: Record<string, string> = {
  statuts: 'Statuts & Règlements',
  rapport: 'Rapports',
  communique: 'Communiqués',
  formulaire: 'Formulaires',
  autre: 'Autre',
}

const categorySeverity: Record<string, string> = {
  statuts: 'info',
  rapport: 'success',
  communique: 'warn',
  formulaire: 'secondary',
  autre: 'contrast',
}

const filtered = computed(() => {
  let list = items.value
  if (filterCategory.value) list = list.filter(d => d.category === filterCategory.value)
  if (filterVisibility.value === 'public') list = list.filter(d => d.is_public)
  if (filterVisibility.value === 'private') list = list.filter(d => !d.is_public)
  if (searchQuery.value) {
    const q = searchQuery.value.toLowerCase()
    list = list.filter(d => d.title.toLowerCase().includes(q) || d.description.toLowerCase().includes(q))
  }
  return list
})

const stats = computed(() => ({
  total: items.value.length,
  public: items.value.filter(d => d.is_public).length,
  private: items.value.filter(d => !d.is_public).length,
  downloads: items.value.reduce((s, d) => s + d.download_count, 0),
}))

async function fetchAll() {
  loading.value = true
  try {
    const { data } = await api.get('/admin/documents/')
    items.value = data
  } catch { toast.error('Erreur lors du chargement des documents.') }
  finally { loading.value = false }
}

onMounted(fetchAll)

// ── Helpers ──

function getExt(url: string): string {
  if (!url) return ''
  const clean = url.split('?')[0]!.split('#')[0]!.replace(/\/+$/, '')
  return (clean.split('.').pop() ?? '').toLowerCase()
}

function fileExt(url: string): string {
  return getExt(url).toUpperCase()
}

type FileKind = 'pdf' | 'image' | 'spreadsheet' | 'archive' | 'word' | 'other'

function getFileKind(url: string): FileKind {
  const ext = getExt(url)
  if (ext === 'pdf') return 'pdf'
  if (['jpg', 'jpeg', 'png', 'webp', 'gif', 'bmp', 'svg'].includes(ext)) return 'image'
  if (['xls', 'xlsx', 'csv', 'ods'].includes(ext)) return 'spreadsheet'
  if (['zip', 'rar', '7z', 'tar', 'gz'].includes(ext)) return 'archive'
  if (['doc', 'docx', 'odt', 'rtf'].includes(ext)) return 'word'
  return 'other'
}

function fileIcon(url: string) {
  const kind = getFileKind(url)
  if (kind === 'pdf') return FileText
  if (kind === 'image') return FileImage
  if (kind === 'spreadsheet') return FileSpreadsheet
  if (kind === 'archive') return FileArchive
  if (kind === 'word') return FileType
  return File
}

const kindColor: Record<FileKind, string> = {
  pdf: 'bg-red-500',
  image: 'bg-violet-500',
  spreadsheet: 'bg-emerald-500',
  archive: 'bg-amber-500',
  word: 'bg-blue-500',
  other: 'bg-gray-400',
}

function formatSize(bytes: number): string {
  if (bytes < 1024) return bytes + ' o'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' Ko'
  return (bytes / (1024 * 1024)).toFixed(1) + ' Mo'
}

function adminPreviewUrl(docId: string): string {
  return `${API_BASE}/admin/documents/${docId}/preview/`
}

// ── Create / Edit ──

const showModal = ref(false)
const editingId = ref<string | null>(null)
const editingDoc = ref<AdminDocument | null>(null)
const saving = ref(false)

const formDefaults = { title: '', description: '', category: 'autre' as DocumentCategory, is_public: false, file: null as File | null }
const form = ref({ ...formDefaults })
const localFileUrl = ref<string | null>(null)
const localFileKind = ref<FileKind>('other')

function openNew() {
  editingId.value = null
  editingDoc.value = null
  form.value = { ...formDefaults }
  clearLocalPreview()
  showModal.value = true
}

function openEdit(doc: AdminDocument) {
  editingId.value = doc.id
  editingDoc.value = doc
  form.value = {
    title: doc.title,
    description: doc.description,
    category: doc.category,
    is_public: doc.is_public,
    file: null,
  }
  clearLocalPreview()
  showModal.value = true
}

function onFileChange(e: Event) {
  const input = e.target as HTMLInputElement
  if (input.files?.[0]) {
    form.value.file = input.files[0]
    clearLocalPreview()
    localFileUrl.value = URL.createObjectURL(input.files[0])
    localFileKind.value = getFileKind(input.files[0].name)
  }
}

function clearLocalPreview() {
  if (localFileUrl.value) {
    URL.revokeObjectURL(localFileUrl.value)
    localFileUrl.value = null
  }
  localFileKind.value = 'other'
}

watch(showModal, (open) => {
  if (!open) clearLocalPreview()
})

async function save() {
  if (!form.value.title.trim()) { toast.warn('Le titre est obligatoire.'); return }
  if (!editingId.value && !form.value.file) { toast.warn('Veuillez sélectionner un fichier.'); return }

  saving.value = true
  try {
    const fd = new FormData()
    fd.append('title', form.value.title)
    fd.append('description', form.value.description)
    fd.append('category', form.value.category)
    fd.append('is_public', String(form.value.is_public))
    if (form.value.file) fd.append('file', form.value.file)

    if (editingId.value) {
      await api.patch(`/admin/documents/${editingId.value}/`, fd)
      toast.success('Document mis à jour.')
    } else {
      await api.post('/admin/documents/', fd)
      toast.success('Document ajouté.')
    }
    showModal.value = false
    await fetchAll()
  } catch {
    toast.error('Erreur lors de l\'enregistrement.')
  } finally { saving.value = false }
}

// ── View detail ──

const viewDoc = ref<AdminDocument | null>(null)

function openView(doc: AdminDocument) {
  viewDoc.value = doc
}

// ── Toggle visibility ──

async function toggleVisibility(doc: AdminDocument) {
  try {
    await api.patch(`/admin/documents/${doc.id}/`, { is_public: !doc.is_public })
    doc.is_public = !doc.is_public
    toast.success(doc.is_public ? 'Document rendu public.' : 'Document rendu privé.')
  } catch { toast.error('Erreur.') }
}

// ── Delete ──

const deleteTarget = ref<AdminDocument | null>(null)
const deleting = ref(false)

async function confirmDelete() {
  if (!deleteTarget.value) return
  deleting.value = true
  try {
    await api.delete(`/admin/documents/${deleteTarget.value.id}/`)
    items.value = items.value.filter(d => d.id !== deleteTarget.value!.id)
    toast.success('Document supprimé.')
    deleteTarget.value = null
  } catch { toast.error('Erreur lors de la suppression.') }
  finally { deleting.value = false }
}
</script>

<template>
  <div class="space-y-4 sm:space-y-6">
    <!-- Header -->
    <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
      <div>
        <h2 class="text-xl sm:text-2xl font-bold text-[var(--color-primary)]">Documents</h2>
        <p class="text-sm text-[var(--color-muted)] mt-0.5">Gérez les documents et ressources du parti</p>
      </div>
      <button @click="openNew" class="inline-flex items-center gap-2 px-4 py-2.5 bg-[var(--color-accent)] text-white text-sm font-semibold rounded-lg hover:bg-[var(--color-accent-hover)] transition-colors cursor-pointer">
        <Plus :size="18" />
        Ajouter un document
      </button>
    </div>

    <!-- KPI -->
    <div class="grid grid-cols-4 gap-2 sm:gap-3">
      <div class="bg-white rounded-xl border border-[var(--color-border)] p-2.5 sm:p-4">
        <div class="flex items-center gap-2 min-w-0">
          <div class="w-8 h-8 sm:w-9 sm:h-9 rounded-lg bg-blue-50 flex items-center justify-center shrink-0">
            <FolderDown :size="16" class="text-blue-600" />
          </div>
          <div class="min-w-0">
            <p class="text-lg sm:text-xl font-bold text-[var(--color-primary)]">{{ stats.total }}</p>
            <p class="text-[9px] sm:text-xs text-[var(--color-muted)] uppercase font-semibold sm:tracking-wide truncate">Total</p>
          </div>
        </div>
      </div>
      <div class="bg-white rounded-xl border border-[var(--color-border)] p-2.5 sm:p-4">
        <div class="flex items-center gap-2 min-w-0">
          <div class="w-8 h-8 sm:w-9 sm:h-9 rounded-lg bg-green-50 flex items-center justify-center shrink-0">
            <Globe :size="16" class="text-green-600" />
          </div>
          <div class="min-w-0">
            <p class="text-lg sm:text-xl font-bold text-green-600">{{ stats.public }}</p>
            <p class="text-[9px] sm:text-xs text-[var(--color-muted)] uppercase font-semibold sm:tracking-wide truncate">Publics</p>
          </div>
        </div>
      </div>
      <div class="bg-white rounded-xl border border-[var(--color-border)] p-2.5 sm:p-4">
        <div class="flex items-center gap-2 min-w-0">
          <div class="w-8 h-8 sm:w-9 sm:h-9 rounded-lg bg-amber-50 flex items-center justify-center shrink-0">
            <Lock :size="16" class="text-amber-600" />
          </div>
          <div class="min-w-0">
            <p class="text-lg sm:text-xl font-bold text-amber-600">{{ stats.private }}</p>
            <p class="text-[9px] sm:text-xs text-[var(--color-muted)] uppercase font-semibold sm:tracking-wide truncate">Privés</p>
          </div>
        </div>
      </div>
      <div class="bg-white rounded-xl border border-[var(--color-border)] p-2.5 sm:p-4">
        <div class="flex items-center gap-2 min-w-0">
          <div class="w-8 h-8 sm:w-9 sm:h-9 rounded-lg bg-purple-50 flex items-center justify-center shrink-0">
            <Download :size="16" class="text-purple-600" />
          </div>
          <div class="min-w-0">
            <p class="text-lg sm:text-xl font-bold text-purple-600">{{ stats.downloads }}</p>
            <p class="text-[9px] sm:text-xs text-[var(--color-muted)] uppercase font-semibold sm:tracking-wide truncate">Télécharg.</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Search + Filters -->
    <div class="bg-white rounded-xl border border-[var(--color-border)] p-4">
      <div class="flex flex-col sm:flex-row gap-3">
        <div class="relative flex-1">
          <Search :size="16" class="absolute left-3 top-1/2 -translate-y-1/2 text-[var(--color-muted)]" />
          <input v-model="searchQuery" placeholder="Rechercher un document..." class="w-full pl-9 pr-4 py-2 text-sm border border-[var(--color-border)] rounded-lg focus:outline-none focus:ring-2 focus:ring-[var(--color-accent)] focus:ring-opacity-30" />
        </div>
        <button @click="showFilters = !showFilters" class="inline-flex items-center gap-2 px-3 py-2 text-sm border border-[var(--color-border)] rounded-lg hover:bg-[var(--color-surface)] transition-colors cursor-pointer" :class="showFilters ? 'bg-[var(--color-surface)] text-[var(--color-accent)]' : 'text-[var(--color-muted)]'">
          <SlidersHorizontal :size="16" />
          Filtres
        </button>
      </div>
      <div v-if="showFilters" class="mt-3 pt-3 border-t border-[var(--color-border)] flex flex-wrap gap-2">
        <button v-for="opt in categoryOptions" :key="opt.value" @click="filterCategory = filterCategory === opt.value ? null : opt.value" class="px-3 py-1.5 text-xs font-medium rounded-full border transition-colors cursor-pointer" :class="filterCategory === opt.value ? 'bg-[var(--color-accent)] text-white border-[var(--color-accent)]' : 'border-[var(--color-border)] text-[var(--color-muted)] hover:border-[var(--color-accent)]'">
          {{ opt.label }}
        </button>
        <span class="w-px h-6 bg-[var(--color-border)] self-center mx-1" />
        <button @click="filterVisibility = filterVisibility === 'public' ? null : 'public'" class="px-3 py-1.5 text-xs font-medium rounded-full border transition-colors cursor-pointer" :class="filterVisibility === 'public' ? 'bg-green-600 text-white border-green-600' : 'border-[var(--color-border)] text-[var(--color-muted)]'">
          <Globe :size="12" class="inline -mt-0.5 mr-1" /> Publics
        </button>
        <button @click="filterVisibility = filterVisibility === 'private' ? null : 'private'" class="px-3 py-1.5 text-xs font-medium rounded-full border transition-colors cursor-pointer" :class="filterVisibility === 'private' ? 'bg-amber-600 text-white border-amber-600' : 'border-[var(--color-border)] text-[var(--color-muted)]'">
          <Lock :size="12" class="inline -mt-0.5 mr-1" /> Privés
        </button>
      </div>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="flex items-center justify-center py-16">
      <Loader2 :size="28" class="animate-spin text-[var(--color-accent)]" />
    </div>

    <!-- Empty -->
    <div v-else-if="!filtered.length" class="bg-white rounded-xl border border-[var(--color-border)] p-12 text-center">
      <FolderDown :size="40" class="mx-auto text-[var(--color-muted)] opacity-40 mb-3" />
      <p class="text-[var(--color-muted)] text-sm">Aucun document trouvé.</p>
    </div>

    <!-- Table (desktop) -->
    <div v-else class="bg-white rounded-xl border border-[var(--color-border)] overflow-hidden hidden sm:block">
      <table class="w-full text-sm">
        <thead class="bg-[var(--color-surface)] border-b border-[var(--color-border)]">
          <tr>
            <th class="text-left px-4 py-3 font-semibold text-[var(--color-muted)] uppercase text-xs tracking-wide">Document</th>
            <th class="text-left px-4 py-3 font-semibold text-[var(--color-muted)] uppercase text-xs tracking-wide">Catégorie</th>
            <th class="text-center px-4 py-3 font-semibold text-[var(--color-muted)] uppercase text-xs tracking-wide">Visibilité</th>
            <th class="text-center px-4 py-3 font-semibold text-[var(--color-muted)] uppercase text-xs tracking-wide">Taille</th>
            <th class="text-center px-4 py-3 font-semibold text-[var(--color-muted)] uppercase text-xs tracking-wide">DL</th>
            <th class="text-right px-4 py-3 font-semibold text-[var(--color-muted)] uppercase text-xs tracking-wide">Actions</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-[var(--color-border)]">
          <tr v-for="doc in filtered" :key="doc.id" class="hover:bg-[var(--color-surface)] transition-colors">
            <td class="px-4 py-3">
              <div class="flex items-center gap-3">
                <div class="w-9 h-9 rounded-lg flex items-center justify-center shrink-0" :class="kindColor[getFileKind(doc.file_url)]">
                  <component :is="fileIcon(doc.file_url)" :size="18" class="text-white" />
                </div>
                <div class="min-w-0">
                  <p class="font-semibold text-[var(--color-primary)] truncate max-w-[260px]">{{ doc.title }}</p>
                  <p class="text-xs text-[var(--color-muted)] truncate max-w-[260px]">{{ doc.description || 'Aucune description' }}</p>
                </div>
              </div>
            </td>
            <td class="px-4 py-3">
              <Tag :value="categoryLabel[doc.category] ?? doc.category" :severity="(categorySeverity[doc.category] as any) ?? 'secondary'" class="text-xs" />
            </td>
            <td class="px-4 py-3 text-center">
              <button @click="toggleVisibility(doc)" class="cursor-pointer" :title="doc.is_public ? 'Rendre privé' : 'Rendre public'">
                <Globe v-if="doc.is_public" :size="18" class="text-green-600" />
                <Lock v-else :size="18" class="text-amber-500" />
              </button>
            </td>
            <td class="px-4 py-3 text-center text-xs text-[var(--color-muted)]">{{ formatSize(doc.file_size) }}</td>
            <td class="px-4 py-3 text-center text-xs font-semibold text-[var(--color-primary)]">{{ doc.download_count }}</td>
            <td class="px-4 py-3 text-right">
              <div class="flex items-center justify-end gap-1">
                <button @click="openView(doc)" class="p-1.5 rounded-lg hover:bg-blue-50 text-[var(--color-muted)] hover:text-blue-600 transition-colors cursor-pointer" title="Voir le détail">
                  <Eye :size="16" />
                </button>
                <a v-if="doc.file_url" :href="doc.file_url" target="_blank" class="p-1.5 rounded-lg hover:bg-[var(--color-surface)] text-[var(--color-muted)] hover:text-blue-600 transition-colors" title="Télécharger">
                  <Download :size="16" />
                </a>
                <button @click="openEdit(doc)" class="p-1.5 rounded-lg hover:bg-[var(--color-surface)] text-[var(--color-muted)] hover:text-[var(--color-accent)] transition-colors cursor-pointer" title="Modifier">
                  <Edit3 :size="16" />
                </button>
                <button @click="deleteTarget = doc" class="p-1.5 rounded-lg hover:bg-red-50 text-[var(--color-muted)] hover:text-red-600 transition-colors cursor-pointer" title="Supprimer">
                  <Trash2 :size="16" />
                </button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Cards (mobile) -->
    <div v-if="!loading && filtered.length" class="sm:hidden space-y-3">
      <div v-for="doc in filtered" :key="doc.id" class="bg-white rounded-xl border border-[var(--color-border)] p-4">
        <div class="flex items-start gap-3">
          <div class="w-10 h-10 rounded-lg flex items-center justify-center shrink-0" :class="kindColor[getFileKind(doc.file_url)]">
            <component :is="fileIcon(doc.file_url)" :size="20" class="text-white" />
          </div>
          <div class="min-w-0 flex-1">
            <p class="font-semibold text-[var(--color-primary)] text-sm truncate">{{ doc.title }}</p>
            <div class="flex items-center gap-2 mt-1 flex-wrap">
              <Tag :value="categoryLabel[doc.category] ?? doc.category" :severity="(categorySeverity[doc.category] as any) ?? 'secondary'" class="text-[10px]" />
              <span class="flex items-center gap-1 text-[10px]" :class="doc.is_public ? 'text-green-600' : 'text-amber-500'">
                <Globe v-if="doc.is_public" :size="10" /> <Lock v-else :size="10" />
                {{ doc.is_public ? 'Public' : 'Privé' }}
              </span>
              <span class="text-[10px] text-[var(--color-muted)]">{{ formatSize(doc.file_size) }}</span>
            </div>
          </div>
        </div>
        <div class="flex items-center justify-between mt-3 pt-3 border-t border-[var(--color-border)]">
          <span class="text-xs text-[var(--color-muted)]">{{ dayjs(doc.created_at).format('DD MMM YYYY') }} &middot; {{ doc.download_count }} DL</span>
          <div class="flex items-center gap-1">
            <button @click="openView(doc)" class="p-1.5 rounded-lg hover:bg-blue-50 text-[var(--color-muted)] hover:text-blue-600 cursor-pointer" title="Voir">
              <Eye :size="15" />
            </button>
            <button @click="toggleVisibility(doc)" class="p-1.5 rounded-lg hover:bg-[var(--color-surface)] cursor-pointer" :title="doc.is_public ? 'Rendre privé' : 'Rendre public'">
              <Globe v-if="doc.is_public" :size="15" class="text-green-600" />
              <EyeOff v-else :size="15" class="text-amber-500" />
            </button>
            <a v-if="doc.file_url" :href="doc.file_url" target="_blank" class="p-1.5 rounded-lg hover:bg-[var(--color-surface)] text-blue-600">
              <Download :size="15" />
            </a>
            <button @click="openEdit(doc)" class="p-1.5 rounded-lg hover:bg-[var(--color-surface)] text-[var(--color-accent)] cursor-pointer">
              <Edit3 :size="15" />
            </button>
            <button @click="deleteTarget = doc" class="p-1.5 rounded-lg hover:bg-red-50 text-red-500 cursor-pointer">
              <Trash2 :size="15" />
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- ═══ Modal Ajout / Modification ═══ -->
    <Teleport to="body">
      <Transition name="modal">
        <div v-if="showModal" class="fixed inset-0 z-[60] flex items-center justify-center p-4 bg-black/40" @click.self="showModal = false">
          <div class="bg-white rounded-2xl shadow-xl w-full max-w-lg max-h-[90vh] overflow-y-auto">
            <div class="flex items-center justify-between p-5 border-b border-[var(--color-border)]">
              <h3 class="font-bold text-lg text-[var(--color-primary)]">{{ editingId ? 'Modifier le document' : 'Ajouter un document' }}</h3>
              <button @click="showModal = false" class="p-1 rounded-lg hover:bg-[var(--color-surface)] cursor-pointer"><X :size="20" /></button>
            </div>
            <form @submit.prevent="save" class="p-5 space-y-4">
              <!-- File preview in form -->
              <div
                v-if="localFileUrl || (editingDoc && editingDoc.file_url)"
                class="rounded-xl border border-[var(--color-border)] overflow-hidden bg-[var(--color-surface)]"
              >
                <p class="px-3 py-2 text-xs font-semibold text-[var(--color-muted)] uppercase tracking-wide border-b border-[var(--color-border)] bg-white">
                  Aperçu du fichier
                </p>
                <div class="h-52 relative">
                  <!-- New local file selected -->
                  <template v-if="localFileUrl">
                    <img
                      v-if="localFileKind === 'image'"
                      :src="localFileUrl"
                      class="w-full h-full object-contain p-2"
                    />
                    <iframe
                      v-else-if="localFileKind === 'pdf'"
                      :src="localFileUrl + '#toolbar=0&navpanes=0&scrollbar=0&view=FitH'"
                      class="w-full h-full border-0"
                    />
                    <div v-else class="w-full h-full flex flex-col items-center justify-center gap-2">
                      <component :is="fileIcon(form.file?.name ?? '')" :size="36" class="text-[var(--color-muted)] opacity-40" />
                      <span class="text-xs font-bold text-[var(--color-muted)] uppercase">{{ form.file?.name?.split('.').pop()?.toUpperCase() }}</span>
                      <span class="text-[11px] text-[var(--color-muted)]">{{ form.file ? formatSize(form.file.size) : '' }}</span>
                    </div>
                  </template>
                  <!-- Existing file (editing) -->
                  <template v-else-if="editingDoc">
                    <img
                      v-if="getFileKind(editingDoc.file_url) === 'image'"
                      :src="editingDoc.file_url"
                      class="w-full h-full object-contain p-2"
                    />
                    <iframe
                      v-else-if="getFileKind(editingDoc.file_url) === 'pdf'"
                      :src="adminPreviewUrl(editingDoc.id) + '#toolbar=0&navpanes=0&scrollbar=0&view=FitH'"
                      class="w-full h-full border-0"
                    />
                    <div v-else class="w-full h-full flex flex-col items-center justify-center gap-2">
                      <component :is="fileIcon(editingDoc.file_url)" :size="36" class="text-[var(--color-muted)] opacity-40" />
                      <span class="text-xs font-bold text-[var(--color-muted)] uppercase">{{ fileExt(editingDoc.file_url) }}</span>
                      <span class="text-[11px] text-[var(--color-muted)]">{{ formatSize(editingDoc.file_size) }}</span>
                    </div>
                  </template>
                </div>
              </div>

              <div>
                <label class="block text-sm font-medium text-[var(--color-primary)] mb-1">Titre *</label>
                <input v-model="form.title" required class="w-full px-3 py-2 text-sm border border-[var(--color-border)] rounded-lg focus:outline-none focus:ring-2 focus:ring-[var(--color-accent)] focus:ring-opacity-30" />
              </div>
              <div>
                <label class="block text-sm font-medium text-[var(--color-primary)] mb-1">Description</label>
                <textarea v-model="form.description" rows="3" class="w-full px-3 py-2 text-sm border border-[var(--color-border)] rounded-lg focus:outline-none focus:ring-2 focus:ring-[var(--color-accent)] focus:ring-opacity-30" />
              </div>
              <div class="grid grid-cols-2 gap-4">
                <div>
                  <label class="block text-sm font-medium text-[var(--color-primary)] mb-1">Catégorie</label>
                  <select v-model="form.category" class="w-full px-3 py-2 text-sm border border-[var(--color-border)] rounded-lg focus:outline-none focus:ring-2 focus:ring-[var(--color-accent)] focus:ring-opacity-30">
                    <option v-for="opt in categoryOptions" :key="opt.value" :value="opt.value">{{ opt.label }}</option>
                  </select>
                </div>
                <div class="flex items-end">
                  <label class="flex items-center gap-2 cursor-pointer">
                    <input type="checkbox" v-model="form.is_public" class="w-4 h-4 rounded border-[var(--color-border)] text-[var(--color-accent)] focus:ring-[var(--color-accent)]" />
                    <span class="text-sm font-medium text-[var(--color-primary)]">Document public</span>
                  </label>
                </div>
              </div>
              <div>
                <label class="block text-sm font-medium text-[var(--color-primary)] mb-1">{{ editingId ? 'Remplacer le fichier' : 'Fichier *' }}</label>
                <input type="file" @change="onFileChange" class="w-full text-sm text-[var(--color-muted)] file:mr-3 file:px-4 file:py-2 file:rounded-lg file:border-0 file:text-sm file:font-semibold file:bg-[var(--color-surface)] file:text-[var(--color-primary)] hover:file:bg-[var(--color-accent-light)] file:cursor-pointer cursor-pointer" accept=".pdf,.doc,.docx,.xls,.xlsx,.ppt,.pptx,.txt,.csv,.zip,.rar,.png,.jpg,.jpeg,.webp" />
              </div>
              <div class="flex justify-end gap-3 pt-2">
                <button type="button" @click="showModal = false" class="px-4 py-2 text-sm font-medium text-[var(--color-muted)] border border-[var(--color-border)] rounded-lg hover:bg-[var(--color-surface)] transition-colors cursor-pointer">Annuler</button>
                <button type="submit" :disabled="saving" class="inline-flex items-center gap-2 px-5 py-2 text-sm font-semibold bg-[var(--color-accent)] text-white rounded-lg hover:bg-[var(--color-accent-hover)] transition-colors disabled:opacity-50 cursor-pointer">
                  <Loader2 v-if="saving" :size="16" class="animate-spin" />
                  {{ editingId ? 'Enregistrer' : 'Ajouter' }}
                </button>
              </div>
            </form>
          </div>
        </div>
      </Transition>
    </Teleport>

    <!-- ═══ Modal Vue détaillée ═══ -->
    <Teleport to="body">
      <Transition name="modal">
        <div v-if="viewDoc" class="fixed inset-0 z-[60] flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm" @click.self="viewDoc = null">
          <div class="bg-white rounded-2xl shadow-2xl w-full max-w-3xl max-h-[92vh] flex flex-col overflow-hidden animate-modal-in">
            <!-- Header -->
            <div class="flex items-center justify-between p-5 border-b border-[var(--color-border)] shrink-0">
              <div class="flex items-center gap-3 min-w-0">
                <div class="w-10 h-10 rounded-xl flex items-center justify-center shrink-0" :class="kindColor[getFileKind(viewDoc.file_url)]">
                  <component :is="fileIcon(viewDoc.file_url)" :size="20" class="text-white" />
                </div>
                <div class="min-w-0">
                  <h3 class="font-bold text-[var(--color-primary)] truncate">{{ viewDoc.title }}</h3>
                  <p class="text-xs text-[var(--color-muted)]">
                    {{ fileExt(viewDoc.file_url) }} &middot; {{ formatSize(viewDoc.file_size) }} &middot; {{ dayjs(viewDoc.created_at).format('DD MMMM YYYY') }}
                  </p>
                </div>
              </div>
              <button @click="viewDoc = null" class="p-2 rounded-xl hover:bg-[var(--color-surface)] cursor-pointer shrink-0 ml-3">
                <X :size="20" />
              </button>
            </div>

            <!-- Document preview -->
            <div class="flex-1 overflow-auto bg-[var(--color-surface)]">
              <img
                v-if="getFileKind(viewDoc.file_url) === 'image'"
                :src="viewDoc.file_url"
                :alt="viewDoc.title"
                class="w-full max-h-[55vh] object-contain p-4"
              />
              <iframe
                v-else-if="getFileKind(viewDoc.file_url) === 'pdf'"
                :src="adminPreviewUrl(viewDoc.id)"
                class="w-full border-0"
                style="height: 55vh"
              />
              <div v-else class="flex flex-col items-center justify-center py-14 gap-4">
                <div class="w-20 h-20 rounded-2xl flex items-center justify-center shadow-lg" :class="kindColor[getFileKind(viewDoc.file_url)]">
                  <component :is="fileIcon(viewDoc.file_url)" :size="40" class="text-white" />
                </div>
                <p class="text-[var(--color-muted)] text-sm">L'aperçu n'est pas disponible pour ce type de fichier.</p>
              </div>
            </div>

            <!-- Metadata -->
            <div class="shrink-0 border-t border-[var(--color-border)] p-5 space-y-3">
              <div v-if="viewDoc.description" class="text-sm text-[var(--color-muted)] leading-relaxed">{{ viewDoc.description }}</div>
              <div class="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs">
                <div class="bg-[var(--color-surface)] rounded-lg px-3 py-2">
                  <p class="text-[var(--color-muted)] font-medium uppercase tracking-wide mb-0.5">Catégorie</p>
                  <p class="text-[var(--color-primary)] font-semibold">{{ categoryLabel[viewDoc.category] ?? viewDoc.category }}</p>
                </div>
                <div class="bg-[var(--color-surface)] rounded-lg px-3 py-2">
                  <p class="text-[var(--color-muted)] font-medium uppercase tracking-wide mb-0.5">Visibilité</p>
                  <p class="font-semibold flex items-center gap-1" :class="viewDoc.is_public ? 'text-green-600' : 'text-amber-600'">
                    <Globe v-if="viewDoc.is_public" :size="12" />
                    <Lock v-else :size="12" />
                    {{ viewDoc.is_public ? 'Public' : 'Privé' }}
                  </p>
                </div>
                <div class="bg-[var(--color-surface)] rounded-lg px-3 py-2">
                  <p class="text-[var(--color-muted)] font-medium uppercase tracking-wide mb-0.5">Téléchargements</p>
                  <p class="text-[var(--color-primary)] font-semibold">{{ viewDoc.download_count }}</p>
                </div>
                <div class="bg-[var(--color-surface)] rounded-lg px-3 py-2">
                  <p class="text-[var(--color-muted)] font-medium uppercase tracking-wide mb-0.5">Auteur</p>
                  <p class="text-[var(--color-primary)] font-semibold">{{ viewDoc.uploaded_by_name || '—' }}</p>
                </div>
              </div>
            </div>

            <!-- Actions -->
            <div class="flex items-center justify-between p-5 border-t border-[var(--color-border)] shrink-0 gap-3">
              <span class="text-xs text-[var(--color-muted)]">Modifié le {{ dayjs(viewDoc.updated_at).format('DD MMM YYYY à HH:mm') }}</span>
              <div class="flex items-center gap-2 shrink-0">
                <a
                  :href="viewDoc.file_url"
                  target="_blank"
                  class="inline-flex items-center gap-1.5 px-3 py-2 text-xs font-medium text-[var(--color-primary)] border border-[var(--color-border)] rounded-lg hover:bg-[var(--color-surface)] transition-colors no-underline"
                >
                  <ExternalLink :size="14" />
                  Ouvrir
                </a>
                <button
                  @click="() => { const d = viewDoc!; viewDoc = null; openEdit(d) }"
                  class="inline-flex items-center gap-1.5 px-3 py-2 text-xs font-semibold text-white bg-[var(--color-accent)] rounded-lg hover:bg-[var(--color-accent-hover)] transition-colors cursor-pointer"
                >
                  <Edit3 :size="14" />
                  Modifier
                </button>
              </div>
            </div>
          </div>
        </div>
      </Transition>
    </Teleport>

    <!-- ═══ Modal Suppression ═══ -->
    <Teleport to="body">
      <Transition name="modal">
        <div v-if="deleteTarget" class="fixed inset-0 z-[60] flex items-center justify-center p-4 bg-black/40" @click.self="deleteTarget = null">
          <div class="bg-white rounded-2xl shadow-xl w-full max-w-sm p-6 text-center">
            <Trash2 :size="36" class="mx-auto text-red-500 mb-3" />
            <h3 class="font-bold text-lg text-[var(--color-primary)] mb-2">Supprimer ce document ?</h3>
            <p class="text-sm text-[var(--color-muted)] mb-5">« {{ deleteTarget.title }} » sera définitivement supprimé.</p>
            <div class="flex justify-center gap-3">
              <button @click="deleteTarget = null" class="px-4 py-2 text-sm font-medium border border-[var(--color-border)] rounded-lg hover:bg-[var(--color-surface)] cursor-pointer">Annuler</button>
              <button @click="confirmDelete" :disabled="deleting" class="inline-flex items-center gap-2 px-5 py-2 text-sm font-semibold bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors disabled:opacity-50 cursor-pointer">
                <Loader2 v-if="deleting" :size="16" class="animate-spin" />
                Supprimer
              </button>
            </div>
          </div>
        </div>
      </Transition>
    </Teleport>
  </div>
</template>

<style scoped>
.modal-enter-active, .modal-leave-active { transition: opacity 200ms ease; }
.modal-enter-from, .modal-leave-to { opacity: 0; }

@keyframes modal-in {
  from { opacity: 0; transform: scale(0.95) translateY(10px); }
  to { opacity: 1; transform: scale(1) translateY(0); }
}
.animate-modal-in { animation: modal-in 250ms ease-out; }
</style>
