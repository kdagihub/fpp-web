<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import api from '@/api'
import {
  AlertTriangle,
  ShieldAlert,
  Loader2,
  X,
  Trash2,
  CheckCircle,
} from 'lucide-vue-next'

const router = useRouter()
const authStore = useAuthStore()

type Step = 'idle' | 'warning' | 'code' | 'confirm' | 'loading' | 'done' | 'error'

const step = ref<Step>('idle')
const code = ref('')
const confirmText = ref('')
const errorMessage = ref('')

const CONFIRMATION_PHRASE = 'URGENCE SUPPRESSION'
const isConfirmValid = computed(() => confirmText.value === CONFIRMATION_PHRASE)

function openWarning() {
  step.value = 'warning'
}

function proceedToCode() {
  step.value = 'code'
  code.value = ''
}

function proceedToConfirm() {
  if (!code.value.trim()) return
  step.value = 'confirm'
  confirmText.value = ''
}

function cancel() {
  step.value = 'idle'
  code.value = ''
  confirmText.value = ''
  errorMessage.value = ''
}

async function executePurge() {
  if (!isConfirmValid.value) return
  step.value = 'loading'
  errorMessage.value = ''

  try {
    await api.post('/emergency/purge/', {
      code: code.value,
      confirmation: CONFIRMATION_PHRASE,
    })
    step.value = 'done'
    setTimeout(() => {
      authStore.logout()
    }, 5000)
  } catch (err: any) {
    step.value = 'error'
    errorMessage.value =
      err?.response?.data?.detail ||
      err?.response?.data?.code?.[0] ||
      'Une erreur est survenue lors de la procédure.'
  }
}
</script>

<template>
  <div class="max-w-2xl">
    <h2 class="text-2xl font-bold text-gray-900 mb-2">Procédure d'urgence</h2>
    <p class="text-sm text-gray-500 mb-8">
      Zone de sécurité critique réservée aux opérateurs d'urgence autorisés.
    </p>

    <!-- ═══ DANGER ZONE ═══ -->
    <div class="rounded-xl border-2 border-red-200 bg-red-50/50 p-6">
      <div class="flex items-start gap-4">
        <div class="w-12 h-12 rounded-xl bg-red-100 flex items-center justify-center shrink-0">
          <ShieldAlert :size="24" class="text-red-600" />
        </div>
        <div class="flex-1 min-w-0">
          <h3 class="text-base font-bold text-red-900">Zone de danger</h3>
          <p class="text-sm text-red-700 mt-1 leading-relaxed">
            Cette action va exporter puis <strong>supprimer définitivement</strong> toutes les données
            sensibles des utilisateurs et membres du parti. Les données chiffrées seront envoyées
            aux adresses email de sécurité configurées avant la suppression.
          </p>
          <button
            @click="openWarning"
            :disabled="step !== 'idle'"
            class="mt-5 inline-flex items-center gap-2 px-5 py-2.5 text-sm font-semibold text-white bg-red-600 rounded-lg hover:bg-red-700 transition-colors cursor-pointer disabled:opacity-40 disabled:cursor-not-allowed"
          >
            <Trash2 :size="16" />
            Lancer la procédure d'urgence
          </button>
        </div>
      </div>
    </div>

    <!-- ═══ MODAL BACKDROP ═══ -->
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
          v-if="step !== 'idle'"
          class="fixed inset-0 bg-black/50 backdrop-blur-sm z-[100] flex items-center justify-center p-4"
          @click.self="step === 'loading' ? null : cancel()"
        >
          <!-- ═══ MODAL 1 — AVERTISSEMENT ═══ -->
          <Transition
            enter-active-class="transition-all duration-200 ease-out"
            enter-from-class="opacity-0 scale-95"
            enter-to-class="opacity-100 scale-100"
            leave-active-class="transition-all duration-150 ease-in"
            leave-from-class="opacity-100 scale-100"
            leave-to-class="opacity-0 scale-95"
          >
            <div
              v-if="step === 'warning'"
              class="bg-white rounded-2xl shadow-2xl max-w-md w-full p-6 relative"
            >
              <button @click="cancel" class="absolute top-4 right-4 p-1 text-gray-400 hover:text-gray-600 cursor-pointer">
                <X :size="20" />
              </button>
              <div class="flex flex-col items-center text-center">
                <div class="w-16 h-16 rounded-full bg-amber-100 flex items-center justify-center mb-4">
                  <AlertTriangle :size="32" class="text-amber-600" />
                </div>
                <h3 class="text-lg font-bold text-gray-900 mb-2">Attention — Opération critique</h3>
                <p class="text-sm text-gray-600 leading-relaxed">
                  Vous accédez à une opération qui va <strong class="text-red-600">supprimer
                  toutes les données sensibles</strong> du parti politique, incluant les comptes
                  utilisateurs et les profils de tous les membres.
                </p>
                <p class="text-sm text-gray-600 mt-3 leading-relaxed">
                  Les données seront exportées et envoyées aux adresses de sécurité
                  avant la suppression. Cette action est <strong>irréversible</strong>.
                </p>
              </div>
              <div class="flex gap-3 mt-6">
                <button
                  @click="cancel"
                  class="flex-1 py-2.5 text-sm font-semibold text-gray-700 bg-gray-100 rounded-xl hover:bg-gray-200 transition-colors cursor-pointer"
                >
                  Annuler
                </button>
                <button
                  @click="proceedToCode"
                  class="flex-1 py-2.5 text-sm font-semibold text-white bg-red-600 rounded-xl hover:bg-red-700 transition-colors cursor-pointer"
                >
                  Continuer
                </button>
              </div>
            </div>
          </Transition>

          <!-- ═══ FORMULAIRE CODE ═══ -->
          <Transition
            enter-active-class="transition-all duration-200 ease-out"
            enter-from-class="opacity-0 scale-95"
            enter-to-class="opacity-100 scale-100"
            leave-active-class="transition-all duration-150 ease-in"
            leave-from-class="opacity-100 scale-100"
            leave-to-class="opacity-0 scale-95"
          >
            <div
              v-if="step === 'code'"
              class="bg-white rounded-2xl shadow-2xl max-w-md w-full p-6 relative"
            >
              <button @click="cancel" class="absolute top-4 right-4 p-1 text-gray-400 hover:text-gray-600 cursor-pointer">
                <X :size="20" />
              </button>
              <div class="flex flex-col items-center text-center mb-5">
                <div class="w-16 h-16 rounded-full bg-red-100 flex items-center justify-center mb-4">
                  <ShieldAlert :size="32" class="text-red-600" />
                </div>
                <h3 class="text-lg font-bold text-gray-900 mb-1">Code d'urgence requis</h3>
                <p class="text-sm text-gray-500">
                  Entrez le code reçu par email dans les dernières 24 heures.
                </p>
              </div>
              <div>
                <label class="block text-xs font-semibold text-gray-500 uppercase tracking-wide mb-1.5">
                  Code d'urgence
                </label>
                <input
                  v-model="code"
                  type="password"
                  placeholder="••••••••••••"
                  autocomplete="off"
                  class="w-full px-4 py-3 text-center text-lg font-mono tracking-[0.2em] border-2 border-gray-200 rounded-xl focus:outline-none focus:border-red-400 focus:ring-2 focus:ring-red-100 transition-all"
                  @keydown.enter="proceedToConfirm"
                >
              </div>
              <div class="flex gap-3 mt-5">
                <button
                  @click="cancel"
                  class="flex-1 py-2.5 text-sm font-semibold text-gray-700 bg-gray-100 rounded-xl hover:bg-gray-200 transition-colors cursor-pointer"
                >
                  Annuler
                </button>
                <button
                  @click="proceedToConfirm"
                  :disabled="!code.trim()"
                  class="flex-1 py-2.5 text-sm font-semibold text-white bg-red-600 rounded-xl hover:bg-red-700 transition-colors cursor-pointer disabled:opacity-40 disabled:cursor-not-allowed"
                >
                  Valider
                </button>
              </div>
            </div>
          </Transition>

          <!-- ═══ MODAL 2 — CONFIRMATION FINALE ═══ -->
          <Transition
            enter-active-class="transition-all duration-200 ease-out"
            enter-from-class="opacity-0 scale-95"
            enter-to-class="opacity-100 scale-100"
            leave-active-class="transition-all duration-150 ease-in"
            leave-from-class="opacity-100 scale-100"
            leave-to-class="opacity-0 scale-95"
          >
            <div
              v-if="step === 'confirm'"
              class="bg-white rounded-2xl shadow-2xl max-w-md w-full p-6 relative"
            >
              <button @click="cancel" class="absolute top-4 right-4 p-1 text-gray-400 hover:text-gray-600 cursor-pointer">
                <X :size="20" />
              </button>
              <div class="flex flex-col items-center text-center mb-5">
                <div class="w-16 h-16 rounded-full bg-red-600 flex items-center justify-center mb-4">
                  <AlertTriangle :size="32" class="text-white" />
                </div>
                <h3 class="text-lg font-bold text-red-900 mb-2">ACTION IRRÉVERSIBLE</h3>
                <div class="text-sm text-gray-600 leading-relaxed text-left space-y-1.5">
                  <p>Cette action va :</p>
                  <ul class="list-disc list-inside space-y-1 text-gray-700">
                    <li>Exporter et chiffrer les données membres</li>
                    <li>Envoyer le backup aux adresses d'urgence</li>
                    <li class="text-red-600 font-semibold">SUPPRIMER toutes les données sensibles</li>
                  </ul>
                </div>
              </div>
              <div>
                <label class="block text-xs font-semibold text-gray-500 uppercase tracking-wide mb-1.5">
                  Tapez « {{ CONFIRMATION_PHRASE }} » pour confirmer
                </label>
                <input
                  v-model="confirmText"
                  type="text"
                  :placeholder="CONFIRMATION_PHRASE"
                  autocomplete="off"
                  spellcheck="false"
                  class="w-full px-4 py-3 text-center text-sm font-semibold border-2 rounded-xl transition-all"
                  :class="[
                    confirmText && isConfirmValid
                      ? 'border-red-400 ring-2 ring-red-100 text-red-700'
                      : 'border-gray-200 focus:border-gray-300 focus:ring-2 focus:ring-gray-100'
                  ]"
                  @keydown.enter="isConfirmValid && executePurge()"
                >
              </div>
              <div class="flex gap-3 mt-5">
                <button
                  @click="cancel"
                  class="flex-1 py-2.5 text-sm font-semibold text-gray-700 bg-gray-100 rounded-xl hover:bg-gray-200 transition-colors cursor-pointer"
                >
                  Annuler
                </button>
                <button
                  @click="executePurge"
                  :disabled="!isConfirmValid"
                  class="flex-1 py-2.5 text-sm font-semibold text-white bg-red-600 rounded-xl hover:bg-red-700 transition-colors cursor-pointer disabled:opacity-40 disabled:cursor-not-allowed"
                >
                  Confirmer la suppression
                </button>
              </div>
            </div>
          </Transition>

          <!-- ═══ LOADING ═══ -->
          <Transition
            enter-active-class="transition-all duration-200 ease-out"
            enter-from-class="opacity-0 scale-95"
            enter-to-class="opacity-100 scale-100"
          >
            <div
              v-if="step === 'loading'"
              class="bg-white rounded-2xl shadow-2xl max-w-sm w-full p-8 text-center"
            >
              <Loader2 :size="48" class="text-red-500 animate-spin mx-auto mb-4" />
              <h3 class="text-lg font-bold text-gray-900 mb-2">Procédure en cours…</h3>
              <p class="text-sm text-gray-500">
                Export, chiffrement et envoi des données en cours.
                Ne fermez pas cette page.
              </p>
            </div>
          </Transition>

          <!-- ═══ SUCCÈS ═══ -->
          <Transition
            enter-active-class="transition-all duration-200 ease-out"
            enter-from-class="opacity-0 scale-95"
            enter-to-class="opacity-100 scale-100"
          >
            <div
              v-if="step === 'done'"
              class="bg-white rounded-2xl shadow-2xl max-w-sm w-full p-8 text-center"
            >
              <div class="w-16 h-16 rounded-full bg-green-100 flex items-center justify-center mx-auto mb-4">
                <CheckCircle :size="32" class="text-green-600" />
              </div>
              <h3 class="text-lg font-bold text-gray-900 mb-2">Procédure terminée</h3>
              <p class="text-sm text-gray-500">
                Les données ont été exportées, chiffrées et envoyées.
                La base de données a été purgée. Vous allez être déconnecté…
              </p>
            </div>
          </Transition>

          <!-- ═══ ERREUR ═══ -->
          <Transition
            enter-active-class="transition-all duration-200 ease-out"
            enter-from-class="opacity-0 scale-95"
            enter-to-class="opacity-100 scale-100"
          >
            <div
              v-if="step === 'error'"
              class="bg-white rounded-2xl shadow-2xl max-w-sm w-full p-8 text-center"
            >
              <div class="w-16 h-16 rounded-full bg-red-100 flex items-center justify-center mx-auto mb-4">
                <X :size="32" class="text-red-600" />
              </div>
              <h3 class="text-lg font-bold text-gray-900 mb-2">Échec de la procédure</h3>
              <p class="text-sm text-red-600 font-medium mb-4">{{ errorMessage }}</p>
              <button
                @click="cancel"
                class="px-6 py-2.5 text-sm font-semibold text-gray-700 bg-gray-100 rounded-xl hover:bg-gray-200 transition-colors cursor-pointer"
              >
                Fermer
              </button>
            </div>
          </Transition>
        </div>
      </Transition>
    </Teleport>
  </div>
</template>
