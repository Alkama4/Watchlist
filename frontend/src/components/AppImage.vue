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
        <img
            v-bind="attrs"
            v-show="!loading && !notFound && attrs?.src"
            :key="attrs?.src"
            @error="onError"
            @load="onLoad"
        >

        <div
            v-if="loading && attrs?.src"
            class="loading-wave"
        ></div>

        <div
            v-else-if="notFound || !attrs?.src"
            class="not-found"
        >
            <Image pack="filled"/>
        </div>
    </div>
</template>

<style scoped>
.image-wrapper {
    position: relative;
    overflow: hidden;
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
