import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import { createPinia } from 'pinia'
import { useAuthStore } from './stores/auth'
import './assets/variables.css'
import './assets/fonts.css'
import './assets/global.css'
import './assets/default-elements.css'

const app = createApp(App)
const pinia = createPinia()

app.use(pinia)
app.use(router)

// Refresh access token immediately
const auth = useAuthStore()
await auth.init()

app.mount('#app')
