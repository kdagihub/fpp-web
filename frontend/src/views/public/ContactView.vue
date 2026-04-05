<script setup lang="ts">
import { ref } from 'vue'
import { useSettingsStore } from '@/stores/settings'
import { useAppToast } from '@/composables/useToast'
import api from '@/api'
import { VueTelInput } from 'vue-tel-input'
import 'vue-tel-input/vue-tel-input.css'
import {
  Mail,
  Phone,
  MapPin,
  Send,
  Loader2,
  Facebook,
  Twitter,
  Instagram,
  Youtube,
  Clock,
  Headset,
} from 'lucide-vue-next'

const settingsStore = useSettingsStore()
const toast = useAppToast()

const form = ref({
  name: '',
  email: '',
  phone: '',
  subject: '',
  message: '',
})

const phoneValid = ref(false)
const phoneTouched = ref(false)

function onPhoneValidate(validation: any) {
  phoneValid.value = !!validation.valid
}

const submitting = ref(false)
const submitted = ref(false)

async function handleSubmit() {
  phoneTouched.value = true
  if (!form.value.phone || !phoneValid.value) {
    toast.error('Erreur', !form.value.phone ? 'Le numéro de téléphone est obligatoire.' : 'Numéro de téléphone invalide.')
    return
  }
  submitting.value = true
  try {
    await api.post('/public/contact/', {
      name: form.value.name,
      email: form.value.email,
      phone: form.value.phone,
      subject: form.value.subject,
      message: form.value.message,
    })
    toast.success('Message envoyé', 'Nous vous répondrons dans les plus brefs délais.')
    submitted.value = true
  } catch (err: any) {
    const msg = err?.response?.data?.detail || 'Erreur lors de l\'envoi du message.'
    toast.error('Erreur', msg)
  } finally {
    submitting.value = false
  }
}

const socials = [
  { key: 'facebook_url', icon: Facebook, label: 'Facebook' },
  { key: 'twitter_url', icon: Twitter, label: 'X / Twitter' },
  { key: 'instagram_url', icon: Instagram, label: 'Instagram' },
  { key: 'youtube_url', icon: Youtube, label: 'YouTube' },
] as const
</script>

<template>
  <div>
    <!-- ════════════════════ HERO ════════════════════ -->
    <section class="bg-[var(--color-primary)] py-16 md:py-20">
      <div class="mx-auto max-w-[var(--container-xl)] px-6">
        <p class="font-heading text-xs font-bold uppercase tracking-[0.15em] text-[var(--color-accent)] mb-3">
          Échangeons
        </p>
        <h1 class="font-heading text-3xl md:text-4xl lg:text-5xl font-extrabold text-white leading-tight mb-4">
          Contactez-nous
        </h1>
        <p class="text-white/60 max-w-xl">
          Une question, une suggestion ou une demande ? Notre équipe est à votre écoute.
        </p>
      </div>
    </section>

    <!-- ════════════════════ FORM + INFO ════════════════════ -->
    <section class="bg-[var(--color-surface)] py-16 md:py-20">
      <div class="mx-auto max-w-[var(--container-xl)] px-6">
        <div class="grid grid-cols-1 lg:grid-cols-12 gap-10">

          <!-- Formulaire -->
          <div class="lg:col-span-7">
            <div class="bg-white border border-[var(--color-border)] rounded-xl p-8 md:p-10">
              <h2 class="font-heading text-xl font-extrabold text-[var(--color-primary)] mb-6">
                Envoyez-nous un message
              </h2>

              <div v-if="submitted" class="text-center py-10">
                <div class="w-14 h-14 rounded-full bg-emerald-50 flex items-center justify-center mx-auto mb-4">
                  <Send :size="24" class="text-emerald-500" />
                </div>
                <h3 class="font-heading text-lg font-bold text-[var(--color-primary)] mb-2">
                  Message envoyé !
                </h3>
                <p class="text-sm text-[var(--color-muted)]">
                  Merci pour votre message. Nous vous répondrons dans les meilleurs délais.
                </p>
                <button
                  class="mt-6 px-6 py-2.5 font-heading text-sm font-bold text-[var(--color-accent)] border-2 border-[var(--color-accent)] rounded-sm cursor-pointer hover:bg-[var(--color-accent)] hover:text-white transition-all"
                  @click="submitted = false; phoneTouched = false; phoneValid = false; form = { name: '', email: '', phone: '', subject: '', message: '' }"
                >
                  Envoyer un autre message
                </button>
              </div>

              <form v-else @submit.prevent="handleSubmit" class="space-y-5">
                <div class="grid grid-cols-1 sm:grid-cols-2 gap-5">
                  <div>
                    <label class="block font-heading text-xs font-bold uppercase tracking-[0.06em] text-[var(--color-muted)] mb-1.5">Nom complet *</label>
                    <input v-model="form.name" required type="text" class="w-full px-4 py-3 border border-[var(--color-border)] rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-[var(--color-accent)] transition">
                  </div>
                  <div>
                    <label class="block font-heading text-xs font-bold uppercase tracking-[0.06em] text-[var(--color-muted)] mb-1.5">Email *</label>
                    <input v-model="form.email" required type="email" class="w-full px-4 py-3 border border-[var(--color-border)] rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-[var(--color-accent)] transition">
                  </div>
                </div>

                <div class="grid grid-cols-1 sm:grid-cols-2 gap-5">
                  <div class="sm:col-span-2 md:col-span-1">
                    <label class="block font-heading text-xs font-bold uppercase tracking-[0.06em] text-[var(--color-muted)] mb-1.5">Téléphone *</label>
                    <vue-tel-input
                      v-model="form.phone"
                      mode="international"
                      default-country="CI"
                      :dropdown-options="{ showDialCodeInSelection: true, showFlags: true, showSearchBox: true }"
                      :input-options="{ placeholder: '07 01 02 03 04', styleClasses: 'text-sm' }"
                      :class="['vue-tel-input--custom', { 'vue-tel-input--error': phoneTouched && (!form.phone || !phoneValid) }]"
                      @validate="onPhoneValidate"
                      @blur="phoneTouched = true"
                    />
                    <p v-if="phoneTouched && !form.phone" class="mt-1 text-xs text-red-500">Le numéro de téléphone est obligatoire.</p>
                    <p v-else-if="phoneTouched && form.phone && !phoneValid" class="mt-1 text-xs text-red-500">Numéro de téléphone invalide.</p>
                  </div>
                  <div class="sm:col-span-2 md:col-span-1">
                    <label class="block font-heading text-xs font-bold uppercase tracking-[0.06em] text-[var(--color-muted)] mb-1.5">Sujet *</label>
                    <input v-model="form.subject" required type="text" class="w-full px-4 py-3 border border-[var(--color-border)] rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-[var(--color-accent)] transition">
                  </div>
                </div>

                <div>
                  <label class="block font-heading text-xs font-bold uppercase tracking-[0.06em] text-[var(--color-muted)] mb-1.5">Message *</label>
                  <textarea v-model="form.message" required rows="5" class="w-full px-4 py-3 border border-[var(--color-border)] rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-[var(--color-accent)] transition resize-none" placeholder="Votre message..."></textarea>
                </div>

                <button
                  type="submit"
                  :disabled="submitting"
                  class="w-full flex items-center justify-center gap-2 px-6 py-3.5 font-heading text-sm font-bold uppercase tracking-[0.04em] bg-[var(--color-accent)] text-white rounded-lg transition-all hover:bg-[var(--color-accent-hover)] cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <Loader2 v-if="submitting" :size="18" class="animate-spin" />
                  <template v-else>
                    Envoyer
                    <Send :size="16" />
                  </template>
                </button>
              </form>
            </div>
          </div>

          <!-- Coordonnées -->
          <div class="lg:col-span-5">
            <div class="bg-white border border-[var(--color-border)] rounded-xl p-8 md:p-10 space-y-8">
              <h2 class="font-heading text-xl font-extrabold text-[var(--color-primary)]">
                Nos coordonnées
              </h2>

              <div v-if="settingsStore.settings?.contact_email" class="flex items-start gap-4">
                <div class="w-10 h-10 rounded-lg bg-[var(--color-accent-light)] flex items-center justify-center shrink-0">
                  <Mail :size="18" class="text-[var(--color-accent)]" />
                </div>
                <div>
                  <p class="font-heading text-xs font-bold uppercase tracking-[0.06em] text-[var(--color-muted)] mb-1">Email</p>
                  <a :href="`mailto:${settingsStore.settings.contact_email}`" class="text-sm font-medium text-[var(--color-primary)] no-underline hover:text-[var(--color-accent)] transition-colors">
                    {{ settingsStore.settings.contact_email }}
                  </a>
                </div>
              </div>

              <div v-if="settingsStore.settings?.whatsapp_number" class="flex items-start gap-4">
                <div class="w-10 h-10 rounded-lg bg-[var(--color-accent-light)] flex items-center justify-center shrink-0">
                  <Phone :size="18" class="text-[var(--color-accent)]" />
                </div>
                <div>
                  <p class="font-heading text-xs font-bold uppercase tracking-[0.06em] text-[var(--color-muted)] mb-1">WhatsApp</p>
                  <a :href="`https://wa.me/${settingsStore.settings.whatsapp_number.replace(/[^0-9+]/g, '')}`" target="_blank" class="text-sm font-medium text-[var(--color-primary)] no-underline hover:text-[var(--color-accent)] transition-colors">
                    {{ settingsStore.settings.whatsapp_number }}
                  </a>
                </div>
              </div>

              <div v-if="settingsStore.settings?.address" class="flex items-start gap-4">
                <div class="w-10 h-10 rounded-lg bg-[var(--color-accent-light)] flex items-center justify-center shrink-0">
                  <MapPin :size="18" class="text-[var(--color-accent)]" />
                </div>
                <div>
                  <p class="font-heading text-xs font-bold uppercase tracking-[0.06em] text-[var(--color-muted)] mb-1">Adresse</p>
                  <p class="text-sm font-medium text-[var(--color-primary)] leading-relaxed">
                    {{ settingsStore.settings.address }}
                  </p>
                </div>
              </div>

              <!-- Disponibilité -->
              <div class="bg-[var(--color-accent-light)] border border-[var(--color-accent)]/15 rounded-xl p-5">
                <div class="flex items-center gap-3 mb-3">
                  <div class="w-9 h-9 rounded-lg bg-white flex items-center justify-center shrink-0">
                    <Headset :size="18" class="text-[var(--color-accent)]" />
                  </div>
                  <p class="font-heading text-sm font-bold text-[var(--color-primary)]">Secrétariat disponible 24h/24, 7j/7</p>
                </div>
                <div class="flex items-start gap-2 ml-12">
                  <Clock :size="13" class="text-[var(--color-muted)] shrink-0 mt-0.5" />
                  <p class="text-xs text-[var(--color-muted)] leading-relaxed">
                    Le délai de réponse peut varier selon le volume de demandes. Nous nous engageons à traiter chaque message dans les meilleurs délais.
                  </p>
                </div>
              </div>

              <!-- Réseaux sociaux -->
              <div>
                <p class="font-heading text-xs font-bold uppercase tracking-[0.06em] text-[var(--color-muted)] mb-4">
                  Suivez-nous
                </p>
                <div class="flex gap-3">
                  <template v-for="social in socials" :key="social.key">
                    <a
                      v-if="settingsStore.settings?.[social.key]"
                      :href="(settingsStore.settings as any)[social.key]"
                      target="_blank"
                      rel="noopener"
                      class="w-10 h-10 rounded-lg bg-[var(--color-surface)] flex items-center justify-center text-[var(--color-muted)] hover:bg-[var(--color-accent)] hover:text-white transition-all no-underline"
                      :title="social.label"
                    >
                      <component :is="social.icon" :size="18" />
                    </a>
                  </template>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>
