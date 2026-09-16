<script setup>
import { Image } from '@boxicons/vue'
import { ref, useAttrs } from 'vue'

const attrs = useAttrs()

const loading = ref(true)
const notFound = ref(false)

const onError = () => {
    loading.value = false
    notFound.value = true
}
const onLoad = () => {
    loading.value = false
}
</script>

<template>
    <div class="image-wrapper">
        <div
            v-if="loading"
            class="loading-wave"
        ></div>

        <div
            v-else-if="notFound"
            class="not-found"
        >
            <Image pack="filled"/>
        </div>

        <img
            v-bind="attrs"
            v-show="!loading && !notFound"
            :key="attrs?.src"
            @error="onError"
            @load="onLoad"
        >
    </div>
</template>

<style scoped>
.image-wrapper {
    position: relative;
    overflow: hidden;
    /* background-color: var(--c-bg-backdrop); */
}

.image-wrapper > * {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    object-fit: cover;
}

.not-found {
    color: var(--c-text-soft);
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    opacity: 0.15;

    svg {
        --size: calc(15% + 20px);
        width: var(--size);
        height: var(--size);
    }
}
</style>
