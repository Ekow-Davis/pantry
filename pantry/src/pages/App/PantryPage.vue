<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { Search, ShoppingBasket, ChevronRight, X } from 'lucide-vue-next'
import { RouterLink } from 'vue-router'
import api from '@/composables/useApi'
import { useNotificationsStore } from '@/stores/notifications'

const notify = useNotificationsStore()

const allIngredients = ref<any[]>([])
const pantry         = ref<any[]>([])  // ingredient objects in pantry
const matches        = ref<any>(null)
const search         = ref('')
const loading        = ref(false)
const matching       = ref(false)

onMounted(async () => {
  const [ingRes, pantryRes] = await Promise.all([
    api.get('/api/v1/ingredients', { params: { page_size: 200 } }),
    api.get('/api/v1/me/pantry'),
  ])
  allIngredients.value = ingRes.data
  pantry.value         = pantryRes.data.ingredients
})

const filtered = () => allIngredients.value.filter(i =>
  i.name.toLowerCase().includes(search.value.toLowerCase())
)

const inPantry = (id: string) => pantry.value.some(i => i.id === id)

async function toggle(ingredient: any) {
  if (inPantry(ingredient.id)) {
    pantry.value = pantry.value.filter(i => i.id !== ingredient.id)
  } else {
    pantry.value.push(ingredient)
  }
  await api.put('/api/v1/me/pantry', { ingredient_ids: pantry.value.map(i => i.id) })
}

async function findMatches() {
  matching.value = true
  try {
    const { data } = await api.get('/api/v1/recommendations/pantry')
    matches.value = data
  } catch {
    notify.error('Could not fetch matches.')
  } finally {
    matching.value = false
  }
}
</script>

<template>
  <div class="max-w-3xl mx-auto">
    <div class="mb-6 animate-fade-up">
      <h1 class="text-3xl font-black mb-1" style="font-family:var(--font-display)">Pantry</h1>
      <p class="text-sm" style="color:var(--color-text-muted)">Select what ingredients you have. We'll tell you what you can cook.</p>
    </div>

    <!-- Selected pantry chips -->
    <div v-if="pantry.length" class="flex flex-wrap gap-2 mb-4 animate-fade-up delay-100">
      <div
        v-for="ing in pantry"
        :key="ing.id"
        class="flex items-center gap-1.5 px-3 py-1.5 rounded-full text-sm font-medium"
        style="background:var(--color-primary-soft); color:var(--color-primary)"
      >
        {{ ing.name }}
        <button @click="toggle(ing)"><X class="w-3 h-3" /></button>
      </div>
    </div>

    <!-- Search + ingredient list -->
    <div class="card p-4 mb-4 animate-fade-up delay-200">
      <div class="relative mb-3">
        <Search class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4" style="color:var(--color-text-faint)" />
        <input v-model="search" class="input !pl-10" placeholder="Search ingredients..." />
      </div>
      <div class="grid grid-cols-2 md:grid-cols-3 gap-2 max-h-64 overflow-y-auto">
        <button
          v-for="ing in filtered()"
          :key="ing.id"
          class="px-3 py-2 rounded-xl text-sm text-left transition-all"
          :style="inPantry(ing.id)
            ? 'background:var(--color-primary); color:#fff; font-weight:600;'
            : 'background:var(--color-surface); color:var(--color-text); border:1px solid var(--color-border-soft)'"
          @click="toggle(ing)"
        >
          {{ ing.name }}
        </button>
      </div>
    </div>

    <button class="btn-primary w-full justify-center mb-6" :disabled="!pantry.length || matching" @click="findMatches">
      <span v-if="matching" class="flex gap-1"><span class="dot-bounce"></span><span class="dot-bounce"></span><span class="dot-bounce"></span></span>
      <template v-else><ShoppingBasket class="w-5 h-5" /> Find What I Can Cook</template>
    </button>

    <!-- Results -->
    <div v-if="matches">
      <!-- Can make -->
      <div v-if="matches.can_make?.length" class="mb-6">
        <h2 class="text-lg font-bold mb-3 flex items-center gap-2" style="font-family:var(--font-display)">
          <span class="badge badge-success">✓ You can make these</span>
        </h2>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
          <RouterLink
            v-for="meal in matches.can_make"
            :key="meal.id"
            :to="`/app/meals/${meal.id}`"
            class="card p-4 no-underline flex items-center gap-3"
          >
            <div class="w-12 h-12 rounded-xl flex items-center justify-center text-2xl flex-shrink-0" style="background:var(--color-success-soft)">🍲</div>
            <div class="flex-1 min-w-0">
              <p class="font-bold truncate" style="color:var(--color-text)">{{ meal.name }}</p>
            </div>
            <ChevronRight class="w-4 h-4 flex-shrink-0" style="color:var(--color-text-faint)" />
          </RouterLink>
        </div>
      </div>

      <!-- Missing one -->
      <div v-if="matches.missing_one?.length" class="mb-6">
        <h2 class="text-lg font-bold mb-3" style="font-family:var(--font-display)">
          <span class="badge badge-warning">Almost there — missing 1</span>
        </h2>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
          <div v-for="item in matches.missing_one" :key="item.meal.id" class="card p-4 flex items-center gap-3">
            <div class="w-12 h-12 rounded-xl flex items-center justify-center text-2xl flex-shrink-0" style="background:var(--color-warning-soft)">🍲</div>
            <div class="flex-1 min-w-0">
              <p class="font-bold truncate" style="color:var(--color-text)">{{ item.meal.name }}</p>
              <p class="text-xs" style="color:var(--color-warning)">Need: {{ item.missing_ingredient?.name }}</p>
            </div>
          </div>
        </div>
      </div>

      <div v-if="!matches.can_make?.length && !matches.missing_one?.length" class="card p-10 text-center">
        <div class="text-5xl mb-3">🔍</div>
        <p class="font-semibold">No close matches found</p>
        <p class="text-sm mt-1" style="color:var(--color-text-muted)">Try adding more ingredients to your pantry</p>
      </div>
    </div>
  </div>
</template>
