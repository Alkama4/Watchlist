<script setup>
import TitleCardCarousel from '@/components/title_cards/TitleCardCarousel.vue';
import TitleHeroCardCarousel from '@/components/title_cards/TitleHeroCardCarousel.vue';
import LoadingIndicator from '@/components/LoadingIndicator.vue';
import { fastApi } from '@/utils/fastApi';
import { onMounted, ref } from 'vue';

const exploreData = ref([]);
const waiting = ref(true);

async function fetchExplore() {
    waiting.value = true;
    try {
        const response = await fastApi.explore();
        exploreData.value = Array.isArray(response) ? response : [];
    } finally {
        waiting.value = false;
    }
}

onMounted(async () => {
    await fetchExplore();
});

</script>

<template>
    <div v-if="!waiting" class="layout-spacing-bottom">
        <div class="layout-contained">
            <h1>Explore Library</h1>
            <p class="soft">Find already forgotten titles from your library</p>

            <div
                v-if="!exploreData?.length"
                class="card not-found-section" 
            >
                <h2>Nothing to explore</h2>
                <p>Couldn't find any movies or tv-shows to display here</p>
            </div>
        </div>
        <template v-for="list in exploreData" :key="`${list.style}-${list.header}`">
            <TitleHeroCardCarousel
                v-if="list?.style === 'hero'"
                :heroCards="list"
            />
            <TitleCardCarousel
                v-else-if="list?.style === 'poster' || list?.style === 'banner'"
                :carouselData="list"
            />
        </template>
    </div>

    <LoadingIndicator v-else/>
</template>

<style scoped>
.not-found-section {
    margin-top: var(--spacing-lg);
}
</style>