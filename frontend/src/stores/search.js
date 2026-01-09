import { defineStore } from 'pinia';

export const useSearchStore = defineStore('search', {
    state: () => ({
        query: '',
        submitTick: 0
    }),
    actions: {
        submit() {
            this.submitTick++;
        }
    }
});
