<script setup>
import { resolveImagePath } from '@/utils/imagePath';
import { timeFormatters } from '@/utils/formatters';

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
            <h3>{{ titleInfo?.name }}</h3>
            <div class="detail-row">
                {{ titleInfo?.tmdb_vote_average }}
                &bull;
                {{ timeFormatters.timestampToYear(titleInfo?.release_date) }}
            </div>
            <div class="detail-row">
                <span>{{ timeFormatters.minutesToHrAndMin(titleInfo?.movie_runtime) }}</span>
            </div>
        </div>
    </router-link>
</template>


<style scoped>
a {
    width: 200px;
    display: flex;
    flex-direction: column;
    text-decoration: none;
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

h3 {
    margin: 0;
}

.detail-row {
    display: flex;
    align-items: center;
    gap: var(--spacing-xs);
    color: var(--c-text-3);
    font-size: var(--fs-neg-1);
}
</style>