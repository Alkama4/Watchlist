<script setup>
import { getTitleImageUrl } from '@/utils/imagePath';
import Tmdb from '@/assets/icons/tmdb.svg';
import { numberFormatters, timeFormatters } from '@/utils/formatters';

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
        class="collection-banner-card btn btn-even-padding no-deco"
    >
        <img
            :src="getTitleImageUrl(tmdbCollection, 400, 'poster')"
            alt=""
            class="poster"
        />

        <div class="details">
            <h4>{{ tmdbCollection?.name }}</h4>

            <div class="meta-row">
                <span class="meta-item">
                    {{ timeFormatters.timestampToYear(tmdbCollection?.first_release_date) }}
                    <template v-if="
                        timeFormatters.timestampToYear(tmdbCollection?.first_release_date)
                        != timeFormatters.timestampToYear(tmdbCollection?.last_release_date)
                    ">
                        - {{ timeFormatters.timestampToYear(tmdbCollection?.last_release_date) }}
                    </template>
                </span>

                <span class="seperator">&bull;</span>

                <span class="meta-item">
                    {{ tmdbCollection?.title_count }} Titles
                </span>

                <span class="seperator">&bull;</span>

                <span class="meta-item">
                    {{ timeFormatters.minutesToHrAndMin(tmdbCollection?.total_runtime) }}
                </span>

                <span class="seperator">&bull;</span>

                <span class="meta-item">
                    <Tmdb class="tmdb-icon"/>
                    {{ numberFormatters.formatNumberToLocale(tmdbCollection?.tmdb_vote_average) }}
                </span>
            </div>

            <p class="overview" :class="{'unavailable': !tmdbCollection?.overview}">
                {{ tmdbCollection?.overview || "No overview available." }}
            </p>
        </div>
    </router-link>
</template>

<style scoped>
.collection-banner-card {
    position: relative;
    display: flex;
    flex-direction: row;
    gap: 0;
    min-width: var(--collection-card-width);
    padding: 0;
    text-align: left;
    font-weight: 400;
    overflow: hidden;
    border-radius: var(--border-radius-md-lg);
    transition: transform 0.2s ease, background-color 0.2s ease;
}

img.poster {
    height: 144px;
    aspect-ratio: 2 / 3;
    object-fit: cover;
    flex-shrink: 0;
}

.details {
    display: flex;
    flex-direction: column;
    flex-grow: 1;
    min-width: 0; /* Prevents text overflow from pushing flex layout */
    gap: var(--spacing-xs);
    padding-inline: var(--spacing-md);

    h4 {
        margin: 0;
        margin-bottom: var(--spacing-xs);
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        display: flex;
        gap: var(--spacing-sm);
        align-items: center;
    }

    .meta-row {
        display: flex;
        flex-wrap: wrap;
        align-items: center;
        gap: var(--spacing-xs);
        font-size: var(--fs-neg-2);
        color: var(--c-text-soft);
        font-weight: 600;

        .meta-item {
            display: flex;
            align-items: center;
            gap: 4px;
        }
    }

    .overview {
        margin: 0;
        font-size: var(--fs-neg-2);
        color: var(--c-text-soft);
        display: -webkit-box;
        -webkit-line-clamp: 2;
        line-clamp: 2;
        -webkit-box-orient: vertical;
        overflow: hidden;
        line-height: 1.4;

        &.unavailable {
            color: var(--c-text-subtle);
            font-style: italic;
        }
    }
}
</style>
