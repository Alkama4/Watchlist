<script setup>
import TitleCard from '@/components/title_cards/TitleCard.vue';
import { fastApi } from '@/utils/fastApi';
import { timeFormatters } from '@/utils/formatters';
import { getTitleImageUrl } from '@/utils/imagePath';
import { computed, onMounted, ref } from 'vue';
import { useRoute } from 'vue-router';

const collectionDetails = ref({});
const route = useRoute();

async function fetchCollectionDetails() {
    const tmdb_collection_id = route.params.tmdb_collection_id;
    collectionDetails.value = await fastApi.collections.tmdb.getById(tmdb_collection_id);
}

const firstYear = computed(() => {
    const releaseDate = collectionDetails.value?.titles?.[0]?.release_date;
    return releaseDate ? timeFormatters.timestampToYear(releaseDate) : null;
});

const lastYear = computed(() => {
    const titles = collectionDetails.value?.titles;
    const releaseDate = titles?.[titles?.length - 1]?.release_date;
    return releaseDate ? timeFormatters.timestampToYear(releaseDate) : null;
});

const combinedRunTime = computed(() => {
    const titles = collectionDetails.value?.titles;
    if (!titles) return 0;
    let count = 0;
    
    for (const title of titles) {
        count += title?.movie_runtime;
    }
    
    return timeFormatters.minutesToHrAndMin(count);
});

const combinedGenres = computed(() => {
    const titles = collectionDetails.value?.titles;
    if (!titles) return [];

    const genreMap = new Map();
    titles.forEach(title => {
        title.genres?.forEach(genre => {
            if (!genreMap.has(genre.tmdb_genre_id)) {
                genreMap.set(genre.tmdb_genre_id, genre);
            }
        });
    });

    return Array.from(genreMap.values());
});

onMounted(async () => {
    await fetchCollectionDetails();
})
</script>

<template>
    <div class="collection-details-page layout-spacing-top layout-spacing-bottom">
        <img
            :src="getTitleImageUrl(collectionDetails, 'original', 'backdrop')"
            alt="Collection backdrop"
            class="backdrop"
        >

        <div class="collection-details layout-contained">
            <div>
                <img
                    :src="getTitleImageUrl(collectionDetails, '800', 'poster')"
                    alt="Collection poster"
                    class="poster"
                >
            </div>
            <div class="collection-info">
                <div class="collection-name">
                    <h1>{{ collectionDetails?.name }}</h1>
                    <h4 v-if="collectionDetails?.name != collectionDetails?.name_original">
                        {{ collectionDetails?.name_original }}
                    </h4>
                </div>
                <div class="general-stats">
                    <div class="stat">
                        {{ firstYear }}
                        <template v-if="firstYear != lastYear">
                            - {{ lastYear }}
                        </template>
                    </div>
                    <span class="sep">|</span>
                    <div class="stat">{{ combinedRunTime }}</div>
                    <span class="sep">|</span>
                    <div class="stat">{{ collectionDetails?.titles?.length }} Movies</div>
                </div>
                <div class="genres">
                    <router-link
                        v-for="genre in combinedGenres"
                        :key="genre.tmdb_genre_id"
                        :to="`/search?genres_inc=${genre.tmdb_genre_id}`"
                        class="btn btn-pill no-deco"
                    >
                        {{ genre?.genre_name }}
                    </router-link>
                </div>
                <p>{{ collectionDetails?.overview }}</p>
            </div>
        </div>

        <div class="collection-titles layout-contained">
            <h3>Titles</h3>
        </div>

        <div class="title-card-grid layout-contained">
            <TitleCard
                v-for="title in collectionDetails?.titles"
                :key="title?.title_id"
                :title-info="title"
                :grid-mode="true"
            />
        </div>

    </div>
</template>

<style scoped>
.collection-details-page > * {
    position: relative;
    z-index: 10;
}

img.backdrop {
    position: absolute;
    top: 0;
    left: 0;
    width: 100vw;
    height: 66vh;
    object-fit: cover;
    /* opacity: 0.25; */
    z-index: 0;
    mask-image: linear-gradient(
        to top,
        rgba(0, 0, 0, 0) 0%,
        rgba(0, 0, 0, calc(1 - var(--details-backdrop-fade-intensity))) 50%
    );
}

.collection-details {
    margin-top: var(--spacing-xl);
    margin-bottom: var(--spacing-xl);
    display: flex;
    flex-direction: row;
    gap: var(--spacing-md-lg);

    img.poster {
        width: 300px;
        /* margin-inline: var(--spacing-md); */
        border-radius: var(--border-radius-lg);
    }

    .collection-info {
        margin-top: var(--spacing-md);
        /* display: flex;
        flex-direction: column; */

        .collection-name {
            margin-bottom: var(--spacing-md);
            display: flex;
            flex-direction: column;
            gap: var(--spacing-xs);
    
            h1, h4 {
                margin: 0
            }
        }
    
        .general-stats {
            display: flex;
            gap: var(--spacing-sm-md);
            font-weight: 600;
    
            .sep {
                color: var(--c-text-subtle);
            }
        }

        .genres {
            display: flex;
            margin-top: var(--spacing-sm-md);
            gap: var(--spacing-sm);
        }

    }
}

.title-card-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(var(--title-card-width), 1fr));
    gap: var(--spacing-lg) var(--spacing-md);

    .title-card {
        width: unset;
    }
}
</style>