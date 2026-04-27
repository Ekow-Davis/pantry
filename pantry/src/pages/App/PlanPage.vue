<script setup lang="ts">
import { onMounted } from 'vue'
import { CalendarDays, RefreshCw, Check, X, ArrowRight } from 'lucide-vue-next'
import { usePlanStore } from '@/stores/plan'
import { useNotificationsStore } from '@/stores/notifications'

const plan   = usePlanStore()
const notify = useNotificationsStore()

onMounted(() => plan.fetchToday())

async function confirm(slotId: string) {
  try {
    await plan.confirmSlot(slotId, 'confirmed')
    notify.success('Slot confirmed!')
  } catch { notify.error('Failed to confirm slot.') }
}

async function skip(slotId: string) {
  try {
    await plan.confirmSlot(slotId, 'skipped')
    notify.info('Slot skipped.')
  } catch { notify.error('Failed to skip slot.') }
}

const statusColors: Record<string, string> = {
  suggested: 'badge-primary',
  confirmed: 'badge-success',
  skipped:   'badge-warning',
  replaced:  'badge-violet',
}
</script>

<template>
  <div class="max-w-2xl mx-auto">
    <div class="flex items-center justify-between mb-6 animate-fade-up">
      <div>
        <h1 class="text-3xl font-black mb-1" style="font-family:var(--font-display)">My Plan</h1>
        <p class="text-sm" style="color:var(--color-text-muted)">Today's meal recommendations</p>
      </div>
      <button class="btn-surface !py-2 !px-4 text-sm" @click="plan.generatePlan()">
        <RefreshCw class="w-4 h-4" /> Regenerate
      </button>
    </div>

    <div v-if="plan.loading" class="flex flex-col gap-4">
      <div v-for="i in 3" :key="i" class="skeleton h-24 rounded-2xl"></div>
    </div>

    <div v-else-if="plan.todayPlan?.slots?.length" class="flex flex-col gap-4">
      <div
        v-for="slot in plan.todayPlan.slots"
        :key="slot.id"
        class="card p-5 animate-fade-up"
      >
        <div class="flex items-start gap-4">
          <div class="w-14 h-14 rounded-xl flex items-center justify-center text-3xl flex-shrink-0"
            style="background:var(--color-primary-soft)">
            {{ slot.slot_type === 'breakfast' ? '🌅' : slot.slot_type === 'lunch' ? '☀️' : '🌙' }}
          </div>
          <div class="flex-1 min-w-0">
            <div class="flex items-center gap-2 mb-0.5">
              <p class="text-xs font-semibold uppercase tracking-wide" style="color:var(--color-text-faint)">{{ slot.slot_type }}</p>
              <span class="badge text-[10px]" :class="statusColors[slot.status]">{{ slot.status }}</span>
            </div>
            <p class="font-bold text-lg mb-1" style="font-family:var(--font-display); color:var(--color-text)">
              {{ slot.meal?.name || '—' }}
            </p>
            <p v-if="slot.meal?.description" class="text-xs line-clamp-1" style="color:var(--color-text-muted)">{{ slot.meal.description }}</p>
          </div>
        </div>

        <div v-if="slot.status === 'suggested'" class="flex gap-2 mt-4">
          <button class="btn-primary !py-2 !px-4 text-sm flex-1 justify-center" @click="confirm(slot.id)">
            <Check class="w-4 h-4" /> Cooked
          </button>
          <button class="btn-surface !py-2 !px-4 text-sm" @click="skip(slot.id)">
            <X class="w-4 h-4" /> Skip
          </button>
        </div>
      </div>
    </div>

    <div v-else class="card p-12 text-center animate-scale-in">
      <div class="text-6xl mb-4">📅</div>
      <p class="font-bold text-xl mb-2" style="font-family:var(--font-display)">No plan for today</p>
      <p class="text-sm mb-6" style="color:var(--color-text-muted)">Generate a plan to get meal recommendations for today.</p>
      <button class="btn-primary" @click="plan.generatePlan()">Generate Plan</button>
    </div>
  </div>
</template>
