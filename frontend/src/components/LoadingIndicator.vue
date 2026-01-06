<template>
    <div>
        <span class="loader spin"></span>
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
}
</style>
