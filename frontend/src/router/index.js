import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useSettingsStore } from '@/stores/settings';

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
        path: `/title/:title_id`,
        name: 'Title details',
        component: () => import('@/views/TitleController.vue'),
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
    routes,
    scrollBehavior(to, from, savedPosition) {
        if (savedPosition) {
            // When using back/forward buttons, return to saved spot
            return savedPosition;
        } else {
            // For new navigation, scroll to top
            return { top: 0 };
        }
    }
})

// Router guard
router.beforeEach(async (to, from, next) => {
    const auth = useAuthStore();

    // Call auth.init() if it hasn't yet been initialized.
    // Handles expiry and auth setup.
    if (!auth.initialized) {
        await auth.init();

        // Sync user settings like themes etc.
        const settings = useSettingsStore();
        await settings.syncSettings();
    }

    // Check special case redirects
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
