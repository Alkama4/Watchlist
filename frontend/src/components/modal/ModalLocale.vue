<script setup>
import ModalBase from '@/components/modal/ModalBase.vue';
import { ref } from 'vue';
import LoadingButton from '../LoadingButton.vue';
import { fastApi } from '@/utils/fastApi';

defineExpose({ open })

const modalRef = ref(null);

const props = defineProps({
    fetchTitleDetails: {
        type: Function,
        required: true
    },
    titleDetails: {
        type: Object,
        required: true
    },
    waitingFor: {
        type: Object,
        required: true
    }
})

function open() {
    modalRef.value.open();
}

async function updateTitleLocale() {
    props.waitingFor.titleLocale = true;
    try {
        const response = await fastApi.titles.setLocale(
            props.titleDetails.title_id,
            props.titleDetails.user_details.chosen_locale
        );
        props.titleDetails.user_details.in_library = response.in_library;
        props.titleDetails.display_locale = response.display_locale;
        await props.fetchTitleDetails();
    } finally {
        props.waitingFor.titleLocale = false;
    }
}
</script>

<template>
    <ModalBase header="Title Language" ref="modalRef" smallCard>
        <div class="active-locale">
            <span class="text-muted">Current locale code: </span> 
            <strong>{{ titleDetails.display_locale }}</strong>
        </div>
        
        <p>
            You can set a custom locale for this title to override your global app settings. 
            Leave blank to use your default language preferences.
        </p>

        <form @submit.prevent="updateTitleLocale">
            <label for="locale">
                Custom Locale Code
            </label>
            <input
                type="text"
                id="locale"
                v-model="titleDetails.user_details.chosen_locale"
                placeholder='e.g. "en-US" or "ja-JP"'
            >
            <LoadingButton
                type="submit"
                :loading="waitingFor?.titleLocale ?? false"
            >
                Save Changes
            </LoadingButton>
        </form>
    </ModalBase>
</template>

<style scoped>
.active-locale {
    background-color: var(--c-bg-level-2);
    padding: var(--spacing-md);
    border-radius: var(--border-radius-md);
}

form {
    max-width: 100%;
}
</style>