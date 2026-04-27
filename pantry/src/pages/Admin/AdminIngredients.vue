<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { Search, Plus, Edit2, Trash2, FlaskConical, AlertCircle } from 'lucide-vue-next'
import { useNotificationsStore } from '@/stores/notifications'
import api from '@/composables/useApi'

const notify      = useNotificationsStore()
const ingredients = ref<any[]>([])
const loading     = ref(true)
const search      = ref('')
const showForm    = ref(false)

const form = ref({ name: '', unit: '', category: '', grams_per_unit: null as number | null })
const saving = ref(false)

async function load() {
  loading.value = true
  try {
    const { data } = await api.get('/api/v1/ingredients', { params: { page_size: 200 } })
    ingredients.value = data
  } finally { loading.value = false }
}

onMounted(load)

const filtered = () => ingredients.value.filter(i =>
  i.name.toLowerCase().includes(search.value.toLowerCase())
)

async function create() {
  if (!form.value.name) { notify.warning('Name is required.'); return }
  saving.value = true
  try {
    const { data } = await api.post('/api/v1/ingredients', form.value)
    ingredients.value.unshift(data)
    showForm.value = false
    form.value = { name: '', unit: '', category: '', grams_per_unit: null }
    notify.success('Ingredient added.')
  } catch (e: any) {
    notify.error(e.response?.data?.detail || 'Failed to add ingredient.')
  } finally { saving.value = false }
}

async function remove(ing: any) {
  if (!confirm(`Delete "${ing.name}"?`)) return
  try {
    await api.delete(`/api/v1/ingredients/${ing.id}`)
    ingredients.value = ingredients.value.filter(i => i.id !== ing.id)
    notify.success('Ingredient deleted.')
  } catch { notify.error('Failed. Ingredient may be in use.') }
}

const missingNutrition = () => ingredients.value.filter(i => !i.nutrition).length
</script>

<template>
  <div>
    <div class="flex items-center justify-between mb-6 animate-fade-up">
      <div>
        <h1 class="text-3xl font-black mb-1" style="font-family:var(--font-display)">Ingredients</h1>
        <p class="text-sm" style="color:var(--color-text-muted)">{{ ingredients.length }} total · {{ missingNutrition() }} missing nutrition data</p>
      </div>
      <button class="btn-primary !py-2 !px-4 text-sm" @click="showForm = !showForm">
        <Plus class="w-4 h-4" /> Add Ingredient
      </button>
    </div>

    <!-- Missing nutrition alert -->
    <div v-if="missingNutrition() > 0" class="flex items-center gap-3 p-4 rounded-xl mb-4 animate-fade-up"
      style="background:var(--color-warning-soft); border:1px solid var(--color-warning)">
      <AlertCircle class="w-5 h-5 flex-shrink-0" style="color:var(--color-warning)" />
      <p class="text-sm font-medium" style="color:var(--color-warning)">
        {{ missingNutrition() }} ingredient(s) are missing nutritional data. Meals using them will show incomplete nutrition.
      </p>
    </div>

    <!-- Add form -->
    <div v-if="showForm" class="card p-5 mb-4 animate-scale-in">
      <h2 class="font-bold mb-4 text-sm uppercase tracking-wide" style="color:var(--color-text-muted)">New Ingredient</h2>
      <div class="grid grid-cols-1 md:grid-cols-2 gap-3 mb-3">
        <div><label class="label">Name *</label><input v-model="form.name" class="input" placeholder="e.g. Kontomire" /></div>
        <div><label class="label">Default unit</label><input v-model="form.unit" class="input" placeholder="g, ml, pieces..." /></div>
        <div><label class="label">Category</label><input v-model="form.category" class="input" placeholder="vegetable, protein, spice..." /></div>
        <div><label class="label">Grams per unit</label><input v-model.number="form.grams_per_unit" type="number" class="input" placeholder="e.g. 120 (for 1 plantain)" /></div>
      </div>
      <div class="flex gap-2">
        <button class="btn-primary !py-2 !px-4 text-sm" :disabled="saving" @click="create">
          <span v-if="saving" class="flex gap-1"><span class="dot-bounce"></span><span class="dot-bounce"></span><span class="dot-bounce"></span></span>
          <template v-else>Add Ingredient</template>
        </button>
        <button class="btn-surface !py-2 !px-4 text-sm" @click="showForm = false">Cancel</button>
      </div>
    </div>

    <div class="relative mb-3 animate-fade-up delay-100">
      <Search class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4" style="color:var(--color-text-faint)" />
      <input v-model="search" class="input !pl-10" placeholder="Search ingredients..." />
    </div>

    <div v-if="loading" class="flex flex-col gap-2">
      <div v-for="i in 8" :key="i" class="skeleton h-12 rounded-xl"></div>
    </div>

    <div v-else class="flex flex-col gap-2 animate-fade-up delay-200">
      <div v-for="ing in filtered()" :key="ing.id"
        class="card p-3 flex items-center gap-3"
        :style="!ing.nutrition ? 'border-left:3px solid var(--color-warning)' : ''">
        <FlaskConical class="w-4 h-4 flex-shrink-0" :style="`color: ${ing.nutrition ? 'var(--color-success)' : 'var(--color-warning)'}`" />
        <div class="flex-1 min-w-0">
          <span class="font-medium text-sm" style="color:var(--color-text)">{{ ing.name }}</span>
          <span v-if="ing.unit" class="text-xs ml-2" style="color:var(--color-text-faint)">{{ ing.unit }}</span>
          <span v-if="ing.category" class="text-xs ml-2 badge badge-primary">{{ ing.category }}</span>
        </div>
        <span v-if="!ing.nutrition" class="text-xs" style="color:var(--color-warning)">No nutrition</span>
        <button @click="remove(ing)"
          class="w-7 h-7 rounded-lg flex items-center justify-center hover:bg-[var(--color-danger-soft)] transition-all flex-shrink-0"
          style="color:var(--color-danger)">
          <Trash2 class="w-3.5 h-3.5" />
        </button>
      </div>
    </div>
  </div>
</template>
