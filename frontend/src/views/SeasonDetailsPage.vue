<script setup>
import { onMounted, ref } from 'vue';
import { resolveImagePath } from '@/utils/imagePath';
import { numberFormatters, timeFormatters } from '@/utils/formatters';
import { useRoute } from 'vue-router';
import { fastApi } from '@/utils/fastApi';
import Tmdb from '@/assets/icons/tmdb.svg'
import router from '@/router';

const route = useRoute();
const season = ref({});

async function fetchTitleDetails() {
    const title_id = route.params.title_id;
    const season_id = route.params.season_id;
    
    const titleDetails = await fastApi.titles.getById(title_id)
    season.value = titleDetails?.seasons.find((season) => {
        if (season.season_id == season_id) return season;
    })
}

function calculateTotalSeasonRuntime(season) {
    let runtime = 0;
    for (let index = 0; index < season?.episodes?.length; index++) {
        const element = season?.episodes[index];
        runtime += element?.runtime;
    }
    return runtime;
}

const handleBack = () => {
    const titlePath = `/title/${route.params.title_id}`;
    const previousPath = window.history.state.back;

    // If the history shows we actually came from that Title page
    if (previousPath && previousPath.includes(titlePath)) {
        router.back();
    } else {
        // Fallback: Just navigate normally
        router.push(titlePath);
    }
};

onMounted(async () => {
    await fetchTitleDetails();
})
</script>

<template>
    <div class="navigation-row layout-contained layout-spacing-top">
        <button class="btn-text no-deco" @click="handleBack">
            <i class="bx bx-chevron-left"></i>
            <span>Back to Title</span>
        </button>
    </div>
    <div class="season layout-contained layout-spacing-bottom">
        <div class="season-details">
            <img 
                :src="resolveImagePath(season, '800', 'poster')"
                :alt="`Season poster: ${season?.season_name}`"
                class="season-poster"
            >
            <h3>{{ season?.season_name }}</h3>
            <div>
                <Tmdb/>
                {{ season?.tmdb_vote_average }}
                &bull;
                {{ season?.episodes?.length }} episodes
                &bull;
                {{ timeFormatters.minutesToHrAndMin(calculateTotalSeasonRuntime(season)) }}
            </div>
            <p>{{ season?.overview }}</p>
        </div>
        <div class="episodes-wrapper">
            <div v-for="episode in season?.episodes" class="episode">
                <img 
                    :src="resolveImagePath(episode, '800', 'backdrop')"
                    :alt="`Episode backdrop: ${episode?.episode_number}. ${episode?.episode_name}`"
                    class="episode-backdrop"
                >
                <div>
                    <h4>{{ episode?.episode_number }}. {{ episode?.episode_name }}</h4>
                    <div>
                        {{ timeFormatters.minutesToHrAndMin(episode.runtime) }}
                        &bull;
                        <Tmdb/>
                        {{ episode.tmdb_vote_average }}
                        ({{ numberFormatters.formatCompactNumber(episode.tmdb_vote_count) }} votes)
                        &bull;
                        {{ timeFormatters.timestampToFullDate(episode.air_date) }}
                    </div>
                    <p>{{ episode.overview }}</p>
                </div>
            </div>
        </div>
    </div>
</template>

<style scoped>
.navigation-row {
    margin-bottom: var(--spacing-md);
}
.navigation-row button {
    font-size: var(--fs-0);
}

.season {
    height: 100%;
    overflow: hidden;
    display: grid;
    grid-template-columns: auto 1fr;
    gap: var(--spacing-md);
}

.season-details {
    width: 400px;
    height: fit-content;
    overflow: scroll;
    background-color: var(--c-bg-section);
    padding: var(--spacing-md);
    padding-bottom: var(--spacing-lg);
    border-radius: var(--border-radius-lg);
}
.season-details img.season-poster {
    width: 100%;
    border-radius: var(--border-radius-lg);
}

.episodes-wrapper {
    display: flex;
    flex-direction: column;
    overflow-y: scroll;
    max-height: 100%;
}

.episode {
    display: grid;
    grid-template-columns: auto 1fr;
    gap: var(--spacing-md);
    max-width: 1400px;
    padding: var(--spacing-sm-md);
    border-radius: var(--border-radius-lg);
    transition: background-color 0.1s ease-out;
}
.episode img.episode-backdrop {
    width: 400px;
    border-radius: var(--border-radius-md);
}
.episode h4 {
    margin-top: 0;
    margin-bottom: var(--spacing-sm);
}
.episode p {
    margin: var(--spacing-sm) 0;
}
</style>