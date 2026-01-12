<script setup>
import { resolveImagePath } from '@/utils/imagePath';
import { timeFormatters } from '@/utils/formatters';
import Tmdb from '@/assets/icons/tmdb.svg'
import { ref, onMounted, onUnmounted } from 'vue';

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
            <router-link
                v-if="heroCards"
                :key="heroCards?.titles[currentIndex]?.title_id"
                :to="`/title/${heroCards?.titles[currentIndex]?.title_id}`"
                class="no-deco hero-card"
            >
                <img
                    :src="resolveImagePath(
                        'original', 
                        heroCards?.titles[currentIndex]?.default_backdrop_image_path, 
                        heroCards?.titles[currentIndex]?.user_details?.chosen_backdrop_image_path
                    )"
                    :alt="`Backdrop for the title ${heroCards?.titles[currentIndex]?.name}`"
                    class="backdrop"
                >
                
                <div class="details layout-contained">
                    <img
                        :src="resolveImagePath(
                            'original', 
                            heroCards?.titles[currentIndex]?.default_logo_image_path, 
                            heroCards?.titles[currentIndex]?.user_details?.chosen_logo_image_path
                        )"
                        :alt="`Backdrop for the title ${heroCards?.titles[currentIndex]?.name}`"
                        class="logo"
                    >
                    <h2>{{ heroCards?.titles[currentIndex]?.name }}</h2>
                    <div class="stats">
                        {{ heroCards?.titles[currentIndex]?.type }}
                        &bull;
                        {{ timeFormatters.timestampToYear(heroCards?.titles[currentIndex]?.release_date) }}
                        &bull;
                        <Tmdb/>
                        {{ heroCards?.titles[currentIndex]?.tmdb_vote_average }}
                        ({{ heroCards?.titles[currentIndex]?.tmdb_vote_count }} votes)
                    </div>
                    <p>{{ heroCards?.titles[currentIndex]?.overview }}</p>
                </div>
            </router-link>
        </Transition>
        <div class="controls">
            <i
                class="bx bx-chevron-left btn btn-text"
                @click.stop.prevent="prev"
            ></i>
             <span>
                {{ currentIndex }}
            </span>
            <i
                class="bx bx-chevron-right btn btn-text"
                @click.stop.prevent="next"
            ></i>
        </div>
    </section>
</template>

<!-- { "title_id": 2, "tmdb_id": 83533, "type": "movie", "name": "Avatar: Fire and Ash", "release_date": "2025-12-17", "overview": "In the wake of the devastating war against the RDA and the loss of their eldest son, Jake Sully and Neytiri face a new threat on Pandora: the Ash People, a violent and power-hungry Na'vi tribe led by the ruthless Varang. Jake's family must fight for their survival and the future of Pandora in a conflict that pushes them to their emotional and physical limits.", "movie_runtime": 198, "show_season_count": 0, "show_episode_count": 0, "tmdb_vote_average": 7.4, "tmdb_vote_count": 1359, "imdb_vote_average": null, "imdb_vote_count": null, "default_poster_image_path": "/cf7hE1ifY4UNbS25tGnaTyyDrI2.jpg", "default_backdrop_image_path": "/vm4H2DivjQoNIm0Vs6i3CTzFxQ0.jpg", "default_logo_image_path": "/qzuSPiHF08bUZXPaXST24ANfoqK.png", "user_details": { "in_library": true, "is_favourite": false, "in_watchlist": false, "watch_count": 0, "chosen_poster_image_path": null, "chosen_backdrop_image_path": null, "chosen_logo_image_path": null } } -->

<style scoped>
.title-hero-cards {
    height: clamp(60vh, 70vh, 80vh);
    max-height: 750px;
    width: 100vw;
    overflow: hidden;
    position: relative;
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
.hero-card * {
    pointer-events: none;
    user-select: none;
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
        rgba(0, 0, 0, 0) 0%,
        rgba(0, 0, 0, 0.45) 66%
    );
}
img.logo {
    max-height: 150px;
    max-width: 400px;
    object-fit: contain;
}

.details {
    width: 100%;
    display: flex;
    flex-direction: column;
}

.details .stats {
    font-weight: 600;
    /* color: var(--c-text-2); */
}

.details p {
    max-width: 80ch;
    overflow: hidden;
    display: -webkit-box;
    -webkit-line-clamp: 4;
            line-clamp: 4; 
    -webkit-box-orient: vertical;
}

.controls {
    position: absolute;
    bottom: 0;
    width: 100%;
    display: flex;
    gap: var(--spacing-sm);
    align-items: center;
    justify-content: space-evenly;
}
.controls i {
    font-size: var(--fs-4);
    padding: 0;
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