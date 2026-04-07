<script setup>
import CollectionCard from '@/components/CollectionCard.vue';
import { fastApi } from '@/utils/fastApi';
import { Clock, Heart, MoviePlay } from '@boxicons/vue';
import { onMounted, ref } from 'vue';
import Jellyfin from '@/assets/icons/jellyfin.svg';

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
    <div class="collections-page layout-contained layout-spacing-top layout-spacing-bottom">
        <h3 class="no-top">Smart Collections</h3>
        <div class="default-collections">
            <router-link
                to="/search?fav=true"
                class="btn btn-favourite no-deco"
            >
                <Heart pack="filled"/>
                <span>Favourites ({{ pageData?.smart_collection_sizes?.is_favourite }} Titles)</span>
            </router-link>
            <router-link
                to="/search?watchlist=true"
                class="btn btn-accent no-deco"
            >
                <Clock pack="filled"/>
                <span>Watchlist ({{ pageData?.smart_collection_sizes?.in_watchlist }} Titles)</span>
            </router-link>
            <router-link
                to="/search?jellyfin=true"
                class="btn no-deco"
            >
                <Jellyfin width="22px" height="22px"/>
                <span>Jellyfin ({{ pageData?.smart_collection_sizes?.jellyfin_link }} Titles)</span>
            </router-link>
            <router-link
                to="/search?video=true"
                class="btn no-deco"
            >
                <MoviePlay pack="filled"/>
                <span>Video Assets ({{ pageData?.smart_collection_sizes?.has_video_assets }} Titles)</span>
            </router-link>
        </div>

        <h3 class="icon-header">TMDB Collections</h3>
        <div class="tmdb-collection-cards-wrapper">
            <CollectionCard
                v-for="tmdbCollection in pageData?.tmdb_collections"
                :key="tmdbCollection?.tmdb_collection_id"
                :tmdbCollection="tmdbCollection"
            />
        </div>

        <h3 class="icon-header">Custom Collections</h3>
        <div
            v-if="!pageData?.collections?.length"
            class="card not-found-section" 
        >
            <h2>No collections found</h2>
            <p>You don't have any custom collections.</p>
            <button>Create your first collection</button>
        </div>
    </div>
</template>

<style scoped>
.default-collections {
    display: flex;
    flex-wrap: wrap;
    gap: var(--spacing-sm-md);

    .btn {
        flex: 1;
        padding: var(--spacing-md) var(--spacing-lg-xl);
        font-size: var(--fs-0);
        border-radius: var(--border-radius-md-lg);
        gap: var(--spacing-xs-sm);
        white-space: nowrap;
    }
}

.tmdb-collection-cards-wrapper {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(var(--collection-card-width), 1fr));
    gap: var(--spacing-md);
}
</style>