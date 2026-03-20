<script setup>
import { defineProps } from 'vue';
import LabelDropDown from './LabelDropDown.vue';
import VideoAssetCard from './VideoAssetCard.vue';

const props = defineProps({
    videoAssets: { type: [Object, Array], default: () => [] },
    title: { type: Object, default: () => ({}) },
    season: { type: [Object, Number, String], default: null },
    episode: { type: Object, default: () => ({}) },
});
</script>

<template>
    <LabelDropDown v-if="videoAssets && videoAssets.length" label="Video Assets" class="video-dropdown">
        <div class="video-list">
            <VideoAssetCard 
                v-for="video in videoAssets" 
                :key="video?.video_asset_id"
                :video="video"
                :title="title"
                :season="season"
                :episode="episode"
            />
        </div>
    </LabelDropDown>
</template>

<style scoped>
.video-dropdown {
    display: flex;
    flex-direction: column;
}

.video-list {
    display: flex;
    flex-direction: column;
    gap: var(--spacing-xs);
    padding: var(--spacing-xs);
    max-height: 40vh;
    overflow-y: auto;
}

/* Featurettes header if you decide to use it for sectioning later */
.featurettes-header {
    font-size: var(--fs-neg-1);
    font-weight: 700;
    text-transform: uppercase;
    color: var(--c-text-subtle);
    padding: var(--spacing-md) var(--spacing-md) var(--spacing-xs);
    border-top: 1px solid var(--c-border-subtle, var(--c-border));
    margin-top: var(--spacing-sm);
    letter-spacing: 0.5px;
}
</style>