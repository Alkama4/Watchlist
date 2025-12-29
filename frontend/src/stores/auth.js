import { defineStore } from 'pinia';
import { fastApi } from '../utils/fastApi';
import router from '@/router';

export const useAuthStore = defineStore('auth', {
    state: () => ({
        accessToken: null
    }),
    actions: {
        async init() {
            try {
                const response = await fastApi.auth.refresh();
                this.accessToken = response.data.access_token;
            } catch {
                this.accessToken = null;
            }
        },
        async login(credentials) {
            const data = await fastApi.auth.login(credentials);
            this.accessToken = data.access_token;
            router.push("/")
        },
        async refresh() {
            const data = await fastApi.auth.refresh();
            this.accessToken = data.access_token;
        },
        async logout() {
            const data = await fastApi.auth.logout();
            if (data) this.accessToken = null;
            router.push("/login")
        }
    }
});
