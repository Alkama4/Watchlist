<script setup>
import { getTitleImageUrl } from '@/utils/imagePath';
import Tmdb from '@/assets/icons/tmdb.svg';
import { timeFormatters } from '@/utils/formatters';

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
        class="tmdb-collection-card btn no-deco"
    >
        <img
            :src="getTitleImageUrl(tmdbCollection, 400, 'poster')"
            alt="Collection poster"
            class="poster"
        />

        <div class="details">
            <h4>{{ tmdbCollection?.name }}</h4>
            <div class="stats">
                <div>
                    {{ timeFormatters.timestampToYear(tmdbCollection?.first_release_date) }}
                    <template v-if="
                        timeFormatters.timestampToYear(tmdbCollection?.first_release_date)
                        != timeFormatters.timestampToYear(tmdbCollection?.last_release_date)
                    ">
                        - {{ timeFormatters.timestampToYear(tmdbCollection?.last_release_date) }}
                    </template>
                </div>
                &bull;
                <div>{{ tmdbCollection?.title_count }} Titles</div>
                &bull;
                <div><Tmdb/> {{ tmdbCollection?.tmdb_vote_average }}</div>
            </div>
        </div>
    </router-link>
</template>

<style scoped>
.tmdb-collection-card {
    display: flex;
    position: relative;
    min-width: var(--collection-card-width);
    padding: 0;
    box-sizing: border-box;
    height: 125px;
    align-items: center;
    justify-content: start;

    overflow: hidden;
    border-radius: var(--border-radius-md-lg);
}

img.poster {
    height: 100%;
    aspect-ratio: 2 / 3;
    /* border-radius: var(--border-radius-md); */
    z-index: 1;
    object-fit: cover;
}

.details {
    z-index: 1;
    display: flex;
    flex-direction: column;
    gap: var(--spacing-sm);
    padding: var(--spacing-sm-md);

    h4 {
        margin: 0;
        display: -webkit-box;
        -webkit-line-clamp: 1;
        line-clamp: 1;
        -webkit-box-orient: vertical;
        overflow: hidden;
    }

    .stats {
        font-size: var(--fs-neg-1);
        color: var(--c-text-soft);
        display: flex;
        gap: var(--spacing-xs) var(--spacing-sm);
        flex-wrap: wrap;
        align-items: center;
        font-weight: 500;

        div {
            flex-wrap: nowrap;
            white-space: nowrap;
        }
    }
}
</style>
