<script setup>
import CollectionCard from '@/components/CollectionCard.vue';
import TitleCardCarousel from '@/components/title_cards/TitleCardCarousel.vue';
import { fastApi } from '@/utils/fastApi';
import { AlbumCovers, Clock, Heart } from '@boxicons/vue';
import { onMounted, ref } from 'vue';

const waiting = ref({});
const pageData = ref({});

async function fetchCollections() {
    waiting.value = true;
    try {
        pageData.value = await fastApi.collectionsView();
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
            <h1>Collections</h1>
            <h3 class="icon-header"><Clock pack="filled" /> Watchlist</h3>
        </div>
        <TitleCardCarousel :carouselData="{titles: pageData?.watchlist}" />

        <div class="layout-contained">
            <h3 class="icon-header"><Heart pack="filled" /> Favourites</h3>
        </div>
        <TitleCardCarousel :carouselData="{titles: pageData?.favourites}" />

        <div class="tmdb-collections-section layout-contained">
            <h3 class="icon-header"><AlbumCovers pack="filled" /> TMDB Collections</h3>
            <div class="tmdb-collection-cards-wrapper">
                <CollectionCard
                    v-for="tmdbCollection in pageData?.tmdb_collections"
                    :key="tmdbCollection?.tmdb_collection_id"
                    :tmdbCollection="tmdbCollection"
                />
            </div>
        </div>

        <div class="collections-section layout-contained">
            <h3 class="icon-header"><AlbumCovers pack="filled" /> Custom Collections</h3>
            <div
                v-if="!pageData?.collections?.length"
                class="card not-found-section" 
            >
                <h2>No collections found</h2>
                <p>You don't have any collections.</p>
                <button>Create your first collection</button>
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

.tmdb-collection-cards-wrapper {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(var(--collection-card-width), 1fr));
    gap: var(--spacing-md);
}
</style>