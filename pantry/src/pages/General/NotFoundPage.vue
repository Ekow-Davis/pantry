<script setup lang="ts">
import { RouterLink } from 'vue-router'
import { Home, ArrowLeft } from 'lucide-vue-next'
</script>

<template>
  <div class="min-h-screen flex items-center justify-center p-4" style="background:var(--color-bg)">
    <div class="text-center animate-fade-up max-w-md">
      <!-- Animated bowl -->
      <div class="text-8xl mb-6 animate-float">🫙</div>

      <h1 class="text-6xl font-black mb-3" style="font-family:var(--font-display); color:var(--color-primary)">404</h1>
      <h2 class="text-2xl font-bold mb-3" style="font-family:var(--font-display)">This pot is empty</h2>
      <p class="mb-8" style="color:var(--color-text-muted)">
        The page you're looking for doesn't exist — but we have plenty of good meals waiting for you.
      </p>

      <div class="flex items-center justify-center gap-3">
        <RouterLink to="/" class="btn-primary">
          <Home class="w-4 h-4" /> Go Home
        </RouterLink>
        <button class="btn-ghost" @click="$router.back()">
          <ArrowLeft class="w-4 h-4" /> Go Back
        </button>
      </div>
    </div>
  </div>
</template>
