<script setup>
import { resolveImagePath } from '@/utils/imagePath';
import { timeFormatters } from '@/utils/formatters';
import Tmdb from '@/assets/icons/tmdb.svg'

defineProps({
    titleInfo: {
        type: Object,
        required: true,
    }
})
</script>

<template>
    <router-link :to="`/title/${titleInfo.title_id}`">
        <img 
            :src="resolveImagePath(
                '800',
                titleInfo?.default_poster_image_path,
                titleInfo?.user_details?.chosen_poster_image_path
            )"
            :alt="`${titleInfo?.type === 'tv' ? 'TV show' : 'Movie'} poster: ${titleInfo?.name}`"
        >
        <div class="details">
            <h5>{{ titleInfo?.name }}</h5>
            <div class="detail-row">
                <Tmdb/>
                {{ titleInfo?.tmdb_vote_average }}
                &bull;
                {{ timeFormatters.timestampToYear(titleInfo?.release_date) }}
            </div>
            <div class="detail-row">
                <template v-if="titleInfo?.type === 'tv'">
                    {{ titleInfo?.show_season_count }} seasons,
                    {{ titleInfo?.show_episode_count }} episodes
                </template>
                <template v-else>{{ timeFormatters.minutesToHrAndMin(titleInfo?.movie_runtime) }}</template>
            </div>
        </div>
        <div v-if="titleInfo?.user_details?.watch_count" class="watch-count-marker">
            <template v-if="titleInfo?.user_details?.watch_count >= 2">
                {{ titleInfo?.user_details?.watch_count }}
            </template>
            <i v-else class="bx bx-check"></i>
        </div>
    </router-link>
</template>


<style scoped>
a {
    width: 200px;
    display: flex;
    flex-direction: column;
    text-decoration: none;
    position: relative;
}

img {
    border-radius: var(--border-radius-md);
    aspect-ratio: 2/3;
    object-fit: cover;
}

.details {
    display: flex;
    flex-direction: column;
    gap: var(--spacing-xs);
    margin-top: var(--spacing-xs-sm);
}

h5 {
    margin: 0;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

.detail-row {
    display: flex;
    align-items: center;
    gap: var(--spacing-xs);
    color: var(--c-text-3);
    font-size: var(--fs-neg-1);
}

.watch-count-marker {
    position: absolute;
    top: var(--spacing-sm);
    left: var(--spacing-sm);
    background-color: var(--c-positive);
    width: var(--spacing-lg);
    height: var(--spacing-lg);
    border-radius: 100px;
    display: flex;
    justify-content: center;
    align-items: center;
    font-weight: 500;
    color: var(--c-text);
}
.watch-count-marker i {
    font-size: var(--fs-3);
}
</style>