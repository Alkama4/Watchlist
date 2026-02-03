<script setup>
import { ref } from 'vue';
import ModalBase from '@/components/modal/ModalBase.vue';
import { resolveImagePath } from '@/utils/imagePath';
import { numberFormatters, timeFormatters } from '@/utils/formatters';
import Tmdb from '@/assets/icons/tmdb.svg'

const season = ref({});
const title = ref({});
const modalRef = ref(null);

function open(seasonObject, titleName) {
    season.value = seasonObject;
    title.value = titleName;
    modalRef.value.open();
}

function calculateTotalSeasonRuntime(season) {
    let runtime = 0;
    for (let index = 0; index < season?.episodes.length; index++) {
        const element = season?.episodes[index];
        runtime += element?.runtime;
    }
    return runtime;
}

defineExpose({ open })
</script>

<template>
    <ModalBase ref="modalRef" :header="title">
        <div class="season">
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
    </ModalBase>
</template>

<style scoped>
.season {
    height: 100%;
    overflow: hidden;
    display: grid;
    grid-template-columns: auto 1fr;
    gap: var(--spacing-md);
}

.season-details {
    width: 400px;
    max-height: 100%;
    overflow: scroll;
    background-color: var(--c-bg-inner-section);
    padding: var(--spacing-md);
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
.episode:hover {
    background-color: var(--c-bg-inner-section);
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