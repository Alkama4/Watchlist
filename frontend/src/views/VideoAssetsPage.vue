<script setup>
import LoadingButton from '@/components/LoadingButton.vue';
import VideoAssetTitleFolder from '@/components/VideoAssetTitleFolder.vue';
import { fastApi } from '@/utils/fastApi';
import { onMounted, ref } from 'vue';

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

onMounted(async () => {
    await fetchVideoAssetTitleFolders();
});
</script>

<template>
    <div class="video-assets-page layout-contained">
        <h1>Video Assets</h1>

        <LoadingButton
            :loading="waitingFor?.vidoeAssetSync"
            @click="syncVideoAssets"
        >
            Manually sync video assets
        </LoadingButton>

        <h2>Unlinked Title Folders</h2>
        <div class="title-folder-wrapper">
            <VideoAssetTitleFolder
                v-for="titleFolder in videoAssetTitleFolders?.unlinked_video_asset_title_folders"
                :titleFolder="titleFolder"
                :key="titleFolder.title_folder_path"
            />
        </div>
        
        <h2>Linked Title Folders</h2>
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
.title-folder-wrapper {
    display: flex;
    flex-direction: column;
    row-gap: var(--spacing-sm-md);
}
</style>