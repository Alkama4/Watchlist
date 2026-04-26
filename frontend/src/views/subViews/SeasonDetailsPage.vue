<script setup>
import { computed, onMounted, onUnmounted, ref } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { getTitleImageUrl } from '@/utils/imagePath';
import { numberFormatters, timeFormatters } from '@/utils/formatters';
import Tmdb from '@/assets/icons/tmdb.svg';
import ModalImages from '@/components/modal/ModalImages.vue';
import { ChevronLeft, Eye, EyeSlash, Images, ListPlay } from '@boxicons/vue';
import { resolveSeasonWatchCount } from '@/utils/titleUtils';
import WatchCountButtons from '@/components/WatchCountButtons.vue';
import KebabMenu from '@/components/KebabMenu.vue';
import VideoAssetListing from '@/components/VideoAssetListing.vue';
import ResponsiveOverlay from '@/components/ResponsiveOverlay.vue';

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
const videoAssetOverlay = ref(null);
const videoAssetEpisode = ref({});

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

function isEpisodeSpoilerVisible(episode) {
    return !!(episode?.spoilersVisible || episode?.user_details?.watch_count > 0);
}


function openEpisodeVideoAssetListing(episode) {''
    videoAssetEpisode.value = episode;
    videoAssetOverlay.value.open();
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
        <div class="top-button-row layout-contained layout-spacing-top">
            <button class="btn-text btn-even-padding" @click="handleBack">
                <ChevronLeft/>
                <span>Back to Overview</span>
            </button>

            <div class="mobile-only">
                <KebabMenu
                    roundButton
                    :menuItems="[
                        { iconComponent: Images, label: 'Manage Images', action: ImagesModal?.open }
                    ]"
                />
            </div>
        </div>
        <div v-if="activeSeason" :key="activeSeason.season_id" class="season layout-contained layout-spacing-bottom">
            <div class="season-details">
                <img 
                    :src="getTitleImageUrl(activeSeason, '800', 'poster')"
                    :key="getTitleImageUrl(activeSeason, '800', 'poster')"
                    :alt="`Season poster: ${activeSeason?.season_name}`"
                    class="season-poster"
                >
                <h3>{{ activeSeason?.season_name }}</h3>
                <div class="meta-row">
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
                    <span class="seperator">|</span>
                    <span>{{ activeSeason?.episodes?.length }} episodes</span>
                    <span class="seperator">|</span>
                    <span>{{ timeFormatters.minutesToHrAndMin(totalRuntime) }}</span>
                    <span class="seperator">|</span>
                    <span>
                        <Tmdb/>
                        {{ numberFormatters.formatNumberToLocale(activeSeason?.tmdb_vote_average) }}
                    </span>
                </div>
                <p :class="{'unavailable': !activeSeason?.overview}">{{ activeSeason?.overview || 'No overview available.' }}</p>
                <div class="actions">
                    <WatchCountButtons
                        :watchCount="resolveSeasonWatchCount(activeSeason)"
                        :title="titleDetails"
                        :season="activeSeason"
                    />

                    <button
                        class="btn-even-padding btn-mobile-icon-padding"
                        @click="toggleSeasonSpoilers"
                        :disabled="resolveSeasonWatchCount(activeSeason)"
                        :title="resolveSeasonWatchCount(activeSeason) 
                            ? 'All episodes watched - no spoilers to show.' 
                            : (areSeasonSpoilersVisible ? 'Hide spoilers' : 'Show spoilers')"
                    >
                        <component :is="areSeasonSpoilersVisible ? EyeSlash : Eye"/>
                    </button>
                    <div class="desktop-only">
                        <KebabMenu
                            horizontalDots
                            :menuItems="[
                                { iconComponent: Images, label: 'Manage Images', action: ImagesModal?.open }
                            ]"
                        />
                    </div>
                </div>
            </div>

            <h3 class="mobile-only">Episodes</h3>
            
            <div class="episodes-wrapper">
                <div
                    v-for="episode in activeSeason?.episodes"
                    :key="episode.episode_id"
                    class="episode"
                >
                    <div
                        class="episode-backdrop-wrapper"
                        :class="{
                            'unwatched': !(episode?.user_details?.watch_count > 0),
                            'spoilers-visible': isEpisodeSpoilerVisible(episode)
                        }"
                    >
                        <img 
                            :src="getTitleImageUrl(episode, '800', 'backdrop')"
                            :alt="`Episode backdrop: ${episode?.episode_number}. ${episode?.episode_name}`"
                            class="episode-backdrop"
                        >
                        <EyeSlash size="lg" class="eye-icon" />
                    </div>
                    <div class="details" :class="{'spoilers-hidden': !isEpisodeSpoilerVisible(episode)}">
                        <h4>
                            <span class="number">{{ episode?.episode_number }}. </span>
                            <span class="name">
                                {{ episode?.episode_name }}
                            </span>
                        </h4>
                        <div class="meta-row">
                            <span>
                                {{ timeFormatters.minutesToHrAndMin(episode.runtime) }}
                            </span>
                            <span class="seperator">&bull;</span>
                            <span>
                                {{ timeFormatters.timestampToFullDate(episode.air_date) }}
                            </span>
                            <span class="seperator">&bull;</span>
                            <span>
                                <Tmdb/>
                                {{ numberFormatters.formatNumberToLocale(episode.tmdb_vote_average) }}
                                ({{ numberFormatters.formatCompactNumber(episode.tmdb_vote_count) }} votes)
                            </span>
                        </div>
                        <div class="overview-wrapper">
                            <span class="overview">
                                {{ episode.overview }}
                            </span>
                        </div>
                        <!-- <p>{{ isEpisodeSpoilerVisible(episode) ? episode.overview : 'Episode overview hidden.' }}</p> -->

                        <div class="controls">
                            <WatchCountButtons
                                :watchCount="episode?.user_details?.watch_count"
                                :title="titleDetails"
                                :episode="episode"
                            />
                            <button
                                class="btn-even-padding btn-mobile-icon-padding"
                                @click="episode.spoilersVisible = !isEpisodeSpoilerVisible(episode)"
                                :disabled="episode?.user_details?.watch_count"
                                :title="episode?.user_details?.watch_count 
                                    ? 'Episode watched - no spoilers to show.' 
                                    : (isEpisodeSpoilerVisible(episode) ? 'Hide spoilers' : 'Show spoilers')"
                            >
                                <component :is="isEpisodeSpoilerVisible(episode) ? EyeSlash : Eye"/>
                            </button>
                            <button
                                v-if="episode?.video_assets"
                                class="btn-even-padding btn-mobile-icon-padding"
                                @click="openEpisodeVideoAssetListing(episode)"
                            >
                                <ListPlay/>
                            </button>
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

        <ResponsiveOverlay ref="videoAssetOverlay" header="Video Assets">
            <VideoAssetListing
                :videoAssets="videoAssetEpisode?.video_assets"
                :title="titleDetails"
                :season="activeSeason"
                :episode="videoAssetEpisode"
            />
        </ResponsiveOverlay>
    </div>
</template>

<style scoped>
.season-details-page {
    --spoiler-transition-setup: 0.35s var(--transition-ease-out-str);
}

.top-button-row {
    margin-bottom: var(--spacing-md);
    display: flex;
    justify-content: space-between;
}
.top-button-row button {
    font-size: var(--fs-0);
}

.season {
    height: 100%;
    overflow: hidden;
    display: grid;
    grid-template-columns: auto 1fr;
    gap: var(--spacing-md);
    padding-bottom: 32px;
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
    }

    .unavailable {
        color: var(--c-text-subtle);
        font-style: italic;
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
    column-gap: var(--spacing-md-lg);
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
            transition: opacity var(--spoiler-transition-setup);
        }
        
        img.episode-backdrop {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            object-fit: cover;
            transition: filter var(--spoiler-transition-setup);
        }

        &.unwatched {
            user-select: none;

            img.episode-backdrop {
                filter: blur(var(--blur-heavy));
            }
            
            .eye-icon {
                opacity: 0.5;
            }
            &.spoilers-visible .eye-icon {
                opacity: 0;
            }

            &.spoilers-visible img.episode-backdrop {
                filter: blur(0px) opacity(1);
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
        .overview-wrapper {
            -webkit-line-clamp: 4;
            line-clamp: 4;
        }
        h4, .overview-wrapper {
            margin: 0;
            display: -webkit-box;
            -webkit-box-orient: vertical;
            overflow: hidden;
        }

        .overview-wrapper, .meta-row {
            color: var(--c-text-soft);
            font-size: var(--fs-neg-1);
        }

        .meta-row {
            font-weight: 600;
            display: flex;
            flex-direction: row;
            flex-wrap: wrap;
            column-gap: var(--spacing-xs-sm);
        }

        .controls {
            margin-top: var(--spacing-sm);
            display: flex;
            gap: var(--spacing-sm);
        }

        .overview-wrapper .overview,
        h4 .name {
            transition: filter var(--spoiler-transition-setup);
        }

        &.spoilers-hidden {
            h4 .name, .overview-wrapper {
                mask-image: 
                    linear-gradient(to bottom, transparent, black 8px, black calc(100% - 8px), transparent),
                    linear-gradient(to right, transparent, black 8px, black calc(100% - 8px), transparent);
                mask-composite: intersect;
            }
            
            .overview-wrapper .overview,
            h4 .name {
                filter: blur(6px);
                user-select: none;
                pointer-events: none;
            }
        }
    }
}


.season-buttons {
    position: fixed;
    bottom: 36px;
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

    .btn {
        white-space: nowrap;
    }
}

@media(max-width: 768px) {
    .season {
        grid-template-columns: 1fr;
        padding-bottom: 62px;
        gap: 0;
    }

    .season-details {
        width: unset;
        padding: 0;
        background-color: transparent;
        display: flex;
        flex-direction: column;
        align-items: center;

        img.season-poster {
            width: 50%;
        }

        p {
            text-align: justify;
        }

        .actions {
            width: 100%;

            .watch-count-buttons,
            .primary-actions {
                flex: 1;
            }
        }

    }

    .episodes-wrapper {
        gap: var(--spacing-md-lg);
    }

    .episode {
        grid-template-columns: 1fr;
        row-gap: var(--spacing-md);
        margin: 0;

        .episode-backdrop-wrapper {
            width: 100%;
        }

        .watch-count-buttons {
            flex: 1;
        }
    }

    .season-buttons {
        bottom: calc(75px + var(--spacing-sm-md));
    }
}
</style>