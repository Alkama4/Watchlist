<script setup>
import Flicking from "@egjs/vue3-flicking";
import TitleCard from "@/components/title_cards/TitleCard.vue";
import { ArrowRightStroke } from "@boxicons/vue";

defineProps({
    carouselData: {
        type: Object,
        required: true
    }
})
</script>

<template>
    <div class="title-carousel layout-full-contained">
        <div v-if="carouselData?.header" class="layout-contained">
            <h3>{{ carouselData?.header }}</h3>
        </div>
        <Flicking                     
            :options="{
                align: 'prev',
                bound: true,
                bounce: '33%',
                renderOnlyVisible: false,
            }"
        >
            <TitleCard 
                v-for="(title, index) in carouselData?.titles"
                :titleInfo="title"
                :index="index"
                :key="title.title_id"
            />
            <router-link 
                v-if="carouselData?.total_pages > 1"
                class="fake-card no-deco"
                :to="'/search'"
            >
                <div>Search for more</div>
                <ArrowRightStroke size="md"/>
            </router-link>
        </Flicking>
    </div>
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

/* Temp solution */
.fake-card {
    width: 200px;
    height: 300px;
    background-color: var(--c-bg-level-1);
    border-radius: var(--border-radius-md);
    display: inline-flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    gap: var(--spacing-sm);
}
.fake-card svg {
    transition: 0.3s transform var(--transition-bounce),
                0.1s scale var(--transition-ease-out),
                0.1s color  var(--transition-ease-out);
}
.fake-card:hover svg {
    transform: translateX(8px);
    scale: 1.05;
}
</style>