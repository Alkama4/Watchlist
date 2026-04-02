<script setup>
import { useAttrs } from 'vue'

const attrs = useAttrs()

defineProps({
    loading: {
        type: Boolean,
        default: false
    },
    size: {
        type: String,
        default: '12px'
    },
    thickness: {
        type: String,
        default: '2px'
    }
})
</script>

<template>
    <button
        v-bind="attrs"
        :disabled="loading || attrs.disabled"
        :class="{'loading': loading}"
    >
        <div v-if="loading" class="loader spin"></div>
        <slot v-else />
    </button>
</template>

<style scoped>
.loader {
    --size: v-bind(size);
    --thickness: v-bind(thickness);
    
    width: var(--size);
    height: var(--size);
    border: var(--thickness) solid currentColor;
    border-top-color: transparent;
    border-radius: 50%; /* standard for circular loaders */
}

.loading {
    cursor: wait;
}

.spin {
    animation: spin 0.8s linear infinite;
}

@keyframes spin {
    to { transform: rotate(360deg); }
}
</style>