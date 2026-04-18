<script setup>
import { ArrowOutUpRightSquare, Check, ChevronDown, File, Folder, FolderCheck, Play, Search } from '@boxicons/vue';
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

    // 2. Access the .value of the media query
    const mobile = isMobile.value;

    if (counts.movie_count > 0) {
        const label = mobile ? 'Mov' : 'Movie';
        parts.push(`${counts.movie_count} ${label}${counts.movie_count > 1 ? 's' : ''}`);
    }
    
    if (counts.episodes_count > 0) {
        const label = mobile ? 'Ep' : 'Episode';
        parts.push(`${counts.episodes_count} ${label}${counts.episodes_count > 1 ? 's' : ''}`);
    }
    
    if (counts.featurette_count > 0) {
        const label = mobile ? 'Feat' : 'Featurette';
        parts.push(`${counts.featurette_count} ${label}${counts.featurette_count > 1 ? 's' : ''}`);
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
                    class="btn no-deco"
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
                    class="btn btn-primary no-deco"
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
                        <Check v-if="asset?.is_linked" pack="filled" color="var(--c-positive)"/>
                        <File v-else color="var(--c-text-faint)"/>

                        <div class="main-details">
                            <h5 class="file-name break-all">{{ asset?.file_name }}</h5>

                            <div class="meta-row">
                                <div class="badge badge-sm" :class="asset?.video_type">{{ asset?.video_type }}</div>
                                <span class="seperator">&bull;</span>
                                <span>{{ asset?.resolution }}</span>
                                <span class="seperator">&bull;</span>
                                <span>{{ videoAssetFormatters.formatSize(asset?.filesize_bytes) }}</span>
                            </div>

                            <div class="meta-row">
                                <template v-if="asset?.is_linked">
                                    <span v-if="asset?.title">{{ isMobile ? '' : 'Linked to: ' }}{{ asset?.title?.name }}</span>
                                    <span v-if="asset?.episode">
                                        -
                                        S{{ String(asset?.episode?.season_number).padStart(2, '0') }}
                                        E{{ String(asset?.episode?.episode_number).padStart(2, '0') }}
                                    </span>
                                </template>
                                <template v-else>
                                    Not linked
                                </template>
                            </div>
                        </div>
    
                        <div class="actions" @click.stop>
                            <a
                                :href="buildVideoAssetUrl(asset, null, getDeviceHandler())"
                                class="btn no-deco"
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
    /* row-gap: var(--spacing-xs-sm); */

    .video-asset {
        display: flex;
        gap: var(--spacing-md);
        padding: var(--spacing-sm-md) var(--spacing-md);
    }

    .badge {
        background-color: var(--c-neutral);
        color: var(--c-text);
    }   
}
</style>