import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useUiStore = defineStore('ui', () => {
  const sidebarCollapsed = ref(false)
  const mobileNavOpen    = ref(false)

  function toggleSidebar()   { sidebarCollapsed.value = !sidebarCollapsed.value }
  function toggleMobileNav() { mobileNavOpen.value    = !mobileNavOpen.value }
  function closeMobileNav()  { mobileNavOpen.value    = false }

  return { sidebarCollapsed, mobileNavOpen, toggleSidebar, toggleMobileNav, closeMobileNav }
})
