<script setup>
import { getTitleImageUrl } from '@/utils/imagePath';
import { numberFormatters, timeFormatters } from '@/utils/formatters';
import Tmdb from '@/assets/icons/tmdb.svg'
import { useSearchStore } from '@/stores/search';
import { fastApi } from '@/utils/fastApi';
import { ref } from 'vue';
import LoadingButton from '@/components/LoadingButton.vue';
import { adjustWatchCount, toggleFavourite, toggleWatchlist } from '@/utils/titleActions';
import { ArrowOutUpRightSquare, Check, Clock, Heart, ListMinus, ListPlus, Minus } from '@boxicons/vue';

const searchStore = useSearchStore();

const props = defineProps({
    titleInfo: {
        type: Object,
        required: true,
    },
    storeImageFlag: {
        type: Boolean,
        default: true
    },
    gridMode: {
        type: Boolean,
        default: false
    },
    index: {
        type: Number,
    }
})

const waiting = ref({})

async function addTitle() {
    waiting.value.library = true;
    try {
        if (props.titleInfo.title_id) {
            await fastApi.titles.library.add(props.titleInfo.title_id)
        } else {
            const response = await fastApi.titles.addToLibrary({
                tmdb_id: props.titleInfo.tmdb_id,
                title_type: props.titleInfo.title_type
            })
            props.titleInfo.title_id = response.title_id;
        }
        
        if (!props.titleInfo.user_details) {
            props.titleInfo.user_details = {
                in_library: true,
                is_favourite: false,
                in_watchlist: false,
                watch_count: 0,
            }
        } else {
            props.titleInfo.user_details.in_library = true
        }
    } finally {
        waiting.value.library = false;
    }
}

async function removeTitle() {
    waiting.value.library = true;
    try {
        await fastApi.titles.library.remove(props.titleInfo.title_id)
        props.titleInfo.user_details.in_library = false;
    } finally {
        waiting.value.library = false;
    }
}
</script>

<template>
    <component 
        :is="titleInfo.title_id ? 'router-link' : 'div'"
        :to="titleInfo.title_id ? `/title/${titleInfo.title_id}` : null"
        :style="`animation-delay: ${(index ?? titleInfo?.batchIndex ?? 0) * 0.01}s`"
        class="title-card"
        :class="{
            'grid-mode': gridMode, 
            'in-library': titleInfo?.user_details?.in_library,
            'is-search-mode': searchStore.tmdbFallback
        }"
        :draggable="gridMode"
    >
        <div class="poster-wrapper">
            <img 
                :src="getTitleImageUrl(titleInfo, '800', 'poster', storeImageFlag)"
                :alt="`${titleInfo?.title_type === 'tv' ? 'TV show' : 'Movie'} poster: ${titleInfo?.name}`"
                :draggable="gridMode"
            >

            <div 
                v-if="searchStore.tmdbFallback || !titleInfo?.user_details?.in_library"
                class="action-overlay"
            >
                <LoadingButton 
                    v-if="!titleInfo?.user_details?.in_library" 
                    class="overlay-btn btn-primary"
                    :loading="waiting?.library"
                    @click.prevent.stop="addTitle"
                >
                    <ListPlus size="md"/>
                </LoadingButton>

                <LoadingButton 
                    v-else 
                    class="overlay-btn btn-danger"
                    :loading="waiting?.library"
                    @click.prevent.stop="removeTitle"
                >
                    <ListMinus size="md"/>
                </LoadingButton>
            </div>

            <a 
                v-if="searchStore.tmdbFallback"
                class="tmdb-external-link btn btn-even-padding"
                :href="`https://www.themoviedb.org/${titleInfo?.title_type}/${titleInfo?.tmdb_id}`"
                target="_blank"
                @click.stop
            >
                <ArrowOutUpRightSquare size="xs"/>
            </a>

            <div v-if="!searchStore.tmdbFallback && titleInfo?.user_details?.in_library" class="indicator-wrapper">
                <div :class="{'active': titleInfo?.user_details?.watch_count}" class="indicator-circle watch-count">
                    <LoadingButton
                        class="inner-action"
                        :class="{'btn-positive': titleInfo?.user_details?.watch_count}"
                        :loading="waiting[`titleWcAdd_${titleInfo?.title_id}`]"
                        @click.prevent.stop="adjustWatchCount.title.add(titleInfo, waiting)"
                    >
                        <template v-if="titleInfo?.user_details?.watch_count >= 2">
                            {{ titleInfo?.user_details?.watch_count }}
                        </template>
                        <Check v-else size="sm"/>
                    </LoadingButton>

                    <LoadingButton
                        class="inner-action"
                        :loading="waiting[`titleWcSub_${titleInfo?.title_id}`]"
                        @click.prevent.stop="adjustWatchCount.title.subtract(titleInfo, waiting)"
                    >
                        <Minus size="sm"/>
                    </LoadingButton>
                </div>
        
                <LoadingButton
                    :class="{ 'active': titleInfo?.user_details?.is_favourite, 'btn-favourite': titleInfo?.user_details?.is_favourite }"
                    class="indicator-circle favourite"
                    :loading="waiting?.toggleFavourite"
                    @click.prevent.stop="toggleFavourite(titleInfo, waiting)" 
                >
                    <Heart size="sm" pack="filled"/>
                </LoadingButton>
        
                <LoadingButton
                    :class="{ 'active': titleInfo?.user_details?.in_watchlist, 'btn-accent': titleInfo?.user_details?.in_watchlist }"
                    class="indicator-circle watchlist"
                    :loading="waiting?.toggleWatchlist"
                    @click.prevent.stop="toggleWatchlist(titleInfo, waiting)" 
                >
                    <Clock size="sm" pack="filled"/>
                </LoadingButton>
            </div>
        </div>

        <div class="details">
            <h5>{{ titleInfo?.name }}</h5>
            <div class="detail-row">
                {{ timeFormatters.timestampToYear(titleInfo?.release_date) }}
                &bull;
                <Tmdb/>
                {{ numberFormatters.formatNumberToLocale(titleInfo?.tmdb_vote_average, {maximumFractionDigits: 1}) || "-" }}
            </div>

            <div v-if="!searchStore.tmdbFallback" class="detail-row">
                <template v-if="titleInfo?.title_type === 'tv'">
                    {{ titleInfo?.show_season_count }} seasons,
                    {{ titleInfo?.show_episode_count }} episodes
                </template>
                <template v-else>{{ timeFormatters.minutesToHrAndMin(titleInfo?.movie_runtime) }}</template>
            </div>
            <div v-else class="detail-row">
                {{ titleInfo?.title_type == 'tv' ? 'TV' : 'Movie' }}
            </div>
        </div>
    </component>
</template>

<style scoped>
.title-card {
    width: var(--title-card-width);
    display: inline-flex;
    flex-direction: column;
    text-decoration: none;
    position: relative;
    margin-right: var(--spacing-md);
    animation: fadeIn 0.5s var(--transition-ease-out) forwards;
    opacity: 0;

    &:last-of-type,
    &.grid-mode {
        margin-right: 0;
    }
}

@keyframes fadeIn {
    to { opacity: 1; }
}

/* ----- Poster Wrapper ----- */
.poster-wrapper {
    position: relative;
    aspect-ratio: 2/3;
    border-radius: var(--border-radius-md);
    overflow: hidden;
}

.poster-wrapper img {
    width: 100%;
    height: 100%;
    object-fit: cover;
    transition: filter 0.2s var(--transition-ease-out);
}

/* Grayscale only applies if NOT in library AND NOT in search mode (e.g. Collections) */
.title-card:not(.in-library) img {
    filter: brightness(0.5) grayscale(1);
}

/* ----- Unified Action Overlay ----- */
.action-overlay {
    position: absolute;
    inset: 0;
    display: flex;
    justify-content: center;
    align-items: center;
    background: rgba(0, 0, 0, 0.4);
    opacity: 0;
    transition: opacity 0.2s var(--transition-ease-out);
}

/* Persistently show the overlay icon slightly faded for missing collection items so they know they can click */
.title-card:not(.in-library) .action-overlay {
    opacity: 0.7;
}

.title-card:hover .action-overlay {
    opacity: 1;
}

.overlay-btn {
    border-radius: 100px;
    width: 42px;
    aspect-ratio: 1;
    padding: var(--spacing-sm);
    transform: scale(0.8);
    transition: transform 0.2s var(--transition-ease-out);
}

.title-card:hover .overlay-btn {
    transform: scale(1);
}

/* ----- TMDB External Link ----- */
.tmdb-external-link {
    position: absolute;
    top: var(--spacing-sm);
    right: var(--spacing-sm);
    opacity: 0;
    transition: opacity 0.2s var(--transition-ease-out),
                background-color 0.1s var(--transition-ease-out);
    z-index: 60;
}

.title-card:hover .tmdb-external-link {
    opacity: 1;
}

/* ----- Details ----- */
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
    color: var(--c-text-soft);
    font-size: var(--fs-neg-1);
}

/* ----- Indicator circles ----- */
.indicator-wrapper {
    position: absolute;
    padding: var(--spacing-sm);
    top: 0;
    left: 0;
    --spacing-amount: 8px;
    z-index: 50;
}

.indicator-circle {
    position: absolute;
    width: var(--spacing-lg);
    height: var(--spacing-lg);
    padding: 0;
    border-radius: 100px;
    left: 0;
    opacity: 0;
    overflow: hidden;
    transition: 
        height 0.2s var(--transition-ease-out),
        left 0.2s var(--transition-ease-out), 
        opacity 0.1s var(--transition-ease-out),
        background-color 0.1s var(--transition-ease-out);

    &.watch-count {
        z-index: 50;
        left: calc(var(--spacing-amount) * 0 + var(--spacing-sm));
        display: flex;
        flex-direction: column;
        gap: var(--spacing-xs);

        &.active {
            background-color: var(--c-positive);

            &:hover {
                background-color: var(--c-neutral);
                height: calc(var(--spacing-lg) * 2 + var(--spacing-xs));
            }
        }

        .inner-action {
            width: var(--spacing-lg);
            height: var(--spacing-lg);
            flex-shrink: 0;
            padding: 0;
            border-radius: 100px;
        }
    }
    &.favourite {
        z-index: 40;
        left: calc(var(--spacing-amount) * 1 + var(--spacing-sm));
    }
    &.watchlist {
        z-index: 30;
        left: calc(var(--spacing-amount) * 2 + var(--spacing-sm));
    }

    &.active {
        opacity: 1;
    }
    &.active:nth-child(1 of .active) {
        left: calc(var(--spacing-amount) * 0 + var(--spacing-sm)) !important;
    }
    &.active:nth-child(2 of .active) {
        left: calc(var(--spacing-amount) * 1 + var(--spacing-sm)) !important;
    }
    &.active:nth-child(3 of .active) {
        left: calc(var(--spacing-amount) * 2 + var(--spacing-sm)) !important;
    }
}

.title-card:hover .indicator-wrapper {
    --spacing-amount: calc(var(--spacing-lg) + var(--spacing-xs));

    .indicator-circle {
        opacity: 1;
    
        &.active:nth-child(1) {
            left: calc(var(--spacing-amount) * 0 + var(--spacing-sm)) !important;
        }
    
        &.active:nth-child(2) {
            left: calc(var(--spacing-amount) * 1 + var(--spacing-sm)) !important;
        }
    
        &.active:nth-child(3) {
            left: calc(var(--spacing-amount) * 2 + var(--spacing-sm)) !important;
        }
    }
}
</style>