<script setup>
import TitleCardCarousel from '@/components/title_cards/TitleCardCarousel.vue';
import { fastApi } from '@/utils/fastApi';
import { getTitleImageUrl } from '@/utils/imagePath';
import { onMounted, ref } from 'vue';
import { useRoute } from 'vue-router';

const collectionDetails = ref({});
const route = useRoute();

async function fetchCollectionDetails() {
    const tmdb_collection_id = route.params.tmdb_collection_id;
    collectionDetails.value = await fastApi.collections.tmdb.getById(tmdb_collection_id);
}

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
            <div>
                <div class="collection-name">
                    <h1>{{ collectionDetails?.name }}</h1>
                    <h4 v-if="collectionDetails?.name != collectionDetails?.name_original">
                        {{ collectionDetails?.name_original }}
                    </h4>
                </div>
                <p>{{ collectionDetails?.overview }}</p>
                {{ collectionDetails }}
            </div>
        </div>

        <TitleCardCarousel
            :carouselData="collectionDetails"
        />
    </div>
</template>

<style scoped>
img.backdrop {
    position: absolute;
    top: 0;
    left: 0;
    width: 100vw;
    height: 100vh;
    object-fit: cover;
    opacity: 0.25;
    z-index: 0;
}

.collection-details {
    display: flex;
    position: relative;
    flex-direction: row;
    gap: var(--spacing-md);
    z-index: 10;

    img.poster {
        width: 300px;
        border-radius: var(--border-radius-lg);
    }

    .collection-name {
        margin-bottom: var(--spacing-md);
        display: flex;
        flex-direction: column;
        gap: var(--spacing-xs);

        h1, h4 {
            margin: 0
        }
    }
}
</style>