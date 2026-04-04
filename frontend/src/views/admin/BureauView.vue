<script setup lang="ts">
import { ref, shallowRef, onMounted, computed } from 'vue'
import api from '@/api'
import { useAppToast } from '@/composables/useToast'
import { getMediaUrl } from '@/utils/media'
import {
  Plus,
  Pencil,
  Trash2,
  GripVertical,
  Users,
  Loader2,
  X,
  Upload,
  Eye,
  EyeOff,
  Save,
} from 'lucide-vue-next'

interface BureauMember {
  id: string
  full_name: string
  title: string
  photo: string | null
  order: number
  is_active: boolean
  created_at: string
  updated_at: string
}

const toast = useAppToast()
const members = ref<BureauMember[]>([])
const loading = ref(true)
const saving = ref(false)

const showDialog = ref(false)
const editingMember = ref<BureauMember | null>(null)
const form = ref({
  full_name: '',
  title: '',
  order: 0,
  is_active: true,
})
const photoFile = shallowRef<File | null>(null)
const photoPreview = ref<string | null>(null)
const photoRemoved = ref(false)

const deleteConfirmId = ref<string | null>(null)
const deleting = ref(false)

const isEditing = computed(() => !!editingMember.value)
const dialogTitle = computed(() => (isEditing.value ? 'Modifier le membre' : 'Ajouter un membre'))

const activeCount = computed(() => members.value.filter((m) => m.is_active).length)

async function fetchMembers() {
  loading.value = true
  try {
    const { data } = await api.get<BureauMember[]>('/admin/bureau/')
    members.value = data
  } catch {
    toast.error('Erreur', 'Impossible de charger les membres du bureau.')
  } finally {
    loading.value = false
  }
}

function openAdd() {
  editingMember.value = null
  form.value = { full_name: '', title: '', order: members.value.length + 1, is_active: true }
  photoFile.value = null
  photoPreview.value = null
  photoRemoved.value = false
  showDialog.value = true
}

function openEdit(member: BureauMember) {
  editingMember.value = member
  form.value = {
    full_name: member.full_name,
    title: member.title,
    order: member.order,
    is_active: member.is_active,
  }
  photoFile.value = null
  photoPreview.value = member.photo ? getMediaUrl(member.photo) : null
  photoRemoved.value = false
  showDialog.value = true
}

function onPhotoChange(event: Event) {
  const input = event.target as HTMLInputElement
  const file = input.files?.[0]
  if (!file) return
  photoFile.value = file
  photoPreview.value = URL.createObjectURL(file)
  photoRemoved.value = false
}

function removePhoto() {
  photoFile.value = null
  photoPreview.value = null
  photoRemoved.value = true
}

async function submitForm() {
  if (!form.value.full_name.trim() || !form.value.title.trim()) {
    toast.warn('Attention', 'Le nom et le titre sont requis.')
    return
  }

  saving.value = true
  const fd = new FormData()
  fd.append('full_name', form.value.full_name)
  fd.append('title', form.value.title)
  fd.append('order', String(form.value.order))
  fd.append('is_active', String(form.value.is_active))
  if (photoFile.value) {
    fd.append('photo', photoFile.value)
  } else if (photoRemoved.value) {
    fd.append('clear_photo', 'true')
  }

  try {
    if (isEditing.value && editingMember.value) {
      await api.patch(`/admin/bureau/${editingMember.value.id}/`, fd)
      toast.success('Modifié', `${form.value.full_name} a été mis à jour.`)
    } else {
      await api.post('/admin/bureau/', fd)
      toast.success('Ajouté', `${form.value.full_name} a été ajouté au bureau.`)
    }
    showDialog.value = false
    await fetchMembers()
  } catch {
    toast.error('Erreur', "L'opération a échoué.")
  } finally {
    saving.value = false
  }
}

async function toggleVisibility(member: BureauMember) {
  try {
    const fd = new FormData()
    fd.append('is_active', String(!member.is_active))
    await api.patch(`/admin/bureau/${member.id}/`, fd)
    member.is_active = !member.is_active
    toast.success('Mis à jour', `${member.full_name} est maintenant ${member.is_active ? 'visible' : 'masqué'}.`)
  } catch {
    toast.error('Erreur', 'Impossible de modifier la visibilité.')
  }
}

function confirmDelete(id: string) {
  deleteConfirmId.value = id
}

async function deleteMember() {
  if (!deleteConfirmId.value) return
  deleting.value = true
  try {
    await api.delete(`/admin/bureau/${deleteConfirmId.value}/`)
    toast.success('Supprimé', 'Le membre a été retiré du bureau.')
    deleteConfirmId.value = null
    await fetchMembers()
  } catch {
    toast.error('Erreur', 'La suppression a échoué.')
  } finally {
    deleting.value = false
  }
}

onMounted(fetchMembers)
</script>

<template>
  <div>
    <!-- Header -->
    <div class="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 mb-8">
      <div>
        <h2 class="font-heading text-2xl font-bold text-[var(--color-primary)]">Bureau National</h2>
        <p class="text-sm text-[var(--color-muted)] mt-1">
          {{ members.length }} membre{{ members.length > 1 ? 's' : '' }}
          <span class="text-[var(--color-accent)]">({{ activeCount }} visible{{ activeCount > 1 ? 's' : '' }})</span>
        </p>
      </div>
      <button
        @click="openAdd"
        class="inline-flex items-center gap-2 px-4 py-2.5 text-sm font-semibold text-white bg-[var(--color-accent)] rounded-lg hover:bg-[var(--color-accent-hover)] transition-colors cursor-pointer"
      >
        <Plus :size="16" />
        Ajouter un membre
      </button>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="flex justify-center py-16">
      <Loader2 :size="32" class="animate-spin text-[var(--color-accent)]" />
    </div>

    <!-- Empty -->
    <div
      v-else-if="members.length === 0"
      class="bg-white border border-[var(--color-border)] rounded-xl p-12 text-center"
    >
      <Users :size="48" class="mx-auto text-[var(--color-muted)] opacity-30 mb-4" />
      <p class="text-[var(--color-muted)] font-medium">Aucun membre du bureau.</p>
      <p class="text-sm text-[var(--color-muted)] mt-1">Ajoutez le premier membre pour le rendre visible sur le site.</p>
    </div>

    <!-- Members grid -->
    <div v-else class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-5">
      <div
        v-for="member in members"
        :key="member.id"
        class="bg-white border rounded-xl overflow-hidden transition-all hover:shadow-[var(--shadow-md)] relative group"
        :class="member.is_active ? 'border-[var(--color-border)]' : 'border-dashed border-gray-300 opacity-60'"
      >
        <!-- Order badge -->
        <div class="absolute top-3 left-3 z-10 flex items-center gap-1 px-2 py-0.5 bg-black/50 backdrop-blur rounded text-xs text-white font-mono">
          <GripVertical :size="12" />
          #{{ member.order }}
        </div>

        <!-- Visibility badge -->
        <div
          v-if="!member.is_active"
          class="absolute top-3 right-3 z-10 px-2 py-0.5 bg-red-500/80 backdrop-blur rounded text-xs text-white font-semibold"
        >
          Masqué
        </div>

        <!-- Photo -->
        <div class="aspect-[4/3] bg-[var(--color-surface)] relative overflow-hidden">
          <img
            v-if="member.photo"
            :src="getMediaUrl(member.photo)"
            :alt="member.full_name"
            class="w-full h-full object-cover object-top"
          />
          <div v-else class="absolute inset-0 flex items-center justify-center">
            <Users :size="40" class="text-[var(--color-muted)] opacity-20" />
          </div>
        </div>

        <!-- Info -->
        <div class="p-4">
          <h3 class="font-heading text-sm font-bold text-[var(--color-primary)] mb-0.5 truncate">
            {{ member.full_name }}
          </h3>
          <p class="text-xs text-[var(--color-accent)] font-semibold uppercase tracking-wide line-clamp-2 leading-relaxed">
            {{ member.title }}
          </p>
        </div>

        <!-- Actions -->
        <div class="flex items-center border-t border-[var(--color-border)] divide-x divide-[var(--color-border)]">
          <button
            @click="openEdit(member)"
            class="flex-1 flex items-center justify-center gap-1.5 py-2.5 text-xs font-medium text-[var(--color-muted)] hover:text-[var(--color-primary)] hover:bg-[var(--color-surface)] transition-colors cursor-pointer"
            title="Modifier"
          >
            <Pencil :size="14" />
            Modifier
          </button>
          <button
            @click="toggleVisibility(member)"
            class="flex-1 flex items-center justify-center gap-1.5 py-2.5 text-xs font-medium transition-colors cursor-pointer"
            :class="member.is_active
              ? 'text-[var(--color-muted)] hover:text-orange-600 hover:bg-orange-50'
              : 'text-green-600 hover:text-green-700 hover:bg-green-50'"
            :title="member.is_active ? 'Masquer' : 'Rendre visible'"
          >
            <EyeOff v-if="member.is_active" :size="14" />
            <Eye v-else :size="14" />
            {{ member.is_active ? 'Masquer' : 'Afficher' }}
          </button>
          <button
            @click="confirmDelete(member.id)"
            class="flex-1 flex items-center justify-center gap-1.5 py-2.5 text-xs font-medium text-[var(--color-muted)] hover:text-red-600 hover:bg-red-50 transition-colors cursor-pointer"
            title="Supprimer"
          >
            <Trash2 :size="14" />
            Supprimer
          </button>
        </div>
      </div>
    </div>

    <!-- ═══ Add / Edit Dialog ═══ -->
    <Teleport to="body">
      <Transition
        enter-active-class="transition-opacity duration-200"
        enter-from-class="opacity-0"
        enter-to-class="opacity-100"
        leave-active-class="transition-opacity duration-150"
        leave-from-class="opacity-100"
        leave-to-class="opacity-0"
      >
        <div
          v-if="showDialog"
          class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/40 backdrop-blur-sm"
          @click.self="showDialog = false"
        >
          <div class="bg-white rounded-2xl shadow-xl w-full max-w-lg max-h-[90vh] overflow-y-auto">
            <!-- Dialog header -->
            <div class="flex items-center justify-between p-6 pb-0">
              <h3 class="font-heading text-lg font-bold text-[var(--color-primary)]">{{ dialogTitle }}</h3>
              <button @click="showDialog = false" class="p-1.5 rounded-lg hover:bg-[var(--color-surface)] transition-colors cursor-pointer">
                <X :size="18" />
              </button>
            </div>

            <form @submit.prevent="submitForm" class="p-6 space-y-5">
              <!-- Photo upload -->
              <div>
                <label class="block text-sm font-medium text-[var(--color-primary)] mb-2">Photo</label>
                <div class="flex items-center gap-4">
                  <div class="w-20 h-20 rounded-xl bg-[var(--color-surface)] border border-[var(--color-border)] overflow-hidden flex items-center justify-center shrink-0">
                    <img v-if="photoPreview" :src="photoPreview" alt="" class="w-full h-full object-cover" />
                    <Users v-else :size="28" class="text-[var(--color-muted)] opacity-30" />
                  </div>
                  <div class="flex flex-col gap-2">
                    <label class="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-[var(--color-accent)] bg-[var(--color-accent-light)] rounded-lg cursor-pointer hover:bg-[var(--color-accent)]/20 transition-colors">
                      <Upload :size="14" />
                      Choisir une photo
                      <input type="file" accept="image/*" class="hidden" @change="onPhotoChange" />
                    </label>
                    <button
                      v-if="photoPreview"
                      type="button"
                      @click="removePhoto"
                      class="text-xs text-red-500 hover:text-red-700 text-left cursor-pointer"
                    >
                      Retirer la photo
                    </button>
                  </div>
                </div>
              </div>

              <!-- Full name -->
              <div>
                <label for="bf-name" class="block text-sm font-medium text-[var(--color-primary)] mb-1.5">
                  Nom complet <span class="text-red-500">*</span>
                </label>
                <input
                  id="bf-name"
                  v-model="form.full_name"
                  type="text"
                  required
                  class="w-full px-3.5 py-2.5 text-sm border border-[var(--color-border)] rounded-lg focus:ring-2 focus:ring-[var(--color-accent)]/30 focus:border-[var(--color-accent)] outline-none transition-all"
                  placeholder="Ex: Dabé Nogbo Wanaminou"
                />
              </div>

              <!-- Title -->
              <div>
                <label for="bf-title" class="block text-sm font-medium text-[var(--color-primary)] mb-1.5">
                  Fonction / Titre <span class="text-red-500">*</span>
                </label>
                <input
                  id="bf-title"
                  v-model="form.title"
                  type="text"
                  required
                  class="w-full px-3.5 py-2.5 text-sm border border-[var(--color-border)] rounded-lg focus:ring-2 focus:ring-[var(--color-accent)]/30 focus:border-[var(--color-accent)] outline-none transition-all"
                  placeholder="Ex: Président"
                />
              </div>

              <!-- Order + visibility -->
              <div class="grid grid-cols-2 gap-4">
                <div>
                  <label for="bf-order" class="block text-sm font-medium text-[var(--color-primary)] mb-1.5">
                    Ordre d'affichage
                  </label>
                  <input
                    id="bf-order"
                    v-model.number="form.order"
                    type="number"
                    min="0"
                    class="w-full px-3.5 py-2.5 text-sm border border-[var(--color-border)] rounded-lg focus:ring-2 focus:ring-[var(--color-accent)]/30 focus:border-[var(--color-accent)] outline-none transition-all"
                  />
                </div>
                <div class="flex items-end">
                  <label class="flex items-center gap-2.5 cursor-pointer select-none">
                    <input
                      v-model="form.is_active"
                      type="checkbox"
                      class="w-4 h-4 rounded border-gray-300 text-[var(--color-accent)] focus:ring-[var(--color-accent)]"
                    />
                    <span class="text-sm font-medium text-[var(--color-primary)]">Visible sur le site</span>
                  </label>
                </div>
              </div>

              <!-- Actions -->
              <div class="flex items-center justify-end gap-3 pt-2">
                <button
                  type="button"
                  @click="showDialog = false"
                  class="px-4 py-2.5 text-sm font-medium text-[var(--color-muted)] hover:text-[var(--color-primary)] transition-colors cursor-pointer"
                >
                  Annuler
                </button>
                <button
                  type="submit"
                  :disabled="saving"
                  class="inline-flex items-center gap-2 px-5 py-2.5 text-sm font-semibold text-white bg-[var(--color-accent)] rounded-lg hover:bg-[var(--color-accent-hover)] transition-colors cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <Loader2 v-if="saving" :size="14" class="animate-spin" />
                  <Save v-else :size="14" />
                  {{ isEditing ? 'Enregistrer' : 'Ajouter' }}
                </button>
              </div>
            </form>
          </div>
        </div>
      </Transition>
    </Teleport>

    <!-- ═══ Delete Confirmation Dialog ═══ -->
    <Teleport to="body">
      <Transition
        enter-active-class="transition-opacity duration-200"
        enter-from-class="opacity-0"
        enter-to-class="opacity-100"
        leave-active-class="transition-opacity duration-150"
        leave-from-class="opacity-100"
        leave-to-class="opacity-0"
      >
        <div
          v-if="deleteConfirmId"
          class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/40 backdrop-blur-sm"
          @click.self="deleteConfirmId = null"
        >
          <div class="bg-white rounded-2xl shadow-xl w-full max-w-sm p-6 text-center">
            <div class="w-12 h-12 rounded-full bg-red-100 flex items-center justify-center mx-auto mb-4">
              <Trash2 :size="22" class="text-red-600" />
            </div>
            <h3 class="font-heading text-lg font-bold text-[var(--color-primary)] mb-2">Confirmer la suppression</h3>
            <p class="text-sm text-[var(--color-muted)] mb-6">
              Cette action est irréversible. Le membre sera définitivement retiré du bureau.
            </p>
            <div class="flex items-center justify-center gap-3">
              <button
                @click="deleteConfirmId = null"
                class="px-4 py-2.5 text-sm font-medium text-[var(--color-muted)] hover:text-[var(--color-primary)] transition-colors cursor-pointer"
              >
                Annuler
              </button>
              <button
                @click="deleteMember"
                :disabled="deleting"
                class="inline-flex items-center gap-2 px-5 py-2.5 text-sm font-semibold text-white bg-red-600 rounded-lg hover:bg-red-700 transition-colors cursor-pointer disabled:opacity-50"
              >
                <Loader2 v-if="deleting" :size="14" class="animate-spin" />
                Supprimer
              </button>
            </div>
          </div>
        </div>
      </Transition>
    </Teleport>
  </div>
</template>
