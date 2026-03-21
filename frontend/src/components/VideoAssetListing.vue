<script setup>
import { computed } from 'vue';
import LabelDropDown from './LabelDropDown.vue';
import VideoAssetCard from './VideoAssetCard.vue';

const props = defineProps({
    videoAssets: { type: [Object, Array], default: () => [] },
    title: { type: Object, default: () => ({}) },
    season: { type: [Object, Number, String], default: null },
    episode: { type: Object, default: () => ({}) },
});

// Group assets by video_type
const groupedAssets = computed(() => {
    const assets = Array.isArray(props.videoAssets) 
        ? props.videoAssets 
        : Object.values(props.videoAssets);

    return assets.reduce((groups, video) => {
        const type = video?.video_type || 'other';
        if (!groups[type]) groups[type] = [];
        groups[type].push(video);
        return groups;
    }, {});
});

const formatHeader = (type) => {
    if (!type) return 'Unknown Assets';
    const cleanType = type.toLowerCase();
    return cleanType.charAt(0).toUpperCase() + cleanType.slice(1) + 's';
};
</script>

<template>
    <LabelDropDown
        v-if="videoAssets && Object.keys(videoAssets).length"
        :label="`Video Assets (${videoAssets.length})`"
    >
        <div class="video-list">
            <div 
                v-for="(videos, type, index) in groupedAssets" 
                :key="type" 
                class="asset-group"
            >
                <hr v-if="index">

                <h6 class="group-header">
                    {{ formatHeader(type) }} ({{ videos.length }})
                </h6>

                <VideoAssetCard 
                    v-for="video in videos" 
                    :key="video?.video_asset_id"
                    :video="video"
                    :title="title"
                    :season="season"
                    :episode="episode"
                />
            </div>
        </div>
    </LabelDropDown>
</template>

<style scoped>
.video-list {
    display: flex;
    flex-direction: column;
    gap: var(--spacing-xs);
    max-height: clamp(300px, 50vh, 700px);
    overflow-y: auto;
}

.asset-group {
    display: flex;
    flex-direction: column;
    gap: 2px;
}

.group-header {
    font-weight: 600;
    /* letter-spacing: 1px; */
    /* text-transform: uppercase; */
    /* font-size: var(--fs-neg-2); */
    color: var(--c-text-subtle);
    padding: var(--spacing-sm) var(--spacing-sm-md) var(--spacing-xs);
    /* position: sticky; */
    top: 0;
    /* background: var(--c-bg-base); */
    /* backdrop-filter: blur(var(--blur-subtle)); */
    /* background-color: var(--c-bg-opaque-base); */
    z-index: 1;
    margin: 0;
}
</style>