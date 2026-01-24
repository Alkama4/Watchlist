<script setup>
import { ref, onMounted, onUnmounted } from "vue";

const showSpinner = ref(false);
const showHint = ref(false);

let spinnerTimer;
let hintTimer;

onMounted(() => {
    spinnerTimer = setTimeout(() => {
        showSpinner.value = true;
    }, 300);

    hintTimer = setTimeout(() => {
        showHint.value = true;
    }, 8000);
});

onUnmounted(() => {
    clearTimeout(spinnerTimer);
    clearTimeout(hintTimer);
});
</script>

<template>
    <div :class="{'show': showSpinner}">
        <span class="loader spin"></span>
        <span :class="{'show': showHint}" class="hint">
            This is taking longer than expected...
        </span>
    </div>
</template>

<style scoped>
div {
    display: flex;
    flex-direction: column;
    gap: var(--spacing-md);
    justify-content: center;
    align-items: center;
    padding: var(--spacing-xl);
    opacity: 0;
    transition: opacity 0.15s ease-out;
}

.loader {
    --size: 32px;
    --thickness: 4px;
    width: var(--size);
    height: var(--size);
    border: var(--thickness) solid var(--c-text);
    border-top-color: transparent;
    border-radius: 100px;
}

.hint {
    color: var(--c-text-3);
    opacity: 0;
    transition: opacity 0.15s ease-out;
}

.show {
    opacity: 1 !important;
}
</style>
