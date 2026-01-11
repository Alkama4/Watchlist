<script setup>
import { onMounted, ref } from 'vue'
import Modal from './Modal.vue'

const buttonCancel = ref(null)
const buttonConfirm = ref(null)

const modalRef = ref(null)
let resolver = null

const { negativeAction } = defineProps({
    header: {
        type: String,
        default: 'Confirm action'
    },
    message: {
        type: String,
        default: 'Are you sure you want to continue?'
    },
    confirmLabel: {
        type: String,
        default: 'Confirm'
    },
    cancelLabel: {
        type: String,
        default: 'Cancel'
    },
    negativeAction: {
        type: Boolean,
        default: false
    }
})

function query() {
    modalRef.value.open()

    setTimeout(() => {
        if (!negativeAction) {
            buttonConfirm.value.focus();
        } else {
            buttonCancel.value.focus();
        }
    }, 1)

    return new Promise(resolve => {
        resolver = resolve
    })
}

function confirm() {
    resolver?.(true)
    modalRef.value.close()
}

function cancel() {
    resolver?.(false)
    modalRef.value.close()
}

function catchClose() {
    resolver?.(false)
}

defineExpose({ query })
</script>

<template>
    <Modal :header="header" ref="modalRef" @closed="catchClose" :smallCard="true">
        <p>{{ message }}</p>
        <div class="button-row">
            <button ref="buttonCancel" @click="cancel">
                {{ cancelLabel }}
            </button>
            <button ref="buttonConfirm" :class="negativeAction ? 'btn-negative' : 'btn-primary'" @click="confirm">
                {{ confirmLabel }}
            </button>
        </div>
    </Modal>
</template>

<style scoped>

</style>
