<script setup>
import { useAttrs } from 'vue'

const attrs = useAttrs()

const { loading } = defineProps({
    loading: {
        type: Boolean,
        required: true
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
    --size: 12px;
    --thickness: 2px;
    width: var(--size);
    height: var(--size);
    border: var(--thickness) solid currentColor;
    border-top-color: transparent;
    border-radius: 100px;
}
.loading {
    cursor: wait;
}
</style>