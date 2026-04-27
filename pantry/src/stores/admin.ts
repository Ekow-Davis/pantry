import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '@/composables/useApi'

export const useAdminStore = defineStore('admin', () => {
  const stats       = ref<any>(null)
  const users       = ref<any[]>([])
  const contributions = ref<any[]>([])
  const loading     = ref(false)

  async function fetchStats() {
    const { data } = await api.get('/api/v1/admin/stats')
    stats.value = data
  }

  async function fetchUsers(params?: any) {
    loading.value = true
    try {
      const { data } = await api.get('/api/v1/admin/users', { params })
      users.value = data
    } finally {
      loading.value = false
    }
  }

  async function fetchContributions(status = 'pending') {
    loading.value = true
    try {
      const { data } = await api.get('/api/v1/admin/contributions', { params: { status } })
      contributions.value = data
    } finally {
      loading.value = false
    }
  }

  async function reviewContribution(id: string, status: string, rejection_reason?: string) {
    await api.patch(`/api/v1/admin/contributions/${id}`, { status, rejection_reason })
    contributions.value = contributions.value.filter(c => c.id !== id)
  }

  async function updateUser(id: string, payload: any) {
    const { data } = await api.patch(`/api/v1/admin/users/${id}`, payload)
    const idx = users.value.findIndex(u => u.id === id)
    if (idx !== -1) users.value[idx] = data
  }

  async function deleteUser(id: string) {
    await api.delete(`/api/v1/admin/users/${id}`)
    users.value = users.value.filter(u => u.id !== id)
  }

  return { stats, users, contributions, loading, fetchStats, fetchUsers, fetchContributions, reviewContribution, updateUser, deleteUser }
})
