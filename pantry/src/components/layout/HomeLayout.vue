<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { RouterLink, RouterView, useRoute } from 'vue-router'
import { Menu, X, ChefHat } from 'lucide-vue-next'
import ThemeSwitcher from '@/components/general/ThemeSwitcher.vue'

const route    = useRoute()
const menuOpen = ref(false)
const scrolled = ref(false)

const navLinks = [
  { to: '/',             label: 'Home' },
  { to: '/how-it-works', label: 'How It Works' },
  { to: '/about',        label: 'About' },
  { to: '/contact',      label: 'Contact' },
  { to: '/donate',       label: 'Donate' },
]

function onScroll() { scrolled.value = window.scrollY > 24 }
onMounted(()  => window.addEventListener('scroll', onScroll))
onUnmounted(() => window.removeEventListener('scroll', onScroll))
</script>

<template>
  <!-- Single root div required for <Transition> in App.vue -->
  <div class="min-h-screen flex flex-col" style="background:var(--color-bg)">

    <!-- Nav -->
    <header
      class="fixed top-0 left-0 right-0 z-40 transition-all duration-300"
      :class="scrolled ? 'shadow-lg' : ''"
      :style="`background: ${scrolled ? 'var(--color-surface-raised)' : 'transparent'}; border-bottom: ${scrolled ? '1px solid var(--color-border-soft)' : 'none'};`"
    >
      <div class="container flex items-center justify-between h-16">
        <RouterLink to="/" class="flex items-center gap-2 font-bold text-xl no-underline" style="color:var(--color-text); font-family:var(--font-display)">
          <div class="w-9 h-9 rounded-xl flex items-center justify-center" style="background:var(--color-primary)">
            <ChefHat class="w-5 h-5 text-white" />
          </div>
          MealWise
        </RouterLink>

        <nav class="hidden md:flex items-center gap-1">
          <RouterLink
            v-for="link in navLinks"
            :key="link.to"
            :to="link.to"
            class="px-4 py-2 rounded-full text-sm font-medium transition-all no-underline"
            :style="route.path === link.to
              ? 'background:var(--color-primary-soft); color:var(--color-primary);'
              : 'color:var(--color-text-muted);'"
          >
            {{ link.label }}
          </RouterLink>
        </nav>

        <div class="flex items-center gap-3">
          <ThemeSwitcher class="hidden md:flex" />
          <RouterLink to="/auth/login"    class="btn-ghost hidden md:inline-flex !py-2 !px-4 text-sm">Sign In</RouterLink>
          <RouterLink to="/auth/register" class="btn-primary hidden md:inline-flex !py-2 !px-4 text-sm">Get Started</RouterLink>
          <button class="md:hidden w-9 h-9 flex items-center justify-center rounded-xl" style="background:var(--color-surface)" @click="menuOpen = !menuOpen">
            <X v-if="menuOpen" class="w-5 h-5" style="color:var(--color-text)" />
            <Menu v-else        class="w-5 h-5" style="color:var(--color-text)" />
          </button>
        </div>
      </div>

      <!-- Mobile menu -->
      <Transition name="page">
        <div v-if="menuOpen" class="md:hidden border-t" style="background:var(--color-surface-raised); border-color:var(--color-border-soft)">
          <div class="container py-4 flex flex-col gap-1">
            <RouterLink
              v-for="link in navLinks"
              :key="link.to"
              :to="link.to"
              class="px-4 py-3 rounded-xl text-sm font-medium no-underline"
              style="color:var(--color-text)"
              @click="menuOpen = false"
            >
              {{ link.label }}
            </RouterLink>
            <div class="divider" />
            <div class="flex items-center justify-between px-2">
              <ThemeSwitcher />
              <div class="flex gap-2">
                <RouterLink to="/auth/login"    class="btn-ghost !py-2 !px-4 text-sm"   @click="menuOpen = false">Sign In</RouterLink>
                <RouterLink to="/auth/register" class="btn-primary !py-2 !px-4 text-sm" @click="menuOpen = false">Get Started</RouterLink>
              </div>
            </div>
          </div>
        </div>
      </Transition>
    </header>

    <!-- Page content -->
    <main class="flex-1 pt-16">
      <RouterView v-slot="{ Component: PageComponent, route: pageRoute }">
        <Transition name="page" mode="out-in">
          <component :is="PageComponent" :key="pageRoute.path" />
        </Transition>
      </RouterView>
    </main>

    <!-- Footer -->
    <footer class="mt-24 border-t" style="background:var(--color-surface); border-color:var(--color-border-soft)">
      <div class="container py-12">
        <div class="grid grid-cols-1 md:grid-cols-4 gap-8 mb-10">
          <div class="md:col-span-2">
            <RouterLink to="/" class="flex items-center gap-2 font-bold text-lg mb-3 no-underline" style="color:var(--color-text); font-family:var(--font-display)">
              <div class="w-8 h-8 rounded-lg flex items-center justify-center" style="background:var(--color-primary)">
                <ChefHat class="w-4 h-4 text-white" />
              </div>
              MealWise
            </RouterLink>
            <p class="text-sm leading-relaxed max-w-xs" style="color:var(--color-text-muted)">
              Your personal meal planning companion, rooted in the rich flavours of West African cuisine.
            </p>
          </div>
          <div>
            <p class="font-semibold text-sm mb-3" style="color:var(--color-text)">Product</p>
            <div class="flex flex-col gap-2">
              <RouterLink v-for="link in navLinks" :key="link.to" :to="link.to" class="text-sm no-underline hover:text-[var(--color-primary)] transition-colors" style="color:var(--color-text-muted)">{{ link.label }}</RouterLink>
            </div>
          </div>
          <div>
            <p class="font-semibold text-sm mb-3" style="color:var(--color-text)">Account</p>
            <div class="flex flex-col gap-2">
              <RouterLink to="/auth/login"    class="text-sm no-underline hover:text-[var(--color-primary)] transition-colors" style="color:var(--color-text-muted)">Sign In</RouterLink>
              <RouterLink to="/auth/register" class="text-sm no-underline hover:text-[var(--color-primary)] transition-colors" style="color:var(--color-text-muted)">Create Account</RouterLink>
            </div>
          </div>
        </div>
        <div class="divider" />
        <div class="flex flex-col md:flex-row items-center justify-between gap-4">
          <p class="text-xs" style="color:var(--color-text-faint)">© {{ new Date().getFullYear() }} MealWise. All rights reserved.</p>
          <p class="text-xs" style="color:var(--color-text-faint)">Made with love for West African cuisine 🍲</p>
        </div>
      </div>
    </footer>

  </div>
</template>