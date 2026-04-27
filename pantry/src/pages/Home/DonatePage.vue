<script setup lang="ts">
import { Heart, Coffee, Star } from 'lucide-vue-next'

const tiers = [
  { icon: Coffee, label: 'Buy us a coffee', amount: '$3', desc: 'Keeps the lights on for a day', color: 'var(--color-warning)', bg: 'var(--color-warning-soft)' },
  { icon: Heart,  label: 'Supporter',        amount: '$10', desc: 'Helps us add more recipes', color: 'var(--color-primary)', bg: 'var(--color-primary-soft)' },
  { icon: Star,   label: 'Champion',          amount: '$25', desc: 'Keeps MealWise free for all', color: 'var(--color-violet)', bg: 'var(--color-violet-soft)' },
]
</script>

<template>
  <section class="section">
    <div class="container max-w-3xl">
      <div class="text-center mb-14">
        <div class="text-6xl mb-4">🫶</div>
        <h1 class="text-5xl font-black mb-4" style="font-family:var(--font-display)">Support <span style="color:var(--color-primary)">MealWise</span></h1>
        <p class="text-lg max-w-lg mx-auto" style="color:var(--color-text-muted)">
          MealWise is a passion project. If it has helped you plan better meals, consider supporting its development.
        </p>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-10">
        <div v-for="tier in tiers" :key="tier.label" class="card p-6 text-center cursor-pointer animate-fade-up hover:scale-105 transition-transform">
          <div class="w-14 h-14 rounded-2xl mx-auto mb-4 flex items-center justify-center"
            :style="`background:${tier.bg}; color:${tier.color}`">
            <component :is="tier.icon" class="w-7 h-7" />
          </div>
          <p class="text-3xl font-black mb-1" style="font-family:var(--font-display)" :style="`color:${tier.color}`">{{ tier.amount }}</p>
          <p class="font-bold mb-1">{{ tier.label }}</p>
          <p class="text-sm" style="color:var(--color-text-muted)">{{ tier.desc }}</p>
          <button class="btn-ghost w-full mt-4 !text-sm">Donate {{ tier.amount }}</button>
        </div>
      </div>

      <div class="card p-6 text-center">
        <p class="text-sm" style="color:var(--color-text-muted)">All donations go directly toward hosting costs, expanding the recipe database, and keeping MealWise free for everyone.</p>
      </div>
    </div>
  </section>
</template>
