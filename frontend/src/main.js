import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import './assets/variables.css'
import './assets/fonts.css'
import './assets/global.css'
import './assets/default-elements.css'

const app = createApp(App)

app.use(router)

app.mount('#app')
