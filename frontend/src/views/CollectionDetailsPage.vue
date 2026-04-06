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
    return timeFormatters.timestampToYear(
        collectionDetails.value?.first_release_date
    );
});

const lastYear = computed(() => {
    return timeFormatters.timestampToYear(
        collectionDetails.value?.last_release_date
    );
});

const formattedRunTime = computed(() => {
    return timeFormatters.minutesToHrAndMin(collectionDetails.value?.total_runtime);
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
                    <div class="stat">{{ formattedRunTime }}</div>
                    <span class="sep">|</span>
                    <div class="stat">{{ collectionDetails?.title_count }} Titles</div>
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
.collection-details-page {
    --details-height: 700px;
}

.collection-details-page > * {
    position: relative;
    z-index: 10;
}

img.backdrop {
    position: absolute;
    top: 0;
    left: 0;
    width: 100vw;
    height: calc(var(--details-height) * 1.5);
    object-fit: cover;
    z-index: 0;
    mask-image: linear-gradient(
        to top,
        rgba(0, 0, 0, 0) 0%,
        rgba(0, 0, 0, 0.25) 50%
    );
}

.collection-details {
    margin-top: var(--spacing-xl);
    margin-bottom: var(--spacing-xl);
    display: flex;
    flex-direction: row;
    align-items: end;
    gap: var(--spacing-md-lg);
    height: var(--details-height);

    img.poster {
        width: 300px;
        border-radius: var(--border-radius-lg);
    }

    .collection-info {
        margin-top: var(--spacing-md);
        display: flex;
        flex-direction: column;
        justify-content: end;

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

@media(min-width: calc(1600px + 10vw)) {
    .collection-details-page {
        --details-height: fit-content;
    }

    img.backdrop {
        --cont-width: 1600px;
        --overlap: 15%;

        height: 100vh;
        max-height: 2000px;
        mask-image: 
            linear-gradient(
                to right,
                rgba(0, 0, 0, 0.5) 0%,
                rgba(0, 0, 0, 0.25) calc((100% - var(--cont-width) + var(--overlap)) / 2),
                rgba(0, 0, 0, 0.25) calc((100% - var(--cont-width) - var(--overlap)) / 2 + var(--cont-width)),
                rgba(0, 0, 0, 0.5) 100%
            ),
            linear-gradient(
                to top,
                rgba(0, 0, 0, 0) 0%,
                rgba(0, 0, 0, 1) 50%
            );
        mask-composite: intersect;
        -webkit-mask-composite: source-in; /* For Safari/Chrome support */
    }
}
</style>