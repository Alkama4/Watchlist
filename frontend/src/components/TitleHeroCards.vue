<script setup>
import { getTitleImageUrl } from '@/utils/imagePath';
import { timeFormatters, numberFormatters } from '@/utils/formatters';
import Tmdb from '@/assets/icons/tmdb.svg'
import { ref, onMounted, onUnmounted } from 'vue';
import PaginationDots from './PaginationDots.vue';
import { fallbackLocale, preferredLocale } from '@/utils/conf';
import { addToWatchCount, subtractFromWatchCount, toggleFavourite, toggleWatchlist } from '@/utils/titleActions';
import LoadingButton from './LoadingButton.vue';

const waitingfor = ref({});
const currentIndex = ref(0);

// We no longer need the setTimeout or direction ref since CSS handles the directional flow
function next() {
    if (!heroCards?.titles?.length) return;
    currentIndex.value = (currentIndex.value + 1) % heroCards.titles.length;
}

function prev() {
    if (!heroCards?.titles?.length) return;
    currentIndex.value = (currentIndex.value - 1 + heroCards.titles.length) % heroCards.titles.length;
}

function handleKeydown(e) {
    if (e.key === 'ArrowRight') {
        next();
    }
    if (e.key === 'ArrowLeft') {
        prev();
    }
}

// Maps each card's index to a physical position on the screen
function getCardPosition(index) {
    const length = heroCards?.titles?.length || 0;
    if (length === 0) return 'hidden-right';
    if (length === 1) return 'center';

    const diff = (index - currentIndex.value + length) % length;

    if (diff === 0) return 'center';
    if (diff === 1) return 'right';
    if (diff === length - 1) return 'left';
    
    // Split remaining cards into hidden states so they enter/exit from the correct sides
    if (diff === length - 2) return 'hidden-left';
    return 'hidden-right';
}

function chooseAgeRating(titleDetails) {
    const ratings = titleDetails?.age_ratings ?? []

    const pref = ratings.find(
        r => r.iso_3166_1 === preferredLocale.iso_3166_1
    )
    if (pref && pref.rating) return pref

    return ratings.find(r => r.iso_3166_1 === fallbackLocale.iso_3166_1) ?? null
}

const { heroCards } = defineProps({
    heroCards: {
        type: Object,
        required: true
    }
})

onMounted(() => {
    window.addEventListener('keydown', handleKeydown);
});

onUnmounted(() => {
    window.removeEventListener('keydown', handleKeydown);
});
</script>

<template>
    <section class="title-hero-cards layout-contained layout-spacing-top">
        <div class="hero-cards-wrapper">
            <div v-if="heroCards?.titles" class="hero-cards-stack">
                <RouterLink
                    v-for="(title, index) in heroCards.titles"
                    :key="title.title_id"
                    class="hero-card no-deco"
                    :class="getCardPosition(index)"
                    :to="`/title/${title.title_id}`"
                >
                    <div class="backdrop-wrapper">
                        <img
                            :src="getTitleImageUrl(title, 'original', 'backdrop')"
                            :alt="`${title.title_type} backdrop: ${title.name}`"
                            class="backdrop"
                        >
                    </div>

                    <img
                        :src="getTitleImageUrl(title, 'original', 'logo')"
                        :alt="`Logo for the title ${title.name}`"
                        class="logo"
                    >

                    <div class="details-wrapper">
                        <div class="details no-deco">
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
        
                                <span>
                                    <Tmdb/>
                                    {{ title.tmdb_vote_average }}
                                </span>
        
                                <template v-if="chooseAgeRating(title)?.rating">
                                    <span>{{ chooseAgeRating(title)?.rating }}</span>
                                </template>
                            </div>
                            <div v-if="title.genres?.length > 0" class="genres">
                                <span v-for="genre in title.genres" :key="genre.genre_name">
                                    {{ genre?.genre_name }}
                                </span>
                            </div>

                            <div class="actions">
                                <div
                                    :class="{
                                        'watched btn': title?.user_details?.watch_count
                                    }"
                                    class="watch-count-buttons"
                                >
                                    <LoadingButton
                                        class="btn-even-padding inner-action"
                                        :class="{'btn-positive': title?.user_details?.watch_count}"
                                        :loading="waitingfor?.watchCountAdd"
                                        @click.prevent="addToWatchCount(title, waitingfor)"
                                    >
                                        <template v-if="title?.user_details?.watch_count >= 2">
                                            {{ title?.user_details?.watch_count }}
                                        </template>
                                        <i v-else class="bx bx-check"></i>
                                    </LoadingButton>

                                    <LoadingButton
                                        class="btn-even-padding inner-action"
                                        :loading="waitingfor?.watchCountSubtract"
                                        @click.prevent="subtractFromWatchCount(title, waitingfor)"
                                    >
                                        <i class="bx bx-minus"></i>
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
                                        <i class="bx bxs-heart"></i>
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
                                        <i class="bx bxs-time"></i>
                                    </LoadingButton>
                                </div>
                            </div>
                        </div>
                    </div>
                </RouterLink>
            </div>
            
            <div class="controls">
                <i
                    class="bx bx-chevron-left btn btn-text"
                    @click.stop.prevent="prev"
                ></i>
                <span>
                    <PaginationDots
                        v-model="currentIndex"
                        :count="heroCards?.titles?.length"
                    />
                </span>
                <i
                    class="bx bx-chevron-right btn btn-text"
                    @click.stop.prevent="next"
                ></i>
            </div>
        </div>
    </section>
</template>

<style scoped>
.title-hero-cards {
    position: relative;
}

.hero-cards-wrapper {
    position: relative;
    height: 100%;
    min-height: 500px;
    max-width: 100%;
    aspect-ratio: 2/1;
    overflow: hidden; /* Prevent horizontal scrollbars during animations */
}

.hero-cards-stack {
    position: relative;
    width: 100%;
    height: 100%;
}

.hero-card {
    position: absolute;
    left: 0; 
    right: 0; 
    margin: 0 auto; 
    
    /* width: 85%;  */
    height: calc(100% - 35.65px - var(--spacing-sm-md));
    max-width: 85%;
    aspect-ratio: 16/9;
    border-radius: var(--border-radius-lg);
    overflow: hidden;
    user-select: none;
    
    transition: all 0.6s var(--transition-ease);
}

/* === Carousel Positions === */

.hero-card.center {
    transform: translateX(0) scale(1);
    opacity: 1;
    z-index: 3;
    pointer-events: auto; /* Only allow interaction with the center card */
    box-shadow: 0 10px 40px rgba(0,0,0,0.5);
}

.hero-card.left {
    transform: translateX(-13%) scale(0.85);
    opacity: 0.5;
    z-index: 2;
    pointer-events: none;
}

.hero-card.right {
    transform: translateX(13%) scale(0.85);
    opacity: 0.5;
    z-index: 2;
    pointer-events: none;
}

.hero-card.hidden-left {
    transform: translateX(-23%) scale(0.7);
    opacity: 0;
    z-index: 1;
    pointer-events: none;
}

.hero-card.hidden-right {
    transform: translateX(23%) scale(0.7);
    opacity: 0;
    z-index: 1;
    pointer-events: none;
}

/* ========================== */

.backdrop-wrapper {
    background-color: var(--hero-backdrop-color);
    position: absolute;
    inset: 0;
    width: 100%;
    height: 100%;
}
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

img.logo {
    object-fit: contain;
    object-position: center;
    position: absolute;
    bottom: 106px;
    left: 50%;
    transform: translateX(-50%);
    height: 20%;
    width: 550px;
    max-width: 100%;
    padding-inline: var(--spacing-lg);
    z-index: 10;
    box-sizing: border-box;
    /* margin-bottom: var(--spacing-md); */
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
    padding: var(--spacing-sm-md) var(--spacing-lg);
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
            font-size: var(--fs-neg-1);
        
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

            i {
                font-size: var(--fs-1);
            }

            .watch-count-buttons {
                display: flex;
                flex-direction: row;
                justify-content: start;
                padding: 0;
                width: 35.2px;
                height: 35.2px;
                overflow: hidden;
                transition: width 0.2s var(--transition-ease-out);

                &.watched:hover {
                    width: calc(35.2px * 2 + var(--spacing-xs));
                }

                .inner-action {
                    aspect-ratio: 1;
                    height: 100%;
                }
                
                i {
                    font-size: var(--fs-2);
                }

            }
        }
    }
}

.controls {
    position: absolute;
    bottom: 0;
    left: 50%;
    transform: translateX(-50%);
    display: flex;
    gap: 2px;
    align-items: center;
    justify-content: center;
    z-index: 10;
}
.controls i {
    font-size: var(--fs-3);
    padding: var(--spacing-xs);
    margin-inline: var(--spacing-xs-sm);
    border-radius: 100px;
    cursor: pointer;
}
</style>