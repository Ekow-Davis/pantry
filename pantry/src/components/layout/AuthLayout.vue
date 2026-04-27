<script setup lang="ts">
import { RouterLink, RouterView } from 'vue-router'
import { ChefHat } from 'lucide-vue-next'
import ThemeSwitcher from '@/components/general/ThemeSwitcher.vue'
</script>

<template>
  <div class="min-h-screen flex flex-col" style="background:var(--color-bg)">
    <!-- Top bar -->
    <div class="flex items-center justify-between px-6 py-4">
      <RouterLink to="/" class="flex items-center gap-2 font-bold text-lg no-underline" style="color:var(--color-text); font-family:var(--font-display)">
        <div class="w-8 h-8 rounded-lg flex items-center justify-center" style="background:var(--color-primary)">
          <ChefHat class="w-4 h-4 text-white" />
        </div>
        MealWise
      </RouterLink>
      <ThemeSwitcher />
    </div>

    <!-- Auth content -->
    <div class="flex-1 flex items-center justify-center px-4 py-8">
      <RouterView v-slot="{ Component }">
        <Transition name="page" mode="out-in">
          <component :is="Component" />
        </Transition>
      </RouterView>
    </div>

    <!-- Decorative bottom strip -->
    <div class="h-1.5 w-full" style="background: linear-gradient(90deg, var(--color-primary), var(--color-primary-hover), #E6A817, var(--color-primary))"></div>
  </div>
</template>
