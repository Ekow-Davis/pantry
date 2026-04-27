<script setup lang="ts">
import { Sun, Moon } from 'lucide-vue-next'
import { useTheme } from '@/composables/useTheme'

const { mode, accent, accentOptions, toggleMode, setAccent } = useTheme()
</script>

<template>
  <div class="flex items-center gap-3">
    <!-- Dark/light toggle -->
    <button
      @click="toggleMode"
      class="w-9 h-9 rounded-full flex items-center justify-center transition-all"
      style="background:var(--color-surface); border:1.5px solid var(--color-border);"
      :title="mode === 'dark' ? 'Switch to light mode' : 'Switch to dark mode'"
    >
      <Sun v-if="mode === 'dark'"  class="w-4 h-4" style="color:var(--color-primary)" />
      <Moon v-else                 class="w-4 h-4" style="color:var(--color-primary)" />
    </button>

    <!-- Accent dots -->
    <div class="flex items-center gap-1.5">
      <button
        v-for="opt in accentOptions"
        :key="opt.key"
        @click="setAccent(opt.key)"
        class="w-5 h-5 rounded-full transition-all border-2"
        :style="{
          backgroundColor: opt.hex,
          borderColor: accent === opt.key ? opt.hex : 'transparent',
          boxShadow: accent === opt.key ? `0 0 0 2px var(--color-bg), 0 0 0 4px ${opt.hex}` : 'none',
          transform: accent === opt.key ? 'scale(1.2)' : 'scale(1)',
        }"
        :title="opt.label"
      />
    </div>
  </div>
</template>
