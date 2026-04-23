<script setup>
import { DotsHorizontalRounded, DotsVerticalRounded } from '@boxicons/vue';
import DropDown from './DropDown.vue';

const props = defineProps({
    horizontalDots: {
        type: Boolean,
        default: false
    },
    menuItems: {
        type: Array,
        default: () => []
    },
    roundButton: {
        type: Boolean,
        default: false
    }
});
</script>

<template>
    <DropDown align="right" :roundButton="roundButton">
        <component
            :is="horizontalDots ? DotsHorizontalRounded : DotsVerticalRounded" 
        />
        <template #content>
            <div class="menu-options">
                <button
                    v-for="item in menuItems"
                    class="btn-text option-button"
                    @click="item?.action"
                >
                    <component
                        :is="item?.iconComponent"
                        pack="filled"
                        size="xs"
                    />
                    <span>{{ item?.label }}</span>
                </button>
            </div>
        </template>
    </DropDown>
</template>

<style scoped>
.menu-options {
    display: flex;
    flex-direction: column;
}

.option-button {
    padding-left: var(--spacing-sm-md);
    padding-right: var(--spacing-lg);
    gap: var(--spacing-md);
    white-space: nowrap;
    justify-content: start;
    font-weight: 500;
}

@media(max-width: 768px) {
    .option-button {
        padding: var(--spacing-sm-md) var(--spacing-md);
        gap: var(--spacing-md-lg);
        font-size: var(--fs-neg-1);
        font-weight: 400;

        svg {
            width: 20px;
            height: 20px;
        }
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