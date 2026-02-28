<script setup>
const props = defineProps({
    modelValue: {
        type: Number,
        required: true
    },
    count: {
        type: Number,
        required: true
    }
});

const emit = defineEmits(['update:modelValue']);

function select(index) {
    if (index === props.modelValue) return;
    emit('update:modelValue', index);
}
</script>

<template>
    <div class="pagination-dots">
        <button
            v-for="index in count"
            :key="index"
            class="dot-wrapper"
            @click="select(index - 1)"
            aria-label="Go to slide"
        >
        <div
            class="dot"
            :class="{ active: index - 1 === modelValue }"
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
}

.dot {
    width: var(--spacing-sm-md);
    height: var(--spacing-sm-md);
    border-radius: 100px;
    background-color: var(--c-text-subtle);

    transition: background-color 0.1s var(--transition-ease-out),
                width 0.2s var(--transition-ease-out);
}

.dot.active {
    background-color: var(--c-text-base);
    width: var(--spacing-md-lg);
}

.dot-wrapper:hover .dot,
.dot-wrapper:active .dot{
    background-color: var(--c-text-strong);
}
</style>
