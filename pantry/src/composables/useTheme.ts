import { ref, watch } from 'vue'

export type ThemeMode = 'light' | 'dark'
export type AccentColor = 'chili' | 'orange' | 'turmeric' | 'amber' | 'cocoa'

const mode = ref<ThemeMode>('light')
const accent = ref<AccentColor>('chili')

export const accentOptions: { key: AccentColor; label: string; hex: string }[] = [
  { key: 'chili',    label: 'Chili Red',      hex: '#C0392B' },
  { key: 'orange',   label: 'Sunset Orange',  hex: '#E8591A' },
  { key: 'turmeric', label: 'Turmeric',       hex: '#E6A817' },
  { key: 'amber',    label: 'Warm Amber',     hex: '#D4820A' },
  { key: 'cocoa',    label: 'Cocoa Brown',    hex: '#6B3A2A' },
]

function applyTheme() {
  const html = document.documentElement
  html.setAttribute('data-theme', mode.value)
  html.setAttribute('data-accent', accent.value)
  localStorage.setItem('mw-theme', mode.value)
  localStorage.setItem('mw-accent', accent.value)
}

function initTheme() {
  const savedMode   = (localStorage.getItem('mw-theme')  as ThemeMode)  || 'light'
  const savedAccent = (localStorage.getItem('mw-accent') as AccentColor) || 'chili'
  mode.value   = savedMode
  accent.value = savedAccent
  applyTheme()
}

function toggleMode() {
  mode.value = mode.value === 'light' ? 'dark' : 'light'
}

function setAccent(a: AccentColor) {
  accent.value = a
}

watch([mode, accent], applyTheme)

export function useTheme() {
  return { mode, accent, accentOptions, initTheme, toggleMode, setAccent }
}
