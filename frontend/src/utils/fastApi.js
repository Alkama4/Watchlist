import axios from 'axios';
import { useAuthStore } from '../stores/auth';
import { API_BASE_URL } from './conf';
import router from '@/router';

// Axios client
const apiClient = axios.create({
    baseURL: API_BASE_URL,
    headers: { 'Content-Type': 'application/json' },
    withCredentials: true // important so cookies are sent automatically
});


// Set the access token into the headers
apiClient.interceptors.request.use((config) => {
    const auth = useAuthStore();

    // Attach token if available
    if (auth.accessToken) {
        config.headers.Authorization = `Bearer ${auth.accessToken}`;
    }

    return config;
});

// Response interceptor for automatic refresh
apiClient.interceptors.response.use(
    response => response,
    async error => {
        const auth = useAuthStore();
        const originalRequest = error.config;

        const isAuthEndpoint =
            originalRequest.url.startsWith('/auth/') &&
            !originalRequest.url.startsWith('/auth/me');

        if (
            error.response?.status === 401 &&
            !originalRequest._retry &&
            !isAuthEndpoint
        ) {
            originalRequest._retry = true;
            try {
                await auth.refresh();
                originalRequest.headers.Authorization = `Bearer ${auth.accessToken}`;
                return apiClient(originalRequest);
            } catch {
                auth.accessToken = null;
                router.push({
                    path: '/login',
                    query: { redirect_reason: 'session_expired' }
                })
            }
        }

        return Promise.reject(error);
    }
);


// Helper to make calls with method, url, and optional data/config
async function fetchData({ method = 'get', url, data = null, config = {} }) {
    const response = await apiClient.request({ method, url, data, ...config });
    console.debug(method.toUpperCase(), url, response);
    return response.data;
}

export const fastApi = {
    home: async () => fetchData({
        method: 'get',
        url: '/home'
    }),
    auth: {
        register: async (data) => fetchData({
            method: 'post',
            url: '/auth/register',
            data
        }),
        login: async (data) => fetchData({
            method: 'post',
            url: '/auth/login',
            data
        }),
        refresh: async () => fetchData({
            method: 'post',
            url: '/auth/refresh'
        }),
        logout: async () => fetchData({
            method: 'post',
            url: '/auth/logout'
        }),
        me: {
            get: async () => fetchData({
                method: 'get',
                url: '/auth/me'
            }),
            put: async (data) => fetchData({
                method: 'put',
                url: '/auth/me',
                data
            }),
            delete: async (data) => fetchData({
                method: 'delete',
                url: '/auth/me',
                data
            }),
            updatePassword: async (data) => fetchData({
                method: 'post',
                url: '/auth/me/password',
                data
            })
        }
    },
    settings: {
        get: async () => fetchData({
            method: 'get',
            url: '/settings/'
        }),
        getByKey: async (key) => fetchData({
            method: 'get',
            url: `/settings/${key}`
        }),
    },
    user_settings: {
        get: async () => fetchData({
            method: 'get',
            url: '/user_settings/'
        }),
        put: async (key, data) => fetchData({
            method: 'put',
            url: `/user_settings/${key}`,
            data
        }),
    },
    titles: {
        search: async (data) => fetchData({
            method: 'post',
            url: '/titles/search',
            data
        }),
        searchTmdb: async (data) => fetchData({
            method: 'post',
            url: '/titles/search/tmdb',
            data
        }),
        addToLibrary: async (data) => fetchData({
            method: 'post',
            url: '/titles/library',
            data
        }),
        getById: async (titleId) => fetchData({
            method: 'get',
            url: `/titles/${titleId}`
        }),
        updateById: async (titleId) => fetchData({
            method: 'put',
            url: `/titles/${titleId}`
        }),
        similarById: async (titleId) => fetchData({
            method: 'get',
            url: `/titles/${titleId}/similar`
        }),
        imagesById: async (titleId) => fetchData({
            method: 'get',
            url: `/titles/${titleId}/images`
        }),
        imagesSetPreference: async (titleId, imageType, data) => fetchData({
            method: 'put',
            url: `/titles/${titleId}/images/${imageType}`,
            data
        }),
        library: {
            add: async (titleId) => fetchData({
                method: 'put',
                url: `/titles/${titleId}/library`
            }),
            remove: async (titleId) => fetchData({
                method: 'delete',
                url: `/titles/${titleId}/library`
            })
        },
        setWatchCount: async (titleId, watchCount) => fetchData({
            method: 'put',
            url: `/titles/${titleId}/watch_count`,
            data: { watch_count: watchCount }
        }),
        setFavourite: async (titleId, isFavourite) => fetchData({
            method: 'put',
            url: `/titles/${titleId}/favourite`,
            data: { is_favourite: isFavourite }
        }),
        setWatchlist: async (titleId, inWatchlist) => fetchData({
            method: 'put',
            url: `/titles/${titleId}/watchlist`,
            data: { in_watchlist: inWatchlist }
        }),
        updateNotes: async (titleId, notes) => fetchData({
            method: 'put',
            url: `/titles/${titleId}/notes`,
            data: { notes }
        })
    },
    seasons: {
        imagesById: async (seasonId) => fetchData({
            method: 'get',
            url: `/seasons/${seasonId}/images`
        }),
        imagesSetPreference: async (seasonId, imageType, data) => fetchData({
            method: 'put',
            url: `/seasons/${seasonId}/images/${imageType}`,
            data
        }),
    },
    media: {
        image: async (size, image_path) => fetchData({
            method: 'get',
            url: `/media/image/${size}/${image_path}`
        })
    }
};
