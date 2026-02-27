<script setup>
const props = defineProps({
    modelValue: {
        type: [Boolean, String, Number, Array, null]
    },
    options: {
        type: Array,
        default: () => [
            { label: 'Yes', value: true,  type: 'positive' },
            { label: 'No', value: false, type: 'negative' }
        ]
    },
    mode: {
        type: String,
        default: 'single-optional',
        validator: (value) => ['single-optional', 'single-required', 'multiple'].includes(value)
    },
    defaultValue: {
        type: [Boolean, String, Number, Array, null],
        default: null
    }
})

const emit = defineEmits(['update:modelValue'])

const isActive = (value) => {
    if (props.mode === 'multiple') {
        return Array.isArray(props.modelValue) && props.modelValue.includes(value)
    }
    return props.modelValue === value
}

const updateValue = (clickedValue) => {
    // MODE 3: Any amount can be active (emits Array)
    if (props.mode === 'multiple') {
        // Ensure we are working with an array
        const currentSelection = Array.isArray(props.modelValue) ? [...props.modelValue] : []
        const valueIndex = currentSelection.indexOf(clickedValue)
        
        if (valueIndex > -1) {
            currentSelection.splice(valueIndex, 1) // Remove if already selected
        } else {
            currentSelection.push(clickedValue) // Add if not selected
        }
        
        emit('update:modelValue', currentSelection)
        return
    }

    // MODE 2: One and only one active (prevents toggling off)
    if (props.mode === 'single-required') {
        if (props.modelValue !== clickedValue) {
            emit('update:modelValue', clickedValue)
        }
        return // Do nothing if they click the already-active button
    }

    // MODE 1: Zero or one active (toggles off to null) - Default
    const newValue = props.modelValue === clickedValue ? props.defaultValue : clickedValue
    emit('update:modelValue', newValue)
}
</script>

<template>
    <div class="options-wrapper">
        <button 
            v-for="opt in options" 
            :key="String(opt.value)"
            class="btn-square btn-text"
            :class="{ [`btn-${opt.type}`]: isActive(opt.value) }"
            @click="updateValue(opt.value)"
        >
            {{ opt.label }}
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
}
</style>