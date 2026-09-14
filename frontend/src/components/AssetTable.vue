<script setup>
import { computed, ref, reactive } from 'vue';
import { ChevronDown, ChevronRight, Eye, Film, Tv } from '@boxicons/vue';
import { fastApi } from '@/utils/fastApi';
import AssetInspector from './AssetInspector.vue';

const props = defineProps({
  items: { type: Array, required: true },
  pagination: { type: Object, default: null },
  loading: { type: Boolean, default: false }
});

const emit = defineEmits(['page-change', 'refresh']);

const expandedRows = ref(new Set());
const detailsCache = reactive({});
const loadingDetails = reactive({});
const pageNumbers = computed(() => {
  const totalPages = props.pagination?.total_pages || 0;
  const currentPage = props.pagination?.page || 1;
  const start = Math.max(1, Math.min(currentPage - 2, totalPages - 4));
  const end = Math.min(totalPages, start + 4);
  return Array.from({ length: Math.max(0, end - start + 1) }, (_, index) => start + index);
});

function changePage(page) {
  const totalPages = props.pagination?.total_pages || 1;
  if (page >= 1 && page <= totalPages && page !== props.pagination?.page) {
    emit('page-change', page);
  }
}

async function toggleRow(folderId) {
  if (expandedRows.value.has(folderId)) {
    const nextRows = new Set(expandedRows.value);
    nextRows.delete(folderId);
    expandedRows.value = nextRows;
    return;
  }

  expandedRows.value = new Set([...expandedRows.value, folderId]);

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

        <tr v-else>
          <td colspan="8" class="empty-state">No assets match the current filters.</td>
        </tr>
      </tbody>
    </table>

    <footer v-if="pagination && pagination.total_items > 0" class="table-footer">
      <span class="result-count">
        Showing {{ ((pagination.page - 1) * pagination.page_size) + 1 }}-{{ Math.min(pagination.page * pagination.page_size, pagination.total_items) }} of {{ pagination.total_items }} folders
      </span>
      <nav class="pagination" aria-label="Asset pages">
        <button class="btn btn-even-padding page-button" :disabled="pagination.page <= 1" aria-label="Previous page" @click="changePage(pagination.page - 1)">
          <ChevronRight class="previous-icon" size="sm" />
        </button>
        <button
          v-for="page in pageNumbers"
          :key="page"
          class="btn btn-even-padding page-button"
          :class="{ 'btn-primary': page === pagination.page }"
          :aria-current="page === pagination.page ? 'page' : undefined"
          @click="changePage(page)"
        >
          {{ page }}
        </button>
        <button class="btn btn-even-padding page-button" :disabled="pagination.page >= pagination.total_pages" aria-label="Next page" @click="changePage(pagination.page + 1)">
          <ChevronRight size="sm" />
        </button>
      </nav>
    </footer>
  </div>
</template>

<style scoped>
.table-card {
  overflow: hidden;
}
.asset-table {
  width: 100%;
}
.master-row {
  cursor: pointer;
}
.expand-cell {
  width: 40px;
  text-align: center;
}
.folder-name {
  max-width: 260px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.linked-title {
  margin-top: 3px;
}
.completion-bar-wrapper {
  display: flex;
  align-items: center;
  min-width: 120px;
  gap: var(--spacing-sm);
}
.progress-bar {
  width: 74px;
  height: 6px;
  overflow: hidden;
  border-radius: 999px;
}
.progress-bar .fill {
  height: 100%;
  border-radius: inherit;
  transition: width 300ms ease;
}
.quality-tag { white-space: nowrap; }
.watch-badge {
  display: inline-flex;
  align-items: center;
  gap: 4px;
}
.inspector-row td { padding: 0; }
.inspector-loading {
  min-height: 150px;
  padding: var(--spacing-lg);
  text-align: center;
}
.skeleton-row td { padding: var(--spacing-sm-md) var(--spacing-md); }
.skeleton-row .loading-wave {
  height: 42px;
  border-radius: var(--border-radius-sm);
}
.empty-state {
  padding: var(--spacing-lg) !important;
  text-align: center;
}
.table-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--spacing-md);
  padding: var(--spacing-sm-md) var(--spacing-md);
}
.result-count { font-size: var(--fs-neg-2); }
.pagination { display: flex; gap: var(--spacing-xs); }
.page-button {
  min-width: 36px;
}
.previous-icon { transform: rotate(180deg); }
@media (max-width: 900px) {
  .table-card { overflow-x: auto; }
  .asset-table { min-width: 820px; }
  .table-footer { min-width: 820px; }
}
@media (max-width: 600px) {
  .table-footer { align-items: flex-start; flex-direction: column; }
}
</style>