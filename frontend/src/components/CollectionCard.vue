<script setup>
import { getTitleImageUrl } from '@/utils/imagePath';
import Tmdb from '@/assets/icons/tmdb.svg';

defineProps({
    tmdbCollection: {
        type: Object,
        required: true,
    },
});
</script>

<template>
    <router-link
        :to="`/collection/${tmdbCollection?.tmdb_collection_id}`"
        class="tmdb-collection-card no-deco"
    >
        <img
            :src="getTitleImageUrl(tmdbCollection, 800, 'backdrop')"
            alt="Collection backdrop"
            class="backdrop"
        />
        <img
            :src="getTitleImageUrl(tmdbCollection, 400, 'poster')"
            alt="Collection poster"
            class="poster"
        />

        <div class="details">
            <h4>{{ tmdbCollection?.name }}</h4>
            <div class="stats">
                <!-- Most values placeholders for now -->
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
</template>

<style scoped>
.tmdb-collection-card {
    display: flex;
    position: relative;
    min-width: var(--collection-card-width);
    /* padding: var(--spacing-sm-md); */
    gap: var(--spacing-md);
    box-sizing: border-box;

    overflow: hidden;
    border-radius: var(--border-radius-md-lg);
}

img.backdrop {
    position: absolute;
    top: 0;
    left: 150px;
    width: 100%;
    height: 100%;
    z-index: 0;
    object-fit: cover;
    /* filter: brightness(0.33); */
    mask-image: linear-gradient(
        to top,
        rgba(0, 0, 0, 0.05) 25%,
        rgba(0, 0, 0, 0.5) 100%
    );
}

img.poster {
    width: 150px;
    aspect-ratio: 2 / 3;
    /* border-radius: var(--border-radius-md); */
    z-index: 1;
    object-fit: cover;
}

.details {
    z-index: 1;
    display: flex;
    flex-direction: column;
    justify-content: end;
    margin-bottom: var(--spacing-md);
    margin-right: var(--spacing-md);
    gap: var(--spacing-sm);

    h4 {
        margin: 0;
    }

    .stats,
    p {
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
        -webkit-line-clamp: 3;
        line-clamp: 3;
        -webkit-box-orient: vertical;
        overflow: hidden;
    }
}
</style>
