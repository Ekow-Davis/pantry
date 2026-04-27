import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '@/composables/useApi'

export interface PlanSlot {
  id: string
  meal: any
  slot_type: string
  slot_order: number
  status: string
}

export interface DailyPlan {
  id: string
  plan_date: string
  status: string
  slots: PlanSlot[]
}

export const usePlanStore = defineStore('plan', () => {
  const todayPlan = ref<DailyPlan | null>(null)
  const loading   = ref(false)

  async function fetchToday() {
    loading.value = true
    try {
      const { data } = await api.get('/api/v1/plan/today')
      todayPlan.value = data
    } finally {
      loading.value = false
    }
  }

  async function generatePlan(date?: string) {
    loading.value = true
    try {
      const { data } = await api.post('/api/v1/plan/generate', undefined, { params: { plan_date: date } })
      todayPlan.value = data
    } finally {
      loading.value = false
    }
  }

  async function confirmSlot(slotId: string, status: string, replacementMealId?: string) {
    const { data } = await api.patch(`/api/v1/plan/slots/${slotId}`, {
      status,
      replacement_meal_id: replacementMealId,
    })
    // Refresh today's plan after slot update
    if (todayPlan.value) {
      todayPlan.value = data
    }
  }

  return { todayPlan, loading, fetchToday, generatePlan, confirmSlot }
})
