import { fileURLToPath, URL } from 'node:url'
import { defineConfig, loadEnv } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '')

  // Backend manzili. TaskFlow.API da CORS sozlanmagan, shuning uchun
  // brauzer to'g'ridan-to'g'ri so'rov yubora olmaydi — dev serverning
  // proxy'si orqali o'tamiz va so'rov bir xil origin'dan ketadi.
  const target = env.VITE_API_TARGET ?? 'https://localhost:7108'

  return {
    plugins: [vue()],

    resolve: {
      alias: {
        '@': fileURLToPath(new URL('./src', import.meta.url)),
      },
    },

    server: {
      port: 5173,
      strictPort: true,
      proxy: {
        '/api': {
          target,
          changeOrigin: true,
          // dotnet dev-certs o'zini imzolagan sertifikat beradi
          secure: false,
        },
        '/hubs': {
          target,
          changeOrigin: true,
          secure: false,
          ws: true,
        },
      },
    },

    build: {
      outDir: 'dist',
      sourcemap: mode !== 'production',
    },
  }
})
