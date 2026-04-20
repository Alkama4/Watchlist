<script setup>
import { ArrowOutUpRightSquare, Check, ChevronDown, File, Folder, FolderCheck, Link, Play, Search, Unlink } from '@boxicons/vue';
import ExpandableWrapper from './ExpandableWrapper.vue';
import { fastApi } from '@/utils/fastApi';
import { computed, ref } from 'vue';
import { videoAssetFormatters } from '@/utils/formatters';
import ModalVideoAssetDetails from './modal/ModalVideoAssetDetails.vue';
import { buildVideoAssetUrl, getDeviceHandler } from '@/utils/videoAssetUtils';
import { useMediaQuery } from '@/utils/useMediaQuery';

const props = defineProps({
    titleFolder: {
        type: Object,
        required: true,
    },
});

const ModalAssetDetails = ref(null);
const modalAsset = ref({});

async function fetchTitleFolderAssets() {
    props.titleFolder.loading = true;
    try {
        props.titleFolder.assets = await fastApi.media.videoAssets.titleFolderAssets(
            props.titleFolder.title_folder_path
        );
    } finally {
        props.titleFolder.loading = false;
    }
}

async function toggleTitleFolderAsset() {
    if (props.titleFolder?.isOpen) {
        props.titleFolder.isOpen = false;
    } else {
        if (!props.titleFolder?.assets) {
            await fetchTitleFolderAssets();
        }
        props.titleFolder.isOpen = true;
    }
}

function openModalAssetDetails(asset) {
    modalAsset.value = asset;
    ModalAssetDetails.value.open();
}


const isMobile = useMediaQuery('(max-width: 768px)');
const assetSummary = computed(() => {
    const counts = props.titleFolder?.counts || {};
    const parts = [];

    if (counts.movie_count > 0) {
        parts.push(`${counts.movie_count} Movie${counts.movie_count > 1 ? 's' : ''}`);
    }
    
    if (counts.episodes_count > 0) {
        parts.push(`${counts.episodes_count} Episode${counts.episodes_count > 1 ? 's' : ''}`);
    }
    
    if (counts.featurette_count > 0) {
        parts.push(`${counts.featurette_count} Feature${counts.featurette_count > 1 ? 's' : ''}`);
    }
    
    return parts.length ? parts : ['0 Assets'];
});
</script>

<template>
    <div class="video-asset-title-folder">
        <button
            class="main-button btn-text"
            @click="toggleTitleFolderAsset(titleFolder)"
        >
            <FolderCheck
                v-if="titleFolder?.counts?.unlinked_count == 0"
                pack="filled"
                color="var(--c-positive)"
            />
            <FolderCheck
                v-else-if="titleFolder?.counts?.unlinked_count > 0 && titleFolder?.counts?.file_count - titleFolder?.counts?.unlinked_count > 0"
                pack="filled"
                color="var(--c-warning)"
            />
            <Folder v-else color="var(--c-text-subtle)"/>

            <div class="main-details">
                <h5 class="folder-name break-all">/{{ titleFolder?.title_folder_name }}</h5>
                <div class="meta-row">
                    <span>
                        {{ titleFolder?.counts?.file_count - titleFolder?.counts?.unlinked_count }}/{{ titleFolder?.counts?.file_count }}
                        {{ isMobile ? 'Linked' : 'Assets Linked' }}
                    </span>
                    <template v-if="titleFolder?.counts?.title_episode_count">
                        <span class="seperator">&bull;</span>
                        <span>
                            {{ titleFolder?.counts?.unique_episodes_linked }}/{{ titleFolder?.counts?.title_episode_count }}
                            {{ isMobile ? 'Episodes' : 'Episodes With Link' }}
                        </span>
                    </template>
                </div>
                <div class="meta-row">
                    <template v-for="(summary, index) in assetSummary">
                        <span>{{ summary }}</span>
                        <span v-if="index < assetSummary?.length - 1" class="seperator">&bull;</span>
                    </template>
                </div>
            </div>
            <div>
                <RouterLink
                    v-if="titleFolder?.is_linked"
                    :to="`/title/${titleFolder?.title_id}`"
                    target="_blank"
                    class="btn btn-mobile-icon-padding no-deco"
                    @click.stop
                >
                    <ArrowOutUpRightSquare size="sm"/>
                    <span class="desktop-only">View Linked Title</span>
                </RouterLink>
                <RouterLink
                    v-else
                    :to="`/search?q=${titleFolder?.title_folder_name?.split(' (')[0]}&tmdb=true`"
                    target="_blank"
                    @click.stop
                    class="btn btn-primary btn-mobile-icon-padding no-deco"
                >
                    <Search size="sm"/>
                    <span class="desktop-only">Search for title</span>
                </RouterLink>
            </div>
            <div>
                <ChevronDown class="chevron" :class="{'active': titleFolder?.isOpen }"/>
            </div>
        </button>
        <ExpandableWrapper :isExpanded="titleFolder?.isOpen">
            <div class="asset-list">
                <template
                    v-for="(asset, index) in titleFolder?.assets"
                    :key="asset.video_asset_id"
                >
                    <button
                        class="video-asset btn-text"
                        @click.prevent="openModalAssetDetails(asset)"
                    >
                        <div class="asset-icon-wrapper">
                            <File v-if="!asset?.is_linked" color="var(--c-text-faint)" />
                            <File v-else color="var(--c-positive)" pack="filled" />
                        </div>

                        <div class="main-details">
                            <h5 class="file-name break-all">{{ asset?.file_name }}</h5>

                            <div class="meta-row">
                                <div v-if="asset?.is_linked" class="badge badge-sm linked">
                                    <Link size="xs"/>
                                    <span>{{ asset?.title?.name }}
                                        <template v-if="asset?.episode">
                                            - S{{ String(asset?.episode?.season_number).padStart(2, '0') }}
                                            E{{ String(asset?.episode?.episode_number).padStart(2, '0') }}
                                        </template>
                                    </span>
                                </div>
                                <div v-else class="badge badge-sm unlinked-placeholder">
                                    <Unlink size="xs"/>
                                    <span>Not Linked</span>
                                </div>

                                <span class="seperator">&bull;</span>
                                <span>{{ asset?.video_type }}</span>
                                <span class="seperator">&bull;</span>
                                <span>{{ asset?.resolution }}</span>
                                <span class="seperator">&bull;</span>
                                <span>{{ videoAssetFormatters.formatSize(asset?.filesize_bytes) }}</span>
                            </div>
                        </div>

    
                        <div class="actions" @click.stop>
                            <a
                                :href="buildVideoAssetUrl(asset, null, getDeviceHandler())"
                                class="btn btn-mobile-icon-padding no-deco"
                            >
                                <Play pack="filled" size="sm"/>
                                <span class="desktop-only">Play</span>
                            </a>
                        </div>
                    </button>
                </template>
            </div>
        </ExpandableWrapper>

        <ModalVideoAssetDetails ref="ModalAssetDetails" :videoAsset="modalAsset"/>
    </div>
</template>

<style scoped>
.video-asset-title-folder {
    display: flex;
    flex-direction: column;
    background-color: var(--c-bg-level-1);
    border-radius: var(--border-radius-md);
    border: 1px solid var(--c-border);
    overflow: hidden;
}

.main-button {
    gap: var(--spacing-md);
    padding: var(--spacing-sm-md) var(--spacing-md);
    justify-content: start;
    border-radius: 0;
    border: 1px solid var(--c-borde);

    .chevron {
        transition: transform 0.1s ease-out;
        &.active { transform: rotate(180deg); }
    }
}

.main-details {
    display: flex;
    flex-direction: column;
    align-items: start;
    flex: 1;
    gap: var(--spacing-xs);
}

h5 {
    text-align: left;
    margin: 0;
    display: -webkit-box;
    -webkit-line-clamp: 1;
    line-clamp: 1;
    -webkit-box-orient: vertical;
    overflow: hidden;
}

.meta-row {
    display: flex;
    flex-wrap: wrap;
    gap: var(--spacing-xs);
    color: var(--c-text-soft);
    font-weight: 400;
    align-items: center;

    span {
        text-align: start;
    }
}

.asset-list {
    border-top: 1px solid var(--c-border);
    display: flex;
    flex-direction: column;
    padding: var(--spacing-sm);
    background-color: var(--c-bg);
}

.video-asset {
    display: flex;
    gap: var(--spacing-md);
    padding: var(--spacing-sm-md) var(--spacing-sm);
}

.asset-icon-wrapper {
    display: flex;
}

.badge {
    display: flex;
    align-items: center;
    gap: 4px;
    font-weight: 500;
    background-color: var(--c-neutral);
    color: var(--c-text);

    &.unlinked-placeholder {
        background-color: transparent;
        border: 1px dashed var(--c-border);
        color: var(--c-text-faint);
        height: 20px;
        box-sizing: border-box;
    }
}
</style>