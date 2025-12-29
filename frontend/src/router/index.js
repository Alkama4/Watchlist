import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/', 
      name: 'Home',
      component: () => import('@/views/HomePage.vue')
    },
    {
      path: '/user', 
      redirect: '/login'
    },
    {
      path: '/login', 
      name: 'Login',
      component: () => import('@/views/LogInPage.vue')
    }
  ],
})

export default router
