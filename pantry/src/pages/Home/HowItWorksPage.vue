<script setup lang="ts">
import { BookOpen, CalendarDays, CheckCircle2, ShoppingBasket, ClipboardList, Utensils } from 'lucide-vue-next'

const steps = [
  {
    icon: ClipboardList,
    title: 'Create your profile',
    desc: "Sign up, set your country, and configure your meal planning preferences — including cooldown days and whether the system should assume a meal was cooked if you forget to confirm.",
  },
  {
    icon: BookOpen,
    title: 'Browse the meal library',
    desc: "Explore hundreds of recipes covering Ghanaian staples (Fufu, Waakye, Banku), West African classics, and international dishes. Filter by category — breakfast, lunch, dinner, snack.",
  },
  {
    icon: Utensils,
    title: 'Set your preferences',
    desc: "Pin specific meals to specific meal times (e.g. Rice Porridge for breakfast only), blacklist ingredients you're allergic to or can't access, and mark meals you love.",
  },
  {
    icon: CalendarDays,
    title: 'Get your daily plan',
    desc: "Each day MealWise generates a 3-slot plan (breakfast, lunch, dinner) filtered through your cooldown rules, slot preferences, and blacklisted ingredients. You can add extra snack slots too.",
  },
  {
    icon: CheckCircle2,
    title: 'Confirm what you cooked',
    desc: "At end of day, mark each slot — cooked, skipped, or replaced with something different. Only confirmed meals consume their cooldown.",
  },
  {
    icon: ShoppingBasket,
    title: 'Discover via the pantry',
    desc: "List your available ingredients and instantly see every meal you can make right now, plus those that need just one more ingredient.",
  },
]
</script>

<template>
  <section class="section">
    <div class="container max-w-4xl">
      <div class="text-center mb-16">
        <span class="badge badge-primary mb-4">How It Works</span>
        <h1 class="text-5xl font-black mb-4" style="font-family:var(--font-display)">
          The MealWise system,<br>
          <span style="color:var(--color-primary)">explained simply</span>
        </h1>
        <p class="text-lg max-w-xl mx-auto" style="color:var(--color-text-muted)">
          Smart planning rules meet your personal preferences. Here's how it all comes together.
        </p>
      </div>

      <!-- Timeline steps -->
      <div class="relative">
        <div class="absolute left-6 top-0 bottom-0 w-0.5 hidden md:block" style="background:var(--color-border)"></div>
        <div class="flex flex-col gap-10">
          <div
            v-for="(step, i) in steps"
            :key="i"
            class="flex gap-6 items-start animate-fade-up"
            :class="`delay-${(i + 1) * 100}`"
          >
            <div class="w-12 h-12 rounded-full flex-shrink-0 flex items-center justify-center text-white font-bold text-sm relative z-10"
              style="background:var(--color-primary)">{{ i + 1 }}</div>
            <div class="card flex-1 p-6">
              <div class="flex items-center gap-3 mb-2">
                <component :is="step.icon" class="w-5 h-5" style="color:var(--color-primary)" />
                <h3 class="text-lg font-bold" style="font-family:var(--font-display)">{{ step.title }}</h3>
              </div>
              <p class="text-sm leading-relaxed" style="color:var(--color-text-muted)">{{ step.desc }}</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Cooldown explainer -->
      <div class="mt-16 p-8 rounded-3xl" style="background:var(--color-primary-soft); border:1.5px solid var(--color-border-soft)">
        <h2 class="text-2xl font-black mb-3" style="font-family:var(--font-display); color:var(--color-primary)">The Cooldown System</h2>
        <p class="text-sm leading-relaxed mb-4" style="color:var(--color-text-muted)">
          The default cooldown is 4 days. If you eat <strong>Jollof Rice on Monday</strong>, MealWise won't recommend it again until <strong>Saturday</strong>.
          This keeps your meals varied without any manual effort. You can adjust the cooldown in settings — anywhere from 1 to 30 days.
        </p>
        <div class="flex flex-wrap gap-3 text-xs font-semibold">
          <span class="badge badge-primary">Monday: Jollof Rice ✓</span>
          <span class="badge badge-warning">Tue–Fri: On cooldown</span>
          <span class="badge badge-success">Saturday: Available again</span>
        </div>
      </div>
    </div>
  </section>
</template>