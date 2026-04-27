<script setup lang="ts">
import { ref } from 'vue'
import { RouterLink } from 'vue-router'
import { Mail, Send } from 'lucide-vue-next'

const email = ref('')
const sent  = ref(false)
</script>

<template>
  <div class="w-full max-w-md animate-fade-up">
    <div class="card p-8">
      <div class="text-center mb-8">
        <div class="text-5xl mb-3">🔑</div>
        <h1 class="text-3xl font-black mb-1" style="font-family:var(--font-display)">Reset password</h1>
        <p class="text-sm" style="color:var(--color-text-muted)">Enter your email and we'll send a reset link</p>
      </div>

      <div v-if="!sent" class="flex flex-col gap-5">
        <div>
          <label class="label">Email</label>
          <div class="relative">
            <Mail class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4" style="color:var(--color-text-faint)" />
            <input v-model="email" type="email" class="input !pl-10" placeholder="you@example.com" />
          </div>
        </div>
        <button class="btn-primary w-full justify-center" @click="sent = true">
          Send Reset Link <Send class="w-4 h-4" />
        </button>
      </div>

      <div v-else class="text-center py-4">
        <div class="text-5xl mb-3">📧</div>
        <p class="font-semibold mb-1">Check your inbox</p>
        <p class="text-sm" style="color:var(--color-text-muted)">A reset link has been sent to <strong>{{ email }}</strong></p>
      </div>

      <div class="divider" />
      <RouterLink to="/auth/login" class="block text-center text-sm font-semibold no-underline hover:underline" style="color:var(--color-primary)">
        Back to Sign In
      </RouterLink>
    </div>
  </div>
</template>
