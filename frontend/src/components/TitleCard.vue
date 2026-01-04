<script setup>
defineProps({
    titleInfo: {
        type: Object,
        required: true,
    }
})
</script>

<template>
    {{ titleInfo }}
</template>