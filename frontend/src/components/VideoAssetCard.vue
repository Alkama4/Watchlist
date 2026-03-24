<script setup>
import { ref, computed } from 'vue'; // Added ref
import { buildVideoAssetUrl } from '@/utils/titleUtils';
import { timeFormatters } from '@/utils/formatters';
import { ChevronDown } from '@boxicons/vue';

const props = defineProps({
    video: { type: Object, required: true },
    title: { type: Object, default: () => ({}) },
    season: { type: [Object, Number, String], default: null },
    episode: { type: Object, default: () => ({}) },
});

const showSpecs = ref(false);


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

const toggleSpecs = () => {
    showSpecs.value = !showSpecs.value;
};

const msToMin = (ms) => {
    return Math.floor(ms / 1000 / 60)
}

const getDeviceHandler = () => {
    // Check modern User-Agent Client Hints (Chrome, Edge, etc.)
    if (navigator.userAgentData?.platform) {
        return navigator.userAgentData.platform === "Android" ? 'mpv-kt' : 'mpv-handler';
    }
    
    // Fallback to the standard userAgent string (Firefox, Safari, older browsers)
    const ua = navigator.userAgent;
    if (/android/i.test(ua)) {
        return 'mpv-kt';
    }

    return 'mpv-handler';
};

const videoAssetUrl = computed(() => {
    const handlerType = getDeviceHandler();
    return buildVideoAssetUrl(props.video, props.title, handlerType, props.season, props.episode);
});

</script>

<template>
    <a 
        :href="videoAssetUrl"
        class="video-card btn btn-text no-deco"
    >
        <div class="card-header">
            <div class="main-section">
                <h5 
                    class="video-title" 
                    :class="{ 'is-expanded': showSpecs }"
                >
                    {{ getVideoLabel(video) }}
                </h5>
                                
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

            <div class="toggle-specs-wrapper">
                <button 
                    class="toggle-specs-btn btn-text btn-even-padding" 
                    @click.stop.prevent="toggleSpecs"
                    :class="{ 'active': showSpecs }"
                >
                    <ChevronDown/>
                </button>
            </div>
        </div>

        <div class="card-specs" :class="{ 'is-expanded': showSpecs }">
            <div class="specs-target">
                <div class="specs-wrapper">
                    <span class="spec-item duration">
                        {{ timeFormatters.minutesToHrAndMin(msToMin(video?.duration_ms)) }}
                    </span>
                    <span class="seperator">&bull;</span>

                    <span class="spec-item codec">{{ video?.codec }}</span>
                    <span class="seperator">&bull;</span>
                    <span class="spec-item">{{ video?.bit_depth }} bit</span>
                    <span class="seperator">&bull;</span>
                    <span class="spec-item">{{ Math.round(video?.frame_rate) }} fps</span>
                    <span class="seperator">&bull;</span>

                    <span class="spec-item">{{ formatBitrate(video?.filesize_bytes, video?.duration_ms) }}</span>
                    <span class="seperator">&bull;</span>
                    <span class="spec-item filesize">{{ formatSize(video?.filesize_bytes) }}</span>
                </div>
            </div>
        </div>
    </a>
</template>

<style scoped>
.video-card {
    display: flex;
    flex-direction: column;
    align-items: start;
    gap: 0;
    padding: var(--spacing-sm) var(--spacing-sm-md);
    flex-shrink: 0;
}

.card-header {
    display: flex;
    flex-direction: row;
    gap: var(--spacing-xs);
    width: 100%;
}

.main-section {
    display: flex;
    flex-direction: column;
    flex: 1;
    min-width: 0;
    gap: var(--spacing-sm);
}

.video-title {
    color: var(--c-text-strong);
    margin: 0;
    line-height: 1.3;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    flex: 1;
    min-width: 0;

    &.is-expanded {
        white-space: normal;
        overflow: visible;
        text-overflow: clip;
        word-break: break-word;
    }
}



.toggle-specs-wrapper {
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
    
    .toggle-specs-btn {
        margin-left: var(--spacing-sm);
        
        svg {
            transition: transform 0.1s var(--transition-ease-out);
        }
        &.active svg {
            transform: rotate(180deg);
        }
    }
}


.badge-group {
    display: flex;
    flex-wrap: nowrap;
    align-items: center;
    gap: var(--spacing-xs);
    color: var(--c-text-soft);
}

.badge {
    font-size: 0.66rem;
    font-weight: 700;
    padding: 2px 6px;
    border-radius: 4px;
    white-space: nowrap;
}

.res-badge {
    background-color: var(--c-text-strong);
    color: var(--c-bg-base);
}
.hdr-badge {
    background-color: var(--c-neutral);
    color: var(--c-text);

    &.dolby-vision {
        background-color: var(--c-accent);
        color: var(--c-text-white);
    }
    &.hdr10-plus {
        background-color: var(--c-favourite);
        color: var(--c-text-white);
    }
    &.hdr10 {
        background-color: var(--c-warning);
        color: var(--c-text-black);
    }
    &.sdr {
        background-color: transparent;
        border: 1px solid var(--c-border);
        color: var(--c-text-subtle);
    }
}

/* Collapsible Specs Logic */
.card-specs {
    display: grid;
    grid-template-rows: 0fr;
    transition: grid-template-rows 0.15s var(--transition-ease-out),
                opacity 0.15s var(--transition-ease-out);
    opacity: 0;
    overflow: hidden;
    width: 100%;
}

.card-specs.is-expanded {
    grid-template-rows: 1fr;
    opacity: 1;
}

/* This inner div ensures the content doesn't pop in abruptly */
.specs-target {
    min-height: 0;
}

.specs-wrapper {
    margin-top: var(--spacing-sm);
    display: flex;
    align-items: center;
    gap: var(--spacing-xs);
    font-size: var(--fs-neg-1);
    color: var(--c-text-soft);
}

.spec-item {
    white-space: nowrap;
}

.seperator {
    opacity: 0.5;
}
</style>