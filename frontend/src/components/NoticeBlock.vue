<script setup>

defineProps({
    header: {
        type: String,
        default: 'Notice'
    },
    icon: {
        type: String,
        default: 'bxs-error'
    },
    type: {
        type: String,
        default: 'info',
        validator: value =>
            ['info', 'negative', 'warning', 'positive'].includes(value)
    },
    message: {
        type: String,
        default: 'Your text here'
    },
})

</script>

<template>
    <div class="notice" :class="type">
        <h5>
            <i class="bx" :class="icon"></i>
            <span>{{ header }}</span>
        </h5>
        <p v-html="message"></p>
    </div>
</template>

<style scoped>
.notice {
    padding: var(--spacing-sm);
    border-radius: var(--border-radius-md);
}
.notice.info {
    background-color: var(--c-accent-transparent);
    border: 1px solid var(--c-accent-border);
}
.notice.positive {
    background-color: var(--c-positive-transparent);
    border: 1px solid var(--c-positive-border);
}
.notice.warning {
    background-color: var(--c-warning-transparent);
    border: 1px solid var(--c-warning-border);
}
.notice.negative {
    background-color: var(--c-negative-transparent);
    border: 1px solid var(--c-negative-border);
}

h5 {
    display: flex;
    flex-direction: row;
    align-items: center;
    margin: 0;
    margin-bottom: var(--spacing-sm);
    gap: var(--spacing-sm);
}
p {
    font-size: var(--fs-neg-1);
    margin: 0;
}
</style>