<script setup>
import LoadingButton from '@/components/LoadingButton.vue';
import VideoAssetTitleFolder from '@/components/VideoAssetTitleFolder.vue';
import { fastApi } from '@/utils/fastApi';
import { RefreshCwAlt } from '@boxicons/vue';
import { computed, onMounted, ref } from 'vue';

const waitingFor = ref({});
const videoAssetTitleFolders = ref({});

async function fetchVideoAssetTitleFolders() {
    videoAssetTitleFolders.value = await fastApi.media.videoAssets.titleFolders();
}

async function syncVideoAssets() {
    waitingFor.value.vidoeAssetSync = true;
    try {
        const response = await fastApi.media.videoAssets.sync();
        alert(`${response.message} ${response.details.added_links} links added, ${response.details.removed_links} links removed, ${response.details.total_links} links in total, ${response.details.total_titles_with_links} titles with links.`)
    } catch(e) {
        alert(JSON.parse(e.request.response).detail);
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
    <div class="video-assets-page layout-contained">
        <h1 class="page-header">
            <span>Video Assets</span>
            <LoadingButton
                :loading="waitingFor?.vidoeAssetSync"
                @click="syncVideoAssets"
            >
                <RefreshCwAlt size="sm"/>
                <span>Scan and Sync</span>
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

        <h3>Unlinked Title Folders ({{ videoAssetTitleFolders?.unlinked_video_asset_title_folders?.length }})</h3>
        <div class="title-folder-wrapper">
            <VideoAssetTitleFolder
                v-for="titleFolder in videoAssetTitleFolders?.unlinked_video_asset_title_folders"
                :titleFolder="titleFolder"
                :key="titleFolder.title_folder_path"
            />
        </div>
        
        <h3>Linked Title Folders ({{ videoAssetTitleFolders?.linked_video_asset_title_folders?.length }})</h3>
        <div class="title-folder-wrapper">
            <VideoAssetTitleFolder
                v-for="titleFolder in videoAssetTitleFolders?.linked_video_asset_title_folders"
                :titleFolder="titleFolder"
                :key="titleFolder.title_folder_path"
            />
        </div>
    </div>
</template>

<style scoped>
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

.title-folder-wrapper {
    display: flex;
    flex-direction: column;
    row-gap: var(--spacing-sm-md);
}
</style>