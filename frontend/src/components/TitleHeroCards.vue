<script setup>
import { resolveImagePath } from '@/utils/imagePath';
import { timeFormatters, numberFormatters } from '@/utils/formatters';
import Tmdb from '@/assets/icons/tmdb.svg'
import { ref, onMounted, onUnmounted } from 'vue';
import PaginationDots from './PaginationDots.vue';

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
            <div
                v-if="heroCards"
                :key="heroCards?.titles[currentIndex]?.title_id"
                class="hero-card"
            >
                <img
                    :src="resolveImagePath(
                        'original', 
                        heroCards?.titles[currentIndex]?.default_backdrop_image_path, 
                        heroCards?.titles[currentIndex]?.user_details?.chosen_backdrop_image_path
                    )"
                    :alt="`${heroCards?.titles[currentIndex]?.type} backdrop: ${heroCards?.titles[currentIndex]?.name}`"
                    class="backdrop"
                >
                
                <RouterLink :to="`/title/${heroCards?.titles[currentIndex]?.title_id}`" class="details no-deco layout-contained">
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
                        {{ heroCards?.titles[currentIndex]?.type == 'movie' ? 'Movie' : 'TV' }}
                        &bull;
                        {{ timeFormatters.timestampToYear(heroCards?.titles[currentIndex]?.release_date) }}
                        &bull;
                        <Tmdb/>
                        {{ heroCards?.titles[currentIndex]?.tmdb_vote_average }}
                        ({{ numberFormatters.formatCompactNumber(heroCards?.titles[currentIndex]?.tmdb_vote_count) }} votes)
                    </div>
                    <p>{{ heroCards?.titles[currentIndex]?.overview }}</p>
                </RouterLink>
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

.details {
    width: 100%;
    display: flex;
    flex-direction: column;
    z-index: 10;
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