import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { VitePWA } from 'vite-plugin-pwa'

// https://vitejs.dev/config/
export default defineConfig({
  base: './',
  plugins: [
    react(),
    VitePWA({
      // Manifest-only mode - no service worker
      registerType: 'autoUpdate',
      injectRegister: null,
      selfDestroying: true,
      manifest: {
        name: 'SÉPTIMA OLA',
        short_name: 'Séptima Ola',
        description: 'Reggae · Ska · Rocksteady desde Ciudad de México',
        theme_color: '#0a0b0d',
        background_color: '#0a0b0d',
        display: 'standalone',
        icons: [
          {
            src: 'logo-192.png',
            sizes: '192x192',
            type: 'image/png',
          },
          {
            src: 'logo-512.png',
            sizes: '512x512',
            type: 'image/png',
          },
        ],
      },
    }),
  ],
  // Build optimization
  build: {
    rollupOptions: {
      output: {
        manualChunks: {
          // Separate vendor chunks to improve caching
          'framer-motion': ['framer-motion'],
          'embla': ['embla-carousel-react'],
        },
      },
    },
  },
})
