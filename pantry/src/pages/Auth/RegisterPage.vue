<script setup lang="ts">
import { ref } from 'vue'
import { RouterLink, useRouter } from 'vue-router'
import { User, Mail, Lock, Eye, EyeOff, Globe } from 'lucide-vue-next'
import { useAuthStore } from '@/stores/auth'
import { useNotificationsStore } from '@/stores/notifications'

const auth   = useAuthStore()
const notify = useNotificationsStore()
const router = useRouter()

const form    = ref({ username: '', email: '', password: '', country: '' })
const showPw  = ref(false)
const loading = ref(false)

const countries = ['Ghana', 'Nigeria', 'Kenya', 'South Africa', 'United Kingdom', 'United States', 'Canada', 'Australia', 'Other']

async function submit() {
  if (!form.value.username || !form.value.email || !form.value.password) {
    notify.warning('Please fill in all required fields.')
    return
  }
  if (form.value.password.length < 8) {
    notify.warning('Password must be at least 8 characters.')
    return
  }
  loading.value = true
  try {
    await auth.register(form.value)
    notify.success('Account created! Please sign in.')
    router.push('/auth/login')
  } catch (err: any) {
    notify.error(err.response?.data?.detail || 'Registration failed. Please try again.')
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="w-full max-w-md animate-fade-up">
    <div class="card p-8">
      <div class="text-center mb-8">
        <div class="text-5xl mb-3">🥘</div>
        <h1 class="text-3xl font-black mb-1" style="font-family:var(--font-display)">Create account</h1>
        <p class="text-sm" style="color:var(--color-text-muted)">Start planning your meals with MealWise</p>
      </div>

      <div class="flex flex-col gap-4">
        <div>
          <label class="label">Username <span style="color:var(--color-danger)">*</span></label>
          <div class="relative">
            <User class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4" style="color:var(--color-text-faint)" />
            <input v-model="form.username" class="input !pl-10" placeholder="yourname" />
          </div>
        </div>

        <div>
          <label class="label">Email <span style="color:var(--color-danger)">*</span></label>
          <div class="relative">
            <Mail class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4" style="color:var(--color-text-faint)" />
            <input v-model="form.email" type="email" class="input !pl-10" placeholder="you@example.com" />
          </div>
        </div>

        <div>
          <label class="label">Password <span style="color:var(--color-danger)">*</span></label>
          <div class="relative">
            <Lock class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4" style="color:var(--color-text-faint)" />
            <input v-model="form.password" :type="showPw ? 'text' : 'password'" class="input !pl-10 !pr-10" placeholder="Min. 8 characters" />
            <button class="absolute right-3 top-1/2 -translate-y-1/2" @click="showPw = !showPw" type="button">
              <EyeOff v-if="showPw" class="w-4 h-4" style="color:var(--color-text-faint)" />
              <Eye     v-else       class="w-4 h-4" style="color:var(--color-text-faint)" />
            </button>
          </div>
        </div>

        <div>
          <label class="label">Country</label>
          <div class="relative">
            <Globe class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4" style="color:var(--color-text-faint)" />
            <select v-model="form.country" class="input !pl-10">
              <option value="">Select your country (optional)</option>
              <option v-for="c in countries" :key="c" :value="c">{{ c }}</option>
            </select>
          </div>
        </div>

        <button class="btn-primary w-full justify-center mt-2" :disabled="loading" @click="submit">
          <span v-if="loading" class="flex gap-1"><span class="dot-bounce"></span><span class="dot-bounce"></span><span class="dot-bounce"></span></span>
          <template v-else>Create Account</template>
        </button>
      </div>

      <div class="divider" />
      <p class="text-center text-sm" style="color:var(--color-text-muted)">
        Already have an account?
        <RouterLink to="/auth/login" class="font-semibold no-underline hover:underline" style="color:var(--color-primary)">Sign in</RouterLink>
      </p>
    </div>
  </div>
</template>
