<script setup>
import { ref } from "vue"

const visible = ref(false)
</script>

<template>
    <div class="tooltip-wrapper" @mouseenter="visible = true" @mouseleave="visible = false">
        <slot/>

        <transition name="fade">
            <div v-if="visible" class="tooltip">
                <slot name="content"/>
            </div>
        </transition>
    </div>
</template>

<style scoped>
.tooltip-wrapper {
    position: relative;
    display: inline-block;
}

.tooltip {
    position: absolute;
    bottom: 120%;
    left: 50%;
    transform: translateX(-50%);
    width: max-content;
    max-width: 40ch;
    z-index: 10;
    
    background: var(--c-bg-level-2);
    color: var(--c-text);
    padding: var(--spacing-sm) var(--spacing-sm-md);
    border-radius: var(--border-radius-md);
    font-size: var(--fs-neg-2);
    text-align: left;
    box-shadow: 0 4px 12px hsla(0, 0%, 0%, 0.2);
}

.fade-enter-active,
.fade-leave-active {
    transition: opacity 0.2s;
}
.fade-enter-from,
.fade-leave-to {
    opacity: 0;
}
</style>