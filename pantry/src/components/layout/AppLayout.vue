<script setup lang="ts">
import { computed } from 'vue'
import { RouterLink, RouterView, useRoute } from 'vue-router'
import {
  LayoutDashboard, CalendarDays, BookOpen, ShoppingBasket,
  History, PlusCircle, Settings, ChefHat, LogOut, Menu, X
} from 'lucide-vue-next'
import { useAuthStore } from '@/stores/auth'
import { useUiStore }   from '@/stores/ui'
import ThemeSwitcher    from '@/components/general/ThemeSwitcher.vue'

const auth  = useAuthStore()
const ui    = useUiStore()
const route = useRoute()

const navItems = [
  { to: '/app/dashboard', icon: LayoutDashboard, label: 'Dashboard' },
  { to: '/app/plan',      icon: CalendarDays,    label: 'My Plan' },
  { to: '/app/meals',     icon: BookOpen,        label: 'Meal Library' },
  { to: '/app/pantry',    icon: ShoppingBasket,  label: 'Pantry' },
  { to: '/app/history',   icon: History,         label: 'History' },
  { to: '/app/contribute',icon: PlusCircle,      label: 'Contribute' },
  { to: '/app/settings',  icon: Settings,        label: 'Settings' },
]

const isActive = (to: string) => route.path.startsWith(to)
</script>

<template>
  <div class="flex h-screen overflow-hidden" style="background:var(--color-bg)">

    <!-- ── Sidebar (desktop) ─────────────────────────────────────────── -->
    <aside
      class="hidden md:flex flex-col border-r transition-all duration-300"
      :class="ui.sidebarCollapsed ? 'w-16' : 'w-56'"
      style="background:var(--color-surface-raised); border-color:var(--color-border-soft)"
    >
      <!-- Logo -->
      <div class="flex items-center gap-3 px-4 h-16 border-b" style="border-color:var(--color-border-soft)">
        <div class="w-8 h-8 rounded-lg flex-shrink-0 flex items-center justify-center" style="background:var(--color-primary)">
          <ChefHat class="w-4 h-4 text-white" />
        </div>
        <span v-if="!ui.sidebarCollapsed" class="font-bold text-base transition-all" style="font-family:var(--font-display); color:var(--color-text)">MealWise</span>
      </div>

      <!-- Nav -->
      <nav class="flex-1 overflow-y-auto py-4 flex flex-col gap-1 px-2">
        <RouterLink
          v-for="item in navItems"
          :key="item.to"
          :to="item.to"
          class="flex items-center gap-3 px-3 py-2.5 rounded-xl transition-all no-underline"
          :class="ui.sidebarCollapsed ? 'justify-center' : ''"
          :style="isActive(item.to)
            ? 'background:var(--color-primary-soft); color:var(--color-primary); font-weight:600;'
            : 'color:var(--color-text-muted);'"
          :title="ui.sidebarCollapsed ? item.label : ''"
        >
          <component :is="item.icon" class="w-5 h-5 flex-shrink-0" />
          <span v-if="!ui.sidebarCollapsed" class="text-sm">{{ item.label }}</span>
        </RouterLink>
      </nav>

      <!-- Bottom -->
      <div class="border-t p-2 flex flex-col gap-1" style="border-color:var(--color-border-soft)">
        <div v-if="!ui.sidebarCollapsed" class="px-3 py-2">
          <ThemeSwitcher />
        </div>
        <button
          class="flex items-center gap-3 px-3 py-2.5 rounded-xl transition-all w-full text-left"
          :class="ui.sidebarCollapsed ? 'justify-center' : ''"
          style="color:var(--color-danger)"
          :style="''"
          @click="auth.logout()"
        >
          <LogOut class="w-5 h-5 flex-shrink-0" />
          <span v-if="!ui.sidebarCollapsed" class="text-sm font-medium">Sign Out</span>
        </button>
        <button
          class="flex items-center justify-center w-full py-2 rounded-xl transition-all"
          style="color:var(--color-text-faint)"
          @click="ui.toggleSidebar()"
        >
          <Menu class="w-4 h-4" />
        </button>
      </div>
    </aside>

    <!-- ── Main content ──────────────────────────────────────────────── -->
    <div class="flex-1 flex flex-col overflow-hidden">
      <!-- Top bar (mobile logo + theme) -->
      <header class="md:hidden flex items-center justify-between px-4 h-14 border-b flex-shrink-0" style="background:var(--color-surface-raised); border-color:var(--color-border-soft)">
        <div class="flex items-center gap-2 font-bold text-base" style="font-family:var(--font-display); color:var(--color-text)">
          <div class="w-7 h-7 rounded-lg flex items-center justify-center" style="background:var(--color-primary)">
            <ChefHat class="w-4 h-4 text-white" />
          </div>
          MealWise
        </div>
        <ThemeSwitcher />
      </header>

      <!-- Scrollable page -->
      <main class="flex-1 overflow-y-auto pb-24 md:pb-6 px-4 md:px-6 py-6">
        <RouterView v-slot="{ Component }">
          <Transition name="page" mode="out-in">
            <component :is="Component" />
          </Transition>
        </RouterView>
      </main>
    </div>

    <!-- ── Bottom nav (mobile) ───────────────────────────────────────── -->
    <nav class="md:hidden fixed bottom-0 left-0 right-0 border-t z-30 flex items-center justify-around px-2 h-16"
      style="background:var(--color-surface-raised); border-color:var(--color-border-soft)">
      <RouterLink
        v-for="item in navItems.slice(0,5)"
        :key="item.to"
        :to="item.to"
        class="flex flex-col items-center gap-0.5 py-1 px-2 rounded-xl transition-all no-underline min-w-0"
        :style="isActive(item.to) ? 'color:var(--color-primary)' : 'color:var(--color-text-faint)'"
      >
        <component :is="item.icon" class="w-5 h-5" />
        <span class="text-[10px] font-medium truncate">{{ item.label }}</span>
      </RouterLink>
    </nav>
  </div>
</template>
