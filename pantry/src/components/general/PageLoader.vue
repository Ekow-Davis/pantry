<script setup lang="ts">
defineProps<{ message?: string }>()
</script>

<template>
  <div class="fixed inset-0 z-50 flex flex-col items-center justify-center gap-6" style="background:var(--color-bg)">
    <!-- Animated pot / bowl -->
    <div class="relative w-20 h-20">
      <div
        class="w-20 h-20 rounded-full flex items-center justify-center text-4xl animate-float"
        style="background:var(--color-primary-soft); color:var(--color-primary)"
      >
        🍲
      </div>
      <div class="absolute inset-0 rounded-full animate-ping opacity-20" style="background:var(--color-primary)"></div>
    </div>

    <!-- Dots -->
    <div class="flex gap-2">
      <span class="dot-bounce" style="color:var(--color-primary)"></span>
      <span class="dot-bounce" style="color:var(--color-primary)"></span>
      <span class="dot-bounce" style="color:var(--color-primary)"></span>
    </div>

    <p v-if="message" class="text-sm font-medium" style="color:var(--color-text-muted)">{{ message }}</p>
  </div>
</template>
