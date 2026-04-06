<script setup>
import { computed } from 'vue';

const props = defineProps({
    progress: {
        type: Number,
        default: 0
    },
    count: {
        type: Number,
        default: 0
    }
});

const emit = defineEmits(['select']);

const normalizedProgress = computed(() => {
    if (props.count <= 0) return 0;
    return ((props.progress % props.count) + props.count) % props.count;
});

function getIntensity(dotIndex) {
    if (props.count <= 0) return 0;
    
    let diff = Math.abs(dotIndex - normalizedProgress.value);
    
    // If the distance is more than half the total dots, 
    // it's actually closer via the "wrap-around" path.
    if (diff > props.count / 2) {
        diff = props.count - diff;
    }

    return Math.max(0, 1 - diff);
}

function select(index) {
    emit('select', index);
}
</script>

<template>
    <div class="pagination-dots">
        <button
            v-for="(_, index) in count"
            :key="index"
            class="dot-wrapper"
            @click="select(index)"
            aria-label="Go to slide"
        >
            <div
                class="dot"
                :style="{ '--intensity': getIntensity(index) }"
            ></div>
        </button>
    </div>
</template>

<style scoped>
.pagination-dots {
    display: flex;
}

.dot-wrapper {
    padding: 2px 4px;
    border-radius: 0;
    background-color: transparent !important;
    border: none;
    cursor: pointer;
}

.dot {
    width: calc(var(--spacing-sm-md) + (var(--spacing-md-lg) - var(--spacing-sm-md)) * var(--intensity, 0));
    height: var(--spacing-sm-md);
    border-radius: 100px;
    background-color: var(--c-text-subtle);
    position: relative;
    overflow: hidden;
}

.dot::after {
    content: '';
    position: absolute;
    inset: 0;
    background-color: var(--c-text);
    opacity: var(--intensity, 0);
    transition: opacity 0.1s var(--transition-ease-out);
}

.dot-wrapper:hover .dot::after,
.dot-wrapper:active .dot::after {
    background-color: var(--c-text-strong);
    opacity: 1;
}
</style>