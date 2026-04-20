<script setup>
import { computed } from 'vue';
import VideoAssetCard from './VideoAssetCard.vue';

const props = defineProps({
    videoAssets: { type: [Object, Array], default: () => [] },
    title: { type: Object, default: () => ({}) },
    season: { type: [Object, Number, String], default: null },
    episode: { type: Object, default: () => ({}) },
});

// Group assets by video_type
const groupedAssets = computed(() => {
    const rawData = props.videoAssets || []; 
    
    const assets = Array.isArray(rawData) 
        ? rawData 
        : Object.values(rawData);

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
    <div class="video-asset-listing">
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
</template>

<style scoped>
.video-asset-listing {
    display: flex;
    flex-direction: column;
    gap: var(--spacing-xs);
    /* max-height: 40vh; */
    overflow-y: auto;
}

.asset-group {
    display: flex;
    flex-direction: column;
    gap: 2px;
}

.group-header {
    font-weight: 600;
    color: var(--c-text-subtle);
    padding: var(--spacing-sm) 0 var(--spacing-xs);
    top: 0;
    z-index: 1;
    margin: 0;
}
</style>