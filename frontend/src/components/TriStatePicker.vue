<script setup>
import { Circle, CheckCircle, XCircle } from '@boxicons/vue';

const props = defineProps({
    options: {
        type: Array,
        required: true
    },
    include: {
        type: Array,
        required: true
    },
    exclude: {
        type: Array,
        required: true
    }
});

const emit = defineEmits(['update:include', 'update:exclude']);

const getSelectionState = (value) => {
    if (props.include.includes(value)) return 'include';
    if (props.exclude.includes(value)) return 'exclude';
    return 'unset';
};

const cycleState = (value) => {
    const newInclude = [...props.include];
    const newExclude = [...props.exclude];

    const currentState = getSelectionState(value);

    if (currentState === 'unset') {
        // Unset -> Include
        newInclude.push(value);
        emit('update:include', newInclude);
    } 
    else if (currentState === 'include') {
        // Include -> Exclude
        const index = newInclude.indexOf(value);
        if (index > -1) newInclude.splice(index, 1);
        newExclude.push(value);
        
        emit('update:include', newInclude);
        emit('update:exclude', newExclude);
    } 
    else if (currentState === 'exclude') {
        // Exclude -> Unset
        const index = newExclude.indexOf(value);
        if (index > -1) newExclude.splice(index, 1);
        
        emit('update:exclude', newExclude);
    }
};
</script>

<template>
    <div class="options-wrapper">
        <button 
            v-for="opt in options" 
            :key="opt.value"
            class="btn-even-padding btn-text"
            :class="{
                'btn-positive': getSelectionState(opt.value) === 'include',
                'btn-negative': getSelectionState(opt.value) === 'exclude'
            }"
            @click="cycleState(opt.value)"
        >
            <CheckCircle v-if="getSelectionState(opt.value) === 'include'" pack="filled" width="16px" height="16px" />
            <XCircle v-else-if="getSelectionState(opt.value) === 'exclude'" pack="filled" width="16px" height="16px" />
            <Circle v-else pack="basic" width="16px" height="16px" />

            <span>{{ opt.label }}</span>
        </button>
    </div>
</template>

<style scoped>
.options-wrapper {
    display: flex;
    flex-direction: column;
    gap: var(--spacing-xs);
}
button {
    white-space: nowrap;
    padding-right: var(--spacing-lg);
    justify-content: start;
    font-weight: 500;
    gap: var(--spacing-sm);
}
</style>