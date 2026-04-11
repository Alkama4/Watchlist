<script setup>
import { ref, onMounted, onUnmounted } from 'vue';
import MobileDrawer from './MobileDrawer.vue';
import ModalBase from './modal/ModalBase.vue';
import { useAttrs } from 'vue';

const attrs = useAttrs();
const props = defineProps({
    breakpoint: { type: Number, default: 768 }
});

const isMobile = ref(false);
const overlayRef = ref(null);

const updateBreakpoint = () => {
    isMobile.value = window.innerWidth <= props.breakpoint;
};

onMounted(() => {
    updateBreakpoint();
    window.addEventListener('resize', updateBreakpoint);
});

onUnmounted(() => window.removeEventListener('resize', updateBreakpoint));

const open = () => overlayRef.value?.open();
const close = () => overlayRef.value?.close();

defineExpose({ open, close });
</script>

<template>
    <MobileDrawer 
        v-if="isMobile" 
        ref="overlayRef" 
        :header="header"
        v-bind="$attrs"
    >
        <slot />
    </MobileDrawer>
    
    <ModalBase 
        v-else 
        ref="overlayRef" 
        :header="header"
        v-bind="$attrs"
    >
        <slot />
    </ModalBase>
</template>
