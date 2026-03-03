<script setup>
import { getTitleImageUrl } from '@/utils/imagePath';
import { timeFormatters, numberFormatters } from '@/utils/formatters';
import Tmdb from '@/assets/icons/tmdb.svg'
import { ref, onMounted, onUnmounted } from 'vue';
import PaginationDots from './PaginationDots.vue';
import { fastApi } from '@/utils/fastApi';
import { fallbackLocale, preferredLocale } from '@/utils/conf';

const currentIndex = ref(0);
const direction = ref('');

function next() {
    direction.value = 'next';
    setTimeout(() => {
        currentIndex.value =
            (currentIndex.value + 1) % heroCards.titles.length;
    }, 1)
}

function prev() {
    direction.value = 'prev';
    setTimeout(() => {
        currentIndex.value =
            (currentIndex.value - 1 + heroCards.titles.length) %
            heroCards.titles.length;
    }, 1)
}

function handleKeydown(e) {
    if (e.key === 'ArrowRight') {
        next();
    }
    if (e.key === 'ArrowLeft') {
        prev();
    }
}

async function toggleFavourite() {
    const title = heroCards.titles[currentIndex.value];

    let response;
    if (title.user_details.is_favourite) {
        response = await fastApi.titles.setFavourite(title.title_id, false);
    } else {
        response = await fastApi.titles.setFavourite(title.title_id, true);
    }
    if (!response) return;

    title.user_details.is_favourite = response.is_favourite;
}

async function toggleWatchlist() {
    const title = heroCards.titles[currentIndex.value];

    let response;
    if (title.user_details.in_watchlist) {
        response = await fastApi.titles.setWatchlist(title.title_id, false);
    } else {
        response = await fastApi.titles.setWatchlist(title.title_id, true);
    }
    if (!response) return;
    
    title.user_details.in_watchlist = response.in_watchlist;
}

function adjustCollections() {
    alert("Collections are under construction.")
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
            <Transition name="hero" mode="default" :class="direction">
                <RouterLink
                    v-if="heroCards"
                    :key="heroCards?.titles[currentIndex]?.title_id"
                    class="hero-card no-deco"
                    :to="`/title/${heroCards?.titles[currentIndex]?.title_id}`"
                >
                    <img
                        :src="getTitleImageUrl(heroCards?.titles[currentIndex], 'original', 'backdrop')"
                        :alt="`${heroCards?.titles[currentIndex]?.title_type} backdrop: ${heroCards?.titles[currentIndex]?.name}`"
                        class="backdrop"
                    >
                    <div class="details-wrapper">
                        <img
                            :src="getTitleImageUrl(heroCards?.titles[currentIndex], 'original', 'logo')"
                            :alt="`Logo for the title ${heroCards?.titles[currentIndex]?.name}`"
                            class="logo"
                        >
                        <div class="details no-deco">
                            <div class="stats">
                                <span>{{ timeFormatters.timestampToYear(heroCards?.titles[currentIndex]?.release_date) }}</span>
        
                                <!-- <span>&bull;</span> -->
                                <span v-if="heroCards?.titles[currentIndex]?.title_type == 'movie'">
                                    {{ timeFormatters.minutesToHrAndMin(heroCards?.titles[currentIndex]?.movie_runtime) }}
                                </span>
                                <span v-else>
                                    {{ heroCards?.titles[currentIndex]?.show_season_count }}
                                    Season{{ heroCards?.titles[currentIndex]?.show_season_count == 1 ? '': 's' }},
                                    {{ heroCards?.titles[currentIndex]?.show_episode_count }}
                                    Episode{{ heroCards?.titles[currentIndex]?.show_episode_count == 1 ? '': 's' }}
                                </span>

                                <!-- <span>&bull;</span> -->
                                <span>
                                    <Tmdb/>
                                    {{ heroCards?.titles[currentIndex]?.tmdb_vote_average }}
                                </span>
        
                                <template v-if="chooseAgeRating(heroCards?.titles[currentIndex])?.rating">
                                    <!-- <span>&bull;</span> -->
                                    <span>{{ chooseAgeRating(heroCards?.titles[currentIndex])?.rating }}</span>
                                </template>
        
                            </div>
                            <div v-if="heroCards?.titles[currentIndex]?.genres?.length > 0" class="genres">
                                <span v-for="genre in heroCards?.titles[currentIndex]?.genres">
                                    {{ genre?.genre_name }}
                                </span>
                            </div>
                        </div>
                        <!-- <div class="actions">
                            <i
                                class="bx bx-check btn btn-text btn-even-padding"
                                :class="{'btn-positive': heroCards?.titles[currentIndex]?.user_details?.is_favourite }"
                                @click.prevent="toggleFavourite"
                            ></i>
                            <i
                                class="bx bxs-heart btn btn-text btn-even-padding"
                                :class="{'btn-favourite': heroCards?.titles[currentIndex]?.user_details?.is_favourite }"
                                @click.prevent="toggleFavourite"
                            ></i>
                            <i
                                class="bx bxs-time btn btn-text btn-even-padding"
                                :class="{'btn-accent': heroCards?.titles[currentIndex]?.user_details?.in_watchlist }"
                                @click.prevent="toggleWatchlist"
                            ></i>
                        </div> -->
                    </div>
                </RouterLink>
            </Transition>
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

    /* transition: aspect-ratio 0.2s ease;
    
    &:hover {
        aspect-ratio: 16/9;
    } */
}

.hero-card {
    --transition-amount: 40px;
    position: absolute;
    width: 100%;
    height: calc(100% - 35.65px - var(--spacing-sm-md));
    border-radius: var(--border-radius-lg);
    overflow: hidden;
    z-index: 1;
}


img.backdrop {
    position: absolute;
    inset: 0;
    width: 100%;
    height: 100%;
    object-fit: cover;
    z-index: -10;

    mask-image: linear-gradient(
        to top,
        rgba(0, 0, 0, 0.2) 80px,
        rgba(0, 0, 0, 1) 100%
    );
}

img.logo {
    object-fit: contain;
    object-position: center;
    width: 100%;
    max-width: 550px;
    max-height: 200px;
    box-sizing: border-box;
    margin-bottom: var(--spacing-md);
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

    /* justify-content: end; */
    z-index: 10;
    padding: var(--spacing-lg);
    box-sizing: border-box;
    overflow: hidden;
    gap: var(--spacing-md);

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
        }

        .genres {
            font-weight: 500;
            margin-top: var(--spacing-sm);
            color: var(--c-text-soft);
            font-size: var(--fs-neg-1);
        
            span::after {
                content: ", ";
            }
            span:nth-last-child(1)::after {
                content: "";
            }
        }
    }
    .actions {
        display: flex;
        gap: var(--spacing-xs-sm);
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
}



/* Transition */
.hero-enter-active,
.hero-leave-active {
    transition: opacity 300ms ease, transform 300ms ease;
}

.hero-enter-from,
.hero-leave-to {
    opacity: 0;
}

/* NEXT */
.next.hero-enter-from {
    transform: translateX(var(--transition-amount));
}
.next.hero-leave-to {
    transform: translateX(calc(-1 * var(--transition-amount)));
}

/* PREV */
.prev.hero-enter-from {
    transform: translateX(calc(-1 * var(--transition-amount)));
}
.prev.hero-leave-to {
    transform: translateX(var(--transition-amount));
}


</style>