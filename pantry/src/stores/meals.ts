import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '@/composables/useApi'

export interface Meal {
  id: string
  name: string
  description?: string
  image_url?: string
  status: string
  popularity_score: number
  is_user_contributed: boolean
  categories: { id: string; name: string; slug: string }[]
  created_at: string
}

export const useMealsStore = defineStore('meals', () => {
  const meals   = ref<Meal[]>([])
  const loading = ref(false)
  const mealOfDay = ref<Meal | null>(null)

  async function fetchMeals(params?: { category?: string; search?: string; page?: number }) {
    loading.value = true
    try {
      const { data } = await api.get('/api/v1/meals', { params })
      meals.value = data
    } finally {
      loading.value = false
    }
  }

  async function fetchMealOfDay() {
    try {
      const { data } = await api.get('/api/v1/meals/of-the-day')
      mealOfDay.value = data
    } catch {}
  }

  return { meals, loading, mealOfDay, fetchMeals, fetchMealOfDay }
})
