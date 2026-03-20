<script setup>
import { defineProps } from 'vue';
import { buildVideoAssetUrl } from '@/utils/titleUtils';
import { timeFormatters } from '@/utils/formatters';

const props = defineProps({
    video: { type: Object, required: true },
    title: { type: Object, default: () => ({}) },
    season: { type: [Object, Number, String], default: null },
    episode: { type: Object, default: () => ({}) },
});

const getHdrTags = (hdrString) => {
    if (!hdrString || hdrString.trim() === "") return ['SDR'];
    const tags = [];
    if (hdrString.includes('Dolby Vision')) tags.push('Dolby Vision');
    if (hdrString.includes('2094 App 4')) tags.push('HDR10+');
    if (hdrString.includes('2086')) tags.push('HDR10');
    return tags.length > 0 ? [...new Set(tags)] : ['SDR'];
};

const formatSize = (bytes) => {
    if (!bytes) return '';
    const gb = bytes / (1024 ** 3);
    return gb >= 1 ? `${gb.toFixed(2)} GB` : `${(bytes / (1024 ** 2)).toFixed(1)} MB`;
};

const formatBitrate = (bytes, ms) => {
    if (!bytes || !ms) return '';
    const mbps = (bytes * 8) / (ms * 1000);
    return `${mbps.toFixed(1)} Mbps`;
};

const formatResolution = (resString) => {
    if (!resString || !resString.includes('x')) return resString;
    const [width, height] = resString.split('x').map(Number);
    const heightFromWidth = Math.round(width * (9 / 16));
    const effectiveHeight = Math.max(height, heightFromWidth);
    return `${effectiveHeight}p`;
};

const getVideoLabel = (video) => {
    if (video?.video_type === 'episode') {
        return `${props.title?.name} (${timeFormatters.timestampToYear(props.title?.release_date)}) - S${props.season?.season_number}E${props.episode?.episode_number}`;
    } else if (video?.video_type === 'movie') {
        return `${props.title?.name} (${timeFormatters.timestampToYear(props.title?.release_date)})`;
    } else {
        return video?.file_name?.split(".")[0] || 'Unknown Source';
    }
};
</script>

<template>
    <a 
        :href="buildVideoAssetUrl(video, title, 'mpv-handler', season, episode)"
        class="video-card btn btn-text no-deco"
    >
        <div class="card-header">
            <h5 class="video-title">{{ getVideoLabel(video) }}</h5>
            <div class="badge-group">
                <span class="badge res-badge">{{ formatResolution(video?.resolution) }}</span>
                <span 
                    v-for="tag in getHdrTags(video?.hdr_type)" 
                    :key="tag"
                    :class="['badge', 'hdr-badge', tag.toLowerCase().replace('+', '-plus').replace(' ', '-')]"
                >
                    {{ tag }}
                </span>
            </div>
        </div>

        <div class="card-specs">
            <span class="spec-item spec-codec">{{ video?.codec }}</span>
            <span class="spec-dot">&bull;</span>
            <span class="spec-item">{{ video?.bit_depth }} bit</span>
            <span class="spec-dot">&bull;</span>
            <span class="spec-item">{{ Math.round(video?.frame_rate) }} fps</span>
            <span class="spec-dot">&bull;</span>
            <span class="spec-item">{{ formatSize(video?.filesize_bytes) }}</span>
            <template v-if="video?.duration_ms">
                <span class="spec-dot">&bull;</span>
                <span class="spec-item">{{ formatBitrate(video?.filesize_bytes, video?.duration_ms) }}</span>
            </template>
        </div>
    </a>
</template>

<style scoped>
.video-card {
    display: flex;
    flex-direction: column;
    align-items: start;
    gap: var(--spacing-xs);
    padding: var(--spacing-sm) var(--spacing-sm-md);
    flex-shrink: 0; /* Prevents squishing in restricted height containers */
}

.card-header {
    display: flex;
    flex-direction: column;
    gap: var(--spacing-xs);
}

.video-title {
    color: var(--c-text-strong);
    margin: 0;
    line-height: 1.3;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

.badge-group {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    gap: var(--spacing-xs);
}

.badge {
    font-size: var(--fs-neg-2);
    font-weight: 700;
    padding: 3px 6px;
    border-radius: 4px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    white-space: nowrap;
}

.res-badge {
    background-color: var(--c-text-strong);
    color: var(--c-bg-base);
}

.hdr-badge {
    background-color: var(--c-neutral);
    color: var(--c-text);
}

.hdr-badge.dolby-vision { background-color: var(--c-accent); }
.hdr-badge.hdr10-plus { background-color: var(--c-favourite); }
.hdr-badge.hdr10 { 
    background-color: var(--c-warning); 
    color: var(--c-text-black);
}
.hdr-badge.sdr { 
    background-color: transparent; 
    border: 1px solid var(--c-border); 
    color: var(--c-text-subtle);
}

.card-specs {
    display: flex;
    align-items: center;
    flex-wrap: nowrap;
    gap: 6px;
    font-size: var(--fs-neg-1);
    color: var(--c-text-soft);
    margin-top: 2px;
}

.spec-item { white-space: nowrap; }
.spec-codec { font-weight: 600; color: var(--c-text); }
.spec-dot { font-size: 0.8em; opacity: 0.5; user-select: none; }
</style>