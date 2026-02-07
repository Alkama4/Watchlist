<script setup>
import { resolveImagePath } from '@/utils/imagePath';
import { timeFormatters } from '@/utils/formatters';
import Tmdb from '@/assets/icons/tmdb.svg'
import { useRoute } from 'vue-router';

const route = useRoute();

defineProps({
    seasonInfo: {
        type: Object,
        required: true,
    }
})

defineEmits(['click'])
</script>

<template>
    <router-link class="season-card btn-text" :to="`/title/${route.params.title_id}?season=${seasonInfo.season_number}`">
        <img 
            :src="resolveImagePath(seasonInfo, '800', 'poster')"
            :alt="`Season poster: ${seasonInfo?.season_name}`"
            draggable="false"
        >

        <div class="details">
            <h5>{{ seasonInfo?.season_name }}</h5>
            <div class="detail-row">
                <Tmdb/>
                {{ seasonInfo?.tmdb_vote_average }}
                &bull;
                {{ timeFormatters.timestampToYear(seasonInfo?.episodes[0]?.air_date) }}
            </div>

            <div class="detail-row">
                {{ seasonInfo?.episodes?.length }} episodes
            </div>
        </div>
    </router-link>
</template>


<style scoped>
.season-card {
    width: 200px;
    display: inline-flex;
    flex-direction: column;
    text-decoration: none;
    position: relative;
    padding-right: var(--spacing-md);
}
.season-card:last-of-type {
    padding-right: 0;
}

img {
    border-radius: var(--border-radius-md);
    aspect-ratio: 2/3;
    object-fit: cover;
}

.button-row {
    margin-top: var(--spacing-sm);
    display: grid;
    grid-template-columns: 1fr auto;
    gap: var(--spacing-sm);
}
.button-row a {
    padding: var(--spacing-sm);
    width: 32px;
    box-sizing: border-box;
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


.indicator-wrapper {
    position: absolute;
    padding: var(--spacing-sm);
    top: 0;
    left: 0;
    height: var(--spacing-lg);
    width: calc(var(--spacing-lg) * 3 + var(--spacing-xs) * 2);
    --spacing-amount: 8px;
}
.indicator-wrapper:hover {
    --spacing-amount: calc(var(--spacing-lg) + var(--spacing-xs));
}

.indicator-circle {
    position: absolute;
    width: var(--spacing-lg);
    height: var(--spacing-lg);
    border-radius: 100px;
    display: flex;
    justify-content: center;
    align-items: center;
    font-weight: 500;
    color: var(--c-text);
    transition: left 0.2s var(--transition-ease-out);
}
.indicator-circle.watch-count {
    background-color: var(--c-positive);
    z-index: 50;
}
.indicator-circle.favourite {
    background-color: var(--c-favourite);
    z-index: 40;
}
.indicator-circle.watchlist {
    background-color: var(--c-accent);
    z-index: 30;
}

.indicator-circle.watch-count i,
.indicator-circle.watch-count i {
    font-size: var(--fs-3);
}
.indicator-circle.watchlist i {
    font-size: var(--fs-1);
}

.indicator-wrapper .indicator-circle:nth-child(1) {
    left: calc(var(--spacing-amount) * 0 + var(--spacing-sm));
}
.indicator-wrapper .indicator-circle:nth-child(2) {
    left: calc(var(--spacing-amount) * 1 + var(--spacing-sm));
}
.indicator-wrapper .indicator-circle:nth-child(3) {
    left: calc(var(--spacing-amount) * 2 + var(--spacing-sm));
}

</style>