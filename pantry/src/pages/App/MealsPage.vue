<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { Search, Filter } from 'lucide-vue-next'
import { RouterLink } from 'vue-router'
import { useMealsStore } from '@/stores/meals'

const meals    = useMealsStore()
const search   = ref('')
const category = ref('')

const categories = [
  { slug: '',          label: 'All' },
  { slug: 'breakfast', label: '🌅 Breakfast' },
  { slug: 'lunch',     label: '☀️ Lunch' },
  { slug: 'dinner',    label: '🌙 Dinner' },
  { slug: 'snack',     label: '🍎 Snack' },
  { slug: 'any',       label: '🍽️ Any' },
]

onMounted(() => meals.fetchMeals())

watch([search, category], () => {
  meals.fetchMeals({ search: search.value || undefined, category: category.value || undefined })
})
</script>

<template>
  <div class="max-w-4xl mx-auto">
    <div class="mb-6 animate-fade-up">
      <h1 class="text-3xl font-black mb-1" style="font-family:var(--font-display)">Meal Library</h1>
      <p class="text-sm" style="color:var(--color-text-muted)">Browse all available recipes</p>
    </div>

    <!-- Filters -->
    <div class="flex flex-col md:flex-row gap-3 mb-6 animate-fade-up delay-100">
      <div class="relative flex-1">
        <Search class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4" style="color:var(--color-text-faint)" />
        <input v-model="search" class="input !pl-10" placeholder="Search meals..." />
      </div>
      <div class="flex gap-2 overflow-x-auto pb-1">
        <button
          v-for="cat in categories"
          :key="cat.slug"
          class="px-4 py-2 rounded-full text-sm font-medium whitespace-nowrap transition-all"
          :style="category === cat.slug
            ? 'background:var(--color-primary); color:#fff;'
            : 'background:var(--color-surface); color:var(--color-text-muted); border:1.5px solid var(--color-border)'"
          @click="category = cat.slug"
        >
          {{ cat.label }}
        </button>
      </div>
    </div>

    <!-- Grid -->
    <div v-if="meals.loading" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      <div v-for="i in 6" :key="i" class="skeleton h-48 rounded-2xl"></div>
    </div>

    <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 animate-fade-up delay-200">
      <RouterLink
        v-for="meal in meals.meals"
        :key="meal.id"
        :to="`/app/meals/${meal.id}`"
        class="card p-4 no-underline block"
      >
        <div class="w-full h-32 rounded-xl flex items-center justify-center text-5xl mb-3"
          style="background:var(--color-primary-soft)">🍲</div>
        <p class="font-bold mb-1 line-clamp-1" style="font-family:var(--font-display); color:var(--color-text)">{{ meal.name }}</p>
        <p class="text-xs line-clamp-2 mb-2" style="color:var(--color-text-muted)">{{ meal.description }}</p>
        <div class="flex flex-wrap gap-1">
          <span v-for="cat in meal.categories" :key="cat.id" class="badge badge-primary">{{ cat.slug }}</span>
        </div>
      </RouterLink>
    </div>

    <div v-if="!meals.loading && !meals.meals.length" class="text-center py-16">
      <div class="text-6xl mb-4">🔍</div>
      <p class="font-semibold">No meals found</p>
      <p class="text-sm mt-1" style="color:var(--color-text-muted)">Try adjusting your search or category filter</p>
    </div>
  </div>
</template>
