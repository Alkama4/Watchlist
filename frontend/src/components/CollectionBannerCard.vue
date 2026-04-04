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
        class="collection-banner-card no-deco"
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
            <h3>{{ tmdbCollection?.name }}</h3>
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
                
                <span>&bull;</span>

                <div class="stats-group">
                    <div>{{ tmdbCollection?.title_count }} Titles</div>
                    <span class="separator">&bull;</span>
                    <div>{{ timeFormatters.minutesToHrAndMin(tmdbCollection?.total_runtime) }}</div>
                </div>

                <span class="separator">&bull;</span>
                
                <div><Tmdb/> {{ tmdbCollection?.tmdb_vote_average }}</div>
            </div>
            <p>{{ tmdbCollection?.overview }}</p>
        </div>
    </router-link>
</template>

<style scoped>
.collection-banner-card {
    display: flex;
    position: relative;
    min-width: var(--collection-card-width);
    padding: var(--spacing-sm-md);
    gap: var(--spacing-md);
    box-sizing: border-box;
    height: 277.5px;
    align-items: center;

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
    opacity: 0.5;
    filter: brightness(0.5);
}

img.poster {
    height: 100%;
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

    h3 {
        margin: 0;
        display: -webkit-box;
        -webkit-line-clamp: 2;
        line-clamp: 2;
        -webkit-box-orient: vertical;
        overflow: hidden;
    }

    .stats,
    p {
        font-size: 0.9rem;
        color: var(--c-text-soft);
    }

    .stats {
        display: flex;
        gap: var(--spacing-xs) var(--spacing-sm);
        flex-wrap: wrap;
        align-items: center; /* Ensures bullets and text align */
        font-weight: 600;

        .stats-group {
            display: flex;
            gap: var(--spacing-sm);
            align-items: center;
        }

        div {
            white-space: nowrap;
        }
    }

    p {
        margin: 0;
        display: -webkit-box;
        -webkit-line-clamp: 6;
        line-clamp: 6;
        -webkit-box-orient: vertical;
        overflow: hidden;
    }
}

@media(max-width: 768px) {
    .stats {
        /* This hides the bullets directly inside .stats (the ones flanking the group) */
        & > .separator {
            display: none;
        }

        .stats-group {
            /* Forces the group to take its own line */
            flex-basis: 100%;
            /* Optional: adjust order if you want it specifically below everything */
            order: 2; 
        }
    }
}
</style>
