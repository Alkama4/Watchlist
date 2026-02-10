<script setup>
import { getTitleImageUrl } from '@/utils/imagePath';
import { timeFormatters } from '@/utils/formatters';
import Tmdb from '@/assets/icons/tmdb.svg'

defineProps({
    titleDetails: {
        type: Object,
        required: true
    }
})
</script>

<template>
    <div class="carousel layout-contained">
        <h4>Seasons</h4>
        <div class="seasons-wrapper">
            <router-link
                v-for="season in titleDetails?.seasons"
                :key="season?.season_id"
                class="season-card btn btn-square no-deco"
                :to="`/title/${titleDetails?.title_id}?season=${season?.season_number}`"
            >
                <img 
                    :src="getTitleImageUrl(season, '800', 'poster')"
                    :alt="`Season poster: ${season?.season_name}`"
                    class="poster"
                >

                <div class="details">
                    <h4>{{ season?.season_name }}</h4>
                    <div class="detail-row">
                        <Tmdb/>
                        {{ season?.tmdb_vote_average }}
                        &bull;
                        {{ timeFormatters.timestampToYear(season?.episodes[0]?.air_date) }}
                    </div>

                    <div class="detail-row">
                        {{ season?.episodes?.length }} episodes
                    </div>
                </div>
            </router-link>
        </div>
    </div>
</template>

<style scoped>
.seasons-wrapper {
    display: flex;
    flex-direction: column;
    gap: var(--spacing-sm-md);
}

.season-card {
    gap: var(--spacing-sm-md);
    border-radius: var(--border-radius-md);
    justify-content: flex-start;
    font-weight: 400;
}

img.poster {
    height: 100px;
    border-radius: var(--border-radius-sm);
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
}

h4 {
    margin: 0;
    margin-bottom: var(--spacing-sm);
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

.detail-row {
    display: flex;
    align-items: center;
    gap: var(--spacing-xs);
    font-size: var(--fs-neg-1);
}

</style>