<script setup>
import { InfoCircle, X } from '@boxicons/vue';

defineProps({
    header: {
        type: String,
        default: 'Notice'
    },
    iconComponent: {
        type: Object,
        default: InfoCircle
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
    },
    loadingEffect: {
        type: Boolean,
        default: false
    }
})
</script>

<template>
    <div class="notice" :class="[type, {'wave': loadingEffect}]">
        <h5>
            <div>
                <component
                    :is="iconComponent"
                    pack="filled"
                    size="sm"
                />
                <span>{{ header }}</span>
            </div>
        </h5>

        <button
            v-if="dismissible"
            @click="$emit('dismiss')"
            aria-label="Dismiss notice"
            class="btn-text"
        >
            <X
                width="16px"
                height="16px"
                removePadding
            />
        </button>
        
        <p v-html="message"></p>

        <slot/>
    </div>
</template>


<style scoped>
.notice {
    padding: var(--spacing-sm);
    border-radius: var(--border-radius-md);
    backdrop-filter: blur(var(--blur-subtle));
    gap: var(--spacing-sm);
    display: flex;
    flex-direction: column;
    min-width: 20rem;
    background-color: var(--notice-bg);

    &.info {
        --notice-bg: var(--c-accent-transparent);
        border: 1px solid var(--c-accent-border);
    }
    &.positive {
        --notice-bg: var(--c-positive-transparent);
        border: 1px solid var(--c-positive-border);
    }
    &.warning {
        --notice-bg: var(--c-warning-transparent);
        border: 1px solid var(--c-warning-border);
    }
    &.negative {
        --notice-bg: var(--c-negative-transparent);
        border: 1px solid var(--c-negative-border);
    }

    &.wave {
        --c-1: var(--notice-bg);
        --c-2: oklch(from var(--c-1) calc(l * 1.25) c h );

        background: linear-gradient(
            90deg,
            var(--c-1) 40%,
            var(--c-2) 70%,
            var(--c-1) 100%
        );
        background-size: 200% 100%;
        animation: highlight-wave 1.25s infinite linear;
    }
}

@keyframes highlight-wave {
    0% {
        background-position: 0% 0;
    }
    100% {
        background-position: -200% 0;
    }
}

h5 {
    display: flex;
    align-items: center;
    gap: var(--spacing-sm);

    margin: 0;
    justify-content: space-between;
}
h5 div {
    display: flex;
    align-items: center;
    gap: var(--spacing-xs-sm);
}
p {
    font-size: var(--fs-neg-2);
    margin: 0;
}
button {
    position: absolute;
    padding: var(--spacing-xs-sm);
    top: var(--spacing-xs);
    right: var(--spacing-xs);
}
</style>