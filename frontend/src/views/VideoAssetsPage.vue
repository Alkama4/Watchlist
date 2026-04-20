<script setup>
import LoadingButton from '@/components/LoadingButton.vue';
import VideoAssetTitleFolder from '@/components/VideoAssetTitleFolder.vue';
import { fastApi } from '@/utils/fastApi';
import { RefreshCwAlt } from '@boxicons/vue';
import { computed, onMounted, ref } from 'vue';

const waitingFor = ref({});
const videoAssetTitleFolders = ref({});

async function fetchVideoAssetTitleFolders() {
    waitingFor.value.pageLoad = true;
    try {
        videoAssetTitleFolders.value = await fastApi.media.videoAssets.titleFolders();
    } finally {
        waitingFor.value.pageLoad = false;
    }
}

async function syncVideoAssets() {
    waitingFor.value.vidoeAssetSync = true;
    try {
        const response = await fastApi.media.videoAssets.sync();
        alert(`added_video_assets_count: ${response.details.added_video_assets_count}
removed_video_assets_count: ${response.details.removed_video_assets_count}
added_links_count: ${response.details.added_links_count}
removed_links_count: ${response.details.removed_links_count}`)
    } catch(e) {
        // alert(JSON.parse(e.request.response).detail);
    } finally {
        waitingFor.value.vidoeAssetSync = false;
        await fetchVideoAssetTitleFolders();
    }
}

const totalLinkedProgressPercent = computed(() => {
    const total = videoAssetTitleFolders.value?.counts?.total_video_assets || 0;
    const linked = videoAssetTitleFolders.value?.counts?.total_linked_video_assets || 0;
    if (total === 0) return 0;
    return Math.min(100, (linked / total) * 100);
});

onMounted(async () => {
    await fetchVideoAssetTitleFolders();
});
</script>

<template>
    <div class="video-assets-page layout-contained layout-spacing-top layout-spacing-bottom">
        <h1 class="page-header">
            <span>Video Assets</span>
            <LoadingButton
                :loading="waitingFor?.vidoeAssetSync"
                @click="syncVideoAssets"
            >
                <RefreshCwAlt size="sm"/>
                <span class="desktop-only">Scan and Sync</span>
                <span class="mobile-only">Scan</span>
            </LoadingButton>
        </h1>

        <section class="overview">
            <div class="cards-holder">
                <div class="stat-card">
                    <label>Video Assets in Total</label>
                    <strong>{{ videoAssetTitleFolders?.counts?.total_video_assets ?? '-' }}</strong>
                </div>
                <div class="stat-card">
                    <label>Movie Assets</label>
                    <strong>{{ videoAssetTitleFolders?.counts?.total_movies ?? '-' }}</strong>
                </div>
                <div class="stat-card">
                    <label>Episode Assets</label>
                    <strong>{{ videoAssetTitleFolders?.counts?.total_episodes ?? '-' }}</strong>
                </div>
                <div class="stat-card">
                    <label>Featurette Assets</label>
                    <strong>{{ videoAssetTitleFolders?.counts?.total_featurettes ?? '-' }}</strong>
                </div>
            </div>

            <div class="progress-indicator-area">
                <label>Assets Linked</label>
                <div class="progress-indicator">
                    <div class="bar" :style="{'width': `${totalLinkedProgressPercent}%`}"></div>
                    
                    <div class="details">
                        {{ videoAssetTitleFolders?.counts?.total_linked_video_assets ?? 0 }} /
                        {{ videoAssetTitleFolders?.counts?.total_video_assets ?? 0 }}
                        ({{ totalLinkedProgressPercent.toFixed(2) }}%)
                    </div>
                </div>
            </div>
        </section>

        <h3>
            Unlinked Title Folders
            <template v-if="videoAssetTitleFolders?.unlinked_video_asset_title_folders?.length">
                ({{ videoAssetTitleFolders?.unlinked_video_asset_title_folders?.length }})
            </template>
        </h3>
        <div
            v-if="waitingFor?.pageLoad || videoAssetTitleFolders?.unlinked_video_asset_title_folders"
            class="title-folder-wrapper"
        >
            <template v-if="waitingFor?.pageLoad">
                <div v-for="skeleton in 5" :key="skeleton" class="title-folder-skeleton loading-wave"></div>
            </template>
            <template v-else>
                <VideoAssetTitleFolder
                    v-for="titleFolder in videoAssetTitleFolders?.unlinked_video_asset_title_folders"
                    :titleFolder="titleFolder"
                    :key="titleFolder.title_folder_path"
                />
            </template>
        </div>
        <div
            v-else
            class="card not-found-section" 
        >
            <h2>All Folders Linked</h2>
            <p>Everything is organized! All detected folders are currently associated with a title.</p>
        </div>
        
        <h3>
            Linked Title Folders
            <template v-if="videoAssetTitleFolders?.linked_video_asset_title_folders?.length">
                ({{ videoAssetTitleFolders?.linked_video_asset_title_folders?.length }})
            </template>
        </h3>
        <div
            v-if="waitingFor?.pageLoad || videoAssetTitleFolders?.linked_video_asset_title_folders"
            class="title-folder-wrapper"
        >
            <template v-if="waitingFor?.pageLoad">
                <div v-for="skeleton in 5" :key="skeleton" class="title-folder-skeleton loading-wave"></div>
            </template>
            <template v-else>
                <VideoAssetTitleFolder
                    v-for="titleFolder in videoAssetTitleFolders?.linked_video_asset_title_folders"
                    :titleFolder="titleFolder"
                    :key="titleFolder.title_folder_path"
                />
            </template>
        </div>
        <div
            v-else
            class="card not-found-section" 
        >
            <h2>No Folders Linked</h2>
            <p>No assets have been linked yet. Get started by scanning for new assets and by searching for the unlinked titles.</p>
        </div>
    </div>
</template>

<style scoped>
/* ---------- Overview ---------- */
.page-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
}

section.overview {
    display: flex;
    flex-direction: column;
    row-gap: var(--spacing-md);
}
.cards-holder {
    display: grid;
    grid-template-columns: 1fr 1fr 1fr 1fr;
    gap: var(--spacing-sm-md);
}

@media (max-width: 768px) {
    .cards-holder {
        grid-template-columns: 1fr 1fr;
    }
}

.stat-card {
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    background-color: var(--c-bg-level-1);
    border-radius: var(--border-radius-md-lg);
    padding: var(--spacing-md-lg) var(--spacing-md);
    text-align: center;

    label {
        color: var(--c-text-subtle);
        font-size: var(--fs-neg-1);
    }

    strong {
        font-size: var(--fs-2);
    }
}

.progress-indicator {
    background-color: var(--c-bg-level-2);
    width: 100%;
    height: var(--spacing-lg);
    border-radius: var(--border-radius-md);
    position: relative;
    overflow: hidden; /* Keep the bar inside the rounded corners */

    .bar {
        height: 100%;
        background-color: var(--c-primary);
        transition: width 1.25s var(--transition-ease-out-str);
    }

    .details {
        position: absolute;
        inset: 0;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: var(--fs-neg-2);
        font-weight: 500;
        pointer-events: none;
        
        color: var(--c-text); 
        mix-blend-mode: difference; 
    }
}


/* ---------- Title Folders ---------- */

.title-folder-wrapper {
    display: flex;
    flex-direction: column;
    row-gap: var(--spacing-sm-md);
}

.title-folder-skeleton {
    height: 84px;
    border-radius: var(--border-radius-md);
}
</style>