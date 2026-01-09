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
        // response is usually { data: { ... } } depending on your API helper
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

    const userMap = Object.fromEntries(
        userSettings.map(s => [s.key, s.value])
    );

    settings.value = baseSettings.map(setting => ({
        ...setting,
        value: userMap[setting.key] ?? setting.default_value
    }));
}

function inputType(setting) {
    if (setting.value_type === 'int') {
        return 'number';
    }
    return 'text';
}

async function updateSetting(setting, event) {
    const input = event.target;

    if (!input.checkValidity()) {
        return;
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
    <div>
        <h1>Account</h1>
        <p>This will be the settings and account details page.</p>

        <div class="card">
            <div>
                <i class="bx bxs-user"></i>
            </div>
            <h2 class="name">{{ username }}</h2>
            <p>User ID: {{ user_id }}</p>
        </div>

        <button @click="logOut">Log out</button>

        <!-- Update details/name -->

        <!-- Change password -->

        <!-- Delete my account -->

        <h1>Settings</h1>

        <div v-for="setting in settings" :key="setting.key">
            <label>{{ setting.label }}</label>

            <!-- Select when enum choices exist -->
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


            <!-- Input otherwise -->
            <input
                v-else
                v-model="setting.value"
                :type="inputType(setting)"
                :placeholder="setting.default_value"
                @blur="updateSetting(setting, $event)"
            />
        </div>
    </div>
</template>

<style scoped>
h2.name {
    margin: 0;
}
</style>