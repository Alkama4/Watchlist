<script setup>
import { ref, reactive, onMounted, watch } from 'vue';
import { fastApi } from '@/utils/fastApi';
import AssetSummaryHeader from '@/components/AssetSummaryHeader.vue';
import AssetFilterBar from '@/components/AssetFilterBar.vue';
import AssetTable from '@/components/AssetTable.vue';

const loading = ref(false);
const syncLoading = ref(false);
const dashboardData = ref(null);

const filters = reactive({
  preset: 'all', // 'all' | 'needs_action' | 'incomplete_tv' | 'multi_version' | 'watchlist_deficit'
  search: '',
  title_type: null,
  sort_by: 'folder_name',
  sort_direction: 'asc',
  page: 1,
  page_size: 20
});

async function fetchDashboard() {
  loading.value = true;
  try {
    const params = { ...filters };
    dashboardData.value = await fastApi.media.videoAssets.getDashboard(params);
  } catch (err) {
    console.error('Failed to load asset dashboard:', err);
  } finally {
    loading.value = false;
  }
}

async function handleSync() {
  syncLoading.value = true;
  try {
    await fastApi.media.videoAssets.sync();
    await fetchDashboard();
  } finally {
    syncLoading.value = false;
  }
}

watch(filters, fetchDashboard, { deep: true });
onMounted(fetchDashboard);
</script>

<template>
  <div class="video-assets-manager layout-contained layout-spacing">
    <AssetSummaryHeader
      :summary="dashboardData?.summary"
      :sync-loading="syncLoading"
      @sync="handleSync"
    />

    <AssetFilterBar
      v-model:preset="filters.preset"
      v-model:search="filters.search"
      v-model:title-type="filters.title_type"
      v-model:sort-by="filters.sort_by"
      v-model:sort-direction="filters.sort_direction"
    />

    <AssetTable
      :items="dashboardData?.items || []"
      :pagination="dashboardData?.pagination"
      :loading="loading"
      @page-change="(p) => filters.page = p"
      @refresh="fetchDashboard"
    />
  </div>
</template>