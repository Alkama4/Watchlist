<script setup>
import { computed, onMounted, onUnmounted, ref } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { getTitleImageUrl } from '@/utils/imagePath';
import { numberFormatters, timeFormatters } from '@/utils/formatters';
import Tmdb from '@/assets/icons/tmdb.svg';
import ModalImages from '../modal/ModalImages.vue';

const props = defineProps({
    titleDetails: {
        type: Object,
        required: true
    }
});

const route = useRoute();
const router = useRouter();
const ImagesModal = ref(null);

const activeSeason = computed(() => {
    const seasonNumber = Number(route.query.season);
    // Find the season in the prop data that matches the URL query
    return props.titleDetails?.seasons?.find(s => s.season_number === seasonNumber) || null;
});

const totalRuntime = computed(() => {
    if (!activeSeason.value?.episodes) return 0;
    return activeSeason.value.episodes.reduce((acc, ep) => acc + (ep.runtime || 0), 0);
});

const handleBack = () => {
    // If we came from the overview of the SAME title
    const previousPath = window.history.state.back;
    const isFromOverview = previousPath && !previousPath.includes('season=');

    if (isFromOverview) {
        router.back();
    } else {
        // Fallback: Strip the query params to go back to the "plain" title page
        router.push({ path: route.path, query: {} });
    }
};

function next() {
    const nextSeason = Number(route.query.season) + 1;
    const hasNextSeason = props.titleDetails.seasons.find(s => s.season_number === nextSeason);

    if (hasNextSeason) {
        router.push({ path: route.path, query: { season: nextSeason } });
    } else {
        router.push({ path: route.path, query: { season: 1 } });
    }
}
function prev() {
    const prevSeason = Number(route.query.season) - 1;
    const hasPrevSeason = props.titleDetails.seasons.find(s => s.season_number === prevSeason);

    if (hasPrevSeason) {
        router.push({ path: route.path, query: { season: prevSeason } });
    } else {
        const seasonNumbers = props.titleDetails.seasons.map(s => s.season_number);
        const maxSeason = Math.max(...seasonNumbers);
        
        router.push({ path: route.path, query: { season: maxSeason } });
    }
}
function handleKeydown(e) {
    if (e.key === 'ArrowRight') {
        next();
    } else if (e.key === 'ArrowLeft') {
        prev();
    } else if (/^\d$/.test(e.key)) { 
        const targetSeason = Number(e.key);
        const exists = props.titleDetails.seasons.find(s => s.season_number === targetSeason);
        if (exists) {
            router.push({ path: route.path, query: { season: targetSeason } });
        }
    }
}
onMounted(() => {
    window.addEventListener('keydown', handleKeydown);
});

onUnmounted(() => {
    window.removeEventListener('keydown', handleKeydown);
});
</script>

<template>
    <div class="season-details-page">
        <div class="back-button-row layout-contained layout-spacing-top">
            <button class="btn-text btn-square" @click="handleBack">
                <i class="bx bx-chevron-left"></i>
                <span>Back to Overview</span>
            </button>
        </div>
        <div v-if="activeSeason" :key="activeSeason.season_id" class="season layout-contained layout-spacing-bottom">
            <div class="season-details">
                <img 
                    :src="getTitleImageUrl(activeSeason, '800', 'poster')"
                    :alt="`Season poster: ${activeSeason?.season_name}`"
                    class="season-poster"
                >
                <h3>{{ activeSeason?.season_name }}</h3>
                <div>
                    <Tmdb/>
                    {{ activeSeason?.tmdb_vote_average }}
                    &bull;
                    {{ activeSeason?.episodes?.length }} episodes
                    &bull;
                    {{ timeFormatters.minutesToHrAndMin(totalRuntime) }}
                </div>
                <p>{{ activeSeason?.overview }}</p>
                <div class="actions">
                    <i
                        class="bx bxs-image btn btn-text btn-square"
                        @click="ImagesModal.open()"
                    ></i>
                </div>
            </div>
            <div class="episodes-wrapper">
                <div v-for="episode in activeSeason?.episodes" class="episode">
                    <img 
                        :src="getTitleImageUrl(episode, '800', 'backdrop')"
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
        <div v-if="titleDetails?.seasons?.length >= 2" class="season-buttons">
            <router-link
                v-for="season in titleDetails?.seasons"
                :to="`/title/${titleDetails?.title_id}?season=${season.season_number}`"
                :class="{'btn-primary': route.query.season == season.season_number}"
                class="btn no-deco"
            >
                {{ season.season_name }}
            </router-link>
        </div>

        <ModalImages
            ref="ImagesModal"
            :seasonId="activeSeason?.season_id"
            :userDetails="activeSeason?.user_details"
        />
    </div>
</template>

<style scoped>
.back-button-row {
    margin-bottom: var(--spacing-md);
}
.back-button-row button {
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
    background-color: var(--c-bg-level-1);
    padding: var(--spacing-md);
    padding-bottom: var(--spacing-lg);
    border-radius: var(--border-radius-lg);
}
.season-details img.season-poster {
    width: 100%;
    aspect-ratio: 2/3;
    background-color: var(--c-bg-level-2);
    object-fit: cover;
    border-radius: var(--border-radius-lg);
}

.episodes-wrapper {
    display: flex;
    flex-direction: column;
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
    aspect-ratio: 16/9;
    background-color: var(--c-bg-level-1);
    object-fit: cover;
    border-radius: var(--border-radius-md);
}
.episode h4 {
    margin-top: 0;
    margin-bottom: var(--spacing-sm);
}
.episode p {
    margin: var(--spacing-sm) 0;
}


.season-buttons {
    position: fixed;
    bottom: var(--spacing-lg);
    left: 50%;
    transform: translateX(-50%);
    max-width: 90vw;
    overflow-x: auto;

    background: var(--c-bg-opaque-base);
    backdrop-filter: blur(var(--blur-heavy));
    border: 1px solid var(--c-border);

    padding: var(--spacing-sm-md);
    border-radius: var(--border-radius-lg);

    display: flex;
    gap: var(--spacing-sm);
}
.season-buttons .btn {
    white-space: nowrap;
    padding: var(--spacing-sm-md) var(--spacing-md-lg);
}
</style>