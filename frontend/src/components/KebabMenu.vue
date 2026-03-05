<script setup>
import { DotsVerticalRounded } from '@boxicons/vue';
import { ref, watch } from 'vue';

const props = defineProps({
    disabled: {
        type: Boolean,
        default: false
    },
    modified: {
        type: Boolean,
        default: false
    },
    menuItems: {
        type: Array,
        default: () => []
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
        class="kebab-menu" 
        :class="{'disabled': disabled}" 
        tabindex="-1"
        @focusout="close"
    >
        <DotsVerticalRounded 
            class="btn btn-text btn-even-padding" 
            :class="{'active': isActive}"
            @click="toggle"
            :disabled="disabled"
        />
        <Transition name="options">
            <div v-if="isActive" class="options" @mousedown.prevent>
                <button v-for="item in menuItems" @click="item?.action" class="btn-even-padding btn-text">
                    <component
                        :is="item?.iconComponent"
                        pack="filled"
                        size="xs"
                    />
                    <span>{{ item?.label }}</span>
                </button>
            </div>
        </Transition>
    </div>
</template>

<style scoped>
.kebab-menu {
    position: relative;
}

.options {
    position: absolute;
    top: 100%;
    right: 0;
    z-index: 100;
    background-color: var(--c-bg-opaque-base);
    backdrop-filter: blur(var(--blur-subtle));
    padding: var(--spacing-xs);
    border-radius: var(--border-radius-md);
    border: 1px solid var(--c-border);

    display: flex;
    flex-direction: column;
    /* gap: var(--spacing-xs); */

    button {
        padding-right: var(--spacing-lg);
        gap: var(--spacing-sm);
        white-space: nowrap;
        justify-content: start;
        font-weight: 500;
    }
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