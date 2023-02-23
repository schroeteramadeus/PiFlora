import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from '@/App.vue'
import router from '@/router'

import '@/assets/css/main.css'
import "@/assets/fontawesome/css/fontawesome.css"
import "@/assets/fontawesome/css/brands.css"
import "@/assets/fontawesome/css/solid.css"
import "@/assets/fontawesome/css/regular.css"
import "@/assets/js/lib.js"

const pinia = createPinia()

const app = createApp(App)
app.use(pinia)
app.use(router)

app.mount('#app')
