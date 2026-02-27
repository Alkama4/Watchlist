<script setup>
import { onMounted, ref } from 'vue'
import { fastApi } from '@/utils/fastApi';
import { useAuthStore } from '@/stores/auth';
import { useSettingsStore } from '@/stores/settings';
import ModalConfimation from '@/components/modal/ModalConfimation.vue';
import ModalBase from '@/components/modal/ModalBase.vue';
import NoticeBlock from '@/components/NoticeBlock.vue';
import FormMessage from '@/components/FormMessage.vue';
import LoadingButton from '@/components/LoadingButton.vue';

// Stores
const auth = useAuthStore();
const settingsStore = useSettingsStore();

// Local State
const username = ref('')
const user_id = ref('')

const deletePassword = ref('')
const deletePasswordElement = ref(null)
const deleteError = ref('')
const formMessageElement = ref(null)

const waitingFor = ref({});

// Modals
const ModalLogOutConfirm = ref(null)
const ModalDeleteFirst = ref(null)
const ModalDeleteSecond = ref(null)

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
    if (!await ModalLogOutConfirm.value.query()) return;
    await auth.logout();
}

function inputType(value_type) {
    if (value_type === 'int') return 'number';
    return 'text';
}

async function handleUpdate(key, event) {
    if (event && event.target) {
        if (!event.target.checkValidity()) return;
    }
    const value = event.target.value;
    await settingsStore.updateSetting(key, value);
}

function toggleCustomTheme() {
    const current = settingsStore.preferences.theme;
    const nextTheme = (current === 'true-black') ? 'midnight' : 'true-black';
    settingsStore.updateSetting('theme', nextTheme);
}

async function deleteAccountInit() {
    if (!await ModalDeleteFirst.value.query()) return;
    ModalDeleteSecond.value.open();
    setTimeout(() => {
        deletePasswordElement.value.focus();
    }, 1)
}

async function deleteAccountFinalize() {
    try {
        await fastApi.auth.me.delete({ password: deletePassword.value })
        ModalDeleteSecond.value.close();
        await auth.logout(true);
    } catch(e) {
        const status = e.response?.status
        const detail = e.response?.data?.detail
        deleteError.value = status === 400 ? "Invalid password" : (detail || e.message);
        formMessageElement.value.show()
    }
}

async function syncJellyfin() {
    waitingFor.value.jellyfinSync = true;
    try {
        const response = await fastApi.integrations.syncJellyfin();
        alert(`${response.message}. ${response.details.newly_linked} links added, ${response.details.total_matched_in_library} links in total, ${response.details.jellyfin_library_size} titles in Jellyfin`)
        console.info(response)
    } finally {
        waitingFor.value.jellyfinSync = false;
    }
}

onMounted(async () => {
    // Parallelize for speed
    await Promise.all([
        checkMe(),
        settingsStore.syncSettings()
    ]);
})
</script>

<template>
    <div class="account-page layout-contained layout-spacing-top layout-spacing-bottom">
        <div class="profile-column">
            <div class="card profile-card">
                <div class="avatar"><i class="bx bxs-user"></i></div>
                <h2 class="name">{{ username }}</h2>
                <p>User ID: {{ user_id }}</p>

                <div class="button-column">
                    <button @click="logOut" class="btn-primary">Log out</button>
                    <button>Change Password</button>
                    <hr>
                    <button @click="deleteAccountInit" class="btn-negative">Delete Account</button>
                </div>
            </div>
        </div>

        <div class="settings-column settings-list">
            <h1>Settings</h1>
            
            <template v-for="setting in settingsStore.schema" :key="setting.key">
                <label>{{ setting.label }}</label>

                <select
                    v-if="setting.enum_choices"
                    :value="settingsStore.preferences[setting.key]"
                    @change="e => settingsStore.updateSetting(setting.key, e.target.value)"
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
                    :value="settingsStore.preferences[setting.key]"
                    :type="inputType(setting.value_type)"
                    :placeholder="setting.default_value"
                    @blur="e => handleUpdate(setting.key, e)"
                />
            </template>

            <label for="theme-toggle">Debug quick theme toggle</label>
            <button @click="toggleCustomTheme" id="theme-toggle">
                Switch to {{ settingsStore.preferences.theme === 'true-black' ? 'Midnight' : 'True Black' }}
            </button>

            <h1 style="margin-top: var(--spacing-lg);">Actions</h1>
            <LoadingButton
                :loading="waitingFor?.jellyfinSync"
                @click="syncJellyfin"
            >
                Manually sync jellyfin
            </LoadingButton>
        </div>


        <ModalConfimation
            ref="ModalLogOutConfirm"
            header="Log out"
            message="Are you sure you want to log out?"
            confirmLabel="Log out"
        />

        <ModalConfimation
            ref="ModalDeleteFirst"
            header="Delete Account"
            message="Are you sure you want to delete your account? You'll need to confirm with your password."
            confirmLabel="Continue"
            :negativeAction="true"
        />
        <ModalBase ref="ModalDeleteSecond" header="Delete Account">
            <NoticeBlock
                type="negative"
                header="Permanent action"
                message="Deleting your account will permanently remove all associated data. This action cannot be undone."
            />

            <form @submit.prevent="deleteAccountFinalize">
                <FormMessage
                    ref="formMessageElement"
                    :msg="deleteError"
                    :dismissable="true"
                />

                <label for="deletePassword">Account password</label>
                <input 
                    ref="deletePasswordElement"
                    id="deletePassword"
                    type="password"
                    placeholder="Confirm your password"
                    v-model="deletePassword"
                />
    
                <div class="button-row">
                    <button @click.prevent="ModalDeleteSecond.close()">
                        Cancel
                    </button>
                    <button type="submit" :disabled="!deletePassword" class="btn-negative">
                        Delete Account Permanently
                    </button>
                </div>
            </form>
        </ModalBase>
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


.notice {
    margin-bottom: var(--spacing-md);
    max-width: 500px;
    box-sizing: border-box;
}

hr {
    margin: var(--spacing-sm) var(--spacing-md);
}

</style>
