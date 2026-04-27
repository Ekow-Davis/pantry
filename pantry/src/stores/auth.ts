import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '@/composables/useApi'
import router from '@/router'

interface User {
  id: string
  username: string
  email: string
  role: 'user' | 'admin'
  country?: string
  timezone: string
  cooldown_days: number
  assume_cooked: boolean
  is_active: boolean
}

export const useAuthStore = defineStore('auth', () => {
  const token        = ref<string | null>(localStorage.getItem('mw-token'))
  const refreshToken = ref<string | null>(localStorage.getItem('mw-refresh'))
  const user         = ref<User | null>(null)

  const isAuthenticated = computed(() => !!token.value)
  const isAdmin         = computed(() => user.value?.role === 'admin')

  function setTokens(access: string, refresh: string) {
    token.value        = access
    refreshToken.value = refresh
    localStorage.setItem('mw-token',   access)
    localStorage.setItem('mw-refresh', refresh)
  }

  async function fetchMe() {
    try {
      const { data } = await api.get('/api/v1/auth/me')
      user.value = data
    } catch {
      logout()
    }
  }

  async function login(email: string, password: string) {
    const { data } = await api.post('/api/v1/auth/login', { email, password })
    setTokens(data.access_token, data.refresh_token)
    await fetchMe()
    router.push(isAdmin.value ? '/admin' : '/app/dashboard')
  }

  async function register(payload: { username: string; email: string; password: string; country?: string }) {
    const { data } = await api.post('/api/v1/auth/register', payload)
    return data
  }

  function logout() {
    token.value        = null
    refreshToken.value = null
    user.value         = null
    localStorage.removeItem('mw-token')
    localStorage.removeItem('mw-refresh')
    router.push('/auth/login')
  }

  // Restore user on app load
  async function init() {
    if (token.value && !user.value) {
      await fetchMe()
    }
  }

  return { token, refreshToken, user, isAuthenticated, isAdmin, setTokens, fetchMe, login, register, logout, init }
})
