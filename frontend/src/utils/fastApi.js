import axios from 'axios';
import { useAuthStore } from '../stores/auth';

const localIP = window.location.hostname; // will be the IP the browser used
const API_BASE_URL = import.meta.env.DEV 
    ? `http://${localIP}:8000` 
    : '/api';

// Axios client
const apiClient = axios.create({
    baseURL: API_BASE_URL,
    headers: { 'Content-Type': 'application/json' },
    withCredentials: true // important so cookies are sent automatically
});

// Seperate client for refreshing
// This way we prevent going to an infinite loop of refresh
const refreshClient = axios.create({
    baseURL: API_BASE_URL,
    headers: { 'Content-Type': 'application/json' },
    withCredentials: true
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
        const auth = useAuthStore?.();
        const originalRequest = error.config;

        if (error.response?.status === 401 && !originalRequest._retry && auth) {
            originalRequest._retry = true; // prevent infinite loop
            try {
                await auth.refresh(); // get a new access token
                originalRequest.headers.Authorization = `Bearer ${auth.accessToken}`;
                return apiClient(originalRequest); // retry original request
            } catch (refreshError) {
                await auth.logout();
                return Promise.reject(refreshError);
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
        refresh: async () =>
            refreshClient.post('/auth/refresh'), // intentionally not using fetchData
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

    titles: {
        post: async (data) => fetchData({
            method: 'post',
            url: '/titles/',
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

        watchlist: {
            put: async (title_id) => fetchData({
                method: 'put',
                url: `/titles/${title_id}/watchlist`
            }),
            delete: async (title_id) => fetchData({
                method: 'delete',
                url: `/titles/${title_id}/watchlist`
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
        
        watchNext: {
            put: async (title_id) => fetchData({
                method: 'put',
                url: `/titles/${title_id}/watch-next`
            }),
            delete: async (title_id) => fetchData({
                method: 'delete',
                url: `/titles/${title_id}/watch-next`
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
