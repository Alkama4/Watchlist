<script setup>
import { X } from '@boxicons/vue'
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

function show() {
    visible.value = true
}

defineExpose({ show })
</script>

<template>
    <div v-if="visible" role="alert" aria-live="assertive" class="form-message">
        <span>{{ msg }}</span>
        <button
            v-if="dismissable"
            @click="close"
            class="btn-text btn-even-padding"
            aria-label="Dismiss message"
        >
            <X size="sm"/>
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

span {
    padding: var(--spacing-sm) var(--spacing-xs);
}
</style>