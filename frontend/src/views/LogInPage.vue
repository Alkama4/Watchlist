<script setup>
import { ref } from 'vue'
import { useAuthStore } from '@/stores/auth'

const username = ref('')
const password = ref('')

async function logIn() {
    const auth = useAuthStore()
    await auth.login({
        username: username.value,
        password: password.value
    })
}
</script>

<template>
    <form @submit.prevent="logIn">
        <h1>Login</h1>

        <label for="username">Username</label>
        <input id="username" v-model="username" type="text">

        <label for="password">Password</label>
        <input id="password" v-model="password" type="password">

        <button type="submit">Login</button>
    </form>
</template>


<style scoped>

</style>