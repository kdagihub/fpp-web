<script setup lang="ts">
import { ref } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useAppToast } from '@/composables/useToast'
import { RouterLink, useRouter } from 'vue-router'
import {
  ArrowLeft,
  Lock,
  Eye,
  EyeOff,
  Save,
  Loader2,
  Shield,
  Mail,
} from 'lucide-vue-next'

const authStore = useAuthStore()
const router = useRouter()
const toast = useAppToast()

const showOld = ref(false)
const showNew = ref(false)
const showConfirm = ref(false)
const changingPwd = ref(false)

const pwdForm = ref({
  old_password: '',
  new_password: '',
  new_password_confirm: '',
})

async function handleChangePassword() {
  if (pwdForm.value.new_password !== pwdForm.value.new_password_confirm) {
    toast.error('Erreur', 'Les mots de passe ne correspondent pas.')
    return
  }
  if (pwdForm.value.new_password.length < 8) {
    toast.error('Erreur', 'Le nouveau mot de passe doit comporter au moins 8 caractères.')
    return
  }
  changingPwd.value = true
  try {
    await authStore.changePassword(
      pwdForm.value.old_password,
      pwdForm.value.new_password,
      pwdForm.value.new_password_confirm,
    )
    toast.success('Mot de passe modifié', 'Veuillez vous reconnecter avec votre nouveau mot de passe.')
    setTimeout(() => router.push('/login'), 1500)
  } catch (err: any) {
    const data = err?.response?.data
    const msg = data?.detail || data?.old_password?.[0] || data?.new_password?.[0] || 'Erreur lors du changement de mot de passe.'
    toast.error('Erreur', msg)
  } finally {
    changingPwd.value = false
  }
}
</script>

<template>
  <div>
    <!-- Header -->
    <div class="flex items-center gap-3 mb-8">
      <RouterLink to="/mon-espace" class="w-9 h-9 rounded-xl bg-white border border-gray-200 flex items-center justify-center text-gray-500 hover:text-gray-900 hover:border-gray-300 transition-all no-underline">
        <ArrowLeft :size="18" />
      </RouterLink>
      <div>
        <h1 class="text-xl font-bold text-gray-900">Paramètres</h1>
        <p class="text-xs text-gray-500">Compte et sécurité</p>
      </div>
    </div>

    <div class="max-w-2xl space-y-6">

      <!-- ─── EMAIL STATUS ─── -->
      <div class="bg-white rounded-2xl border border-gray-200/80 p-6 shadow-sm">
        <div class="flex items-center gap-3 mb-4">
          <div class="w-10 h-10 rounded-xl bg-blue-50 flex items-center justify-center">
            <Mail :size="20" class="text-blue-500" />
          </div>
          <div>
            <h3 class="text-sm font-bold text-gray-900">Adresse email</h3>
            <p class="text-xs text-gray-500">{{ authStore.user?.email }}</p>
          </div>
          <span
            v-if="authStore.user?.email_verified"
            class="ml-auto inline-flex items-center gap-1 text-[11px] font-semibold text-green-700 bg-green-50 px-2.5 py-1 rounded-full"
          >
            <Shield :size="12" />
            Vérifié
          </span>
        </div>
      </div>

      <!-- ─── CHANGE PASSWORD ─── -->
      <div class="bg-white rounded-2xl border border-gray-200/80 p-6 shadow-sm">
        <div class="flex items-center gap-3 mb-6">
          <div class="w-10 h-10 rounded-xl bg-amber-50 flex items-center justify-center">
            <Lock :size="20" class="text-amber-600" />
          </div>
          <div>
            <h3 class="text-sm font-bold text-gray-900">Changer le mot de passe</h3>
            <p class="text-xs text-gray-500">Assurez-vous d'utiliser un mot de passe fort</p>
          </div>
        </div>

        <form @submit.prevent="handleChangePassword" class="space-y-4">
          <div>
            <label class="text-[11px] font-semibold text-gray-500 uppercase tracking-wide">Mot de passe actuel</label>
            <div class="relative mt-1">
              <input
                v-model="pwdForm.old_password"
                :type="showOld ? 'text' : 'password'"
                required
                class="w-full px-3 py-2.5 pr-10 text-sm border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-400/50"
              >
              <button
                type="button"
                @click="showOld = !showOld"
                class="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600 cursor-pointer"
              >
                <Eye v-if="!showOld" :size="16" />
                <EyeOff v-else :size="16" />
              </button>
            </div>
          </div>

          <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label class="text-[11px] font-semibold text-gray-500 uppercase tracking-wide">Nouveau mot de passe</label>
              <div class="relative mt-1">
                <input
                  v-model="pwdForm.new_password"
                  :type="showNew ? 'text' : 'password'"
                  required
                  minlength="8"
                  class="w-full px-3 py-2.5 pr-10 text-sm border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-400/50"
                >
                <button
                  type="button"
                  @click="showNew = !showNew"
                  class="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600 cursor-pointer"
                >
                  <Eye v-if="!showNew" :size="16" />
                  <EyeOff v-else :size="16" />
                </button>
              </div>
            </div>
            <div>
              <label class="text-[11px] font-semibold text-gray-500 uppercase tracking-wide">Confirmation</label>
              <div class="relative mt-1">
                <input
                  v-model="pwdForm.new_password_confirm"
                  :type="showConfirm ? 'text' : 'password'"
                  required
                  minlength="8"
                  class="w-full px-3 py-2.5 pr-10 text-sm border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-400/50"
                >
                <button
                  type="button"
                  @click="showConfirm = !showConfirm"
                  class="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600 cursor-pointer"
                >
                  <Eye v-if="!showConfirm" :size="16" />
                  <EyeOff v-else :size="16" />
                </button>
              </div>
            </div>
          </div>

          <div class="pt-2">
            <button
              type="submit"
              :disabled="changingPwd"
              class="inline-flex items-center gap-1.5 px-5 py-2.5 text-sm font-semibold text-white bg-gray-900 rounded-lg hover:bg-gray-800 transition-all cursor-pointer disabled:opacity-50"
            >
              <Loader2 v-if="changingPwd" :size="14" class="animate-spin" />
              <Save v-else :size="14" />
              Mettre à jour
            </button>
          </div>
        </form>
      </div>

      <!-- ─── DANGER ZONE ─── -->
      <div class="bg-white rounded-2xl border border-red-200/50 p-6 shadow-sm">
        <h3 class="text-sm font-bold text-red-600 mb-2">Zone sensible</h3>
        <p class="text-xs text-gray-500 mb-4">
          Pour toute demande de suppression de compte ou de données, contactez-nous à info@fpp-ci.online.
        </p>
      </div>
    </div>
  </div>
</template>
