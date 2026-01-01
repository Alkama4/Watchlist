<script setup>
import { ref } from 'vue'
import { useAuthStore } from '@/stores/auth'
import FormMessage from '@/components/FormMessage.vue'

const username = ref('')
const password = ref('')
const formError = ref('')
const formMessage = ref(null)

async function logIn() {
    const auth = useAuthStore()
    try {
        await auth.login({
            username: username.value,
            password: password.value
        })
    } catch (e) {
        const status = e.response?.status
        const detail = e.response?.data?.detail

        if (status === 401) {
            formError.value = "Invalid username or password. Please try again."
        } else if (status) {
            formError.value = `Error ${status}: ${detail || 'Something went wrong.'}`
        } else {
            formError.value = `Unexpected error: ${e.message || 'Please try again later.'}`
        }

        formMessage.value.open()
    }

}
</script>

<template>
    <div class="login-page">
        <form @submit.prevent="logIn" class="card">
            <h1>Login</h1>
    
            <FormMessage
                ref="formMessage"
                :msg="formError"
                :dismissable="true"
            />
    
            <label for="username">Username</label>
            <input 
                id="username" 
                v-model="username" 
                type="text" 
                required 
                minlength="1"
                placeholder="Enter your username"
            >
    
            <label for="password">Password</label>
            <input 
                id="password" 
                v-model="password" 
                type="password" 
                required 
                minlength="1"
                placeholder="Enter your password"
            >
    
            <div class="actions">
                <router-link class="subtle" to="/register">No account?</router-link>
                <button type="submit" class="btn-primary">Login</button>
            </div>
        </form>
    </div>
</template>


<style scoped>
.login-page {
    min-height: calc(100vh - 36px);
    padding: var(--spacing-xl) 0;
    box-sizing: border-box;
    display: flex;
    align-items: center;
    justify-content: center;
}

</style>