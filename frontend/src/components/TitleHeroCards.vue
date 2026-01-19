<script setup>
import { resolveImagePath } from '@/utils/imagePath';
import { timeFormatters, numberFormatters } from '@/utils/formatters';
import Tmdb from '@/assets/icons/tmdb.svg'
import { ref, onMounted, onUnmounted } from 'vue';
import PaginationDots from './PaginationDots.vue';
import { fastApi } from '@/utils/fastApi';

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
    <section class="title-hero-cards">
        <Transition name="hero" mode="default" :class="direction">
            <div
                v-if="heroCards"
                :key="heroCards?.titles[currentIndex]?.title_id"
                class="hero-card"
            >
                <img
                    :src="resolveImagePath(heroCards?.titles[currentIndex], 'original', 'backdrop')"
                    :alt="`${heroCards?.titles[currentIndex]?.title_type} backdrop: ${heroCards?.titles[currentIndex]?.name}`"
                    class="backdrop"
                >
                <div class="details-wrapper layout-contained">
                    <RouterLink :to="`/title/${heroCards?.titles[currentIndex]?.title_id}`" class="details no-deco">
                        <img
                            :src="resolveImagePath(heroCards?.titles[currentIndex], 'original', 'logo')"
                            :alt="`Backdrop for the title ${heroCards?.titles[currentIndex]?.name}`"
                            class="logo"
                        >
                        <h2>
                            {{ heroCards?.titles[currentIndex]?.name }}
                            ({{ timeFormatters.timestampToYear(heroCards?.titles[currentIndex]?.release_date) }})
                        </h2>
                        <div class="stats">
                            <span class="tmdb">
                                <span>
                                    <Tmdb/>
                                    {{ heroCards?.titles[currentIndex]?.tmdb_vote_average }}
                                </span>
                                <span class="tiny">
                                    ({{ numberFormatters.formatCompactNumber(heroCards?.titles[currentIndex]?.tmdb_vote_count) }} votes)
                                </span>
                            </span>
    
                            <span>&vert;</span>
                            <span v-if="heroCards?.titles[currentIndex]?.title_type == 'movie'">
                                {{ timeFormatters.minutesToHrAndMin(heroCards?.titles[currentIndex]?.movie_runtime) }}
                            </span>
                            <span v-else>
                                {{ heroCards?.titles[currentIndex]?.show_season_count }}
                                Season{{ heroCards?.titles[currentIndex]?.show_season_count == 1 ? '': 's' }},
                                {{ heroCards?.titles[currentIndex]?.show_episode_count }}
                                Episode{{ heroCards?.titles[currentIndex]?.show_episode_count == 1 ? '': 's' }}
                            </span>
    
                            <template v-if="heroCards?.titles[currentIndex]?.age_rating">
                                <span>&vert;</span>
                                <span>{{ heroCards?.titles[currentIndex]?.age_rating }}</span>
                            </template>
    
                            <template v-if="heroCards?.titles[currentIndex]?.genres?.length > 0">
                                <span>&vert;</span>
                                <div class="genres">
                                    <span v-for="genre in heroCards?.titles[currentIndex]?.genres">
                                        {{ genre }}
                                    </span>
                                </div>
                            </template>
                        </div>
                        <p>{{ heroCards?.titles[currentIndex]?.overview }}</p>
                    </RouterLink>
                    <div class="actions">
                        <i
                            class="bx bxs-heart btn btn-text btn-square"
                            :class="{'btn-favourite': heroCards?.titles[currentIndex]?.user_details?.is_favourite }"
                            @click="toggleFavourite"
                        ></i>
                        <i
                            class="bx bxs-time btn btn-text btn-square"
                            :class="{'btn-accent': heroCards?.titles[currentIndex]?.user_details?.in_watchlist }"
                            @click="toggleWatchlist"
                        ></i>
                        <i
                            class="bx bxs-collection btn btn-text btn-square"
                            @click="adjustCollections"
                        ></i>
                    </div>
                </div>
            </div>
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
    </section>
</template>


<style scoped>
.title-hero-cards {
    height: 85vh;
    max-height: 1200px;
    min-height: 550px;
    width: 100vw;
    position: relative;
    overflow: hidden;
}

.hero-card {
    --transition-amount: 40px;
    position: absolute;
    width: 100%;
    height: 100%;

    display: flex;
    flex-direction: column;
    justify-content: center;
}

img.backdrop {
    position: absolute;
    inset: 0;
    margin-left: calc(-1 * var(--transition-amount));
    width: calc(100% + var(--transition-amount) * 2);
    height: 100%;
    /* max-height: calc(1200px + 15vh); */
    object-fit: cover;
    mask-image: linear-gradient(
        to top,
        rgba(0, 0, 0, 0) 0%,
        rgba(0, 0, 0, 0.35) 30%
    );
}
img.logo {
    max-height: 150px;
    max-width: 400px;
    object-fit: contain;
}

.details-wrapper {
    width: 100%;
    display: flex;
    flex-direction: column;
    z-index: 10;
}

.details {
    width: 100%;
    display: flex;
    flex-direction: column;
}

.details .stats {
    font-weight: 600;
    display: flex;
    gap: var(--spacing-sm);
    align-items: center;
}

.details .tmdb {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: var(--spacing-xs);
    /* font-size: var(--fs-1); */
}

.details .tmdb .tiny {
    font-size: var(--fs-neg-2);
    font-weight: 500;
    filter: brightness(0.75);
    margin-bottom: 0px;
    margin-top: -4px;
}

.details .genres > span::after {
    content: ", ";
}
.details .genres > span:nth-last-child(1)::after {
    content: "";
}

.details p {
    max-width: 80ch;
    overflow: hidden;
    display: -webkit-box;
    -webkit-line-clamp: 4;
            line-clamp: 4; 
    -webkit-box-orient: vertical;
}


.actions {
    display: flex;
    gap: var(--spacing-sm);
}

.controls {
    position: absolute;
    bottom: 0;
    left: 50%;
    transform: translateX(-50%);
    display: flex;
    gap: var(--spacing-sm);
    align-items: center;
    justify-content: center;
}
.controls i {
    font-size: 2.5rem;
    padding: var(--spacing-sm);
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