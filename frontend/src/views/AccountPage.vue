<script setup>
import { onMounted, ref } from 'vue'
import { fastApi } from '@/utils/fastApi';
import { useAuthStore } from '@/stores/auth';

const username = ref('')
const user_id = ref('')
const settings = ref([]);

async function checkMe() {
    try {
        const response = await fastApi.auth.me.get()
        const user = response.data || response
        username.value = user.username
        user_id.value = user.user_id
    } catch (err) {
        console.error('Failed to fetch user details', err)
    }
}

async function logOut() {
    const auth = useAuthStore();
    await auth.logout()
}

async function fetchSettings() {
    const baseSettings = await fastApi.settings.get();
    const userSettings = await fastApi.user_settings.get();
    const userMap = Object.fromEntries(userSettings.map(s => [s.key, s.value]));
    settings.value = baseSettings.map(setting => ({
        ...setting,
        value: userMap[setting.key] ?? setting.default_value
    }));
}

function inputType(setting) {
    if (setting.value_type === 'int') return 'number';
    return 'text';
}

async function updateSetting(setting, event) {
    if (event) {
        const input = event.target;
        if (!input.checkValidity()) return;
    }
    let value = String(setting.value);
    await fastApi.user_settings.put(setting.key, { value });
}

onMounted(async () => {
    await checkMe();
    await fetchSettings();
})
</script>

<template>
    <div class="account-page">
        <div class="profile-column">
            <div class="card profile-card">
                <div class="avatar">
                    <i class="bx bxs-user"></i>
                </div>
                <h2 class="name">{{ username }}</h2>
                <p>User ID: {{ user_id }}</p>

                <div class="button-column">
                    <button @click="logOut" class="btn-primary">Log out</button>
                    <button >Change Password</button>
                    <button class="btn-negative">Delete Account</button>
                </div>
            </div>
        </div>

        <div class="settings-column settings-list">
            <h1>Settings</h1>
            <template v-for="setting in settings" :key="setting.key">
                <label>{{ setting.label }}</label>

                <select
                    v-if="setting.enum_choices"
                    v-model="setting.value"
                    @change="updateSetting(setting)"
                >
                    <option
                        v-for="choice in setting.enum_choices"
                        :key="choice.value"
                        :value="choice.value"
                    >
                        {{ choice.label }}
                    </option>
                </select>

                <input
                    v-else
                    v-model="setting.value"
                    :type="inputType(setting)"
                    :placeholder="setting.default_value"
                    @blur="updateSetting(setting, $event)"
                />
            </template>
        </div>
    </div>
</template>

<style scoped>
.account-page {
    display: flex;
    gap: var(--spacing-lg);
    flex-wrap: wrap;
}

/* Profile / Actions column */
.profile-column {
    flex: 1 1 300px;
}
.profile-card {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: var(--spacing-sm);
}
.profile-card .avatar {
    font-size: 3rem;
}
.profile-card .name {
    margin: 0;
}


/* Settings column */
.settings-column {
    flex: 2 1 400px;
}
</style>
