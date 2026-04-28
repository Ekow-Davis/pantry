<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { RouterLink } from 'vue-router'
import { ArrowRight, Flame, Leaf, CalendarDays, ShoppingBasket } from 'lucide-vue-next'

const visible = ref(false)
onMounted(() => setTimeout(() => (visible.value = true), 100))

const stats = [
  { value: '200+', label: 'West African Recipes' },
  { value: '15+',  label: 'Ghanaian Dishes' },
  { value: '4-day',label: 'Smart Cooldown' },
]

const features = [
  {
    icon: CalendarDays,
    title: 'Smart Meal Planning',
    desc: 'Auto-generate daily meal plans that respect your cooldown rules, ingredient preferences, and dietary restrictions.',
    color: 'var(--color-primary)',
    bg: 'var(--color-primary-soft)',
  },
  {
    icon: Flame,
    title: 'West African Focus',
    desc: 'Hundreds of authentic Ghanaian and West African recipes — from Fufu to Jollof, all at your fingertips.',
    color: '#E8591A',
    bg: '#fef0ea',
  },
  {
    icon: ShoppingBasket,
    title: 'Pantry Matcher',
    desc: 'Tell us what ingredients you have. We tell you exactly what you can cook right now — no trips needed.',
    color: 'var(--color-success)',
    bg: 'var(--color-success-soft)',
  },
  {
    icon: Leaf,
    title: 'Nutrition Tracking',
    desc: 'Per-ingredient nutrition data sourced from FAO/WHO and USDA. Know exactly what goes into every meal.',
    color: '#7C3AED',
    bg: 'var(--color-violet-soft)',
  },
]

const floatingFoods = [
  { emoji: '🍲', size: 'w-20 h-20', pos: 'top-8 right-12',      delay: '0s',   anim: 'animate-float' },
  { emoji: '🌶️', size: 'w-14 h-14', pos: 'top-32 right-2',      delay: '0.8s', anim: 'animate-float-slow' },
  { emoji: '🍗', size: 'w-16 h-16', pos: 'bottom-24 right-16',  delay: '0.4s', anim: 'animate-float-alt' },
  { emoji: '🥘', size: 'w-12 h-12', pos: 'top-20 left-8',       delay: '1.2s', anim: 'animate-float' },
  { emoji: '🌿', size: 'w-10 h-10', pos: 'bottom-32 left-4',    delay: '0.6s', anim: 'animate-float-slow' },
]
</script>

<template>
  <!-- Single root element required for <Transition> to work correctly -->
  <div>

    <!-- ── HERO ──────────────────────────────────────────────────────── -->
    <section class="relative overflow-hidden min-h-[92vh] flex items-center" style="background:var(--color-bg)">
      <div class="absolute -top-32 -right-32 w-96 h-96 rounded-full opacity-20 animate-blob"
        style="background: radial-gradient(circle, var(--color-primary) 0%, transparent 70%)"></div>
      <div class="absolute -bottom-20 -left-20 w-80 h-80 rounded-full opacity-15 animate-blob"
        style="background: radial-gradient(circle, #E6A817 0%, transparent 70%); animation-delay: 2s"></div>

      <div
        v-for="(food, i) in floatingFoods"
        :key="i"
        class="absolute hidden lg:flex items-center justify-center rounded-full shadow-lg text-3xl select-none"
        :class="[food.size, food.pos, food.anim]"
        :style="`animation-delay: ${food.delay}; background: var(--color-surface-raised); border: 1.5px solid var(--color-border-soft);`"
      >
        {{ food.emoji }}
      </div>

      <div class="container relative z-10">
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">

          <div :class="visible ? 'animate-fade-up' : 'opacity-0'">
            <div class="inline-flex items-center gap-2 px-4 py-2 rounded-full mb-6 text-sm font-semibold"
              style="background:var(--color-primary-soft); color:var(--color-primary)">
              <Flame class="w-4 h-4" />
              Ghanaian & West African Cuisine
            </div>

            <h1 class="text-5xl md:text-6xl lg:text-7xl font-black mb-6 leading-tight"
              style="font-family:var(--font-display); color:var(--color-text)">
              Plan meals
              <span style="color:var(--color-primary)"> the<br>West African</span>
              way.
            </h1>

            <p class="text-lg mb-8 max-w-lg leading-relaxed" style="color:var(--color-text-muted)">
              Smart meal planning built around authentic Ghanaian and West African recipes. Stop repeating meals, discover new dishes, and cook with confidence every day.
            </p>

            <div class="flex flex-wrap items-center gap-4 mb-10">
              <RouterLink to="/auth/register" class="btn-primary text-base !py-3 !px-8">
                Start Planning Free <ArrowRight class="w-5 h-5" />
              </RouterLink>
              <RouterLink to="/how-it-works" class="btn-ghost text-base !py-3 !px-8">
                See How It Works
              </RouterLink>
            </div>

            <div class="flex flex-wrap gap-6">
              <div v-for="stat in stats" :key="stat.value">
                <p class="text-2xl font-black" style="font-family:var(--font-display); color:var(--color-primary)">{{ stat.value }}</p>
                <p class="text-xs font-medium" style="color:var(--color-text-muted)">{{ stat.label }}</p>
              </div>
            </div>
          </div>

          <div class="relative flex items-center justify-center" :class="visible ? 'animate-scale-in delay-300' : 'opacity-0'">
            <div class="relative w-72 h-72 md:w-96 md:h-96">
              <div class="absolute inset-0 rounded-full border-2 border-dashed opacity-20 animate-spin-slow"
                style="border-color:var(--color-primary)"></div>
              <div class="absolute inset-6 food-blob-anim flex items-center justify-center text-8xl shadow-2xl"
                style="background: linear-gradient(135deg, var(--color-primary-soft), var(--color-surface-raised))">🍲</div>
              <div class="absolute top-2 left-1/2 -translate-x-1/2 w-14 h-14 rounded-full flex items-center justify-center text-2xl shadow-md animate-float"
                style="background:var(--color-surface-raised); border:1.5px solid var(--color-border-soft)">🌶️</div>
              <div class="absolute right-2 top-1/2 -translate-y-1/2 w-14 h-14 rounded-full flex items-center justify-center text-2xl shadow-md animate-float-slow"
                style="background:var(--color-surface-raised); border:1.5px solid var(--color-border-soft)">🍗</div>
              <div class="absolute bottom-2 left-1/2 -translate-x-1/2 w-14 h-14 rounded-full flex items-center justify-center text-2xl shadow-md animate-float-alt"
                style="background:var(--color-surface-raised); border:1.5px solid var(--color-border-soft)">🥜</div>
              <div class="absolute left-2 top-1/2 -translate-y-1/2 w-14 h-14 rounded-full flex items-center justify-center text-2xl shadow-md animate-float"
                style="background:var(--color-surface-raised); border:1.5px solid var(--color-border-soft)">🌿</div>
            </div>
          </div>

        </div>
      </div>
    </section>

    <!-- ── FEATURES ──────────────────────────────────────────────────── -->
    <section class="section" style="background:var(--color-surface)">
      <div class="container">
        <div class="text-center mb-14">
          <span class="badge badge-primary mb-3">Why MealWise</span>
          <h2 class="text-4xl md:text-5xl font-black mb-4" style="font-family:var(--font-display)">Everything you need to</h2>
          <h2 class="text-4xl md:text-5xl font-black" style="font-family:var(--font-display); color:var(--color-primary)">eat well, every day</h2>
        </div>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div
            v-for="(feat, i) in features"
            :key="feat.title"
            class="card p-6 flex gap-4 items-start animate-fade-up"
            :class="`delay-${(i + 1) * 100}`"
          >
            <div class="w-12 h-12 rounded-xl flex-shrink-0 flex items-center justify-center"
              :style="`background:${feat.bg}; color:${feat.color}`">
              <component :is="feat.icon" class="w-6 h-6" />
            </div>
            <div>
              <h3 class="text-lg font-bold mb-1" style="font-family:var(--font-display)">{{ feat.title }}</h3>
              <p class="text-sm leading-relaxed" style="color:var(--color-text-muted)">{{ feat.desc }}</p>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- ── HOW IT WORKS TEASER ───────────────────────────────────────── -->
    <section class="section">
      <div class="container">
        <div class="text-center mb-14">
          <h2 class="text-4xl md:text-5xl font-black mb-4" style="font-family:var(--font-display)">Up and running</h2>
          <h2 class="text-4xl md:text-5xl font-black" style="font-family:var(--font-display); color:var(--color-primary)">in 3 steps</h2>
        </div>
        <div class="grid grid-cols-1 md:grid-cols-3 gap-8">
          <div
            v-for="(step, i) in [
              { n: '01', icon: '🧑‍🍳', title: 'Create your profile',  desc: 'Set your food preferences, cooldown period, and any ingredient restrictions or allergies.' },
              { n: '02', icon: '📅',   title: 'Get your daily plan',   desc: 'MealWise generates breakfast, lunch and dinner recommendations that respect your rules.' },
              { n: '03', icon: '✅',   title: 'Cook and confirm',      desc: 'Mark what you cooked, log extras, and let the system learn your habits over time.' },
            ]"
            :key="i"
            class="text-center animate-fade-up"
            :class="`delay-${(i + 1) * 200}`"
          >
            <div class="w-20 h-20 rounded-2xl mx-auto mb-4 flex items-center justify-center text-4xl shadow-md"
              style="background:var(--color-primary-soft)">{{ step.icon }}</div>
            <div class="text-5xl font-black opacity-10 mb-1" style="font-family:var(--font-display); color:var(--color-primary)">{{ step.n }}</div>
            <h3 class="text-xl font-bold mb-2" style="font-family:var(--font-display)">{{ step.title }}</h3>
            <p class="text-sm leading-relaxed" style="color:var(--color-text-muted)">{{ step.desc }}</p>
          </div>
        </div>
        <div class="text-center mt-12">
          <RouterLink to="/auth/register" class="btn-primary text-base !py-3 !px-10">
            Get Started Free <ArrowRight class="w-5 h-5" />
          </RouterLink>
        </div>
      </div>
    </section>

    <!-- ── CTA BANNER ────────────────────────────────────────────────── -->
    <section class="section-sm">
      <div class="container">
        <div class="relative overflow-hidden rounded-3xl p-10 md:p-16 text-center"
          style="background: linear-gradient(135deg, var(--color-primary), var(--color-primary-hover))">
          <div class="text-6xl mb-4">🍛</div>
          <h2 class="text-3xl md:text-5xl font-black text-white mb-4" style="font-family:var(--font-display)">
            Start eating smarter today
          </h2>
          <p class="text-white/80 text-lg mb-8 max-w-lg mx-auto">
            Join MealWise and bring structure, variety and authentic West African flavour to every meal.
          </p>
          <RouterLink to="/auth/register"
            class="inline-flex items-center gap-2 px-8 py-3 rounded-full font-semibold text-base transition-all"
            style="background:#fff; color:var(--color-primary)"
          >
            Create Free Account <ArrowRight class="w-5 h-5" />
          </RouterLink>
        </div>
      </div>
    </section>

  </div>
</template>