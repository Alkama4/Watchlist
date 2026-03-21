<script setup>
import { ref, onMounted, onUnmounted } from 'vue';
import Flicking from '@egjs/vue3-flicking';
import { useFlickingReactiveAPI } from "@egjs/vue3-flicking";
import TitleHeroCard from './TitleHeroCard.vue';

const flicking = ref(null);
const { indexProgress } = useFlickingReactiveAPI(flicking);

const { heroCards } = defineProps({
    heroCards: { type: Object, required: true }
});

function handleKeydown(e) {
    if (!flicking.value) return;

    if (e.key === 'ArrowRight') {
        flicking.value.next().catch(() => {}); 
    }
    if (e.key === 'ArrowLeft') {
        flicking.value.prev().catch(() => {});
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
    <section class="title-hero-card-carousel layout-full-contained layout-spacing-top">
        <Flicking 
            ref="flicking"
            :options="{
                bounce: '33%',
                renderOnlyVisible: false,
                circular: false
            }"
        >
            <TitleHeroCard
                v-for="(title, index) in heroCards.titles"
                :key="title.title_id"
                :title="title"
                :index="index"
                :index-progress="indexProgress"
            />
        </Flicking>
    </section>
</template>

<style scoped>
@import url("/node_modules/@egjs/vue3-flicking/dist/flicking.css");
.flicking-viewport {
    overflow: hidden;
    padding-inline: var(--spacing-layout-inline);
    box-sizing: border-box;
    mask-image: linear-gradient(
        to right, 
        transparent 0, 
        white var(--spacing-layout-inline), 
        white calc(100% - var(--spacing-layout-inline)), 
        transparent 100%
    );
}
</style>
