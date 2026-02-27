import { defineStore } from 'pinia'
import { fastApi } from '@/utils/fastApi'

export const useSettingsStore = defineStore('settings', {
    state: () => ({
        // The "Blueprint" from GET /settings/ (Schema, choices, defaults)
        schema: [],
        
        // The actual active key-value pairs (Defaults + Overrides)
        // We pre-load theme from LocalStorage for the zero-latency index.html script
        preferences: {
            theme: localStorage.getItem('theme') || 'dark', 
        },
        
        isLoaded: false,
    }),

    actions: {
        _handle_special_cases(key, value) {
            if (key === 'theme') {
                localStorage.setItem('theme', value)
                document.documentElement.setAttribute('data-theme', value)
            }
            if (key === 'language') {
                localStorage.setItem('language', value)
            }
        },
        
        async syncSettings() {
            try {
                const [schemaRes, overridesRes] = await Promise.all([
                    fastApi.settings.get(),
                    fastApi.user_settings.get()
                ])

                const overrideMap = overridesRes.reduce((acc, item) => {
                    acc[item.key] = item.value
                    return acc
                }, {})

                schemaRes.forEach(setting => {
                    const activeValue = overrideMap[setting.key] !== undefined 
                        ? overrideMap[setting.key] 
                        : setting.default_value

                    this.preferences[setting.key] = activeValue

                    this._handle_special_cases(setting.key, activeValue);
                })

                this.schema = schemaRes
                this.isLoaded = true

            } catch (e) {
                console.error("Failed to sync dynamic settings:", e)
            }
        },

        async updateSetting(key, newValue) {
            this.preferences[key] = newValue
            this._handle_special_cases(key, newValue);
            try {
                await fastApi.user_settings.put(key, { value: newValue })
            } catch (err) {
                console.error(`Failed to update setting ${key}:`, err)
                // TODO: revert UI changes here
            }
        }
    }
})