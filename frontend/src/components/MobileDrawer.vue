<script setup>
import { useMediaQuery } from '@/utils/useMediaQuery';
import { ref, onUnmounted, onMounted, computed, watch } from 'vue'

const visible = ref(false)
const contentRef = ref(null)

const props = defineProps({
    modelValue: Boolean,
    header: String
});

const emit = defineEmits(['update:modelValue', 'closed']);

watch(() => props.modelValue, (val) => {
    if (val) open()
    else close()
})


const isMobile = useMediaQuery('(max-width: 768px)')
watch(isMobile, (mobile) => {
    // If the screen grows to desktop while drawer is "open", clean up
    if (!mobile && visible.value) {
        close()
    }
})

const startY = ref(0)
const currentY = ref(0)
const isDragging = ref(false)

function open() {
    if (!isMobile.value) return

    visible.value = true;
    document.body.classList.add('no-scroll');
    emit('update:modelValue', true);
}

function close() {
    visible.value = false;
    document.body.classList.remove('no-scroll');
    setTimeout(() => { currentY.value = 0 }, 300) ;
    emit('update:modelValue', false);
    emit('closed');
}

const handleEscape = (event) => {
    if (event.key === 'Escape') close()
}

const onTouchStart = (event) => {
    // Only track start if we are at the top of the scroll
    // (Or if we are touching the handle/header which doesn't scroll)
    startY.value = event.touches[0].clientY
    isDragging.value = true
}

const onTouchMove = (event) => {
    if (!isDragging.value) return
    
    const y = event.touches[0].clientY
    const deltaY = y - startY.value
    
    // 2. Logic: Only allow dragging if:
    // a) The user is pulling DOWN (deltaY > 0)
    // b) The content scroll position is at the very top (scrollTop <= 0)
    const isAtTop = contentRef.value ? contentRef.value.scrollTop <= 0 : true

    if (deltaY > 0 && isAtTop) {
        // Prevent the browser from trying to scroll/bounce the content
        if (event.cancelable) event.preventDefault() 
        currentY.value = deltaY
    } else {
        // If they start scrolling UP or are not at top, reset dragging
        // so the native scroll takes over
        currentY.value = 0
        if (!isAtTop) isDragging.value = false
    }
}

const onTouchEnd = () => {
    isDragging.value = false
    if (currentY.value > 100) {
        close()
    } else {
        currentY.value = 0
    }
}

const drawerStyle = computed(() => {
    if (!isDragging.value && currentY.value === 0) return {}
    return {
        transform: `translateY(${currentY.value}px)`,
        transition: isDragging.value ? 'none' : 'transform 0.25s var(--transition-ease-out)'
    }
})

defineExpose({ open, close })

onMounted(() => {
    window.addEventListener('keydown', handleEscape)
})

onUnmounted(() => {
    window.removeEventListener('keydown', handleEscape)
    document.body.classList.remove('no-scroll')
})
</script>

<template>
    <teleport to="body">
        <Transition name="drawer-fade">
            <div 
                v-if="visible"
                class="drawer-backdrop"
                @click="close"
            >
                <div 
                    class="drawer-card card" 
                    :style="drawerStyle"
                    @click.stop
                    @touchstart="onTouchStart"
                    @touchmove="onTouchMove"
                    @touchend="onTouchEnd"
                >
                    <div class="handle">
                        <div class="handle-pill"></div>
                    </div>
                    
                    <div class="drawer-content" ref="contentRef">
                        <slot></slot>
                    </div>
                </div>
            </div>
        </Transition>
    </teleport>
</template>
<style scoped>
.drawer-backdrop {
    position: fixed;
    top: 0;
    bottom: 0;
    left: 0;
    right: 0;
    background-color: var(--c-bg-backdrop);
    display: flex;
    align-items: flex-end; 
    justify-content: center;
    cursor: pointer;
    /* backdrop-filter: blur(var(--blur-subtle)); */
    z-index: var(--z-modal);
    transition: opacity 0.25s var(--transition-ease-out);
}

.drawer-card {
    cursor: auto;
    width: 100%;
    max-height: 66vh;
    box-sizing: border-box;
    display: flex;
    flex-direction: column;
    border-radius: var(--border-radius-lg) var(--border-radius-lg) 0 0;
    padding: 0 var(--spacing-md);
    transition: transform 0.25s var(--transition-ease-out);
}

.handle {
    padding: var(--spacing-sm-md) 0;
    touch-action: pan-y; 
}

.handle-pill {
    width: 40px;
    height: 5px;
    background-color: var(--c-border);
    border-radius: 100px;
    margin: 0 auto 0 auto;
}

.drawer-content {
    overflow-y: auto;
    padding: 0;
    padding-bottom: var(--spacing-md);
}


.drawer-fade-enter-from,
.drawer-fade-leave-to {
    opacity: 0;
    transform: translateY(0%);
}

.drawer-fade-enter-from .drawer-card,
.drawer-fade-leave-to .drawer-card {
    transform: translateY(100%);
}
</style>