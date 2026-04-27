<script setup lang="ts">
import { useNotificationsStore } from '@/stores/notifications'
import { CheckCircle, XCircle, AlertTriangle, Info, X } from 'lucide-vue-next'

const store = useNotificationsStore()

const icons = { success: CheckCircle, error: XCircle, warning: AlertTriangle, info: Info }
const colors = {
  success: 'border-l-[var(--color-success)] bg-[var(--color-success-soft)]',
  error:   'border-l-[var(--color-danger)]  bg-[var(--color-danger-soft)]',
  warning: 'border-l-[var(--color-warning)] bg-[var(--color-warning-soft)]',
  info:    'border-l-[var(--color-info)]    bg-[var(--color-info-soft)]',
}
const iconColors = {
  success: 'text-[var(--color-success)]',
  error:   'text-[var(--color-danger)]',
  warning: 'text-[var(--color-warning)]',
  info:    'text-[var(--color-info)]',
}
</script>

<template>
  <Teleport to="body">
    <div class="fixed top-4 right-4 z-[9999] flex flex-col gap-2 w-80 max-w-[calc(100vw-2rem)]">
      <TransitionGroup name="toast">
        <div
          v-for="toast in store.toasts"
          :key="toast.id"
          class="flex items-start gap-3 p-4 rounded-xl border-l-4 shadow-lg cursor-pointer select-none"
          :class="colors[toast.type]"
          @click="store.remove(toast.id)"
        >
          <component :is="icons[toast.type]" class="w-5 h-5 flex-shrink-0 mt-0.5" :class="iconColors[toast.type]" />
          <p class="flex-1 text-sm font-medium" style="color:var(--color-text)">{{ toast.message }}</p>
          <X class="w-4 h-4 flex-shrink-0 opacity-50 hover:opacity-100 transition-opacity" style="color:var(--color-text)" />
        </div>
      </TransitionGroup>
    </div>
  </Teleport>
</template>
