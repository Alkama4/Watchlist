<script setup>
import Flicking from "@egjs/vue3-flicking";
import TitleCard from "./TitleCard.vue";

defineProps({
    carouselData: {
        type: Object,
        required: true
    }
})
</script>

<template>
    <div class="carousel layout-full-contained">
        <div class="layout-contained">
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
                v-for="title in carouselData?.titles"
                :titleInfo="title"
                :key="title.title_id"
            />
            <router-link 
                v-if="list?.total_pages > 1"
                class="fake-card"
                :to="'/search'"
            >
                Show more
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
        var(--c-bg) var(--spacing-layout-inline), 
        var(--c-bg) calc(100% - var(--spacing-layout-inline)), 
        transparent 100%
    );
}
</style>