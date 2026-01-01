<script setup>
import { ref } from 'vue'

defineProps({
    msg: {
        type: String,
        required: true
    },
    dismissable: {
        type: Boolean,
        default: false
    }
})

const visible = ref(false)
const emit = defineEmits(['close'])

function close() {
    visible.value = false
    emit('close')
}

function open() {
    visible.value = true
}

defineExpose({ open })
</script>

<template>
    <div v-if="visible" role="alert" aria-live="assertive" class="form-message">
        <span>{{ msg }}</span>
        <button
            v-if="dismissable"
            @click="close"
            class="btn-text btn-square"
            aria-label="Dismiss message"
        >
            <i class="bx bx-x"></i>
        </button>
    </div>
</template>

<style scoped>
.form-message {
    background-color: var(--c-negative);
    border-radius: 8px;
    padding: 0px var(--spacing-sm);
    /* margin-top: var(--spacing-sm); */
    margin-bottom: var(--spacing-md);

    display: flex;
    justify-content: space-between;
    align-items: center;
}

i {
    font-size: var(--fs-2);
}

span {
    padding: var(--spacing-sm) var(--spacing-xs);
}
</style>