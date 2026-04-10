<script setup>
import { computed, ref } from 'vue'
import { getTitleImageUrl } from '@/utils/imagePath';
import { numberFormatters, timeFormatters } from '@/utils/formatters';
import Tmdb from '@/assets/icons/tmdb.svg'
import { Check, ChevronDown, ChevronUp } from '@boxicons/vue';
import { resolveSeasonWatchCount } from '@/utils/titleUtils';

defineProps({
    titleDetails: {
        type: Object,
        required: true
    }
})

const wrapper = ref(null);
const expanded = ref(false);
const visibleSeasons = 2;

const cardHeight = 128;
const gapHeight = 16;
const fadeOverlayHeight = 68;

const limitHeight = (cardHeight + gapHeight) * visibleSeasons + fadeOverlayHeight;
const scrollHeight = computed(() => wrapper.value?.scrollHeight);
const limitOverflow = computed(() => scrollHeight.value > limitHeight);

const computedHeight = computed(() => {
    if (!limitOverflow.value) return scrollHeight.value  // content fits, use natural height
    return expanded.value ? scrollHeight.value + 38 + 12 : limitHeight
})
</script>

<template>
    <div class="season-listing">
        <h3>Seasons</h3>
        <div class="seasons-container" :style="{ height: computedHeight + 'px' }">
            <div ref="wrapper" class="seasons-wrapper">
                <router-link
                    v-for="season in titleDetails?.seasons"
                    :key="season?.season_id"
                    class="season-card btn btn-even-padding no-deco"
                    :to="`/title/${titleDetails?.title_id}?season=${season?.season_number}`"
                >
                    <img 
                        :src="getTitleImageUrl(season, '800', 'poster')"
                        :alt="`Season poster: ${season?.season_name}`"
                        class="poster"
                    >

                    <div class="details">
                        <h4>
                            <div v-if="resolveSeasonWatchCount(season)" class="watch-count">
                                <template v-if="resolveSeasonWatchCount(season) == 1"><Check size="xs"/></template>
                                <template v-else>{{ resolveSeasonWatchCount(season) }}</template>
                            </div>
                            {{ season?.season_name }}
                        </h4>
                        
                        <div class="meta-row">
                            <span class="meta-item">
                                {{ timeFormatters.timestampToYear(season?.episodes?.[0]?.air_date) }}
                                <template v-if="
                                    season?.episodes?.length > 1 && 
                                    timeFormatters.timestampToYear(season?.episodes?.[0]?.air_date) !== 
                                    timeFormatters.timestampToYear(season?.episodes?.[season.episodes.length - 1]?.air_date)
                                ">
                                    - {{ timeFormatters.timestampToYear(season?.episodes?.[season.episodes.length - 1]?.air_date) }}
                                </template>
                            </span>

                            <span class="seperator">&bull;</span>

                            <span class="meta-item">
                                {{ season?.episodes?.length }} episodes
                            </span>

                            <span class="seperator">&bull;</span>

                            <span class="meta-item">
                                <Tmdb class="tmdb-icon"/>
                                {{ numberFormatters.formatNumberToLocale(season?.tmdb_vote_average) }}
                            </span>
                        </div>

                        <p class="overview" :class="{'unavailable': !season?.overview}">
                            {{ season?.overview || "No overview available." }}
                        </p>
                    </div>
                </router-link>
            </div>

            <div
                v-if="limitOverflow"
                class="fade-overlay"
                :class="{'expanded': expanded}" @click="expanded = !expanded"
            >
                <div class="show-more-text">
                    <template v-if="expanded">
                        <ChevronUp/> Show less <ChevronUp/>
                    </template>
                    <template v-else>
                        <ChevronDown/> Show more <ChevronDown/>
                    </template>
                </div>
            </div>
        </div>
    </div>
</template>

<style scoped>
.season-listing {
    margin-top: var(--spacing-lg);
}
.seasons-container {
    position: relative;
    overflow: hidden;
    transition: height 0.25s var(--transition-ease-out);
}
.seasons-wrapper {
    display: flex;
    flex-direction: column;
    gap: var(--spacing-md);
}

.season-card {
    position: relative;
    display: flex;
    flex-direction: row;
    gap: 0;
    /* border-radius: var(--border-radius-md-lg); */
    overflow: hidden;
    padding: 0;
    /* align-items: flex-start; */
    text-align: left;
    font-weight: 400;
    transition: transform 0.2s ease, background-color 0.2s ease;
}

img.poster {
    height: 128px;
    aspect-ratio: 2/3;
    /* border-radius: var(--border-radius-md-lg); */
    object-fit: cover;
    flex-shrink: 0;
}

.details {
    display: flex;
    flex-direction: column;
    flex-grow: 1;
    min-width: 0; /* Prevents text overflow from pushing flex layout */
    gap: var(--spacing-sm);
    /* padding-top: var(--spacing-xs); */
    padding-inline: var(--spacing-md);

    h4 {
        margin: 0;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        display: flex;
        gap: var(--spacing-sm);
        align-items: center;
    }

    .watch-count {
        background-color: var(--c-positive);
        border-radius: 100px;
        display: flex;
        justify-content: center;
        align-items: center;
        
        font-weight: 600;
        font-size: var(--fs-neg-2);
        width: var(--spacing-md-lg);
        height: var(--spacing-md-lg);
    }

    .meta-row {
        display: flex;
        flex-wrap: wrap;
        align-items: center;
        gap: var(--spacing-xs);
        font-size: var(--fs-neg-2);
        color: var(--c-text-soft);
        font-weight: 600;
    
        .meta-item {
            display: flex;
            align-items: center;
            gap: 4px;
        }
    }
    
    .overview {
        margin: 0;
        font-size: var(--fs-neg-2);
        color: var(--c-text-soft);
        display: -webkit-box;
        -webkit-line-clamp: 2;
        line-clamp: 2;
        -webkit-box-orient: vertical;
        overflow: hidden;
        line-height: 1.4;

        &.unavailable {
            color: var(--c-text-subtle);
            font-style: italic;
        }
    }
}


/* Fade Overlay */
.fade-overlay {
    position: absolute;
    bottom: 0;
    left: 0;
    right: 0;
    height: 68px;
    background: linear-gradient(to bottom, transparent, var(--c-bg));
    display: flex;
    align-items: flex-end;
    cursor: pointer;
    transition: height 0.25s var(--transition-ease-out);
    
    &.expanded {
        height: 38px;
    }
    &:hover .show-more-text {
        transform: translateY(4px);
    }
    &:hover.expanded .show-more-text {
        transform: translateY(-4px);
    }

    .show-more-text {
        width: 100%;
        height: 100%;
        display: flex;
        justify-content: center;
        align-items: center;
        font-weight: 600;
        font-size: var(--fs-neg-1);
        gap: var(--spacing-md);
        background-color: transparent !important;
        transition: 0.3s transform var(--transition-bounce);
    }
}
</style>