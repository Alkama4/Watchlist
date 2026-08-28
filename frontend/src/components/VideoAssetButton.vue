<script setup>
import { ChevronDown, Play } from '@boxicons/vue';
import { ref, computed } from 'vue';
import ResponsiveOverlay from './ResponsiveOverlay.vue';
import VideoAssetListing from './VideoAssetListing.vue';
import { buildVideoAssetUrl, getDeviceHandler } from '@/utils/videoAssetUtils.js';

const props = defineProps({
    titleDetails: {
        type: Object,
        default: {}
    },
    isPrimary: {
        type: Boolean,
        default: true
    }
});

const videoAssetOverlay = ref(null);

const primaryAssetCandidate = computed(() => {
    const assets = props.titleDetails?.video_assets ?? [];
    return assets
        .filter(asset => asset.video_type === 'movie')
        .sort((a, b) => b.filesize_bytes - a.filesize_bytes)[0];
})
</script>

<template>
    <div class="video-asset-button" v-if="primaryAssetCandidate">
        <a
            :href="buildVideoAssetUrl(primaryAssetCandidate, titleDetails, getDeviceHandler())"
            class="btn no-deco"
            :class="{'btn-primary': isPrimary}"
        >
            <Play pack="filled"/>
            Play
        </a>
        <button
            class="btn-even-padding"
            :class="{'btn-primary': isPrimary}"
            @click="videoAssetOverlay.open()"
        >
            <ChevronDown/>
        </button>
    </div>

    <ResponsiveOverlay ref="videoAssetOverlay" header="Video Assets">
        <VideoAssetListing
            :videoAssets="titleDetails?.video_assets"
            :title="titleDetails"
        />
    </ResponsiveOverlay>
</template>

<style scoped>
.video-asset-button {
    display: flex;
    border-radius: 1000px;
    overflow: hidden;
    width: fit-content;
    
    a {
        padding: var(--spacing-sm-md) var(--spacing-md-lg);
        border-top-right-radius: 0;
        border-bottom-right-radius: 0;
        flex: 1;
    }
    button {
        border-top-left-radius: 0;
        border-bottom-left-radius: 0;
        padding-right: var(--spacing-md);
    }
}

@media (max-width: 768px) {
    .video-asset-button {
        width: 100%;
        min-width: fit-content;
    }
}
</style>