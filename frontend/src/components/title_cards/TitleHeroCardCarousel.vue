<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue';
import Flicking from '@egjs/vue3-flicking';
import { useFlickingReactiveAPI } from '@egjs/vue3-flicking';
import TitleHeroCard from '@/components/title_cards/TitleHeroCard.vue';
import { ChevronLeft, ChevronRight } from '@boxicons/vue';
import PaginationDots from '@/components/PaginationDots.vue';
import { getTitleImageUrl } from '@/utils/imagePath';
import AppImage from '@/components/AppImage.vue';

const flicking = ref(null);
const { indexProgress } = useFlickingReactiveAPI(flicking);

const props = defineProps({
    heroCards: { type: Object, required: true }
});

const titles = computed(() => props.heroCards?.titles ?? []);
const total = computed(() => titles.value.length);

const wrappedProgress = computed(() => {
    if (!total.value) return 0;
    const p = indexProgress.value ?? 0;
    return ((p % total.value) + total.value) % total.value;
});

function getTitleWeight(index, progress, count) {
    if (!count) return 0;
    let diff = Math.abs(index - progress);
    if (diff > count / 2) diff = count - diff;
    return Math.max(0, 1 - diff);
}

const backdropLayers = computed(() => {
    const p = wrappedProgress.value;
    const count = total.value;

    return titles.value
        .map((title, index) => ({
            title,
            opacity: getTitleWeight(index, p, count)
        }))
        .filter((layer) => layer.opacity > 0);
});

function handleKeydown(e) {
    if (!flicking.value) return;
    if (e.key === 'ArrowRight') flicking.value.next().catch(() => {});
    if (e.key === 'ArrowLeft') flicking.value.prev().catch(() => {});
}

onMounted(() => window.addEventListener('keydown', handleKeydown));
onUnmounted(() => window.removeEventListener('keydown', handleKeydown));
</script>

<template>
    <section class="title-hero-card-carousel layout-full-contained">
        <div class="ambient-backdrop" aria-hidden="true">
            <AppImage
                v-for="layer in backdropLayers"
                :key="layer.title.title_id"
                :src="getTitleImageUrl(layer.title, 'blur', 'backdrop')"
                alt=""
                class="ambient-layer"
                :style="{ opacity: layer.opacity }"
            />
        </div>

        <div class="carousel-wrapper">
            <Flicking
                ref="flicking"
                class="carousel-foreground"
                :options="{
                    bounce: '33%',
                    renderOnlyVisible: false,
                    circular: true
                }"
            >
                <TitleHeroCard
                    v-for="(title, index) in heroCards.titles"
                    :key="title.title_id"
                    :title="title"
                    :index="index"
                    :index-progress="indexProgress"
                    :total="heroCards.titles.length"
                />
            </Flicking>

            <div class="controls carousel-foreground">
                <ChevronLeft
                    remove-padding
                    class="btn btn-text btn-even-padding"
                    @click.stop.prevent="flicking?.prev().catch(() => {})"
                />
                <span>
                    <PaginationDots
                        :progress="indexProgress"
                        :count="heroCards?.titles?.length"
                        @select="(idx) => flicking?.moveTo(idx).catch(() => {})"
                    />
                </span>
                <ChevronRight
                    remove-padding
                    class="btn btn-text btn-even-padding"
                    @click.stop.prevent="flicking?.next().catch(() => {})"
                />
            </div>
        </div>
    </section>
</template>

<style scoped>
@import url("/node_modules/@egjs/vue3-flicking/dist/flicking.css");

.carousel-wrapper {
    position: relative;
}

.carousel-foreground {
    position: relative;
    z-index: 1;
}

.ambient-backdrop {
    position: absolute;
    top: 0;
    left: 50%;
    transform: translateX(-50%);
    width: 100vw;
    height: 100vh;
    pointer-events: none;
    overflow: hidden;
    z-index: 0;

    mask-image:
        radial-gradient(
            circle at 50% 20%,
            rgba(0, 0, 0, var(--hero-backdrop-blur-opacity)) 0%,
            rgba(0, 0, 0, 0) 100%
        ),
        linear-gradient(
            to bottom,
            rgba(0, 0, 0, 1) 75%,
            rgba(0, 0, 0, 0) 100%
        );
    mask-composite: intersect;
}

.ambient-layer {
    position: absolute;
    inset: 0;
    width: 100%;
    height: 100%;
    object-fit: cover;
    will-change: opacity;
}

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

.controls {
    margin-top: var(--spacing-sm-md);
    display: flex;
    align-items: center;
    justify-content: center;
}
.controls svg {
    margin-inline: var(--spacing-xs-sm);
    border-radius: 100px;
}
</style>