import { createApp } from 'vue'
import App from '@/App.vue'
import router from '@/router'
import { createPinia } from 'pinia'
import '@/assets/variables.css'
import '@/assets/fonts.css'
import '@/assets/base.css'
import '@/assets/buttons.css'
import '@/assets/utilities.css'
import '@/assets/classes.css'
import '@/assets/themes.css'
import 'boxicons/css/boxicons.min.css'
import "@egjs/vue3-flicking/dist/flicking-inline.css";

const app = createApp(App)
const pinia = createPinia()

app.use(pinia)
app.use(router)

app.mount('#app')
