<script setup lang="ts">
import { onMounted } from 'vue'
import { CalendarDays, RefreshCw, Sparkles, ChefHat, ArrowRight } from 'lucide-vue-next'
import { useAuthStore } from '@/stores/auth'
import { usePlanStore  } from '@/stores/plan'
import { useMealsStore } from '@/stores/meals'
import { RouterLink } from 'vue-router'

const auth   = useAuthStore()
const plan   = usePlanStore()
const meals  = useMealsStore()

onMounted(async () => {
  await Promise.all([plan.fetchToday(), meals.fetchMealOfDay()])
})

const slotLabels: Record<string, string> = {
  breakfast: '🌅 Breakfast',
  lunch:     '☀️ Lunch',
  dinner:    '🌙 Dinner',
  snack:     '🍎 Snack',
}

const statusColors: Record<string, string> = {
  suggested:  'badge-primary',
  confirmed:  'badge-success',
  skipped:    'badge-warning',
  replaced:   'badge-violet',
}

function today() {
  return new Date().toLocaleDateString('en-GB', { weekday: 'long', day: 'numeric', month: 'long' })
}
</script>

<template>
  <div class="max-w-3xl mx-auto">
    <!-- Greeting -->
    <div class="mb-8 animate-fade-up">
      <h1 class="text-3xl font-black mb-1" style="font-family:var(--font-display)">
        Good {{ new Date().getHours() < 12 ? 'morning' : new Date().getHours() < 17 ? 'afternoon' : 'evening' }},
        <span style="color:var(--color-primary)">{{ auth.user?.username }}</span> 👋
      </h1>
      <p class="text-sm" style="color:var(--color-text-muted)">{{ today() }}</p>
    </div>

    <!-- Today's Plan -->
    <div class="card p-6 mb-6 animate-fade-up delay-100">
      <div class="flex items-center justify-between mb-4">
        <div class="flex items-center gap-2">
          <CalendarDays class="w-5 h-5" style="color:var(--color-primary)" />
          <h2 class="text-lg font-bold" style="font-family:var(--font-display)">Today's Plan</h2>
        </div>
        <button class="btn-surface !py-1.5 !px-3 text-xs" @click="plan.generatePlan()">
          <RefreshCw class="w-3 h-3" /> Regenerate
        </button>
      </div>

      <div v-if="plan.loading" class="flex flex-col gap-3">
        <div v-for="i in 3" :key="i" class="skeleton h-16 rounded-xl"></div>
      </div>

      <div v-else-if="plan.todayPlan?.slots?.length" class="flex flex-col gap-3">
        <div
          v-for="slot in plan.todayPlan.slots"
          :key="slot.id"
          class="flex items-center gap-4 p-4 rounded-xl"
          style="background:var(--color-surface); border:1px solid var(--color-border-soft)"
        >
          <div class="text-2xl w-10 text-center">{{ slot.slot_type === 'breakfast' ? '🌅' : slot.slot_type === 'lunch' ? '☀️' : '🌙' }}</div>
          <div class="flex-1 min-w-0">
            <p class="text-xs font-semibold uppercase tracking-wide mb-0.5" style="color:var(--color-text-faint)">{{ slot.slot_type }}</p>
            <p class="font-semibold truncate" style="color:var(--color-text)">{{ slot.meal?.name || 'No meal recommended' }}</p>
          </div>
          <span class="badge" :class="statusColors[slot.status]">{{ slot.status }}</span>
        </div>
      </div>

      <div v-else class="text-center py-8">
        <div class="text-5xl mb-3">📅</div>
        <p class="font-semibold mb-2">No plan yet</p>
        <button class="btn-primary" @click="plan.generatePlan()">Generate Today's Plan</button>
      </div>

      <RouterLink to="/app/plan" class="flex items-center justify-center gap-1 mt-4 text-sm font-medium no-underline" style="color:var(--color-primary)">
        View full plan <ArrowRight class="w-4 h-4" />
      </RouterLink>
    </div>

    <!-- Meal of the Day -->
    <div v-if="meals.mealOfDay" class="card p-6 mb-6 animate-fade-up delay-200">
      <div class="flex items-center gap-2 mb-4">
        <Sparkles class="w-5 h-5" style="color:var(--color-violet)" />
        <h2 class="text-lg font-bold" style="font-family:var(--font-display)">Meal of the Day</h2>
        <span class="badge badge-violet ml-auto">Featured</span>
      </div>
      <div class="flex items-center gap-4">
        <div class="w-16 h-16 rounded-2xl flex items-center justify-center text-3xl flex-shrink-0"
          style="background:var(--color-violet-soft)">🍛</div>
        <div class="flex-1 min-w-0">
          <p class="font-bold text-lg mb-0.5" style="font-family:var(--font-display)">{{ meals.mealOfDay.name }}</p>
          <p class="text-sm line-clamp-2" style="color:var(--color-text-muted)">{{ meals.mealOfDay.description }}</p>
        </div>
        <RouterLink :to="`/app/meals/${meals.mealOfDay.id}`" class="btn-ghost !py-2 !px-3 text-sm flex-shrink-0">View</RouterLink>
      </div>
    </div>

    <!-- Quick links -->
    <div class="grid grid-cols-2 md:grid-cols-4 gap-3 animate-fade-up delay-300">
      <RouterLink v-for="link in [
        { to: '/app/meals',    icon: '📚', label: 'Meal Library' },
        { to: '/app/pantry',   icon: '🛒', label: 'Pantry' },
        { to: '/app/history',  icon: '📖', label: 'History' },
        { to: '/app/settings', icon: '⚙️', label: 'Settings' },
      ]" :key="link.to" :to="link.to"
        class="card p-4 text-center no-underline flex flex-col items-center gap-2"
      >
        <span class="text-2xl">{{ link.icon }}</span>
        <span class="text-xs font-semibold" style="color:var(--color-text-muted)">{{ link.label }}</span>
      </RouterLink>
    </div>
  </div>
</template>
