<script setup>
import { fastApi } from '@/utils/fastApi';
import { useAuthStore } from '@/stores/auth';

async function logIn() {
    const auth = useAuthStore();
    await auth.login({ password: "string", username: "string" })
}

async function checkState() {
    const auth = useAuthStore();
    console.log(auth.$state);
}

async function checkMe() {
    console.log(await fastApi.auth.me.get())
}

</script>

<template>
    <div>
        <h1>Login</h1>

        <button @click="logIn">Log In</button>
        <button @click="checkState">Check state</button>
        <button @click="checkMe">Check me</button>
    </div>
</template>
