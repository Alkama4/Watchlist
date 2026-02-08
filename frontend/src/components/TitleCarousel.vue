<script setup>
import Flicking from "@egjs/vue3-flicking";
import TitleCard from "@/components/TitleCard.vue";

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
                v-if="carouselData?.total_pages > 1"
                class="fake-card no-deco"
                :to="'/search'"
            >
                <div>Search for more</div>
                <i class="bx bx-right-arrow-alt"></i>
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
    background-color: var(--c-bg-section);
    border-radius: var(--border-radius-md);
    display: inline-flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    gap: var(--spacing-sm);
}
.fake-card i {
    font-size: var(--fs-4);
    transition: 0.3s transform var(--transition-bounce),
                0.1s scale var(--transition-ease-out),
                0.1s color  var(--transition-ease-out);
}
.fake-card:hover i {
    transform: translateX(8px);
    scale: 1.05;
}
</style>