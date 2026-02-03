import { defineStore } from 'pinia';
import { fastApi } from '../utils/fastApi';
import router from '@/router';

export const useAuthStore = defineStore('auth', {
    state: () => ({
        accessToken: null,
        initialized: false
    }),
    actions: {
        async init() {
            if (this.initialized) return this.accessToken;
            try {
                const response = await fastApi.auth.refresh();
                this.accessToken = response.access_token;
            } catch {
                this.accessToken = null;
            } finally {
                this.initialized = true;
            }
            return this.accessToken;
        },
        async login(credentials) {
            try {
                const data = await fastApi.auth.login(credentials);
                this.accessToken = data.access_token;
                router.push('/');
            } catch (e) {
                this.accessToken = null;
                throw e;
            }
        },
        async refresh() {
            const response = await fastApi.auth.refresh();
            this.accessToken = response.access_token;
            return response.access_token;
        },
        async logout(quiet = false) {
            try {
                if (!quiet) await fastApi.auth.logout();
            } finally {
                this.$reset();  // Reset store values
                router.push({
                    path: '/login',
                    query: { redirect_reason: 'logged_out' }
                })
            }
        }
    }
});
