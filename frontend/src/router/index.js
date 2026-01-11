import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const routes = [
    {
        path: '/',
        name: 'Home',
        component: () => import('@/views/HomePage.vue'),
        meta: { requiresAuth: true }
    },
        {
        path: '/search',
        name: 'Search',
        component: () => import('@/views/SearchPage.vue'),
        meta: { requiresAuth: true }
    },
    {
        path: '/account',
        name: 'Account',
        component: () => import('@/views/AccountPage.vue'),
        meta: { requiresAuth: true }
    },
    {
        path: '/login',
        name: 'Login',
        component: () => import('@/views/LogInPage.vue'),
        meta: { redirectAuthToAccount: true }
    },
    {
        path: '/register',
        name: 'Register',
        component: () => import('@/views/RegisterPage.vue'),
        meta: { redirectAuthToAccount: true }
    },
    {
        path: '/debug',
        name: 'Debug',
        component: () => import('@/views/DebugPage.vue')
    },
    {
        path: '/:pathMatch(.*)*',
        name: '404',
        component: () => import('@/views/NotFoundPage.vue')
    }
]

const router = createRouter({
    history: createWebHistory(import.meta.env.BASE_URL),
    routes
})

// Router guard
router.beforeEach(async (to, from, next) => {
    const auth = useAuthStore();

    // Wait for auth.init() if it hasn't finished
    if (!auth.initialized) {
        await auth.init();
    }

    if (to.meta.requiresAuth && !auth.accessToken) {
        console.log(auth.accessToken)
        return next({ name: 'Login' });
    }

    if (to.meta.redirectAuthToAccount && auth.accessToken) {
        return next({ name: 'Account' });
    }

    next();
});

export default router
