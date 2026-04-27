<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { Calendar } from 'lucide-vue-next'
import { useAuthStore } from '@/stores/auth'
import api from '@/composables/useApi'

const history = ref<any[]>([])
const loading = ref(true)

onMounted(async () => {
  try {
    const { data } = await api.get('/api/v1/me/history', { params: { limit: 50 } })
    history.value = data
  } finally {
    loading.value = false
  }
})

function formatDate(d: string) {
  return new Date(d).toLocaleDateString('en-GB', { weekday: 'short', day: 'numeric', month: 'short' })
}
</script>

<template>
  <div class="max-w-2xl mx-auto">
    <div class="mb-6 animate-fade-up">
      <h1 class="text-3xl font-black mb-1" style="font-family:var(--font-display)">Meal History</h1>
      <p class="text-sm" style="color:var(--color-text-muted)">Everything you've cooked recently</p>
    </div>

    <div v-if="loading" class="flex flex-col gap-3">
      <div v-for="i in 6" :key="i" class="skeleton h-16 rounded-xl"></div>
    </div>

    <div v-else-if="history.length" class="flex flex-col gap-2 animate-fade-up delay-100">
      <div
        v-for="entry in history"
        :key="entry.id"
        class="card p-4 flex items-center gap-4"
      >
        <div class="w-12 h-12 rounded-xl flex items-center justify-center text-2xl flex-shrink-0"
          style="background:var(--color-primary-soft)">🍲</div>
        <div class="flex-1 min-w-0">
          <p class="font-bold truncate" style="color:var(--color-text)">{{ entry.meal.name }}</p>
          <p class="text-xs" style="color:var(--color-text-faint)">{{ formatDate(entry.eaten_on) }}</p>
        </div>
        <span v-if="!entry.was_planned" class="badge badge-violet text-xs">Extra</span>
      </div>
    </div>

    <div v-else class="card p-12 text-center">
      <div class="text-6xl mb-4">📖</div>
      <p class="font-bold text-xl mb-2" style="font-family:var(--font-display)">No history yet</p>
      <p class="text-sm" style="color:var(--color-text-muted)">Start confirming meals from your daily plan to build up your history.</p>
    </div>
  </div>
</template>
