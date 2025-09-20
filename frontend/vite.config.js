import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  build: {
    outDir: 'dist',
    assetsDir: 'assets',
  },
  server: {
    proxy: {
      '/api': {
        target: process.env.NODE_ENV === 'production' 
          ? 'https://phishguard-pro.vercel.app'  // Update this after deployment
          : 'http://127.0.0.1:5001',
        changeOrigin: true,
      },
    },
  },
})
