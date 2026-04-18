<script setup>
import { ref, computed, watch, onMounted, onUnmounted } from 'vue';

const props = defineProps({
    isExpanded: {
        type: Boolean,
        default: false,
    },
    duration: {
        type: String,
        default: '300ms',
    },
    maxHeight: {
        type: Number,
        default: null
    }
});

const contentRef = ref(null);
const currentHeight = ref('0px');
const skipTransition = ref(false);

const dynamicStyle = computed(() => ({
    height: currentHeight.value,
    transitionDuration: skipTransition.value ? '0s' : props.duration,
    overflowY: props.maxHeight && parseInt(currentHeight.value) >= props.maxHeight ? 'auto' : 'hidden',
    overflowX: 'hidden'
}));

watch(() => props.isExpanded, (expanded) => {
    skipTransition.value = false;
    if (expanded) {
        const scrollHeight = contentRef.value?.scrollHeight || 0;
        // 3. Apply the cap
        const targetHeight = props.maxHeight ? Math.min(scrollHeight, props.maxHeight) : scrollHeight;
        currentHeight.value = `${targetHeight}px`;
    } else {
        currentHeight.value = '0px';
    }
}, { immediate: true });

let observer = null;

onMounted(() => {
    observer = new ResizeObserver((entries) => {
        if (!props.isExpanded) return;

        for (const entry of entries) {
            const newHeight = entry.target.scrollHeight;
            
            // 4. Apply the cap here too for dynamic content changes
            const cappedHeight = props.maxHeight ? Math.min(newHeight, props.maxHeight) : newHeight;

            skipTransition.value = true;
            currentHeight.value = `${cappedHeight}px`;

            requestAnimationFrame(() => {
                skipTransition.value = false;
            });
        }
    });

    if (contentRef.value) {
        observer.observe(contentRef.value);
    }
});

onUnmounted(() => {
    if (observer) observer.disconnect();
});
</script>

<template>
    <div
        class="expandable-wrapper"
        :style="dynamicStyle"
    >
        <div ref="contentRef">
            <slot />
        </div>
    </div>
</template>

<style scoped>
.expandable-wrapper {
    overflow: hidden;
    transition-property: height;
    transition-timing-function: var(--transition-ease-out-str);
    padding: 0;
}

</style>

