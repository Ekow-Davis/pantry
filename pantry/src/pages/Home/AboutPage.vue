<script setup lang="ts">
import { Heart, Globe, Utensils } from 'lucide-vue-next'
</script>

<template>
  <section class="section">
    <div class="container max-w-3xl">
      <div class="text-center mb-14">
        <span class="badge badge-primary mb-4">About</span>
        <h1 class="text-5xl font-black mb-4" style="font-family:var(--font-display)">
          Built for<br><span style="color:var(--color-primary)">West African kitchens</span>
        </h1>
      </div>

      <div class="card p-8 mb-8 animate-fade-up">
        <div class="flex items-center gap-3 mb-4">
          <div class="w-10 h-10 rounded-xl flex items-center justify-center" style="background:var(--color-primary-soft)">
            <Heart class="w-5 h-5" style="color:var(--color-primary)" />
          </div>
          <h2 class="text-2xl font-black" style="font-family:var(--font-display)">The Origin</h2>
        </div>
        <p class="leading-relaxed mb-3" style="color:var(--color-text-muted)">
          MealWise was born out of a simple frustration: most meal planning apps are built around Western cuisines, with databases that barely acknowledge the depth and variety of African food. Planning meals for a Ghanaian household meant dealing with apps that had never heard of Fufu, Waakye, or Kontomire stew.
        </p>
        <p class="leading-relaxed" style="color:var(--color-text-muted)">
          So we built something different. A meal planner that starts from the perspective of a West African kitchen — where Banku is a staple, Jollof is a religion, and Palm Nut Soup is weekend comfort food.
        </p>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
        <div class="card p-6 animate-fade-up delay-200">
          <div class="w-10 h-10 rounded-xl flex items-center justify-center mb-3" style="background:var(--color-success-soft)">
            <Globe class="w-5 h-5" style="color:var(--color-success)" />
          </div>
          <h3 class="text-lg font-bold mb-2" style="font-family:var(--font-display)">Culturally Grounded</h3>
          <p class="text-sm leading-relaxed" style="color:var(--color-text-muted)">Our recipe database is built with cultural accuracy. Nutritional data is sourced from the FAO/WHO West African Food Composition Table — the most accurate data source for the region.</p>
        </div>
        <div class="card p-6 animate-fade-up delay-300">
          <div class="w-10 h-10 rounded-xl flex items-center justify-center mb-3" style="background:var(--color-violet-soft)">
            <Utensils class="w-5 h-5" style="color:var(--color-violet)" />
          </div>
          <h3 class="text-lg font-bold mb-2" style="font-family:var(--font-display)">Community Driven</h3>
          <p class="text-sm leading-relaxed" style="color:var(--color-text-muted)">Users can submit their own recipes for review. Every approved recipe grows the library for everyone — turning MealWise into a living cookbook.</p>
        </div>
      </div>
    </div>
  </section>
</template>
