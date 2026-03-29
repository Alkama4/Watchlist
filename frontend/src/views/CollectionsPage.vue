<script setup>
import TitleCardCarousel from '@/components/title_cards/TitleCardCarousel.vue';
import { fastApi } from '@/utils/fastApi';
import { AlbumCovers, Clock, Heart } from '@boxicons/vue';
import { onMounted, ref } from 'vue';

const waiting = ref({});
const pageData = ref({});

async function fetchCollections() {
    waiting.value = true;
    try {
        pageData.value = await fastApi.collections();
    } finally {
        waiting.value = false;
    }
}

onMounted(async () => {
    await fetchCollections();
});
</script>

<template>
    <div class="collections-page layout-spacing-top layout-spacing-bottom">
        <div class="layout-contained">
            <h3 class="icon-header"><Clock pack="filled"/> Watchlist</h3>
        </div>
        <TitleCardCarousel :carouselData="pageData?.watchlist"/>
        
        <div class="layout-contained">
            <h3 class="icon-header"><Heart pack="filled"/> Favourites</h3>
        </div>
        <TitleCardCarousel :carouselData="pageData?.favourites"/>
        <div class="collections-section layout-contained">
            <h3 class="icon-header"><AlbumCovers pack="filled"/> Custom Collections</h3>
            <div
                v-if="!pageData?.collections?.length"
                class="card not-found-section" 
            >
                <h2>No collections found</h2>
                <p>You don't have any collections.</p>
                <button>
                    Create your first collection
                </button>
            </div>
        </div>
    </div>
</template>

<style scoped>
.icon-header {
    display: flex;
    align-items: center;
    gap: var(--spacing-sm);
}
</style>