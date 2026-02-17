<script setup>
import { computed } from 'vue';

const { seasons } = defineProps({
    seasons: {
        type: Array,
        required: true
    }
})

const getRatingOpacity = (rating) => {
    if (!rating || rating === 0) return 0.1; // Very faint for unrated
    
    const bucket = Math.floor(rating);
    
    // Mapping buckets to Opacity
    if (bucket >= 9) return 1;
    if (bucket >= 8) return 0.725;
    if (bucket >= 7) return 0.5;
    if (bucket >= 6) return 0.35;
    if (bucket >= 5) return 0.25;
    
    return 0.175; // Floor for anything below 5
}

const maxEpisodeCount = computed(() => {
    if (!seasons || seasons.length === 0) return 0;
    return Math.max(...seasons.map(season => season?.episodes?.length || 0));
})
</script>

<template>
    <div class="episode-map">
        <div class="season-row">
            <div class="tile"></div>
            <div v-for="num in maxEpisodeCount" class="tile label">
                E{{ num }}
            </div>
        </div>
        <div v-for="season in seasons" :key="season?.id" class="season-row">
            <div class="tile label">S{{ season?.season_number }}</div>
            <div 
                v-for="episode in season?.episodes" 
                :key="episode?.episode_id" 
                class="tile"
                :style="{ 
                    backgroundColor: `oklch(from var(--c-positive) calc(l + var(--l-step-1)) c h / ${getRatingOpacity(episode?.tmdb_vote_average)})
                    `,
                }"
                :title="`S${season?.season_number}E${episode?.episode_number}`"
            >
                {{ episode?.tmdb_vote_average.toFixed(1) }}
            </div>
        </div>
    </div>
</template>

<style scoped>
.episode-map {
    display: flex;
    flex-direction: column;
    gap: var(--spacing-xs-sm);
    overflow-x: auto;
}

.season-row {
    display: flex;
    align-items: center;
    flex-wrap: nowrap;
    gap: var(--spacing-xs);
}

.season-label {
    font-size: var(--fs-neg-1);
    font-weight: bold;
    min-width: 30px;
    color: var(--text-muted); /* Assuming you have a muted text var */
}

.episodes-container {
    display: flex;
    flex-wrap: wrap; 
    gap: 4px;
}

.tile {
    font-weight: 400;
    width: 28px; 
    min-width: 28px;
    padding: var(--spacing-sm);
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    border-radius: var(--border-radius-sm);
}
.tile.label {
    font-size: var(--fs-neg-1);
    color: var(--c-text-soft);
}
</style>