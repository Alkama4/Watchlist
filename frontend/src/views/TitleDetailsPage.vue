<script setup>
import LoadingButton from '@/components/LoadingButton.vue';
import { fastApi } from '@/utils/fastApi';
import { resolveImagePath } from '@/utils/imagePath';
import { onMounted, ref } from 'vue';
import { useRoute } from 'vue-router';

const route = useRoute();
const titleDetails = ref({});
const waiting = ref({})

async function updateTitleDetails() {
    waiting.value.titleUpdate = true;
    try {
        await fastApi.titles.updateById(titleDetails.value.title_id);
        await fetchTitleDetails();
    } finally {
        waiting.value.titleUpdate = false;
    }
}

async function fetchTitleDetails() {
    const title_id = route.params.title_id;
    titleDetails.value = await fastApi.titles.getById(title_id)
}

onMounted(async () => {
    await fetchTitleDetails();
})
</script>

<template>
    <div class="title-details-page layout-contained layout-spacing-top layout-spacing-bottom">
        <img 
            :src="resolveImagePath(titleDetails, 'original', 'backdrop')"
            :alt="`${titleDetails?.type} backdrop: ${titleDetails?.name}`"
            class="backdrop"
        >

        <img 
            :src="resolveImagePath(titleDetails, 'original', 'poster')"
            :alt="`${titleDetails?.type} poster: ${titleDetails?.name}`"
            class="poster"
        >

        <h1>{{ titleDetails.name }}</h1>

        <LoadingButton
            @click="updateTitleDetails"
            :loading="waiting?.titleUpdate"
        >
            Update
        </LoadingButton>
        <p>{{ titleDetails }}</p>
    </div>
</template>

<style scoped>
img.backdrop {
    width: 100vw;
    height: 100vh;
    top: 0;
    left: 0;
    position: absolute;
    object-fit: cover;
    z-index: -10;

    mask-image: linear-gradient(
        to top,
        rgba(0, 0, 0, 0) 0%,
        rgba(0, 0, 0, 0.25) 35%
    );
}
img.poster {
    width: 200px;
    border-radius: var(--border-radius-md);
}
</style>
