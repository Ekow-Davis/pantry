import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

// Factory function — must be called AFTER app.use(pinia) in main.ts.
// Avoids the "getActivePinia was called but there was no active Pinia" error
// that happens when the router is created as a module-level singleton.
export function createAppRouter() {
  const router = createRouter({
    history: createWebHistory(),
    scrollBehavior: () => ({ top: 0, behavior: 'smooth' }),
    routes: [

      {
        path: '/',
        component: () => import('@/components/layout/HomeLayout.vue'),
        children: [
          { path: '',             name: 'landing',      component: () => import('@/pages/Home/LandingPage.vue') },
          { path: 'how-it-works', name: 'how-it-works', component: () => import('@/pages/Home/HowItWorksPage.vue') },
          { path: 'about',        name: 'about',        component: () => import('@/pages/Home/AboutPage.vue') },
          { path: 'contact',      name: 'contact',      component: () => import('@/pages/Home/ContactPage.vue') },
          { path: 'donate',       name: 'donate',       component: () => import('@/pages/Home/DonatePage.vue') },
        ],
      },

      {
        path: '/auth',
        component: () => import('@/components/layout/AuthLayout.vue'),
        meta: { guestOnly: true },
        children: [
          { path: 'login',           name: 'login',           component: () => import('@/pages/Auth/LoginPage.vue') },
          { path: 'register',        name: 'register',        component: () => import('@/pages/Auth/RegisterPage.vue') },
          { path: 'forgot-password', name: 'forgot-password', component: () => import('@/pages/Auth/ForgotPasswordPage.vue') },
          { path: 'reset-password',  name: 'reset-password',  component: () => import('@/pages/Auth/ResetPasswordPage.vue') },
        ],
      },

      {
        path: '/app',
        component: () => import('@/components/layout/AppLayout.vue'),
        meta: { requiresAuth: true },
        children: [
          { path: '',           redirect: '/app/dashboard' },
          { path: 'dashboard',  name: 'dashboard',   component: () => import('@/pages/App/DashboardPage.vue') },
          { path: 'plan',       name: 'plan',         component: () => import('@/pages/App/PlanPage.vue') },
          { path: 'meals',      name: 'meals',        component: () => import('@/pages/App/MealsPage.vue') },
          { path: 'meals/:id',  name: 'meal-detail',  component: () => import('@/pages/App/MealDetailPage.vue') },
          { path: 'pantry',     name: 'pantry',       component: () => import('@/pages/App/PantryPage.vue') },
          { path: 'history',    name: 'history',      component: () => import('@/pages/App/HistoryPage.vue') },
          { path: 'contribute', name: 'contribute',   component: () => import('@/pages/App/ContributePage.vue') },
          { path: 'settings',   name: 'settings',     component: () => import('@/pages/App/SettingsPage.vue') },
        ],
      },

      {
        path: '/admin',
        component: () => import('@/components/layout/AdminLayout.vue'),
        meta: { requiresAuth: true, requiresAdmin: true },
        children: [
          { path: '',              redirect: '/admin/dashboard' },
          { path: 'dashboard',     name: 'admin-dashboard',     component: () => import('@/pages/Admin/AdminDashboard.vue') },
          { path: 'users',         name: 'admin-users',         component: () => import('@/pages/Admin/AdminUsers.vue') },
          { path: 'meals',         name: 'admin-meals',         component: () => import('@/pages/Admin/AdminMeals.vue') },
          { path: 'contributions', name: 'admin-contributions', component: () => import('@/pages/Admin/AdminContributions.vue') },
          { path: 'ingredients',   name: 'admin-ingredients',   component: () => import('@/pages/Admin/AdminIngredients.vue') },
          { path: 'stats',         name: 'admin-stats',         component: () => import('@/pages/Admin/AdminStats.vue') },
        ],
      },

      { path: '/:pathMatch(.*)*', name: 'not-found', component: () => import('@/pages/General/NotFoundPage.vue') },
    ],
  })

  router.beforeEach(async (to, _from, next) => {
    const auth = useAuthStore()
    await auth.init()

    if (to.meta.requiresAuth && !auth.isAuthenticated) {
      return next({ name: 'login', query: { redirect: to.fullPath } })
    }
    if (to.meta.requiresAdmin && !auth.isAdmin) {
      return next({ name: 'dashboard' })
    }
    if (to.meta.guestOnly && auth.isAuthenticated) {
      return next(auth.isAdmin ? '/admin' : '/app/dashboard')
    }
    next()
  })

  return router
}