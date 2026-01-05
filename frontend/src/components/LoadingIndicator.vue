<template>
    <div>
        <span class="loader"></span>
    </div>
</template>

<style scoped>
div {
    display: flex;
    justify-content: center;
    align-items: center;
    padding: var(--spacing-xl);
}

.loader {
    --size: 32px;
    --thickness: 4px;
    width: var(--size);
    height: var(--size);
    border: var(--thickness) solid var(--c-text);
    border-top-color: transparent;
    border-radius: 100px;
    animation: spin 0.8s linear infinite;
}

@keyframes spin {
    0% {
        transform: rotate(0deg);
    }
    100% {
        transform: rotate(360deg);
    }
}
</style>
