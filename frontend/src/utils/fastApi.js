import axios from 'axios';
import { useAuthStore } from '../stores/auth';
import { API_BASE_URL } from './conf';


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
                originalRequest.headers.Authorization =
                    `Bearer ${auth.accessToken}`;
                return apiClient(originalRequest);
            } catch {
                auth.accessToken = null;
                router.push('/login');
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
            password: async (data) => fetchData({
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
        post: async (data) => fetchData({
            method: 'post',
            url: '/titles/',
            data
        }),
        search: async (data) => fetchData({
            method: 'post',
            url: '/titles/search',
            data
        }),
        searchTMDB: async (data) => fetchData({
            method: 'post',
            url: '/titles/search/tmdb',
            data
        }),
        getById: async (title_id) => fetchData({
            method: 'get',
            url: `/titles/${title_id}`
        }),
        putById: async (title_id, data) => fetchData({
            method: 'put',
            url: `/titles/${title_id}`,
            data
        }),

        library: {
            put: async (title_id) => fetchData({
                method: 'put',
                url: `/titles/${title_id}/library`
            }),
            delete: async (title_id) => fetchData({
                method: 'delete',
                url: `/titles/${title_id}/library`
            })
        },

        favourite: {
            put: async (title_id) => fetchData({
                method: 'put',
                url: `/titles/${title_id}/favourite`
            }),
            delete: async (title_id) => fetchData({
                method: 'delete',
                url: `/titles/${title_id}/favourite`
            })
        },
        
        watchlist: {
            put: async (title_id) => fetchData({
                method: 'put',
                url: `/titles/${title_id}/watchlist`
            }),
            delete: async (title_id) => fetchData({
                method: 'delete',
                url: `/titles/${title_id}/watchlist`
            })
        }
    },

    media: {
        image: async (size, image_path) => fetchData({
            method: 'get',
            url: `/media/image/${size}/${image_path}`
        })
    }
};
