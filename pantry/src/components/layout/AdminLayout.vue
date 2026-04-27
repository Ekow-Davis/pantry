<script setup lang="ts">
import { RouterLink, RouterView, useRoute } from 'vue-router'
import {
  LayoutDashboard, Users, BookOpen, Inbox,
  FlaskConical, BarChart3, ChefHat, LogOut, ArrowLeft
} from 'lucide-vue-next'
import { useAuthStore } from '@/stores/auth'
import { useUiStore }   from '@/stores/ui'
import ThemeSwitcher    from '@/components/general/ThemeSwitcher.vue'

const auth  = useAuthStore()
const ui    = useUiStore()
const route = useRoute()

const navItems = [
  { to: '/admin/dashboard',     icon: LayoutDashboard, label: 'Dashboard' },
  { to: '/admin/users',         icon: Users,           label: 'Users' },
  { to: '/admin/meals',         icon: BookOpen,        label: 'Meals' },
  { to: '/admin/contributions', icon: Inbox,           label: 'Contributions' },
  { to: '/admin/ingredients',   icon: FlaskConical,    label: 'Ingredients' },
  { to: '/admin/stats',         icon: BarChart3,       label: 'Statistics' },
]

const isActive = (to: string) => route.path.startsWith(to)
</script>

<template>
  <div class="flex h-screen overflow-hidden" style="background:var(--color-bg)">

    <!-- Sidebar -->
    <aside class="hidden md:flex flex-col w-56 border-r flex-shrink-0" style="background:var(--color-surface-raised); border-color:var(--color-border-soft)">
      <div class="flex items-center gap-3 px-4 h-16 border-b" style="border-color:var(--color-border-soft)">
        <div class="w-8 h-8 rounded-lg flex-shrink-0 flex items-center justify-center" style="background:var(--color-danger)">
          <ChefHat class="w-4 h-4 text-white" />
        </div>
        <div>
          <p class="font-bold text-sm" style="font-family:var(--font-display); color:var(--color-text)">MealWise</p>
          <p class="text-[10px] font-semibold uppercase tracking-widest" style="color:var(--color-danger)">Admin</p>
        </div>
      </div>

      <nav class="flex-1 overflow-y-auto py-4 flex flex-col gap-1 px-2">
        <RouterLink
          v-for="item in navItems"
          :key="item.to"
          :to="item.to"
          class="flex items-center gap-3 px-3 py-2.5 rounded-xl transition-all no-underline text-sm"
          :style="isActive(item.to)
            ? 'background:var(--color-danger-soft); color:var(--color-danger); font-weight:600;'
            : 'color:var(--color-text-muted);'"
        >
          <component :is="item.icon" class="w-5 h-5 flex-shrink-0" />
          {{ item.label }}
        </RouterLink>
      </nav>

      <div class="border-t p-3 flex flex-col gap-2" style="border-color:var(--color-border-soft)">
        <ThemeSwitcher />
        <RouterLink to="/app/dashboard" class="flex items-center gap-2 px-3 py-2 rounded-xl text-sm no-underline transition-all" style="color:var(--color-text-muted)">
          <ArrowLeft class="w-4 h-4" /> Back to App
        </RouterLink>
        <button class="flex items-center gap-2 px-3 py-2 rounded-xl text-sm w-full text-left transition-all" style="color:var(--color-danger)" @click="auth.logout()">
          <LogOut class="w-4 h-4" /> Sign Out
        </button>
      </div>
    </aside>

    <!-- Content -->
    <div class="flex-1 flex flex-col overflow-hidden">
      <header class="flex items-center justify-between px-6 h-16 border-b flex-shrink-0" style="background:var(--color-surface-raised); border-color:var(--color-border-soft)">
        <h1 class="text-lg font-bold" style="font-family:var(--font-display); color:var(--color-text)">
          {{ navItems.find(n => route.path.startsWith(n.to))?.label || 'Admin' }}
        </h1>
        <div class="flex items-center gap-3">
          <ThemeSwitcher class="md:hidden" />
          <span class="text-sm font-medium px-3 py-1 rounded-full badge-danger">{{ auth.user?.username }}</span>
        </div>
      </header>

      <main class="flex-1 overflow-y-auto p-6">
        <RouterView v-slot="{ Component }">
          <Transition name="page" mode="out-in">
            <component :is="Component" />
          </Transition>
        </RouterView>
      </main>
    </div>
  </div>
</template>
