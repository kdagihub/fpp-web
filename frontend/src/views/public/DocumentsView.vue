<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import api from '@/api'
import type { PublicDocument, DocumentCategory } from '@/types'
import dayjs from 'dayjs'
import 'dayjs/locale/fr'

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api'

import {
  Download,
  Search,
  FileText,
  FileSpreadsheet,
  FileImage,
  File,
  FolderDown,
  Loader2,
  Filter,
  LayoutGrid,
  List,
  Eye,
  X,
  ExternalLink,
  FileArchive,
  FileCode,
  FileType,
} from 'lucide-vue-next'

dayjs.locale('fr')

const docs = ref<PublicDocument[]>([])
const loading = ref(true)
const searchQuery = ref('')
const activeCategory = ref<DocumentCategory | null>(null)
const viewMode = ref<'grid' | 'list'>('grid')
const previewDoc = ref<PublicDocument | null>(null)

const categories: { value: DocumentCategory; label: string; icon: string }[] = [
  { value: 'statuts', label: 'Statuts & Règlements', icon: '📜' },
  { value: 'rapport', label: 'Rapports', icon: '📊' },
  { value: 'communique', label: 'Communiqués', icon: '📢' },
  { value: 'formulaire', label: 'Formulaires', icon: '📋' },
  { value: 'autre', label: 'Autre', icon: '📁' },
]

const categoryLabel: Record<string, string> = {
  statuts: 'Statuts & Règlements',
  rapport: 'Rapports',
  communique: 'Communiqués',
  formulaire: 'Formulaires',
  autre: 'Autre',
}

const filtered = computed(() => {
  let list = docs.value
  if (activeCategory.value) list = list.filter(d => d.category === activeCategory.value)
  if (searchQuery.value) {
    const q = searchQuery.value.toLowerCase()
    list = list.filter(d => d.title.toLowerCase().includes(q) || d.description.toLowerCase().includes(q))
  }
  return list
})

async function fetchDocs() {
  loading.value = true
  try {
    const { data } = await api.get('/public/documents/')
    docs.value = data.results ?? data
  } catch { /* silent */ }
  finally { loading.value = false }
}

async function trackDownload(doc: PublicDocument) {
  try { await api.post(`/public/documents/${doc.id}/download/`) } catch { /* silent */ }
}

function formatSize(bytes: number): string {
  if (bytes < 1024) return bytes + ' o'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' Ko'
  return (bytes / (1024 * 1024)).toFixed(1) + ' Mo'
}

function getExt(url: string): string {
  if (!url) return ''
  const clean = url.split('?')[0]!.split('#')[0]!.replace(/\/+$/, '')
  return (clean.split('.').pop() ?? '').toLowerCase()
}

function fileExt(url: string): string {
  return getExt(url).toUpperCase()
}

type FileKind = 'pdf' | 'image' | 'spreadsheet' | 'archive' | 'code' | 'word' | 'other'

function getFileKind(url: string): FileKind {
  const ext = getExt(url)
  if (ext === 'pdf') return 'pdf'
  if (['jpg', 'jpeg', 'png', 'webp', 'gif', 'bmp', 'svg'].includes(ext)) return 'image'
  if (['xls', 'xlsx', 'csv', 'ods'].includes(ext)) return 'spreadsheet'
  if (['zip', 'rar', '7z', 'tar', 'gz'].includes(ext)) return 'archive'
  if (['doc', 'docx', 'odt', 'rtf'].includes(ext)) return 'word'
  if (['html', 'css', 'js', 'ts', 'json', 'xml'].includes(ext)) return 'code'
  return 'other'
}

function fileIcon(url: string) {
  const kind = getFileKind(url)
  if (kind === 'pdf') return FileText
  if (kind === 'image') return FileImage
  if (kind === 'spreadsheet') return FileSpreadsheet
  if (kind === 'archive') return FileArchive
  if (kind === 'code') return FileCode
  if (kind === 'word') return FileType
  return File
}

const kindStyle: Record<FileKind, { bg: string; accent: string; icon: string }> = {
  pdf:         { bg: 'from-red-50 to-red-100',    accent: 'text-red-500',    icon: 'bg-red-500' },
  image:       { bg: 'from-violet-50 to-violet-100', accent: 'text-violet-500', icon: 'bg-violet-500' },
  spreadsheet: { bg: 'from-emerald-50 to-emerald-100', accent: 'text-emerald-600', icon: 'bg-emerald-500' },
  archive:     { bg: 'from-amber-50 to-amber-100', accent: 'text-amber-600', icon: 'bg-amber-500' },
  word:        { bg: 'from-blue-50 to-blue-100',   accent: 'text-blue-500',   icon: 'bg-blue-500' },
  code:        { bg: 'from-slate-50 to-slate-200', accent: 'text-slate-500',  icon: 'bg-slate-500' },
  other:       { bg: 'from-gray-50 to-gray-100',   accent: 'text-gray-400',   icon: 'bg-gray-400' },
}

function previewUrl(doc: PublicDocument): string {
  return `${API_BASE}/public/documents/${doc.id}/preview/`
}

function openPreview(doc: PublicDocument) {
  previewDoc.value = doc
}

onMounted(fetchDocs)
</script>

<template>
  <div class="min-h-screen">
    <!-- Hero -->
    <section class="relative bg-[var(--color-primary)] text-white overflow-hidden">
      <div class="absolute inset-0 opacity-5">
        <div class="absolute inset-0 bg-[url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNDAiIGhlaWdodD0iNDAiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+PGNpcmNsZSBjeD0iMjAiIGN5PSIyMCIgcj0iMSIgZmlsbD0id2hpdGUiLz48L3N2Zz4=')]" />
      </div>
      <div class="relative mx-auto max-w-[var(--container-xl)] px-6 py-16 sm:py-20 text-center">
        <div class="inline-flex items-center gap-2 px-4 py-1.5 bg-white/10 rounded-full text-sm font-medium mb-6 backdrop-blur-sm">
          <FolderDown :size="16" />
          Ressources du parti
        </div>
        <h1 class="font-heading text-3xl sm:text-4xl font-extrabold tracking-tight mb-4">
          Documents & Ressources
        </h1>
        <p class="text-white/70 text-base sm:text-lg max-w-2xl mx-auto leading-relaxed">
          Retrouvez les statuts, règlements, communiqués et documents officiels du Front Patriotique Panafricain.
        </p>
      </div>
    </section>

    <!-- Content -->
    <section class="mx-auto max-w-[var(--container-xl)] px-6 py-10 sm:py-14">
      <!-- Search + View toggle -->
      <div class="flex flex-col sm:flex-row gap-4 mb-8">
        <div class="relative flex-1">
          <Search :size="18" class="absolute left-3.5 top-1/2 -translate-y-1/2 text-[var(--color-muted)]" />
          <input
            v-model="searchQuery"
            placeholder="Rechercher un document..."
            class="w-full pl-11 pr-4 py-3 text-sm border border-[var(--color-border)] rounded-xl bg-white focus:outline-none focus:ring-2 focus:ring-[var(--color-accent)] focus:ring-opacity-30"
          />
        </div>
        <div class="flex items-center bg-white border border-[var(--color-border)] rounded-xl p-1 shrink-0 self-start">
          <button
            @click="viewMode = 'grid'"
            class="p-2 rounded-lg transition-colors cursor-pointer"
            :class="viewMode === 'grid' ? 'bg-[var(--color-accent)] text-white' : 'text-[var(--color-muted)] hover:text-[var(--color-primary)]'"
            title="Vue grille"
          >
            <LayoutGrid :size="18" />
          </button>
          <button
            @click="viewMode = 'list'"
            class="p-2 rounded-lg transition-colors cursor-pointer"
            :class="viewMode === 'list' ? 'bg-[var(--color-accent)] text-white' : 'text-[var(--color-muted)] hover:text-[var(--color-primary)]'"
            title="Vue liste"
          >
            <List :size="18" />
          </button>
        </div>
      </div>

      <!-- Category tabs -->
      <div class="flex gap-2 mb-8 overflow-x-auto pb-2 scrollbar-hide">
        <button
          @click="activeCategory = null"
          class="shrink-0 whitespace-nowrap px-4 py-2 text-sm font-semibold rounded-xl border transition-all cursor-pointer"
          :class="!activeCategory ? 'bg-[var(--color-accent)] text-white border-[var(--color-accent)]' : 'bg-white text-[var(--color-muted)] border-[var(--color-border)] hover:border-[var(--color-accent)] hover:text-[var(--color-accent)]'"
        >
          <Filter :size="14" class="inline -mt-0.5 mr-1.5" />
          Tous
        </button>
        <button
          v-for="cat in categories"
          :key="cat.value"
          @click="activeCategory = activeCategory === cat.value ? null : cat.value"
          class="shrink-0 whitespace-nowrap px-4 py-2 text-sm font-semibold rounded-xl border transition-all cursor-pointer"
          :class="activeCategory === cat.value ? 'bg-[var(--color-accent)] text-white border-[var(--color-accent)]' : 'bg-white text-[var(--color-muted)] border-[var(--color-border)] hover:border-[var(--color-accent)] hover:text-[var(--color-accent)]'"
        >
          <span class="mr-1.5">{{ cat.icon }}</span>
          {{ cat.label }}
        </button>
      </div>

      <!-- Loading -->
      <div v-if="loading" class="flex items-center justify-center py-20">
        <Loader2 :size="32" class="animate-spin text-[var(--color-accent)]" />
      </div>

      <!-- Empty -->
      <div v-else-if="!filtered.length" class="text-center py-20">
        <FolderDown :size="48" class="mx-auto text-[var(--color-muted)] opacity-30 mb-4" />
        <p class="text-[var(--color-muted)] text-lg font-medium">Aucun document disponible</p>
        <p class="text-[var(--color-muted)] text-sm mt-1">Revenez plus tard pour consulter les ressources du parti.</p>
      </div>

      <!-- ═══ GRID VIEW ═══ -->
      <div v-else-if="viewMode === 'grid'" class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 sm:gap-5">
        <div
          v-for="doc in filtered"
          :key="doc.id"
          class="group bg-white rounded-2xl border border-[var(--color-border)] overflow-hidden hover:shadow-lg hover:border-[var(--color-accent)]/30 transition-all duration-200 flex flex-col"
        >
          <!-- Preview area -->
          <div class="relative w-full h-48 overflow-hidden">
            <!-- Image preview -->
            <img
              v-if="getFileKind(doc.file_url) === 'image'"
              :src="doc.file_url"
              :alt="doc.title"
              class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
            />
            <!-- PDF: native browser preview via dedicated endpoint -->
            <iframe
              v-else-if="getFileKind(doc.file_url) === 'pdf'"
              :src="previewUrl(doc) + '#toolbar=0&navpanes=0&scrollbar=0&view=FitH'"
              class="w-full h-full border-0 pointer-events-none"
              loading="lazy"
            />
            <!-- Other formats: styled file-type card -->
            <div
              v-else
              class="w-full h-full bg-gradient-to-br flex flex-col items-center justify-center gap-3 relative"
              :class="kindStyle[getFileKind(doc.file_url)].bg"
            >
              <div
                class="w-16 h-16 rounded-2xl flex items-center justify-center shadow-md"
                :class="kindStyle[getFileKind(doc.file_url)].icon"
              >
                <component :is="fileIcon(doc.file_url)" :size="30" class="text-white" />
              </div>
              <span
                class="text-xs font-bold uppercase tracking-widest"
                :class="kindStyle[getFileKind(doc.file_url)].accent"
              >
                {{ fileExt(doc.file_url) }}
              </span>
              <div class="absolute bottom-4 left-6 right-6 space-y-1.5 opacity-[0.12]">
                <div class="h-1.5 rounded-full bg-current w-full" :class="kindStyle[getFileKind(doc.file_url)].accent" />
                <div class="h-1.5 rounded-full bg-current w-3/4" :class="kindStyle[getFileKind(doc.file_url)].accent" />
                <div class="h-1.5 rounded-full bg-current w-1/2" :class="kindStyle[getFileKind(doc.file_url)].accent" />
              </div>
            </div>
            <!-- Overlay badge -->
            <div class="absolute top-3 left-3">
              <span class="text-[10px] font-bold uppercase tracking-wide px-2.5 py-1 rounded-lg bg-black/60 text-white backdrop-blur-sm">
                {{ fileExt(doc.file_url) }} &middot; {{ formatSize(doc.file_size) }}
              </span>
            </div>
          </div>

          <!-- Card body -->
          <div class="p-5 flex flex-col flex-1">
            <h3 class="font-bold text-[var(--color-primary)] text-sm leading-tight mb-1.5 group-hover:text-[var(--color-accent)] transition-colors line-clamp-2">{{ doc.title }}</h3>
            <p v-if="doc.description" class="text-xs text-[var(--color-muted)] leading-relaxed mb-4 line-clamp-2 flex-1">{{ doc.description }}</p>
            <div v-else class="flex-1" />

            <div class="flex items-center justify-between pt-3 border-t border-[var(--color-border)]">
              <span class="text-xs text-[var(--color-muted)]">{{ dayjs(doc.created_at).format('DD MMM YYYY') }}</span>
              <div class="flex items-center gap-1.5">
                <button
                  @click="openPreview(doc)"
                  class="inline-flex items-center gap-1 text-xs font-semibold text-[var(--color-muted)] hover:text-[var(--color-accent)] px-2.5 py-1.5 rounded-full hover:bg-[var(--color-accent-light)] transition-all cursor-pointer"
                  title="Aperçu"
                >
                  <Eye :size="13" />
                </button>
                <a
                  :href="doc.file_url"
                  target="_blank"
                  @click="trackDownload(doc)"
                  class="inline-flex items-center gap-1.5 text-xs font-semibold text-[var(--color-accent)] px-3 py-1.5 rounded-full bg-[var(--color-accent-light)] hover:bg-[var(--color-accent)] hover:text-white transition-all no-underline"
                >
                  <Download :size="13" />
                  Télécharger
                </a>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- ═══ LIST VIEW ═══ -->
      <div v-else class="bg-white rounded-2xl border border-[var(--color-border)] overflow-hidden">
        <!-- Desktop table -->
        <div class="hidden sm:block overflow-x-auto">
          <table class="w-full text-sm">
            <thead class="bg-[var(--color-surface)] border-b border-[var(--color-border)]">
              <tr>
                <th class="text-left px-5 py-3.5 font-semibold text-[var(--color-muted)] uppercase text-xs tracking-wide">Document</th>
                <th class="text-left px-5 py-3.5 font-semibold text-[var(--color-muted)] uppercase text-xs tracking-wide">Catégorie</th>
                <th class="text-left px-5 py-3.5 font-semibold text-[var(--color-muted)] uppercase text-xs tracking-wide">Format</th>
                <th class="text-left px-5 py-3.5 font-semibold text-[var(--color-muted)] uppercase text-xs tracking-wide">Taille</th>
                <th class="text-left px-5 py-3.5 font-semibold text-[var(--color-muted)] uppercase text-xs tracking-wide">Date</th>
                <th class="text-right px-5 py-3.5 font-semibold text-[var(--color-muted)] uppercase text-xs tracking-wide">Actions</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-[var(--color-border)]">
              <tr v-for="doc in filtered" :key="doc.id" class="hover:bg-[var(--color-surface)]/50 transition-colors">
                <td class="px-5 py-4">
                  <div class="flex items-center gap-3 min-w-0">
                    <div
                      class="w-9 h-9 rounded-lg flex items-center justify-center shrink-0"
                      :class="kindStyle[getFileKind(doc.file_url)].icon"
                    >
                      <component :is="fileIcon(doc.file_url)" :size="18" class="text-white" />
                    </div>
                    <div class="min-w-0">
                      <p class="font-semibold text-[var(--color-primary)] truncate max-w-[280px]">{{ doc.title }}</p>
                      <p v-if="doc.description" class="text-xs text-[var(--color-muted)] truncate max-w-[280px]">{{ doc.description }}</p>
                    </div>
                  </div>
                </td>
                <td class="px-5 py-4">
                  <span class="text-xs font-medium text-[var(--color-muted)]">{{ categoryLabel[doc.category] ?? doc.category }}</span>
                </td>
                <td class="px-5 py-4">
                  <span
                    class="text-[10px] font-bold uppercase tracking-wide px-2 py-1 rounded-md"
                    :class="kindStyle[getFileKind(doc.file_url)].bg + ' ' + kindStyle[getFileKind(doc.file_url)].accent"
                  >
                    {{ fileExt(doc.file_url) }}
                  </span>
                </td>
                <td class="px-5 py-4 text-xs text-[var(--color-muted)] whitespace-nowrap">{{ formatSize(doc.file_size) }}</td>
                <td class="px-5 py-4 text-xs text-[var(--color-muted)] whitespace-nowrap">{{ dayjs(doc.created_at).format('DD MMM YYYY') }}</td>
                <td class="px-5 py-4 text-right">
                  <div class="flex items-center justify-end gap-1">
                    <button
                      @click="openPreview(doc)"
                      class="p-2 rounded-lg hover:bg-[var(--color-accent-light)] text-[var(--color-muted)] hover:text-[var(--color-accent)] transition-colors cursor-pointer"
                      title="Aperçu"
                    >
                      <Eye :size="17" />
                    </button>
                    <a
                      :href="doc.file_url"
                      target="_blank"
                      @click="trackDownload(doc)"
                      class="p-2 rounded-lg hover:bg-[var(--color-accent-light)] text-[var(--color-accent)] transition-colors no-underline"
                      title="Télécharger"
                    >
                      <Download :size="17" />
                    </a>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Mobile list -->
        <div class="sm:hidden divide-y divide-[var(--color-border)]">
          <div v-for="doc in filtered" :key="doc.id" class="p-4 flex items-center gap-3">
            <div
              class="w-10 h-10 rounded-lg flex items-center justify-center shrink-0"
              :class="kindStyle[getFileKind(doc.file_url)].icon"
            >
              <component :is="fileIcon(doc.file_url)" :size="20" class="text-white" />
            </div>
            <div class="min-w-0 flex-1">
              <p class="font-semibold text-[var(--color-primary)] text-sm truncate">{{ doc.title }}</p>
              <p class="text-[11px] text-[var(--color-muted)]">
                {{ fileExt(doc.file_url) }} &middot; {{ formatSize(doc.file_size) }} &middot; {{ dayjs(doc.created_at).format('DD MMM YYYY') }}
              </p>
            </div>
            <div class="flex items-center gap-0.5 shrink-0">
              <button @click="openPreview(doc)" class="p-2 text-[var(--color-muted)] hover:text-[var(--color-accent)] cursor-pointer" title="Aperçu">
                <Eye :size="18" />
              </button>
              <a :href="doc.file_url" target="_blank" @click="trackDownload(doc)" class="p-2 text-[var(--color-accent)] no-underline" title="Télécharger">
                <Download :size="18" />
              </a>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- ═══ Preview Modal ═══ -->
    <Teleport to="body">
      <Transition name="modal">
        <div
          v-if="previewDoc"
          class="fixed inset-0 z-[60] flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm"
          @click.self="previewDoc = null"
        >
          <div class="bg-white rounded-2xl shadow-2xl w-full max-w-3xl max-h-[90vh] flex flex-col overflow-hidden animate-modal-in">
            <!-- Header -->
            <div class="flex items-center justify-between p-5 border-b border-[var(--color-border)] shrink-0">
              <div class="flex items-center gap-3 min-w-0">
                <div
                  class="w-10 h-10 rounded-xl flex items-center justify-center shrink-0"
                  :class="kindStyle[getFileKind(previewDoc.file_url)].icon"
                >
                  <component :is="fileIcon(previewDoc.file_url)" :size="20" class="text-white" />
                </div>
                <div class="min-w-0">
                  <h3 class="font-bold text-[var(--color-primary)] truncate">{{ previewDoc.title }}</h3>
                  <p class="text-xs text-[var(--color-muted)]">
                    {{ fileExt(previewDoc.file_url) }} &middot; {{ formatSize(previewDoc.file_size) }} &middot; {{ dayjs(previewDoc.created_at).format('DD MMMM YYYY') }}
                  </p>
                </div>
              </div>
              <button @click="previewDoc = null" class="p-2 rounded-xl hover:bg-[var(--color-surface)] cursor-pointer shrink-0 ml-3">
                <X :size="20" />
              </button>
            </div>

            <!-- Preview body -->
            <div class="flex-1 overflow-auto bg-[var(--color-surface)]">
              <!-- Image: direct display -->
              <div v-if="getFileKind(previewDoc.file_url) === 'image'" class="flex items-center justify-center p-6">
                <img :src="previewDoc.file_url" :alt="previewDoc.title" class="max-w-full max-h-[65vh] object-contain rounded-lg shadow-md" />
              </div>

              <!-- PDF: native browser viewer via preview endpoint -->
              <iframe
                v-else-if="getFileKind(previewDoc.file_url) === 'pdf'"
                :src="previewUrl(previewDoc)"
                class="w-full border-0 min-h-[60vh]"
                style="height: 65vh"
              />

              <!-- Other formats: info + action -->
              <div v-else class="flex flex-col items-center justify-center py-16 gap-5">
                <div
                  class="w-20 h-20 rounded-2xl flex items-center justify-center shadow-lg"
                  :class="kindStyle[getFileKind(previewDoc.file_url)].icon"
                >
                  <component :is="fileIcon(previewDoc.file_url)" :size="40" class="text-white" />
                </div>
                <div class="text-center">
                  <p class="text-[var(--color-primary)] font-semibold text-lg mb-1">Fichier {{ fileExt(previewDoc.file_url) }}</p>
                  <p class="text-[var(--color-muted)] text-sm">
                    L'aperçu n'est pas disponible pour ce type de fichier.
                  </p>
                  <p class="text-xs text-[var(--color-muted)] opacity-60 mt-1">Téléchargez le document pour le consulter.</p>
                </div>
              </div>
            </div>

            <!-- Description -->
            <div v-if="previewDoc.description" class="px-5 py-3 border-t border-[var(--color-border)] shrink-0">
              <p class="text-sm text-[var(--color-muted)] leading-relaxed">{{ previewDoc.description }}</p>
            </div>

            <!-- Footer -->
            <div class="flex items-center justify-between p-5 border-t border-[var(--color-border)] shrink-0 gap-3">
              <div class="text-xs text-[var(--color-muted)] min-w-0">
                <span class="font-medium">{{ categoryLabel[previewDoc.category] ?? previewDoc.category }}</span>
                <span v-if="previewDoc.uploaded_by_name"> &middot; Par {{ previewDoc.uploaded_by_name }}</span>
              </div>
              <div class="flex items-center gap-2 shrink-0">
                <a
                  :href="previewDoc.file_url"
                  target="_blank"
                  class="inline-flex items-center gap-2 px-4 py-2 text-sm font-medium text-[var(--color-primary)] border border-[var(--color-border)] rounded-xl hover:bg-[var(--color-surface)] transition-colors no-underline"
                >
                  <ExternalLink :size="15" />
                  Ouvrir
                </a>
                <a
                  :href="previewDoc.file_url"
                  target="_blank"
                  :download="previewDoc.title"
                  @click="trackDownload(previewDoc)"
                  class="inline-flex items-center gap-2 px-5 py-2 text-sm font-semibold bg-[var(--color-accent)] text-white rounded-xl hover:bg-[var(--color-accent-hover)] transition-colors no-underline"
                >
                  <Download :size="15" />
                  Télécharger
                </a>
              </div>
            </div>
          </div>
        </div>
      </Transition>
    </Teleport>
  </div>
</template>

<style scoped>
.scrollbar-hide { -ms-overflow-style: none; scrollbar-width: none; }
.scrollbar-hide::-webkit-scrollbar { display: none; }

.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.modal-enter-active, .modal-leave-active { transition: opacity 200ms ease; }
.modal-enter-from, .modal-leave-to { opacity: 0; }

@keyframes modal-in {
  from { opacity: 0; transform: scale(0.95) translateY(10px); }
  to { opacity: 1; transform: scale(1) translateY(0); }
}
.animate-modal-in { animation: modal-in 250ms ease-out; }
</style>
