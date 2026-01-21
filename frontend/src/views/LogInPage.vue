<script setup>
import { ref, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import FormMessage from '@/components/FormMessage.vue'
import { useRoute, useRouter } from 'vue-router'
import NoticeBlock from '@/components/NoticeBlock.vue'

const username = ref('')
const password = ref('')
const formError = ref('')
const formMessage = ref(null)
const redirectNotice = ref(null)

const route = useRoute()
const router = useRouter()

onMounted(() => {
    redirectNotice.value = getRedirectNotice()
})

function getRedirectNotice() {
    switch (route.query.redirect_reason) {
        case 'session_expired':
            return {
                type: 'warning',
                header: 'Session expired',
                message: 'Your session expired. Please log in again.'
            }
        case 'account_created':
            return {
                type: 'success',
                header: 'Account created',
                message: 'Your account was created successfully. You can now log in.'
            }
        case 'logged_out':
            return {
                type: 'info',
                header: 'Logged out',
                message: 'You have been logged out.'
            }
        default:
            return null
    }
}

function handleNoticeDismiss() {
    redirectNotice.value = null
    // Remove the query from URL
    router.replace({ query: {} })
}

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

        formMessage.value.show()
    }
}
</script>

<template>
    <div class="login-page">
        <NoticeBlock
            v-if="redirectNotice"
            :type="redirectNotice.type"
            :header="redirectNotice.header"
            :message="redirectNotice.message"
            dismissible
            @dismiss="handleNoticeDismiss"
        />
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
    
            <button type="submit" class="btn-primary">Login</button>
        </form>
        <span class="subtle" style="font-size: var(--fs-neg-1);">
            Don't have an account?
            <router-link class="subtle" to="/register">
                Register here.
            </router-link>
        </span>
    </div>
</template>


<style scoped>
.login-page {
    min-height: calc(100vh - 36px);
    padding: var(--spacing-xl) 0;
    box-sizing: border-box;
    display: flex;
    flex-direction: column;
    gap: var(--spacing-md);
    align-items: center;
    justify-content: center;
}

</style>