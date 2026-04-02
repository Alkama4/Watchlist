<script setup>
import TitleCardCarousel from '@/components/title_cards/TitleCardCarousel.vue';
import { fastApi } from '@/utils/fastApi';
import { getTitleImageUrl } from '@/utils/imagePath';
import { AlbumCovers, Clock, Heart } from '@boxicons/vue';
import { onMounted, ref } from 'vue';
import Tmdb from '@/assets/icons/tmdb.svg';

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
            <h3 class="icon-header"><Clock pack="filled"/> Watchlist</h3>
        </div>
        <TitleCardCarousel :carouselData="{titles: pageData?.watchlist}"/>
        
        <div class="layout-contained">
            <h3 class="icon-header"><Heart pack="filled"/> Favourites</h3>
        </div>
        <TitleCardCarousel :carouselData="{titles: pageData?.favourites}"/>

        <div class="tmdb-collections-section layout-contained">
            <h3 class="icon-header"><AlbumCovers pack="filled"/> TMDB Collections</h3>
            <div class="tmdb-collection-cards-wrapper">
                <router-link
                    v-for="tmdbCollection in pageData?.tmdb_collections"
                    :to="`/collection/${tmdbCollection?.tmdb_collection_id}`"
                    class="tmdb-collection-card no-deco"
                >
                    <img
                        :src="getTitleImageUrl(tmdbCollection, 800, 'backdrop')"
                        alt="Collection backdrop"
                        class="backdrop"
                    >
                    <img
                        :src="getTitleImageUrl(tmdbCollection, 400, 'poster')"
                        alt="Collection poster"
                        class="poster"
                    >

                    <div class="details">
                        <h4>{{ tmdbCollection?.name }}</h4>
                        <div class="stats">
                            <div>2019 - 2020</div>
                            &bull;
                            <div>3h 42min</div>
                            &bull;
                            <div><Tmdb/> 7.8</div>
                            &bull;
                            <div>{{ tmdbCollection?.title_count }} Titles</div>
                        </div>

                        <p>{{ tmdbCollection?.overview }}</p>
                    </div>
                </router-link>
            </div>
        </div>

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

.tmdb-collection-cards-wrapper {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(var(--collection-card-width), 1fr));
    gap: var(--spacing-lg) var(--spacing-md);
}

.tmdb-collection-card {
    display: flex;
    position: relative;
    min-width: var(--collection-card-width);

    overflow: hidden;
    border-radius: var(--border-radius-md);

    img.backdrop {
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        z-index: 0;

        filter: brightness(0.5) blur(8px);
    }

    img.poster {
        width: 150px;
        aspect-ratio: 2/3;
        z-index: 1;
        object-fit: cover;
    }

    .details {
        z-index: 1;
        margin: var(--spacing-md);
        display: flex;
        flex-direction: column;
        gap: var(--spacing-sm);

        h4 {
            margin: 0;
        }
        .stats, p {
            font-size: 0.9rem;
            color: var(--c-text-soft);
        }
        .stats {
            display: flex;
            gap: var(--spacing-sm);

            div {
                flex-wrap: nowrap;
                white-space: nowrap;
            }
        }
        p {
            margin: 0;
            display: -webkit-box;
            -webkit-line-clamp: 7;
            line-clamp: 7;
            -webkit-box-orient: vertical;
            overflow: hidden;
        }
    }

}
</style>