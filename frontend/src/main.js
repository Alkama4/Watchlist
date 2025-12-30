import { createApp } from 'vue'
import App from '@/App.vue'
import router from '@/router'
import { createPinia } from 'pinia'
import { useAuthStore } from '@/stores/auth'
import '@/assets/variables.css'
import '@/assets/fonts.css'
import '@/assets/base.css'

const app = createApp(App)
const pinia = createPinia()

app.use(pinia)

// Refresh access token immediately
const auth = useAuthStore()
await auth.init()

app.use(router)

app.mount('#app')
