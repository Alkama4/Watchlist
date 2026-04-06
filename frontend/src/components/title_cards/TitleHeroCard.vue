<script setup>
import { getTitleImageUrl } from '@/utils/imagePath';
import { numberFormatters, timeFormatters } from '@/utils/formatters';
import Tmdb from '@/assets/icons/tmdb.svg'
import { computed, ref } from 'vue';
import { adjustWatchCount, toggleFavourite, toggleWatchlist } from '@/utils/titleActions';
import LoadingButton from '../LoadingButton.vue';
import { Check, Clock, Heart, Minus } from '@boxicons/vue';

const waitingfor = ref({});

const props = defineProps({
    title: {
        type: Object,
        required: true
    },
    index: {
        type: Number,
        required: true
    },
    indexProgress: {
        type: Number,
        default: 0
    },
    total: {
        type: Number,
        required: true
    }
});


const cardProgress = computed(() => {
    let diff = props.index - props.indexProgress;
    const half = props.total / 2;

    if (diff > half) diff -= props.total;
    if (diff < -half) diff += props.total;

    return diff;
});
const cardVisibility = computed(() => {
    const distance = Math.abs(cardProgress.value);
    return Math.max(0, 1 - distance);
});

const backdropStyle = computed(() => ({
    opacity: cardVisibility.value * 0.5 + 0.5
}));

const logoStyle = computed(() => ({
    transform: `translateX(calc(-50% + ${cardProgress.value * -10}cqw))`, 
    opacity: cardVisibility.value
}));

const detailsStyle = computed(() => ({
    transform: `translateX(${cardProgress.value * -10}cqw)`,
    opacity: cardVisibility.value
}));
</script>

<template>
    <RouterLink
        :key="title.title_id"
        class="title-hero-card no-deco"
        :class="positionClass"
        :to="`/title/${title.title_id}`"
        draggable="false"
    >
        <div class="backdrop-wrapper">
            <img
                :src="getTitleImageUrl(title, 'original', 'backdrop')"
                :alt="`${title.title_type} backdrop: ${title.name}`"
                :style="backdropStyle"
                class="backdrop"
                draggable="false"
            >
        </div>

        <img
            :src="getTitleImageUrl(title, 'original', 'logo')"
            :alt="`Logo for the title ${title.name}`"
            :style="logoStyle"
            class="logo"
            draggable="false"
        >

        <div class="details-wrapper">
            <div class="details no-deco" :style="detailsStyle">
                <div class="stats">
                    <span>{{ timeFormatters.timestampToYear(title.release_date) }}</span>

                    <span v-if="title.title_type == 'movie'">
                        {{ timeFormatters.minutesToHrAndMin(title.movie_runtime) }}
                    </span>
                    <span v-else>
                        {{ title.show_season_count }}
                        Season{{ title.show_season_count == 1 ? '': 's' }},
                        {{ title.show_episode_count }}
                        Episode{{ title.show_episode_count == 1 ? '': 's' }}
                    </span>

                    <template v-if="title?.age_rating?.rating">
                        <span>{{ title?.age_rating?.rating }}</span>
                    </template>

                    <span>
                        <Tmdb/>
                        {{ numberFormatters.formatNumberToLocale(title.tmdb_vote_average) }}
                    </span>
                </div>

                <div v-if="title.genres?.length > 0" class="genres" >
                    <span v-for="genre in title.genres" :key="genre.genre_name">
                        {{ genre?.genre_name }}
                    </span>
                </div>

                <div class="actions" >
                    <div
                        :class="{
                            'watched btn': title?.user_details?.watch_count
                        }"
                        class="watch-count-buttons"
                        @click.prevent
                    >
                        <LoadingButton
                            class="btn-even-padding inner-action add-button"
                            :class="{'btn-positive': title?.user_details?.watch_count}"
                            :loading="waitingfor[`titleWcAdd_${title?.title_id}`]"
                            @click.prevent="adjustWatchCount.title.add(title, waitingfor)"
                        >
                            <template v-if="title?.user_details?.watch_count >= 2">
                                {{ title?.user_details?.watch_count }}
                            </template>
                            <Check v-else/>
                        </LoadingButton>

                        <LoadingButton
                            class="btn-even-padding inner-action"
                            :loading="waitingfor[`titleWcSub_${title?.title_id}`]"
                            @click.prevent="adjustWatchCount.title.subtract(title, waitingfor)"
                        >
                            <Minus/>
                        </LoadingButton>
                    </div>
                    
                    <div>
                        <LoadingButton
                            :class="{
                                'active': title?.user_details?.is_favourite,
                                'btn-favourite': title?.user_details?.is_favourite
                            }"
                            class="btn-even-padding favourite"
                            :loading="waitingfor?.favourite"
                            @click.prevent="toggleFavourite(title, waitingfor)" 
                        >
                            <Heart pack="filled" size="sm"/>
                        </LoadingButton>
                    </div>
                    
                    <div>
                        <LoadingButton
                            :class="{
                                'active': title?.user_details?.in_watchlist,
                                'btn-accent': title?.user_details?.in_watchlist
                            }"
                            class="btn-even-padding watchlist"
                            :loading="waitingfor?.watchlist"
                            @click.prevent="toggleWatchlist(title, waitingfor)" 
                        >
                            <Clock pack="filled" size="sm"/>
                        </LoadingButton>
                    </div>
                </div>
            </div>
        </div>
    </RouterLink>
</template>

<style scoped>
.title-hero-card {
    width: 100%;
    
    /* The core calculations */
    --max-clamp: min(calc(90vw / 2), 600px);
    --dynamic-max-height: clamp(450px, 55vh, var(--max-clamp));
    
    /* Limit height to resolved max height and safety min limit */
    min-height: 350px;
    max-height: var(--dynamic-max-height);
    
    /* Cap the max-width at an aspect ratio based on resolved height */
    max-width: calc(var(--dynamic-max-height) * 18.5 / 9);
    
    /* Natural ratio for in between/smaller screens */
    aspect-ratio: 1.25;

    margin-right: var(--spacing-md-lg);
    border-radius: var(--border-radius-lg);
    overflow: hidden;
    user-select: none;
    position: relative;
    container-type: inline-size
}
/* .title-hero-card:last-of-type {
    margin-right: 0;
} */

.backdrop-wrapper {
    background-color: var(--hero-backdrop-color);
    position: absolute;
    inset: 0;
    width: 100%;
    height: 100%;

    img.backdrop {
        width: 100%;
        height: 100%;
        object-fit: cover;
    
        mask-image: linear-gradient(
            to top,
            rgba(0, 0, 0, var(--hero-backdrop-opacity)) 80px,
            rgba(0, 0, 0, 1) 100%
        );
    }
}

img.logo {
    object-fit: contain;
    object-position: bottom center;
    position: absolute;
    bottom: calc(115px + var(--spacing-sm-md));
    left: 50%;
    transform: translateX(-50%);
    height: 20%;
    width: 500px;
    max-width: 100%;
    padding-inline: var(--spacing-lg);
    z-index: 10;
    box-sizing: border-box;
}

.details-wrapper {
    left: 0;
    width: 100%;
    bottom: 0;
    position: absolute;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    z-index: 10;
    padding: var(--spacing-md) var(--spacing-lg);
    box-sizing: border-box;
    overflow: hidden;

    .details {
        width: 100%;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;

        .stats {
            font-weight: 500;
            display: flex;
            gap: var(--spacing-md-lg);
            align-items: center;
            white-space: nowrap;
            color: var(--c-text-white);
        }

        .genres {
            font-weight: 500;
            margin-top: var(--spacing-sm);
            color: var(--c-text-white-soft);
            font-size: var(--fs-neg-2);
            white-space: nowrap;
        
            span::after {
                content: ", ";
            }
            span:nth-last-child(1)::after {
                content: "";
            }
        }

        .actions {
            z-index: 11;
            margin-top: var(--spacing-sm-md);

            display: flex;
            justify-content: start;
            column-gap: var(--spacing-xs-sm);

            button {
                border-radius: 100px;
            }

            .watch-count-buttons {
                border-radius: 100px;
                display: flex;
                flex-direction: row;
                justify-content: start;
                padding: 0;
                width: 36px;
                height: 36px;
                overflow: hidden;
                transition: width 0.2s var(--transition-ease-out);

                &.watched {
                    background-color: var(--c-neutral);

                    &:hover {
                        width: calc(36px * 2 + var(--spacing-xs));
                    }
                }

                .inner-action {
                    box-sizing: border-box;
                    aspect-ratio: 1;
                    height: 100%;
                    font-weight: 500;
                }
            }
        }
    }
}
</style>