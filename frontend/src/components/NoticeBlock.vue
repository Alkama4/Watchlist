<script setup>
defineProps({
    header: {
        type: String,
        default: 'Notice'
    },
    icon: {
        type: String,
        default: 'bxs-info-circle'
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
    dismissible: {
        type: Boolean,
        default: false
    }
})
</script>

<template>
    <div class="notice" :class="type">
        <h5>
            <div>
                <i class="bx" :class="icon"></i>
                <span>{{ header }}</span>
            </div>

            <button
                v-if="dismissible"
                @click="$emit('dismiss')"
                class="btn-text btn-square"
                aria-label="Dismiss notice"
            >
                <i class="bx bx-x"></i>
            </button>
        </h5>

        <p v-html="message"></p>
    </div>
</template>


<style scoped>
.notice {
    padding: var(--spacing-sm);
    border-radius: var(--border-radius-md);
    backdrop-filter: blur(var(--blur-subtle));
    min-width: 20rem;
}
.notice.info {
    background-color: var(--c-watchlist-transparent);
    border: 1px solid var(--c-watchlist-border);
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

.dismiss {
    margin-left: auto;
    background: none;
    border: none;
    font-size: 1.2em;
    cursor: pointer;
}

h5 {
    display: flex;
    align-items: center;
    gap: var(--spacing-sm);

    margin: 0;
    margin-bottom: var(--spacing-sm);
    justify-content: space-between;
}
h5 div {
    display: flex;
    align-items: center;
    gap: var(--spacing-sm);
}
p {
    font-size: var(--fs-neg-1);
    margin: 0;
}
button {
    padding: 0;
}
button i {
    font-size: var(--fs-2);
}
</style>