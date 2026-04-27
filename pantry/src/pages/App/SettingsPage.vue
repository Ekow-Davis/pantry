<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { Settings, Sun, Moon, Palette, Bell, ShieldAlert } from 'lucide-vue-next'
import { useAuthStore } from '@/stores/auth'
import { useTheme, accentOptions } from '@/composables/useTheme'
import { useNotificationsStore } from '@/stores/notifications'
import api from '@/composables/useApi'
import ThemeSwitcher from '@/components/general/ThemeSwitcher.vue'

const auth   = useAuthStore()
const { mode, accent, toggleMode, setAccent } = useTheme()
const notify = useNotificationsStore()

const cooldown     = ref(auth.user?.cooldown_days ?? 4)
const assumeCooked = ref(auth.user?.assume_cooked ?? true)
const saving       = ref(false)

async function savePreferences() {
  saving.value = true
  try {
    await api.patch('/api/v1/me/preferences', {
      cooldown_days: cooldown.value,
      assume_cooked: assumeCooked.value,
    })
    await auth.fetchMe()
    notify.success('Preferences saved!')
  } catch {
    notify.error('Failed to save preferences.')
  } finally {
    saving.value = false
  }
}
</script>

<template>
  <div class="max-w-2xl mx-auto">
    <div class="mb-6 animate-fade-up">
      <h1 class="text-3xl font-black mb-1" style="font-family:var(--font-display)">Settings</h1>
    </div>

    <!-- Theme -->
    <div class="card p-6 mb-4 animate-fade-up delay-100">
      <h2 class="text-lg font-bold mb-4 flex items-center gap-2" style="font-family:var(--font-display)">
        <Palette class="w-5 h-5" style="color:var(--color-primary)" /> Appearance
      </h2>
      <div class="flex items-center justify-between mb-5">
        <div>
          <p class="font-medium">Theme</p>
          <p class="text-sm" style="color:var(--color-text-muted)">{{ mode === 'dark' ? 'Dark mode' : 'Light mode' }}</p>
        </div>
        <button @click="toggleMode" class="btn-surface !py-2 !px-4 text-sm">
          <Sun v-if="mode === 'dark'" class="w-4 h-4" />
          <Moon v-else class="w-4 h-4" />
          {{ mode === 'dark' ? 'Light' : 'Dark' }}
        </button>
      </div>
      <div>
        <p class="font-medium mb-2">Accent colour</p>
        <div class="flex gap-3">
          <button
            v-for="opt in accentOptions"
            :key="opt.key"
            @click="setAccent(opt.key)"
            class="flex flex-col items-center gap-1.5 p-2 rounded-xl transition-all"
            :style="accent === opt.key ? 'background:var(--color-surface)' : ''"
          >
            <div class="w-8 h-8 rounded-full border-2"
              :style="`background:${opt.hex}; border-color: ${accent === opt.key ? opt.hex : 'transparent'}; box-shadow: ${accent === opt.key ? `0 0 0 2px var(--color-bg), 0 0 0 4px ${opt.hex}` : 'none'}`"></div>
            <span class="text-[10px] font-medium" style="color:var(--color-text-muted)">{{ opt.label }}</span>
          </button>
        </div>
      </div>
    </div>

    <!-- Planning preferences -->
    <div class="card p-6 mb-4 animate-fade-up delay-200">
      <h2 class="text-lg font-bold mb-4 flex items-center gap-2" style="font-family:var(--font-display)">
        <Settings class="w-5 h-5" style="color:var(--color-primary)" /> Planning Preferences
      </h2>

      <div class="flex flex-col gap-5">
        <div>
          <div class="flex items-center justify-between mb-2">
            <div>
              <p class="font-medium">Cooldown period</p>
              <p class="text-sm" style="color:var(--color-text-muted)">Days before a meal can be recommended again</p>
            </div>
            <span class="text-2xl font-black" style="font-family:var(--font-display); color:var(--color-primary)">{{ cooldown }}</span>
          </div>
          <input v-model="cooldown" type="range" min="1" max="30" class="w-full accent-[var(--color-primary)]" />
          <div class="flex justify-between text-xs mt-1" style="color:var(--color-text-faint)">
            <span>1 day</span><span>30 days</span>
          </div>
        </div>

        <div class="flex items-center justify-between">
          <div>
            <p class="font-medium">Assume cooked if not confirmed</p>
            <p class="text-sm" style="color:var(--color-text-muted)">At end of day, treat unconfirmed slots as cooked</p>
          </div>
          <button
            class="w-12 h-6 rounded-full transition-all relative"
            :style="`background: ${assumeCooked ? 'var(--color-primary)' : 'var(--color-border)'}`"
            @click="assumeCooked = !assumeCooked"
          >
            <span class="absolute top-0.5 w-5 h-5 rounded-full bg-white shadow transition-all"
              :style="`left: ${assumeCooked ? '1.5rem' : '0.125rem'}`"></span>
          </button>
        </div>

        <button class="btn-primary self-end" :disabled="saving" @click="savePreferences">
          <span v-if="saving" class="flex gap-1"><span class="dot-bounce"></span><span class="dot-bounce"></span><span class="dot-bounce"></span></span>
          <template v-else>Save Preferences</template>
        </button>
      </div>
    </div>

    <!-- Account -->
    <div class="card p-6 animate-fade-up delay-300">
      <h2 class="text-lg font-bold mb-4 flex items-center gap-2" style="font-family:var(--font-display)">
        <ShieldAlert class="w-5 h-5" style="color:var(--color-danger)" /> Account
      </h2>
      <div class="flex items-center justify-between">
        <div>
          <p class="font-medium">{{ auth.user?.email }}</p>
          <p class="text-sm" style="color:var(--color-text-muted)">Signed in as {{ auth.user?.username }}</p>
        </div>
        <button class="btn-surface !text-sm !py-2 !px-4" style="color:var(--color-danger)" @click="auth.logout()">
          Sign Out
        </button>
      </div>
    </div>
  </div>
</template>
