import { createApp } from 'vue'
import { createPinia } from 'pinia'
import { createAppRouter } from './router'
import App from './App.vue'
import './style.css'

const app   = createApp(App)
const pinia = createPinia()

app.use(pinia)

const router = createAppRouter()
app.use(router)

// Only register service worker in production — in dev it intercepts
// Vite's HMR requests and causes "Failed to fetch" network errors.
if ('serviceWorker' in navigator && import.meta.env.PROD) {
  navigator.serviceWorker.register('/sw.js').catch(() => {})
}

app.mount('#app')