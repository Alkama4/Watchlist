<script setup>
import CollectionCard from '@/components/CollectionCard.vue';
import { fastApi } from '@/utils/fastApi';
import { Clock, Heart, MoviePlay } from '@boxicons/vue';
import { onMounted, ref } from 'vue';
import Jellyfin from '@/assets/icons/jellyfin.svg';
import LoadingIndicator from '@/components/LoadingIndicator.vue';

const pageLoading = ref({});
const pageData = ref({});

async function fetchCollections() {
    pageLoading.value = true;
    try {
        pageData.value = await fastApi.collectionsView();
    } finally {
        pageLoading.value = false;
    }
}

onMounted(async () => {
    await fetchCollections();
});
</script>

<template>
    <LoadingIndicator v-if="pageLoading"/>

    <div v-else class="collections-page layout-contained layout-spacing-top layout-spacing-bottom">
        <h3 class="no-top">Smart Collections</h3>
        <div class="default-collections">
            <router-link
                to="/smart_collection?header=Favourites&fav=true"
                class="btn btn-favourite no-deco"
            >
                <Heart pack="filled"/>
                <div class="text">
                    <div>Favourites</div>
                    <div class="stats">{{ pageData?.smart_collection_sizes?.is_favourite }} Titles</div>
                </div>
            </router-link>
            <router-link
                to="/smart_collection?header=Watchlist&watchlist=true"
                class="btn btn-accent no-deco"
            >
                <Clock pack="filled"/>
                <div class="text">
                    <div>Watchlist</div>
                    <div class="stats">{{ pageData?.smart_collection_sizes?.in_watchlist }} Titles</div>
                </div>
            </router-link>
            <router-link
                to="/smart_collection?header=Jellyfin&jellyfin=true"
                class="btn no-deco"
            >
                <Jellyfin class="custom"/>
                <div class="text">
                    <div>Jellyfin</div>
                    <div class="stats">{{ pageData?.smart_collection_sizes?.jellyfin_link }} Titles</div>
                </div>
            </router-link>
            <router-link
                to="/smart_collection?header=Video+Assets&video=true"
                class="btn no-deco"
            >
                <MoviePlay pack="filled"/>
                <div class="text">
                    <div>Video Assets</div>
                    <div class="stats">{{ pageData?.smart_collection_sizes?.has_video_assets }} Titles</div>
                </div>
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
        min-width: 240px;
        justify-content: start;
        padding: 0;
        font-size: var(--fs-0);
        border-radius: var(--border-radius-md-lg);
        gap: 0;
        
        white-space: nowrap;
        overflow: hidden;

        svg {
            height: 28px;
            width: 28px;
            min-width: 28px;
            backdrop-filter: brightness(0.8);
            padding: var(--spacing-md) var(--spacing-md);
        }

        .text {
            padding-left: var(--spacing-md);
            padding-right: var(--spacing-lg);
        }
        
        .stats {
            color: var(--c-text-subtle);
            font-weight: 400;
            font-size: var(--fs-neg-1);
        }
        &:hover .stats {
            color: var(--c-text-soft);
        }
    }
}

.tmdb-collection-cards-wrapper {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(var(--collection-card-width), 1fr));
    gap: var(--spacing-md);
}
</style>