import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'
import { setUnauthorizedHandler } from './api/client'
import { useAuthStore } from './stores/auth'
import './assets/styles/base.css'

const app = createApp(App)

app.use(createPinia())

const auth = useAuthStore()

// Router guard'i ishlashidan oldin saqlangan tokenni tiklaymiz,
// aks holda sahifa yangilanganda foydalanuvchi login'ga tushib ketadi.
auth.restore()

app.use(router)

// 401 kelganda sessiyani tozalab, login sahifasiga yuboramiz.
// Buni shu yerda ulaymiz, chunki store router'ni bilmaydi.
setUnauthorizedHandler(() => {
  auth.logout()

  if (router.currentRoute.value.meta.public !== true) {
    void router.push({
      name: 'login',
      query: { redirect: router.currentRoute.value.fullPath },
    })
  }
})

app.mount('#app')
