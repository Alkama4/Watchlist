<script setup>
import { ref, reactive } from 'vue';
import { ChevronDown, ChevronRight, Eye, Film, Tv } from '@boxicons/vue';
import { fastApi } from '@/utils/fastApi';
import AssetInspector from './AssetInspector.vue';

const props = defineProps({
  items: { type: Array, required: true },
  pagination: { type: Object, default: null },
  loading: { type: Boolean, default: false }
});

const expandedRows = ref(new Set());
const detailsCache = reactive({});
const loadingDetails = reactive({});

async function toggleRow(folderId) {
  if (expandedRows.value.has(folderId)) {
    expandedRows.value.delete(folderId);
    return;
  }

  expandedRows.value.add(folderId);

  if (!detailsCache[folderId]) {
    loadingDetails[folderId] = true;
    try {
      detailsCache[folderId] = await fastApi.media.videoAssets.getDetails(folderId);
    } catch (err) {
      console.error(`Error loading details for ${folderId}:`, err);
    } finally {
      loadingDetails[folderId] = false;
    }
  }
}
</script>

<template>
  <div class="table-card">
    <table class="asset-table">
      <thead>
        <tr>
          <th style="width: 40px;"></th>
          <th>Folder / Title</th>
          <th>Type</th>
          <th>Completion</th>
          <th>Versions</th>
          <th>Quality</th>
          <th>Size</th>
          <th>Activity</th>
        </tr>
      </thead>
      <tbody>
        <template v-if="loading">
          <tr v-for="i in 5" :key="i" class="skeleton-row">
            <td colspan="8"><div class="loading-wave"></div></td>
          </tr>
        </template>

        <template v-else-if="items.length > 0">
          <template v-for="item in items" :key="item.folder_id">
            <!-- Row Tier 2 -->
            <tr class="master-row" :class="{ expanded: expandedRows.has(item.folder_id) }" @click="toggleRow(item.folder_id)">
              <td class="expand-cell">
                <component :is="expandedRows.has(item.folder_id) ? ChevronDown : ChevronRight" size="sm" />
              </td>
              <td>
                <div class="folder-name">{{ item.folder_name }}</div>
                <div v-if="item.linked_title" class="linked-title">
                  {{ item.linked_title.name }} <span class="year">({{ item.linked_title.release_year }})</span>
                </div>
                <div v-else class="badge badge-warning">Unlinked Directory</div>
              </td>
              <td>
                <span v-if="item.linked_title" class="type-icon">
                  <Film v-if="item.linked_title.type === 'movie'" size="sm" />
                  <Tv v-else size="sm" />
                </span>
                <span v-else>-</span>
              </td>
              <td>
                <div class="completion-bar-wrapper">
                  <div class="progress-bar">
                    <div
                      class="fill"
                      :style="{ width: `${item.completion.percentage}%` }"
                      :class="{ complete: item.completion.percentage === 100 }"
                    ></div>
                  </div>
                  <small>{{ item.completion.percentage }}%</small>
                </div>
              </td>
              <td>
                <span class="badge" :class="item.metrics.version_count > 1 ? 'badge-info' : 'badge-neutral'">
                  {{ item.metrics.version_count }} {{ item.metrics.version_count === 1 ? 'ver' : 'vers' }}
                </span>
              </td>
              <td>
                <span class="quality-tag">{{ item.quality_summary.primary_badge }}</span>
                <span v-if="!item.quality_summary.is_uniform" class="badge badge-warning margin-left">Mixed</span>
              </td>
              <td>{{ item.metrics.total_size_gb.toFixed(1) }} GB</td>
              <td>
                <span v-if="item.engagement.active_watchers_count > 0" class="watch-badge">
                  <Eye size="sm" /> {{ item.engagement.active_watchers_count }}
                </span>
              </td>
            </tr>

            <!-- Inspector Tier 3 -->
            <tr v-if="expandedRows.has(item.folder_id)" class="inspector-row">
              <td colspan="8">
                <div v-if="loadingDetails[item.folder_id]" class="inspector-loading">
                  Loading detailed media layout...
                </div>
                <AssetInspector
                  v-else-if="detailsCache[item.folder_id]"
                  :details="detailsCache[item.folder_id]"
                />
              </td>
            </tr>
          </template>
        </template>
      </tbody>
    </table>
  </div>
</template>