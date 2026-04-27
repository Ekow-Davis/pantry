<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { Search, EyeOff, Eye, Trash2 } from 'lucide-vue-next'
import { useNotificationsStore } from '@/stores/notifications'
import api from '@/composables/useApi'

const notify  = useNotificationsStore()
const meals   = ref<any[]>([])
const loading = ref(true)
const search  = ref('')
const status  = ref('')

async function load() {
  loading.value = true
  try {
    const { data } = await api.get('/api/v1/admin/meals', { params: { status: status.value || undefined, page_size: 100 } })
    meals.value = data
  } finally {
    loading.value = false
  }
}

onMounted(load)

const filtered = () => meals.value.filter(m =>
  m.name.toLowerCase().includes(search.value.toLowerCase())
)

async function hide(meal: any) {
  try {
    await api.patch(`/api/v1/meals/${meal.id}/hide`)
    meal.status = 'hidden'
    notify.success(`${meal.name} hidden.`)
  } catch { notify.error('Failed.') }
}

async function unhide(meal: any) {
  try {
    await api.patch(`/api/v1/meals/${meal.id}/unhide`)
    meal.status = 'active'
    notify.success(`${meal.name} restored.`)
  } catch { notify.error('Failed.') }
}

async function remove(meal: any) {
  if (!confirm(`Delete "${meal.name}"? This cannot be undone.`)) return
  try {
    await api.delete(`/api/v1/meals/${meal.id}`)
    meals.value = meals.value.filter(m => m.id !== meal.id)
    notify.success('Meal deleted.')
  } catch { notify.error('Failed to delete meal.') }
}

const statusColors: Record<string, string> = {
  active:   'badge-success',
  hidden:   'badge-warning',
  pending:  'badge-primary',
  rejected: 'badge-danger',
}
</script>

<template>
  <div>
    <div class="flex items-center justify-between mb-6 animate-fade-up">
      <div>
        <h1 class="text-3xl font-black mb-1" style="font-family:var(--font-display)">Meals</h1>
        <p class="text-sm" style="color:var(--color-text-muted)">Manage the meal library</p>
      </div>
    </div>

    <div class="flex flex-col md:flex-row gap-3 mb-4 animate-fade-up delay-100">
      <div class="relative flex-1">
        <Search class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4" style="color:var(--color-text-faint)" />
        <input v-model="search" class="input !pl-10" placeholder="Search meals..." />
      </div>
      <div class="flex gap-2">
        <button v-for="s in ['', 'active', 'hidden', 'pending', 'rejected']" :key="s"
          class="px-3 py-2 rounded-full text-xs font-semibold transition-all"
          :style="status === s ? 'background:var(--color-danger); color:#fff' : 'background:var(--color-surface); color:var(--color-text-muted); border:1px solid var(--color-border)'"
          @click="status = s; load()">
          {{ s || 'All' }}
        </button>
      </div>
    </div>

    <div v-if="loading" class="flex flex-col gap-3">
      <div v-for="i in 6" :key="i" class="skeleton h-16 rounded-xl"></div>
    </div>

    <div v-else class="flex flex-col gap-2 animate-fade-up delay-200">
      <div v-for="meal in filtered()" :key="meal.id" class="card p-4 flex items-center gap-4">
        <div class="w-12 h-12 rounded-xl flex items-center justify-center text-2xl flex-shrink-0"
          style="background:var(--color-primary-soft)">🍲</div>
        <div class="flex-1 min-w-0">
          <div class="flex items-center gap-2 flex-wrap">
            <p class="font-bold text-sm" style="color:var(--color-text)">{{ meal.name }}</p>
            <span class="badge text-[10px]" :class="statusColors[meal.status]">{{ meal.status }}</span>
            <span v-if="meal.is_user_contributed" class="badge badge-violet text-[10px]">User submitted</span>
          </div>
          <div class="flex flex-wrap gap-1 mt-1">
            <span v-for="cat in meal.categories" :key="cat.id" class="badge badge-primary text-[10px]">{{ cat.slug }}</span>
          </div>
        </div>
        <div class="flex items-center gap-1 flex-shrink-0">
          <button v-if="meal.status === 'active'" @click="hide(meal)" title="Hide meal"
            class="w-8 h-8 rounded-lg flex items-center justify-center hover:bg-[var(--color-warning-soft)] transition-all"
            style="color:var(--color-warning)">
            <EyeOff class="w-4 h-4" />
          </button>
          <button v-else-if="meal.status === 'hidden'" @click="unhide(meal)" title="Show meal"
            class="w-8 h-8 rounded-lg flex items-center justify-center hover:bg-[var(--color-success-soft)] transition-all"
            style="color:var(--color-success)">
            <Eye class="w-4 h-4" />
          </button>
          <button @click="remove(meal)" title="Delete"
            class="w-8 h-8 rounded-lg flex items-center justify-center hover:bg-[var(--color-danger-soft)] transition-all"
            style="color:var(--color-danger)">
            <Trash2 class="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>

    <div v-if="!loading && !filtered().length" class="card p-10 text-center mt-4">
      <div class="text-5xl mb-3">🍽️</div>
      <p class="font-semibold">No meals found</p>
    </div>
  </div>
</template>
