<script setup lang="ts">
import { onMounted } from 'vue'
import { BarChart3, TrendingUp, Users, BookOpen, FlaskConical, FileCheck } from 'lucide-vue-next'
import { useAdminStore } from '@/stores/admin'

const admin = useAdminStore()
onMounted(() => admin.fetchStats())
</script>

<template>
  <div>
    <div class="mb-6 animate-fade-up">
      <h1 class="text-3xl font-black mb-1" style="font-family:var(--font-display)">Statistics</h1>
      <p class="text-sm" style="color:var(--color-text-muted)">System-wide usage and health metrics</p>
    </div>

    <div v-if="!admin.stats" class="grid grid-cols-1 md:grid-cols-2 gap-4">
      <div v-for="i in 6" :key="i" class="skeleton h-32 rounded-xl"></div>
    </div>

    <div v-else class="flex flex-col gap-6">

      <!-- Meals breakdown -->
      <div class="card p-6 animate-fade-up delay-100">
        <h2 class="text-lg font-bold mb-4 flex items-center gap-2" style="font-family:var(--font-display)">
          <BookOpen class="w-5 h-5" style="color:var(--color-primary)" /> Meal Library
        </h2>
        <div class="grid grid-cols-2 md:grid-cols-4 gap-3">
          <div v-for="(val, key) in {
            'Total': admin.stats.total_meals,
            'Active': admin.stats.active_meals,
            'Hidden': admin.stats.hidden_meals,
            'Pending': admin.stats.pending_meals,
          }" :key="key" class="p-4 rounded-xl text-center" style="background:var(--color-surface)">
            <p class="text-2xl font-black" style="font-family:var(--font-display); color:var(--color-primary)">{{ val }}</p>
            <p class="text-xs" style="color:var(--color-text-muted)">{{ key }}</p>
          </div>
        </div>
      </div>

      <!-- Users breakdown -->
      <div class="card p-6 animate-fade-up delay-200">
        <h2 class="text-lg font-bold mb-4 flex items-center gap-2" style="font-family:var(--font-display)">
          <Users class="w-5 h-5" style="color:var(--color-success)" /> Users
        </h2>
        <div class="grid grid-cols-2 md:grid-cols-3 gap-3">
          <div v-for="(val, key) in {
            'Total': admin.stats.total_users,
            'Active': admin.stats.active_users,
            'Admins': admin.stats.admin_users,
          }" :key="key" class="p-4 rounded-xl text-center" style="background:var(--color-surface)">
            <p class="text-2xl font-black" style="font-family:var(--font-display); color:var(--color-success)">{{ val }}</p>
            <p class="text-xs" style="color:var(--color-text-muted)">{{ key }}</p>
          </div>
        </div>
      </div>

      <!-- Contributions breakdown -->
      <div class="card p-6 animate-fade-up delay-300">
        <h2 class="text-lg font-bold mb-4 flex items-center gap-2" style="font-family:var(--font-display)">
          <FileCheck class="w-5 h-5" style="color:var(--color-violet)" /> Contributions
        </h2>
        <div class="grid grid-cols-2 md:grid-cols-3 gap-3">
          <div v-for="(val, key) in {
            'Pending':  admin.stats.pending_contributions,
            'Approved': admin.stats.approved_contributions,
            'Rejected': admin.stats.rejected_contributions,
          }" :key="key" class="p-4 rounded-xl text-center" style="background:var(--color-surface)">
            <p class="text-2xl font-black" style="font-family:var(--font-display); color:var(--color-violet)">{{ val }}</p>
            <p class="text-xs" style="color:var(--color-text-muted)">{{ key }}</p>
          </div>
        </div>
      </div>

      <!-- Ingredient nutrition coverage -->
      <div class="card p-6 animate-fade-up delay-400">
        <h2 class="text-lg font-bold mb-4 flex items-center gap-2" style="font-family:var(--font-display)">
          <FlaskConical class="w-5 h-5" style="color:var(--color-warning)" /> Nutrition Coverage
        </h2>
        <div class="flex items-center gap-4 mb-3">
          <div class="flex-1 h-4 rounded-full overflow-hidden" style="background:var(--color-surface)">
            <div class="h-full rounded-full transition-all"
              :style="`width: ${admin.stats.total_ingredients > 0 ? Math.round(((admin.stats.total_ingredients - admin.stats.ingredients_missing_nutrition) / admin.stats.total_ingredients) * 100) : 0}%; background: var(--color-success)`">
            </div>
          </div>
          <span class="text-sm font-bold" style="color:var(--color-success)">
            {{ admin.stats.total_ingredients > 0 ? Math.round(((admin.stats.total_ingredients - admin.stats.ingredients_missing_nutrition) / admin.stats.total_ingredients) * 100) : 0 }}%
          </span>
        </div>
        <p class="text-sm" style="color:var(--color-text-muted)">
          {{ admin.stats.total_ingredients - admin.stats.ingredients_missing_nutrition }} of {{ admin.stats.total_ingredients }} ingredients have nutrition data.
          <span v-if="admin.stats.ingredients_missing_nutrition > 0" style="color:var(--color-warning)">
            {{ admin.stats.ingredients_missing_nutrition }} still missing.
          </span>
        </p>
      </div>

      <!-- Activity -->
      <div class="card p-6 animate-fade-up delay-500">
        <h2 class="text-lg font-bold mb-4 flex items-center gap-2" style="font-family:var(--font-display)">
          <TrendingUp class="w-5 h-5" style="color:var(--color-primary)" /> Activity
        </h2>
        <div class="p-4 rounded-xl text-center" style="background:var(--color-surface)">
          <p class="text-4xl font-black mb-1" style="font-family:var(--font-display); color:var(--color-primary)">{{ admin.stats.total_log_entries }}</p>
          <p class="text-sm" style="color:var(--color-text-muted)">Total meals logged across all users</p>
        </div>
      </div>
    </div>
  </div>
</template>
