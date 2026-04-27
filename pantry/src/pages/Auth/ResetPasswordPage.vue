<script setup lang="ts">
import { ref } from 'vue'
import { RouterLink } from 'vue-router'
import { Lock, Eye, EyeOff } from 'lucide-vue-next'

const password  = ref('')
const confirm   = ref('')
const showPw    = ref(false)
const showCf    = ref(false)
const done      = ref(false)
</script>

<template>
  <div class="w-full max-w-md animate-fade-up">
    <div class="card p-8">
      <div class="text-center mb-8">
        <div class="text-5xl mb-3">🔒</div>
        <h1 class="text-3xl font-black mb-1" style="font-family:var(--font-display)">New password</h1>
        <p class="text-sm" style="color:var(--color-text-muted)">Choose a strong new password</p>
      </div>

      <div v-if="!done" class="flex flex-col gap-5">
        <div>
          <label class="label">New Password</label>
          <div class="relative">
            <Lock class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4" style="color:var(--color-text-faint)" />
            <input v-model="password" :type="showPw ? 'text' : 'password'" class="input !pl-10 !pr-10" placeholder="Min. 8 characters" />
            <button class="absolute right-3 top-1/2 -translate-y-1/2" @click="showPw = !showPw" type="button">
              <EyeOff v-if="showPw" class="w-4 h-4" style="color:var(--color-text-faint)" /><Eye v-else class="w-4 h-4" style="color:var(--color-text-faint)" />
            </button>
          </div>
        </div>
        <div>
          <label class="label">Confirm Password</label>
          <div class="relative">
            <Lock class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4" style="color:var(--color-text-faint)" />
            <input v-model="confirm" :type="showCf ? 'text' : 'password'" class="input !pl-10 !pr-10" placeholder="Repeat password" />
            <button class="absolute right-3 top-1/2 -translate-y-1/2" @click="showCf = !showCf" type="button">
              <EyeOff v-if="showCf" class="w-4 h-4" style="color:var(--color-text-faint)" /><Eye v-else class="w-4 h-4" style="color:var(--color-text-faint)" />
            </button>
          </div>
        </div>
        <button class="btn-primary w-full justify-center" @click="done = true">Set New Password</button>
      </div>

      <div v-else class="text-center py-4">
        <div class="text-5xl mb-3">✅</div>
        <p class="font-semibold mb-2">Password updated!</p>
        <RouterLink to="/auth/login" class="btn-primary inline-flex">Sign In Now</RouterLink>
      </div>
    </div>
  </div>
</template>
