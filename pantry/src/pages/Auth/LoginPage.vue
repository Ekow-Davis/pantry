<script setup lang="ts">
import { ref } from 'vue'
import { RouterLink, useRoute } from 'vue-router'
import { Mail, Lock, Eye, EyeOff, LogIn } from 'lucide-vue-next'
import { useAuthStore } from '@/stores/auth'
import { useNotificationsStore } from '@/stores/notifications'

const auth   = useAuthStore()
const notify = useNotificationsStore()
const route  = useRoute()

const email    = ref('')
const password = ref('')
const showPw   = ref(false)
const loading  = ref(false)

async function submit() {
  if (!email.value || !password.value) {
    notify.warning('Please fill in all fields.')
    return
  }
  loading.value = true
  try {
    await auth.login(email.value, password.value)
    notify.success('Welcome back!')
  } catch (err: any) {
    notify.error(err.response?.data?.detail || 'Login failed. Please check your credentials.')
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="w-full max-w-md animate-fade-up">
    <div class="card p-8">
      <div class="text-center mb-8">
        <div class="text-5xl mb-3">🍲</div>
        <h1 class="text-3xl font-black mb-1" style="font-family:var(--font-display)">Welcome back</h1>
        <p class="text-sm" style="color:var(--color-text-muted)">Sign in to your MealWise account</p>
      </div>

      <div class="flex flex-col gap-5">
        <div>
          <label class="label">Email</label>
          <div class="relative">
            <Mail class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4" style="color:var(--color-text-faint)" />
            <input v-model="email" type="email" class="input !pl-10" placeholder="you@example.com" @keyup.enter="submit" />
          </div>
        </div>

        <div>
          <label class="label">Password</label>
          <div class="relative">
            <Lock class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4" style="color:var(--color-text-faint)" />
            <input v-model="password" :type="showPw ? 'text' : 'password'" class="input !pl-10 !pr-10" placeholder="••••••••" @keyup.enter="submit" />
            <button class="absolute right-3 top-1/2 -translate-y-1/2" @click="showPw = !showPw" type="button">
              <EyeOff v-if="showPw" class="w-4 h-4" style="color:var(--color-text-faint)" />
              <Eye     v-else        class="w-4 h-4" style="color:var(--color-text-faint)" />
            </button>
          </div>
          <RouterLink to="/auth/forgot-password" class="text-xs mt-1 inline-block no-underline hover:underline" style="color:var(--color-primary)">
            Forgot password?
          </RouterLink>
        </div>

        <button class="btn-primary w-full justify-center" :disabled="loading" @click="submit">
          <span v-if="loading" class="flex gap-1"><span class="dot-bounce"></span><span class="dot-bounce"></span><span class="dot-bounce"></span></span>
          <template v-else><LogIn class="w-4 h-4" /> Sign In</template>
        </button>
      </div>

      <div class="divider" />
      <p class="text-center text-sm" style="color:var(--color-text-muted)">
        Don't have an account?
        <RouterLink to="/auth/register" class="font-semibold no-underline hover:underline" style="color:var(--color-primary)">Create one</RouterLink>
      </p>
    </div>
  </div>
</template>
