<script setup>
import { ChevronDown, Circle } from '@boxicons/vue';
import { ref, watch } from 'vue';
import MobileDrawer from './MobileDrawer.vue';

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
const drawer = ref(null);

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

    <div class="search-filter-mobile">
        <button
            class="btn-text btn-even-padding" 
            @click="drawer?.open()"
            :disabled="disabled"
        >
            <Circle
                v-if="modified"
                pack="filled"
                class="dot active"
                height="8px"
                width="8px"
            />
            <span>{{ label }}</span>
        </button>
        
        <MobileDrawer ref="drawer" :header="label">
            <slot/>
        </MobileDrawer>
    </div>
</template>

<style scoped>
.search-filter {
    position: relative;
    display: inline-block; 
}
.search-filter-mobile {
    display: none; 
}

button {
    position: relative;
    display: flex;
    align-items: center;

    span {
        padding-left: var(--spacing-xs);
        white-space: nowrap;
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
        right: 30px; /* You might need to adjust this depending on your button padding */
        top: 8px;

        &.active {
            color: var(--c-positive, green);
        }
    }
}

.options {
    position: absolute;
    top: 100%;
    max-height: clamp(300px, 50vh, 700px);
    overflow-y: auto;

    background-color: var(--c-bg-opaque-base);
    backdrop-filter: blur(var(--blur-subtle));
    border: 1px solid var(--c-border);

    padding: var(--spacing-xs);
    border-radius: var(--border-radius-md-lg);
    
    z-index: 100;
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

@media(max-width: 768px) {
    .search-filter {
        display: none;
    }
    .search-filter-mobile {
        display: block;
    }

    .search-filter-mobile button .dot {
        position: relative;
        right: auto;
        top: auto;
    }
}
</style>