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
        meta: { requiresAuth: true, title: 'Search' }
    },
    {
        path: '/library',
        name: 'Library',
        component: () => import('@/views/SearchPage.vue'),
        meta: { requiresAuth: true, title: 'Library' }
    },
    {
        path: '/smart_collection/:smart_collection_id',
        name: 'Smart Collection',
        component: () => import('@/views/SearchPage.vue'),
        meta: { requiresAuth: true, title: 'Smart Collection' }
    },
    {
        path: '/collections',
        name: 'Collections',
        component: () => import('@/views/CollectionsPage.vue'),
        meta: { requiresAuth: true, title: 'Collections' }
    },
    {
        path: `/title/:title_id`,
        name: 'Title details',
        component: () => import('@/views/TitleController.vue'),
        meta: { requiresAuth: true, title: 'Title Details' }
    },
    {
        path: `/collection/:tmdb_collection_id`,
        name: 'Collection details',
        component: () => import('@/views/CollectionDetailsPage.vue'),
        meta: { requiresAuth: true, title: 'Collection Details' }
    },
    {
        path: '/video_assets',
        name: 'Video Assets',
        component: () => import('@/views/VideoAssetsPage.vue'),
        meta: { requiresAuth: true, title: 'Video Assets' }
    },
    {
        path: '/account',
        name: 'Account',
        component: () => import('@/views/AccountPage.vue'),
        meta: { requiresAuth: true, title: 'Account' }
    },
    {
        path: '/login',
        name: 'Login',
        component: () => import('@/views/LogInPage.vue'),
        meta: { redirectAuthToAccount: true, title: 'Login' }
    },
    {
        path: '/register',
        name: 'Register',
        component: () => import('@/views/RegisterPage.vue'),
        meta: { redirectAuthToAccount: true, title: 'Register' }
    },
    {
        path: '/debug',
        name: 'Debug',
        component: () => import('@/views/DebugPage.vue'),
        meta: { title: 'Debug' }
    },
    {
        path: '/:pathMatch(.*)*',
        name: '404',
        component: () => import('@/views/NotFoundPage.vue'),
        meta: { title: 'Not Found' }
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
    }

    // Check special case redirects
    if (to.meta.requiresAuth && !auth.accessToken) {
        return next({ name: 'Login' });
    }
    if (to.meta.redirectAuthToAccount && auth.accessToken) {
        return next({ name: 'Account' });
    }

    next();
});

router.afterEach((to) => {
    document.title = to.meta.title ? `${to.meta.title} - Watchlist` : 'Watchlist';
});

export default router
