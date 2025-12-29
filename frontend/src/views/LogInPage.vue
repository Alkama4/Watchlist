<script setup>
import { useAuthStore } from '@/stores/auth';

async function logIn() {
    const auth = useAuthStore();
    await auth.login({ password: "string", username: "string" })
}
</script>

<template>
    <div>
        <h1>Login</h1>

        <button @click="logIn">Log In</button>
    </div>
</template>
