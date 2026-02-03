<script setup>
import Flicking from "@egjs/vue3-flicking";
import SeasonCard from "../card/SeasonCard.vue";
import ModalSeason from "../ModalSeason.vue";

defineProps({
    seasons: {
        type: Object,
        required: true
    }
})
</script>

<template>
    <div class="carousel layout-full-contained">
        <div class="layout-contained">
            <h3>Seasons</h3>
        </div>
        <Flicking                     
            :options="{
                align: 'prev',
                bound: true,
                bounce: '33%',
                renderOnlyVisible: false,
            }"
        >
            <SeasonCard 
                v-for="season in seasons"
                :key="season.season_id"
                :seasonInfo="season"
                @click="$refs.SeasonModal.open(season)"
            />
        </Flicking>

        <ModalSeason ref="SeasonModal"/>
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

.season {
    width: 200px;
    display: inline-flex;
    flex-direction: column;
    text-decoration: none;
    position: relative;
    padding-right: var(--spacing-md);
}
.season:last-of-type {
    padding-right: 0;
}

img {
    border-radius: var(--border-radius-md);
    aspect-ratio: 2/3;
    object-fit: cover;
}

.details {
    display: flex;
    flex-direction: column;
    gap: var(--spacing-xs);
    margin-top: var(--spacing-xs-sm);
}

h5 {
    margin: 0;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

.detail-row {
    display: flex;
    align-items: center;
    gap: var(--spacing-xs);
    color: var(--c-text-3);
    font-size: var(--fs-neg-1);
}

</style>