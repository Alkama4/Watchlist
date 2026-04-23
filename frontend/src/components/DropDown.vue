<script setup>
import { ChevronDown } from '@boxicons/vue';
import { ref, watch } from 'vue';
import MobileDrawer from './MobileDrawer.vue';

const props = defineProps({
    disabled: {
        type: Boolean,
        default: false
    },
    hasChevron: {
        type: Boolean,
        default: false
    },
    align: {
        type: String,
        default: 'left',
        validator: (value) => ['left', 'right'].includes(value)
    },
    drawerHeader: {
        type: String,
        default: ''
    },
    roundButton: {
        type: Boolean,
        default: false
    }
});

const isActive = ref(false);
const drawer = ref(null);

function toggle() {
    if (!props.disabled) {
        isActive.value = !isActive.value;
    }
}

function close() {
    isActive.value = false;
}

// Automatically close the dropdown if it becomes disabled while open
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
        class="dropdown dropdown-desktop" 
        :class="{'disabled': disabled}" 
        tabindex="-1"
        @focusout="close"
    >
        <button 
            class="btn-even-padding trigger-button" 
            :class="{'active': isActive}"
            @click="toggle"
            :disabled="disabled"
        >
            <slot />
            <ChevronDown v-if="hasChevron" class="chevron"/>
        </button>

        <Transition name="options">
            <div 
                v-if="isActive" 
                class="desktop-options" 
                :class="`align-${align}`" 
                @mousedown.prevent
            >
                <slot name="content" />
            </div>
        </Transition>
    </div>

    <div class="dropdown dropdown-mobile">
        <button
            class="btn-even-padding trigger-button" 
            :class="{'round': roundButton}"
            @click="drawer?.open()"
            :disabled="disabled"
        >
            <slot />
            <ChevronDown v-if="hasChevron" class="chevron"/>
        </button>
        
        <MobileDrawer ref="drawer" :header="drawerHeader">
            <slot name="content" />
        </MobileDrawer>
    </div>
</template>

<style scoped>
/* --- Desktop Styles --- */
.dropdown-desktop {
    position: relative;
    display: inline-block; 
}

.trigger-button {
    position: relative;
    display: flex;
    align-items: center;
    gap: var(--spacing-xs, 4px);
    white-space: nowrap;

    &.round {
        border-radius: 100px;
    }
}

.chevron {
    transition: transform 0.1s ease-out;
}

.trigger-button.active .chevron {
    transform: rotate(180deg);
}

.desktop-options {
    position: absolute;
    top: calc(100% + var(--spacing-sm));
    max-height: clamp(300px, 50vh, 700px);
    overflow-y: auto;
    
    background-color: var(--c-bg-opaque-base);
    backdrop-filter: blur(var(--blur-subtle));
    border: 1px solid var(--c-border);
    
    padding: var(--spacing-xs);
    border-radius: var(--border-radius-md-lg);
    z-index: 100;

    display: flex;
    flex-direction: column;
}

/* Alignment Modifiers */
.align-left {
    left: 0;
}

.align-right {
    right: 0;
}

/* Transitions */
.options-enter-active,
.options-leave-active {
    transition: opacity 0.1s ease, transform 0.1s ease;
}

.options-enter-from,
.options-leave-to {
    transform: translateY(-8px);
    opacity: 0;
}

/* --- Mobile Styles --- */
.dropdown-mobile {
    display: none; 
}

@media(max-width: 768px) {
    .dropdown-desktop {
        display: none;
    }
    .dropdown-mobile {
        display: flex;
        flex-direction: column;
    }
}
</style>
