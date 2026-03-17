<script setup>
import { computed, onMounted, onUnmounted, ref } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { getTitleImageUrl } from '@/utils/imagePath';
import { numberFormatters, timeFormatters } from '@/utils/formatters';
import Tmdb from '@/assets/icons/tmdb.svg';
import ModalImages from '@/components/modal/ModalImages.vue';
import { ChevronLeft, Eye, EyeSlash, Image, Images } from '@boxicons/vue';
import { adjustWatchCount } from '@/utils/titleActions';
import LoadingButton from '@/components/LoadingButton.vue';
import { resolveSeasonWatchCount } from '@/utils/titleUtils';
import WatchCountButtons from '@/components/WatchCountButtons.vue';
import KebabMenu from '@/components/KebabMenu.vue';

const props = defineProps({
    titleDetails: {
        type: Object,
        required: true
    },
    tmdbBaseUrl: {
        type: String,
        required: true
    }
});

const route = useRoute();
const router = useRouter();
const ImagesModal = ref(null);
const waitingFor = ref({});

const activeSeason = computed(() => {
    const seasonNumber = Number(route.query.season);
    // Find the season in the prop data that matches the URL query
    return props.titleDetails?.seasons?.find(s => s.season_number === seasonNumber) || null;
});

const totalRuntime = computed(() => {
    if (!activeSeason.value?.episodes) return 0;
    return activeSeason.value.episodes.reduce((acc, ep) => acc + (ep.runtime || 0), 0);
});

const areSeasonSpoilersVisible = computed(() => {
    if (!activeSeason.value?.episodes) return false;

    const unwatchedEpisodes = activeSeason.value.episodes.filter(
        ep => !(ep.user_details?.watch_count > 0)
    );

    return unwatchedEpisodes.some(episode => isEpisodeSpoilerVisible(episode));
});

// 2. Updated Toggle Logic
function toggleSeasonSpoilers() {
    if (!activeSeason.value?.episodes) return;
    // If they are currently visible, we want to hide them (false), and vice-versa
    const targetState = !areSeasonSpoilersVisible.value; 
    activeSeason.value.episodes.forEach(episode => {
        if (!(episode.user_details?.watch_count > 0)) {
            episode.spoilersVisible = targetState;
        }
    });
}

// 3. Updated Helper Name & Logic
function isEpisodeSpoilerVisible(episode) {
    return !!(episode?.spoilersVisible || episode?.user_details?.watch_count > 0);
}

// 4. Updated Obfuscation Parameter
function getObfuscatedText(text, isVisible) {
    if (!text) return '';
    if (isVisible) return text; // Logic flipped: return text if visible

    const charPool = "eeeettttaaaoooinnnsssrrrhhhddllluuuccmmffyywwggppbvkxqjzeeeeettttaaaoooinnnsssrrrhhhddllluuuccmmffyywwggpp";
    let seed = 0;
    for (let i = 0; i < text.length; i++) {
        seed = ((seed << 5) - seed) + text.charCodeAt(i);
        seed = seed & seed;
    }

    return text.split('').map((char, index) => {
        if (/[ \n\t.,!?;:]/.test(char)) return char;
        const x = Math.sin(seed + index + char.charCodeAt(0)) * 10000;
        const pseudoRandom = Math.floor(Math.abs(x));
        return charPool[pseudoRandom % charPool.length];
    }).join('');
}

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
            <button class="btn-text btn-even-padding" @click="handleBack">
                <ChevronLeft/>
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
                <div class="meta-row">
                    <span>
                        <Tmdb/>
                        {{ numberFormatters.formatNumberToLocale(activeSeason?.tmdb_vote_average) }}
                    </span>
                    |
                    <span>
                        {{ timeFormatters.timestampToYear(activeSeason?.episodes?.[0]?.air_date) }}
                        <template v-if="
                            activeSeason?.episodes?.length > 1 && 
                            timeFormatters.timestampToYear(activeSeason?.episodes?.[0]?.air_date) !== 
                            timeFormatters.timestampToYear(activeSeason?.episodes?.[activeSeason.episodes.length - 1]?.air_date)
                        ">
                            - {{ timeFormatters.timestampToYear(activeSeason?.episodes?.[activeSeason.episodes.length - 1]?.air_date) }}
                        </template>
                    </span>
                    |
                    <span>{{ activeSeason?.episodes?.length }} episodes</span>
                    |
                    <span>{{ timeFormatters.minutesToHrAndMin(totalRuntime) }}</span>
                </div>
                <p>{{ activeSeason?.overview }}</p>
                <div class="actions">
                    <div class="primary-actions">
                        <WatchCountButtons
                            :watchCount="resolveSeasonWatchCount(activeSeason)"
                            :title="titleDetails"
                            :season="activeSeason"
                        />

                        <component
                            :is="areSeasonSpoilersVisible ? Eye : EyeSlash"
                            class="btn btn-text btn-even-padding"
                            @click="toggleSeasonSpoilers"
                        />
                    </div>

                    <KebabMenu
                        :menuItems="[
                            { iconComponent: Images, label: 'Manage Images', action: ImagesModal?.open }
                        ]"
                    />
                </div>
            </div>
            <div class="episodes-wrapper">
                <div v-for="episode in activeSeason?.episodes" :key="episode.episode_id" class="episode">
                    <div
                        class="episode-backdrop-wrapper"
                        :class="{
                            'btn-text unwatched': !(episode?.user_details?.watch_count > 0),
                            'spoilers-visible': isEpisodeSpoilerVisible(episode)
                        }"
                        @click="episode.spoilersVisible = !isEpisodeSpoilerVisible(episode)"
                    >
                        <img 
                            :src="getTitleImageUrl(episode, '800', 'backdrop')"
                            :alt="`Episode backdrop: ${episode?.episode_number}. ${episode?.episode_name}`"
                            class="episode-backdrop"
                        >
                        <Eye v-if="isEpisodeSpoilerVisible(episode)" size="lg" class="eye-icon" />
                        <EyeSlash v-else size="lg" class="eye-icon" />
                    </div>
                    <div class="details">
                        <h4>
                            <span class="number">{{ episode?.episode_number }}. </span>
                            <span class="name">
                                {{ getObfuscatedText(episode?.episode_name, isEpisodeSpoilerVisible(episode)) }}
                            </span>
                        </h4>
                        <div>
                            {{ timeFormatters.minutesToHrAndMin(episode.runtime) }}
                            &bull;
                            <Tmdb/>
                            {{ numberFormatters.formatNumberToLocale(episode.tmdb_vote_average) }}
                            ({{ numberFormatters.formatCompactNumber(episode.tmdb_vote_count) }} votes)
                            &bull;
                            {{ timeFormatters.timestampToFullDate(episode.air_date) }}
                        </div>
                        <p>{{ getObfuscatedText(episode.overview, isEpisodeSpoilerVisible(episode)) }}</p>

                        <div class="controls">
                            <WatchCountButtons
                                :watchCount="episode?.user_details?.watch_count"
                                :title="titleDetails"
                                :episode="episode"
                            />
                        </div>
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
            :tmdbBaseUrl="tmdbBaseUrl"
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
    /* padding-bottom: var(--spacing-lg); */
    border-radius: var(--border-radius-lg);

    img.season-poster {
        width: 100%;
        aspect-ratio: 2/3;
        background-color: var(--c-bg-level-2);
        object-fit: cover;
        border-radius: var(--border-radius-lg);
    }
    .meta-row {
        display: flex;
        flex-direction: row;
        align-items: center;
        column-gap: var(--spacing-sm-md);
        row-gap: var(--spacing-xs);
        font-weight: 600;
        flex-wrap: wrap;
    }
    .actions {
        display: flex;
        gap: var(--spacing-sm);
        justify-content: space-between;

        .primary-actions {
            display: flex;
            gap: var(--spacing-sm);
        }
    }
}

.episodes-wrapper {
    display: flex;
    flex-direction: column;
    max-height: 100%;
    /* gap: var(--spacing-lg); */
}

.episode {
    display: grid;
    grid-template-columns: auto 1fr;
    gap: var(--spacing-md-lg);
    max-width: 1400px;
    margin: var(--spacing-sm-md);
    border-radius: var(--border-radius-lg);
    transition: background-color 0.1s ease-out;

    .episode-backdrop-wrapper {
        position: relative;
        width: 400px;
        aspect-ratio: 16/9;
        background-color: var(--c-bg-level-1);
        border-radius: var(--border-radius-md);
        overflow: hidden;

        .eye-icon {
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translateX(-50%) translateY(-50%);
            opacity: 0;
            transition: opacity 0.1s var(--transition-ease-out);
        }
        
        img.episode-backdrop {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            object-fit: cover;
            transition: filter 0.1s var(--transition-ease-out);
        }

        &.unwatched {
            user-select: none;

            img.episode-backdrop {
                filter: blur(var(--blur-heavy));
            }
            
            .eye-icon {
                opacity: 1;
            }
            &.spoilers-visible:not(:hover) .eye-icon {
                opacity: 0;
            }

            &.spoilers-visible img.episode-backdrop {
                filter: blur(0px) opacity(1);
            }
            &:hover img.episode-backdrop {
                filter: blur(var(--blur-heavy)) opacity(0.66);
            }
            &.spoilers-visible:hover img.episode-backdrop {
                filter: blur(0px) opacity(0.66);
            }
        }
    }

    .details {
        display: flex;
        flex-direction: column;
        justify-content: center;
        gap: var(--spacing-sm);
    
        h4 {
            -webkit-line-clamp: 1;
            line-clamp: 1;
        }
        p {
            -webkit-line-clamp: 4;
            line-clamp: 4;
        }
        h4,
        p {
            margin: 0;
            display: -webkit-box;
            -webkit-box-orient: vertical;
            overflow: hidden;
        }

        .controls {
            margin-top: var(--spacing-sm);
        }
    }
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