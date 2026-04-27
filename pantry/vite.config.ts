import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import tailwindcss from '@tailwindcss/vite'
// import { VitePWA } from 'vite-plugin-pwa'
import { fileURLToPath, URL } from 'node:url'

export default defineConfig({
  plugins: [
    vue(),
    tailwindcss(),
    // VitePWA({
    //   registerType: 'autoUpdate',
    //   includeAssets: ['icon-192.png', 'icon-512.png'],
    //   manifest: {
    //     name: 'MealWise',
    //     short_name: 'MealWise',
    //     description: 'Your personal West African meal planner',
    //     theme_color: '#C0392B',
    //     background_color: '#FDF6EE',
    //     display: 'standalone',
    //     icons: [
    //       { src: '/icon-192.png', sizes: '192x192', type: 'image/png' },
    //       { src: '/icon-512.png', sizes: '512x512', type: 'image/png' },
    //     ],
    //   },
    //   workbox: {
    //     runtimeCaching: [
    //       { urlPattern: /\/api\/v1\/meals/, handler: 'StaleWhileRevalidate' },
    //       { urlPattern: /\/api\/v1\/plan/, handler: 'NetworkFirst' },
    //     ],
    //   },
    // }),
  ],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url)),
    },
  },
})
