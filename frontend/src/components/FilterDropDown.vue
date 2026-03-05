<script setup>
import { ChevronDown, Circle } from '@boxicons/vue';
import { ref, watch } from 'vue';

const props = defineProps({
    label: {
        type: String,
        required: true
    },
    disabled: {
        type: Boolean,
        default: false
    },
    modified: {
        type: Boolean,
        default: false
    }
});

const isActive = ref(false);

function toggle() {
    if (!props.disabled) {
        isActive.value = !isActive.value;
    }
}
function close() {
    isActive.value = false;
}

watch(
    () => props.disabled,
    (newDisabled) => {
        if (newDisabled) {
            close();
        }
    }
);
</script>

<template>
    <div 
        class="search-filter" 
        :class="{'disabled': disabled}" 
        tabindex="-1"
        @focusout="close"
    >
        <button 
            class="btn-text btn-even-padding" 
            :class="{'active': isActive}"
            @click="toggle"
            :disabled="disabled"
        >
            <Circle
                pack="filled"
                :class="{'active': modified}"
                class="dot"
                height="8px"
                width="8px"
            />
            <span>{{ label }}</span>
            <ChevronDown class="chevron"/>
        </button>
        <Transition name="options">
            <div v-if="isActive" class="options" @mousedown.prevent>
                <slot/>
            </div>
        </Transition>
    </div>
</template>

<style scoped>
.search-filter {
    position: relative;
}

button {
    position: relative;

    span {
        padding-left: var(--spacing-xs);
    }

    .chevron {
        transition: transform 0.1s ease-out;
    }
    &.active .chevron {
        transform: rotate(180deg);
    }

    .dot {
        color: transparent;
        position: absolute;
        right: 30px;
        top: 8px;

        &.active {
            color: var(--c-positive);
        }
    }
}

.options {
    position: absolute;
    top: 100%;
    z-index: 100;
    background-color: var(--c-bg-opaque-base);
    backdrop-filter: blur(var(--blur-subtle));
    padding: var(--spacing-xs);
    border-radius: var(--border-radius-md);
    border: 1px solid var(--c-border);
}

.options-enter-active,
.options-leave-active {
    transition: opacity 0.1s ease, transform 0.1s ease;
}

.options-enter-from,
.options-leave-to {
    transform: translateY(-8px);
    opacity: 0;
}

</style>