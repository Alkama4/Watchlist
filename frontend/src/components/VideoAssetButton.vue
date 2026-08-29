<script setup>
import { ChevronDown, Play } from '@boxicons/vue';
import { ref, computed } from 'vue';
import ResponsiveOverlay from './ResponsiveOverlay.vue';
import VideoAssetListing from './VideoAssetListing.vue';
import { buildVideoAssetUrl, getDeviceHandler } from '@/utils/videoAssetUtils.js';

const props = defineProps({
    titleDetails: {
        type: Object,
        default: () => ({})
    },
    isPrimary: {
        type: Boolean,
        default: true
    },
    seasonNum: {
        type: Number,
        default: null
    },
    episodeNum: {
        type: Number,
        default: null
    }
});

const videoAssetOverlay = ref(null);

const isEpisodeMode = computed(() => {
    return props.seasonNum != null && props.episodeNum != null;
});

const targetEpisode = computed(() => {
    if (!isEpisodeMode.value) return null;

    const season = props.titleDetails?.seasons?.find((s) => s.season_number === props.seasonNum);
    return season?.episodes?.find((e) => e.episode_number === props.episodeNum) ?? null;
});

const allAssets = computed(() => {
    const assets = isEpisodeMode.value 
        ? targetEpisode.value?.video_assets 
        : props.titleDetails?.video_assets;

    return assets?.length ? assets : null;
});

const defaultVideoAsset = computed(() => {
    if (!allAssets.value) return null;

    const playables = isEpisodeMode.value
        ? allAssets.value
        : allAssets.value.filter(asset => asset.video_type === 'movie');

    if (!playables.length) return null;

    return [...playables].sort((a, b) => b.filesize_bytes - a.filesize_bytes)[0];
});
</script>

<template>
    <div class="video-asset-button" v-if="allAssets">
        <a
            v-if="defaultVideoAsset"
            :href="buildVideoAssetUrl(defaultVideoAsset, titleDetails, getDeviceHandler(), seasonNum, episodeNum)"
            class="btn no-deco play-button"
            :class="{'btn-primary': isPrimary}"
        >
            <Play pack="filled"/>
            Play
        </a>
        <button
            v-else
            disabled
            class="btn no-deco play-button"
            :class="{'btn-primary': isPrimary}"
        >
            <Play pack="filled"/>
            Play
        </button>

        <button
            class="btn-even-padding more-button"
            :class="{'btn-primary': isPrimary}"
            @click="videoAssetOverlay.open()"
        >
            <ChevronDown/>
        </button>
    </div>

    <ResponsiveOverlay ref="videoAssetOverlay" header="Video Assets">
        <VideoAssetListing
            :videoAssets="isEpisodeMode ? targetEpisode?.video_assets : titleDetails?.video_assets"
            :title="titleDetails"
            :seasonNum="seasonNum"
            :episodeNum="episodeNum"
        />
    </ResponsiveOverlay>
</template>

<style scoped>
.video-asset-button {
    display: flex;
    width: fit-content;
    
    .play-button {
        padding: var(--spacing-sm-md) var(--spacing-md-lg);

        border-top-left-radius: 1000px;
        border-bottom-left-radius: 1000px;
        border-top-right-radius: 0;
        border-bottom-right-radius: 0;
        flex: 1;
    }
    .more-button {
        border-top-right-radius: 1000px;
        border-bottom-right-radius: 1000px;
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