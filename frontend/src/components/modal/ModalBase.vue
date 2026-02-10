<script setup>
import { ref, onUnmounted, onMounted } from 'vue'

const visible = ref(false)

const emit = defineEmits(['closed'])

defineProps({
    header: {
        type: String,
        required: false
    },
    smallCard: {
        type: Boolean,
        default: false,
    },
    minimumCard: {
        type: Boolean,
        default: false
    }
})

function open() {
    visible.value = true
    document.body.classList.add('no-scroll');
}

function close() {
    emit('closed')
    visible.value = false
    document.body.classList.remove('no-scroll');
}

const handleEscape = (event) => {
    if (event.key === 'Escape') {
        close();
    }
};

defineExpose({ open, close })


onMounted(() => {
    window.addEventListener('keydown', handleEscape);
})

onUnmounted(() => {
    window.addEventListener('keydown', handleEscape);
    document.body.classList.remove('no-scroll');
})
</script>

<template>
    <teleport to="body">
        <Transition name="modal-fade">
            <div 
                v-if="visible"
                class="modal-backdrop"
                @click="close"
            >
                <div 
                    class="card" 
                    :class="{'small': smallCard, 'min-content': minimumCard}"
                    @click.stop
                >
                    <div class="header-row">
                        <h2 class="no-top">{{ header }}</h2>
                        <i class="bx bx-x btn-text subtle" @click="close"></i>
                    </div>
                    <slot></slot>
                </div>
            </div>
        </Transition>
    </teleport>
</template>

<style scoped>
.modal-backdrop {
    position: fixed;
    top: 0;
    bottom: 0;
    left: 0;
    right: 0;
    background-color: var(--c-bg-backdrop);
    display: flex;
    align-items: center;
    justify-content: center;
    padding: var(--spacing-lg) 2.5vw;
    cursor: pointer;
    backdrop-filter: blur(var(--blur-subtle));
    
    z-index: var(--z-modal);
}

.modal-fade-enter-active {
    transition: opacity 0.15s ease-out;
}
.modal-fade-leave-active {
    transition: opacity 0.15s ease-in;
}
.modal-fade-enter-from,
.modal-fade-leave-to {
    opacity: 0;
}

.modal-fade-enter-active .card {
    transition: transform 0.15s ease-out;
}
.modal-fade-leave-active .card {
    transition: transform 0.15s ease-in;
}
.modal-fade-enter-from .card,
.modal-fade-leave-to .card {
    transform: translateY(16px);
}

.card {
    cursor: auto;
    max-height: 80vh;
    max-width: 100%;
    box-sizing: border-box;
    display: flex;
    flex-direction: column;
}
.card.small {
    max-width: 600px;
}
.card.min-content {
    width: min-content;
}

.header-row {
    display: flex;
    align-items: flex-start;
    justify-content: space-between;
}
.header-row i {
    font-size: var(--fs-3);
}
</style>