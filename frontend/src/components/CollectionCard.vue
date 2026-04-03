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
                <div>{{ timeFormatters.minutesToHrAndMin(tmdbCollection?.total_runtime) }}</div>
                &bull;
                <div><Tmdb/> {{ tmdbCollection?.tmdb_vote_average }}</div>
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
    padding: var(--spacing-sm-md);
    gap: var(--spacing-md);
    box-sizing: border-box;
    height: 277.5px;
    align-items: end;

    overflow: hidden;
    border-radius: var(--border-radius-md-lg);
}

img.backdrop {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    z-index: 0;
    object-fit: cover;
    mask-image: linear-gradient(
        to top,
        rgba(0, 0, 0, 0.05) 25%,
        rgba(0, 0, 0, 0.5) 100%
    );
}

img.poster {
    height: 150px;
    aspect-ratio: 2 / 3;
    border-radius: var(--border-radius-md);
    z-index: 1;
    object-fit: cover;
}

.details {
    z-index: 1;
    display: flex;
    flex-direction: column;
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
