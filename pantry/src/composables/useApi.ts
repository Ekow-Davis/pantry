import axios from 'axios'
import { useAuthStore } from '@/stores/auth'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
  timeout: 15000,
})

api.interceptors.request.use((config) => {
  const auth = useAuthStore()
  if (auth.token) {
    config.headers.Authorization = `Bearer ${auth.token}`
  }
  return config
})

api.interceptors.response.use(
  (res) => res,
  async (err) => {
    const auth = useAuthStore()
    if (err.response?.status === 401 && auth.refreshToken) {
      try {
        const { data } = await axios.post(
          `${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/api/v1/auth/refresh`,
          { refresh_token: auth.refreshToken }
        )
        auth.setTokens(data.access_token, data.refresh_token)
        err.config.headers.Authorization = `Bearer ${data.access_token}`
        return api.request(err.config)
      } catch {
        auth.logout()
      }
    }
    return Promise.reject(err)
  }
)

export function useApi() {
  return { api }
}

export default api
