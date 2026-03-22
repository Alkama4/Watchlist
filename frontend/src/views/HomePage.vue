<script setup>
import TitleHeroCards from '@/components/title_cards/TitleHeroCards.vue';
import TitleCardCarousel from '@/components/title_cards/TitleCardCarousel.vue';
import { fastApi } from '@/utils/fastApi';
import { onMounted, ref } from 'vue';
import { Captions, Disc, Film, FilmRollAlt, Happy, HappyBeaming, ListPlay, Movie, Pause, Play, PlayCircle, Popcorn, StopCircle, Tv, Video, VideoCinema } from '@boxicons/vue';
import LoadingIndicator from '@/components/LoadingIndicator.vue';
import TitleHeroCardCarousel from '@/components/title_cards/TitleHeroCardCarousel.vue';

const homeData = ref({});
const waiting = ref(true);

async function fetchHome() {
    waiting.value = true;
    try {
        homeData.value = await fastApi.home();
    } finally {
        waiting.value = false;
    }
}

onMounted(async () => {
    await fetchHome();
});

const iconList = [
    { comp: FilmRollAlt,  scale: 1.0},
    { comp: Video,        scale: 1.0},
    { comp: ListPlay,     scale: 1.2},
    { comp: Play,         scale: 1.1},
    { comp: Film,         scale: 1.5},
    { comp: VideoCinema,  scale: 2.0},
    { comp: Tv,           scale: 1.4},
    { comp: Pause,        scale: 0.9},
    { comp: Popcorn,      scale: 1.8},
    { comp: Captions,     scale: 0.8},
    { comp: Movie,        scale: 1.6},
    { comp: StopCircle,   scale: 0.8},
];

const rows = 3;
const cols = 4;
const jitterAmount = 0.125;

const scatteredIcons = iconList.map((icon, index) => {
    // Determine grid position
    const row = Math.floor(index / cols);
    const col = index % cols;

    // Calculate base percentage (center of the cell)
    const basePercentX = (col / cols) + (1 / (cols * 2));
    const basePercentY = (row / rows) + (1 / (rows * 2));

    // Add jitter (-jitterAmount to +jitterAmount)
    const jitterX = (Math.random() * 2 - 1) * jitterAmount;
    const jitterY = (Math.random() * 2 - 1) * jitterAmount;

    return {
        comp: icon.comp,
        style: {
            '--grid-x': (basePercentX + jitterX) * 90 + '%',
            '--grid-y': (basePercentY + jitterY) * 100 + '%',
            '--icon-rot': `${Math.floor(Math.random() * 40) - 20}deg`,
            '--icon-scale': icon.scale,
        }
    };
});
</script>

<template>
    <div v-if="homeData?.normal_cards?.length > 0" class="home-page layout-spacing-bottom layout-spacing-top">
        <TitleHeroCardCarousel :heroCards="homeData?.hero_cards" />
        <TitleCardCarousel v-for="list in homeData?.normal_cards" :carouselData="list"/>
    </div>

    <LoadingIndicator v-else-if="waiting"/>
    
    <div v-else class="home-page-initial layout-contained layout-spacing-bottom layout-spacing-top">
        <div class="initial-greeting card">
            <h1>Your library starts here</h1>
            <p>
                Start building your digital collection. Search for the movies and shows you own or want to watch to keep track of everything in one place.
            </p>
            <RouterLink to="/search" class="btn btn-primary no-deco">
                Find your first title
            </RouterLink> 
        </div>

        <div class="icon-cloud">
            <div 
                v-for="(icon, index) in scatteredIcons" 
                :key="index"
                class="icon-wrapper"
                :style="icon.style"
            >
                <component 
                    :is="icon.comp" 
                    pack="filled"
                    class="scattered-icon"
                    size="xl"
                />
            </div>
        </div>
    </div>
</template>

<style scoped>
.home-page-initial {
    position: relative;
    min-height: 80vh;
    display: flex;
    align-items: center;
    overflow: hidden;
}

.initial-greeting {
    position: relative;
    z-index: 10;
    width: 60ch;
    max-width: 100%;

    h1 {
        margin-top: 0;
    }
}

.icon-cloud {
    position: absolute;
    inset: 0;
    z-index: 1;
    pointer-events: none;
}

.icon-wrapper {
    position: absolute;
    color: var(--c-neutral);
    left: var(--grid-x);
    top: var(--grid-y);
    transform: translate(-50%, -50%) scale(var(--icon-scale)) rotate(var(--icon-rot));
}

@media (min-width: 768px) {
    .icon-wrapper {
        left: calc(50% + (var(--grid-x) * 0.5));
        top: var(--grid-y); 
    }
}
</style>