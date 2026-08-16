import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// https://vite.dev/config/
export default defineConfig({
  plugins: [vue()],
  server: {
    port: 5173,
    strictPort: true,
    watch: {
      ignored: ['**/src-tauri/**'],
    },
    proxy: {
      '^/process': {
        target: 'http://127.0.0.1:8001',
        changeOrigin: true,
        ws: true,
      },
      '^/sessions': {
        target: 'http://127.0.0.1:8001',
        changeOrigin: true,
        ws: true,
      },
      '^/api': {
        target: 'http://127.0.0.1:8001',
        changeOrigin: true,
        ws: true,
      },
      '^/ai': {
        target: 'http://127.0.0.1:8001',
        changeOrigin: true,
        ws: true,
        bypass(req) {
          const url = req.url ?? ''
          if (url === '/ai-tools' || url.startsWith('/ai-tools?')) {
            return '/index.html'
          }
        },
      },
      '^/knowledge': {
        target: 'http://127.0.0.1:8001',
        changeOrigin: true,
        ws: true,
        bypass(req) {
          const url = req.url ?? ''
          if (url === '/knowledge' || url.startsWith('/knowledge?')) {
            return '/index.html'
          }
        },
      },
      '^/quiz': {
        target: 'http://127.0.0.1:8001',
        changeOrigin: true,
      },
      '^/wrongbook': {
        target: 'http://127.0.0.1:8001',
        changeOrigin: true,
        bypass(req) {
          const url = req.url ?? ''
          if (url === '/wrongbook' || url.startsWith('/wrongbook?')) {
            return '/index.html'
          }
        },
      },
      '^/interviews': {
        target: 'http://127.0.0.1:8001',
        changeOrigin: true,
      },
      '^/analytics': {
        target: 'http://127.0.0.1:8001',
        changeOrigin: true,
      },
    },
  },
})
