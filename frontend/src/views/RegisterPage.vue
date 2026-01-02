<script setup>
import { ref } from 'vue'
import { fastApi } from '@/utils/fastApi'
import FormMessage from '@/components/FormMessage.vue'
import Modal from '@/components/Modal.vue'

const username = ref('')
const password = ref('')
const passwordRepeat = ref('')
const formError = ref('')
const formMessage = ref(null)
const modal = ref(null)

function validateRepeatPassword(e) {
    const input = e.target
    if (input.value !== password.value) {
        input.setCustomValidity("Passwords do not match")
    } else {
        input.setCustomValidity("")
    }
}

async function register() {
    try {
        const response = await fastApi.auth.register({
            username: username.value,
            password: password.value
        })

        console.debug(response)
        modal.value.open();
    } catch (e) {
        const status = e.response?.status
        const detail = e.response?.data?.detail

        if (status === 400) {
            formError.value = "The username is already taken. Please choose another one."
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
    <div class="register-page">
        <form @submit.prevent="register" class="card">
            <h1>Register</h1>
    
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
                placeholder="Choose a username"
            >
    
            <label for="password">Password</label>
            <input 
                id="password" 
                v-model="password" 
                type="password" 
                required 
                minlength="1"
                placeholder="Create a secure password"
            >

            <label for="passwordRepeat">Repeat password</label>
            <input
                id="passwordRepeat"
                type="password"
                v-model="passwordRepeat"
                required
                @input="validateRepeatPassword"
                placeholder="Confirm your password"
            >

            <div class="checkbox-row">
                <input 
                    id="termsCheckbox"
                    type="checkbox"
                    required
                >
                <label for="termsCheckbox">
                    I assure that I will remember my password (it cannot be recovered)
                </label>
            </div>
    
            <button type="submit" class="btn-primary">Create account</button>
        </form>
        <span class="subtle" style="font-size: var(--fs-neg-1);">
            Already have an account?
            <router-link class="subtle" to="/login">
                Login.
            </router-link>
        </span>

        <Modal ref="modal" header="Account Created">
            <p>Your account has been created successfully. You can now log in.</p>
            <div class="button-row">
                <button @click="close">Close</button>
                <router-link to="/login" class="btn btn-primary no-deco">
                    Go to login
                </router-link>
            </div>
        </Modal>
    </div>
</template>


<style scoped>
.register-page {
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