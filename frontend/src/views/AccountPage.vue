<script setup>
import { ref } from 'vue'
import { fastApi } from '@/utils/fastApi';
import { useAuthStore } from '@/stores/auth';

const username = ref('')
const user_id = ref('')

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
</script>

<template>
    <div>
        <h1>Account</h1>
        <p>This will be the settings and account details page.</p>

        <button @click="checkMe">Check my details</button>

        <ul>
            <li>Username: {{ username }}</li>
            <li>User ID: {{ user_id }}</li>
        </ul>

        <button @click="logOut">Log out</button>
    </div>
</template>
