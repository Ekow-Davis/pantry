<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ArrowLeft, Clock, Users, Flame, Leaf } from 'lucide-vue-next'
import api from '@/composables/useApi'

const route  = useRoute()
const router = useRouter()
const meal   = ref<any>(null)
const loading = ref(true)

onMounted(async () => {
  try {
    const { data } = await api.get(`/api/v1/meals/${route.params.id}`)
    meal.value = data
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <div class="max-w-3xl mx-auto">
    <button class="flex items-center gap-2 mb-6 text-sm font-medium" style="color:var(--color-text-muted)" @click="router.back()">
      <ArrowLeft class="w-4 h-4" /> Back
    </button>

    <div v-if="loading" class="flex flex-col gap-4">
      <div class="skeleton h-64 rounded-3xl"></div>
      <div class="skeleton h-8 rounded-xl w-2/3"></div>
      <div class="skeleton h-4 rounded-xl"></div>
    </div>

    <div v-else-if="meal" class="animate-fade-up">
      <!-- Hero image -->
      <div class="w-full h-64 rounded-3xl flex items-center justify-center text-8xl mb-6 shadow-lg"
        style="background: linear-gradient(135deg, var(--color-primary-soft), var(--color-surface))">🍲</div>

      <!-- Title + categories -->
      <div class="flex flex-wrap items-start justify-between gap-3 mb-4">
        <div>
          <h1 class="text-4xl font-black mb-1" style="font-family:var(--font-display)">{{ meal.name }}</h1>
          <div class="flex flex-wrap gap-1 mt-2">
            <span v-for="cat in meal.categories" :key="cat.id" class="badge badge-primary">{{ cat.slug }}</span>
          </div>
        </div>
      </div>

      <p class="mb-6 leading-relaxed" style="color:var(--color-text-muted)">{{ meal.description }}</p>

      <!-- Nutrition -->
      <div v-if="meal.nutrition" class="card p-5 mb-6">
        <h2 class="text-lg font-bold mb-4 flex items-center gap-2" style="font-family:var(--font-display)">
          <Flame class="w-5 h-5" style="color:var(--color-warning)" /> Nutrition per serving
        </h2>
        <div class="grid grid-cols-2 md:grid-cols-5 gap-3">
          <div v-for="(val, key) in { Calories: meal.nutrition.calories, Protein: meal.nutrition.protein_g, Carbs: meal.nutrition.carbs_g, Fat: meal.nutrition.fat_g, Fibre: meal.nutrition.fiber_g }" :key="key"
            class="text-center p-3 rounded-xl" style="background:var(--color-surface)">
            <p class="text-xl font-black" style="font-family:var(--font-display); color:var(--color-primary)">{{ val ?? '?' }}</p>
            <p class="text-xs" style="color:var(--color-text-muted)">{{ key }}</p>
          </div>
        </div>
        <p v-if="!meal.nutrition.nutrition_complete" class="text-xs mt-3 badge badge-warning">⚠️ Partial nutritional data</p>
      </div>

      <!-- Recipe -->
      <div v-if="meal.recipe" class="card p-6 mb-6">
        <h2 class="text-lg font-bold mb-4 flex items-center gap-2" style="font-family:var(--font-display)">
          <Leaf class="w-5 h-5" style="color:var(--color-success)" /> Recipe
        </h2>
        <div class="flex gap-4 mb-4">
          <span v-if="meal.recipe.prep_time_mins" class="badge badge-primary"><Clock class="w-3 h-3" /> Prep {{ meal.recipe.prep_time_mins }}min</span>
          <span v-if="meal.recipe.cook_time_mins" class="badge badge-warning"><Clock class="w-3 h-3" /> Cook {{ meal.recipe.cook_time_mins }}min</span>
          <span v-if="meal.recipe.servings" class="badge badge-success"><Users class="w-3 h-3" /> Serves {{ meal.recipe.servings }}</span>
        </div>

        <h3 class="font-bold mb-2 text-sm uppercase tracking-wide" style="color:var(--color-text-muted)">Ingredients</h3>
        <ul class="flex flex-col gap-1 mb-5">
          <li v-for="ri in meal.recipe.ingredients" :key="ri.id"
            class="flex items-center gap-2 text-sm py-1.5 border-b" style="border-color:var(--color-border-soft)">
            <span class="w-2 h-2 rounded-full flex-shrink-0" :style="`background: ${ri.is_essential ? 'var(--color-primary)' : 'var(--color-border)'}`"></span>
            <span>{{ ri.ingredient.name }}</span>
            <span v-if="ri.quantity" class="ml-auto" style="color:var(--color-text-muted)">{{ ri.quantity }} {{ ri.unit }}</span>
            <span v-if="ri.is_essential" class="badge badge-primary text-[10px] !py-0.5">essential</span>
          </li>
        </ul>

        <h3 class="font-bold mb-2 text-sm uppercase tracking-wide" style="color:var(--color-text-muted)">Instructions</h3>
        <p class="text-sm leading-relaxed whitespace-pre-line" style="color:var(--color-text-muted)">{{ meal.recipe.instructions || 'No instructions provided yet.' }}</p>
      </div>
    </div>
  </div>
</template>
