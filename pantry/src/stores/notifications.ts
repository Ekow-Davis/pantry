import { defineStore } from 'pinia'
import { ref } from 'vue'

export type ToastType = 'success' | 'error' | 'warning' | 'info'

export interface Toast {
  id: string
  type: ToastType
  message: string
  duration?: number
}

export const useNotificationsStore = defineStore('notifications', () => {
  const toasts = ref<Toast[]>([])

  function add(message: string, type: ToastType = 'info', duration = 4000) {
    const id = Math.random().toString(36).slice(2)
    toasts.value.push({ id, type, message, duration })
    if (duration > 0) {
      setTimeout(() => remove(id), duration)
    }
    return id
  }

  function remove(id: string) {
    toasts.value = toasts.value.filter(t => t.id !== id)
  }

  const success = (msg: string) => add(msg, 'success')
  const error   = (msg: string) => add(msg, 'error')
  const warning = (msg: string) => add(msg, 'warning')
  const info    = (msg: string) => add(msg, 'info')

  return { toasts, add, remove, success, error, warning, info }
})
