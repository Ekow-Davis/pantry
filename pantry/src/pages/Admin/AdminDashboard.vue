<script setup lang="ts">
import { onMounted } from 'vue'
import { Users, BookOpen, Inbox, FlaskConical, TrendingUp, AlertCircle } from 'lucide-vue-next'
import { useAdminStore } from '@/stores/admin'
import { RouterLink } from 'vue-router'

const admin = useAdminStore()
onMounted(() => admin.fetchStats())
</script>

<template>
  <div>
    <div class="mb-6 animate-fade-up">
      <h1 class="text-3xl font-black mb-1" style="font-family:var(--font-display)">Admin Dashboard</h1>
      <p class="text-sm" style="color:var(--color-text-muted)">System overview at a glance</p>
    </div>

    <!-- Stats grid -->
    <div v-if="admin.stats" class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4 mb-8 animate-fade-up delay-100">
      <div v-for="stat in [
        { label: 'Total Users',    value: admin.stats.total_users,           icon: Users,       color: 'var(--color-primary)',  bg: 'var(--color-primary-soft)' },
        { label: 'Active Meals',   value: admin.stats.active_meals,          icon: BookOpen,    color: 'var(--color-success)',  bg: 'var(--color-success-soft)' },
        { label: 'Pending Review', value: admin.stats.pending_contributions, icon: Inbox,       color: 'var(--color-warning)',  bg: 'var(--color-warning-soft)' },
        { label: 'Missing Nutrition', value: admin.stats.ingredients_missing_nutrition, icon: AlertCircle, color: 'var(--color-danger)', bg: 'var(--color-danger-soft)' },
        { label: 'Total Meals',    value: admin.stats.total_meals,           icon: BookOpen,    color: 'var(--color-violet)',   bg: 'var(--color-violet-soft)' },
        { label: 'Total Logs',     value: admin.stats.total_log_entries,     icon: TrendingUp,  color: 'var(--color-info)',     bg: 'var(--color-info-soft)' },
        { label: 'Ingredients',    value: admin.stats.total_ingredients,     icon: FlaskConical,color: 'var(--color-cocoa)',    bg: 'var(--color-primary-soft)' },
        { label: 'Admin Users',    value: admin.stats.admin_users,           icon: Users,       color: 'var(--color-danger)',   bg: 'var(--color-danger-soft)' },
      ]" :key="stat.label" class="card p-4">
        <div class="flex items-center gap-3 mb-2">
          <div class="w-9 h-9 rounded-xl flex items-center justify-center flex-shrink-0"
            :style="`background:${stat.bg}; color:${stat.color}`">
            <component :is="stat.icon" class="w-4 h-4" />
          </div>
          <p class="text-xs font-semibold" style="color:var(--color-text-muted)">{{ stat.label }}</p>
        </div>
        <p class="text-3xl font-black" style="font-family:var(--font-display)" :style="`color:${stat.color}`">{{ stat.value }}</p>
      </div>
    </div>

    <div v-else class="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
      <div v-for="i in 8" :key="i" class="skeleton h-24 rounded-xl"></div>
    </div>

    <!-- Quick links -->
    <h2 class="text-lg font-bold mb-4 animate-fade-up delay-200" style="font-family:var(--font-display)">Quick Actions</h2>
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 animate-fade-up delay-300">
      <RouterLink
        v-for="link in [
          { to: '/admin/contributions', label: 'Review Contributions', desc: 'Approve or reject user-submitted meals', icon: Inbox, urgent: admin.stats?.pending_contributions > 0 },
          { to: '/admin/users',         label: 'Manage Users',         desc: 'View, edit, or deactivate user accounts', icon: Users, urgent: false },
          { to: '/admin/meals',         label: 'Manage Meals',         desc: 'Edit, hide, or delete meals in the library', icon: BookOpen, urgent: false },
          { to: '/admin/ingredients',   label: 'Manage Ingredients',   desc: 'Add or update ingredient nutrition data', icon: FlaskConical, urgent: admin.stats?.ingredients_missing_nutrition > 0 },
          { to: '/admin/stats',         label: 'Statistics',           desc: 'Detailed system analytics and usage', icon: TrendingUp, urgent: false },
        ]"
        :key="link.to"
        :to="link.to"
        class="card p-5 no-underline flex gap-4 items-start"
      >
        <div class="w-10 h-10 rounded-xl flex-shrink-0 flex items-center justify-center"
          :style="link.urgent ? 'background:var(--color-warning-soft); color:var(--color-warning)' : 'background:var(--color-danger-soft); color:var(--color-danger)'">
          <component :is="link.icon" class="w-5 h-5" />
        </div>
        <div>
          <p class="font-bold text-sm mb-0.5" style="color:var(--color-text)">{{ link.label }}</p>
          <p class="text-xs" style="color:var(--color-text-muted)">{{ link.desc }}</p>
          <span v-if="link.urgent" class="badge badge-warning text-[10px] mt-1">Needs attention</span>
        </div>
      </RouterLink>
    </div>
  </div>
</template>
