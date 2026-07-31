<script setup>
import LabelDropDown from '@/components/LabelDropDown.vue';
import OptionPicker from '@/components/OptionPicker.vue';
import LoadingButton from '@/components/LoadingButton.vue';
import { fastApi } from '@/utils/fastApi';
import {
    ArrowDownNarrowWide,
    ArrowDownUp,
    ArrowDownWideNarrow,
    Capitalize,
    CheckCircle,
    ChevronDown,
    ChevronRight,
    Clock,
    Film,
    HardDrive,
    MinusCircle,
    PieChart,
    RefreshCwAlt,
    Tv,
    XCircle,
    AlertTriangle
} from '@boxicons/vue';
import { ref, reactive, watch, onMounted } from 'vue';

const items = ref([]);
const loading = ref(false);

// Row expansion and drill-down detail caches
const expandedRows = ref(new Set());
const detailsData = ref({});
const loadingDetails = ref({});

const filters = reactive({
    min_size_gb: null,
    asset_status: null,
    in_watchlist: null,
    title_type: null,
    sort_by: 'default',
    sort_direction: 'asc',
    page_number: 1,
    page_size: 20
});

// Options
const typeOptions = [
    { icon: Film, label: 'Movie', value: 'movie', type: 'primary' },
    { icon: Tv, label: 'TV-show', value: 'tv', type: 'primary' }
];

const assetStatusOptions = [
    { icon: CheckCircle, label: 'Complete', value: 'complete', type: 'positive' },
    { icon: XCircle, label: 'Incomplete', value: 'incomplete', type: 'warning' },
    { icon: MinusCircle, label: 'Missing all', value: 'missing_all', type: 'negative' }
];

const watchlistOptions = [
    { icon: Clock, label: 'In watchlist', value: true, type: 'positive' },
    { icon: Clock, iconNotFilled: true, label: 'Not in watchlist', value: false, type: 'negative' }
];

const sortByOptions = [
    { icon: Capitalize, label: 'Folder Name', value: 'default', type: 'primary' },
    { icon: HardDrive, label: 'Total Size', value: 'size', type: 'primary' },
    { icon: PieChart, label: 'Completion', value: 'completion', type: 'primary' }
];

async function fetchAuditData() {
    loading.value = true;
    try {
        const params = { ...filters };
        Object.keys(params).forEach(key => {
            if (params[key] === null || params[key] === '') delete params[key];
        });

        items.value = await fastApi.media.videoAssets.audit(params);
    } catch (error) {
        console.error('Failed to fetch video asset audit data:', error);
    } finally {
        loading.value = false;
    }
}

async function toggleRow(folderId) {
    if (expandedRows.value.has(folderId)) {
        expandedRows.value.delete(folderId);
        return;
    }

    expandedRows.value.add(folderId);

    // Fetch details on demand if not cached
    if (!detailsData.value[folderId]) {
        loadingDetails.value[folderId] = true;
        try {
            const data = await fastApi.media.videoAssets.getAuditDetails(folderId);
            detailsData.value[folderId] = data;
        } catch (error) {
            console.error(`Failed to load details for folder ${folderId}:`, error);
        } finally {
            loadingDetails.value[folderId] = false;
        }
    }
}

function cycleSortDirection() {
    filters.sort_direction = filters.sort_direction === 'asc' ? 'desc' : 'asc';
}

function isDirty(key) {
    if (key === 'min_size_gb') return filters.min_size_gb !== null && filters.min_size_gb !== '';
    if (key === 'sort_by') return filters.sort_by !== 'default';
    if (key === 'asset_status') return filters.asset_status !== null;
    return filters[key] !== null;
}

watch(
    () => [
        filters.min_size_gb,
        filters.asset_status,
        filters.in_watchlist,
        filters.title_type,
        filters.sort_by,
        filters.sort_direction,
        filters.page_size
    ],
    () => {
        filters.page_number = 1;
        fetchAuditData();
    }
);

watch(() => filters.page_number, fetchAuditData);

onMounted(fetchAuditData);
</script>

<template>
    <div class="audit-page layout-contained layout-spacing-top layout-spacing-bottom">
        <header class="page-header">
            <h1>Video Assets Audit</h1>
            <LoadingButton :loading="loading" @click="fetchAuditData">
                <RefreshCwAlt size="sm" />
                <span>Refresh Audit</span>
            </LoadingButton>
        </header>

        <!-- Filters Toolbar -->
        <div class="filters margin-fix">
            <div class="left-filters">
                <LabelDropDown label="Type" :modified="isDirty('title_type')">
                    <OptionPicker v-model="filters.title_type" :options="typeOptions" />
                </LabelDropDown>

                <LabelDropDown label="Asset status" :modified="isDirty('asset_status')">
                    <OptionPicker v-model="filters.asset_status" :options="assetStatusOptions" />
                </LabelDropDown>

                <LabelDropDown label="Watchlist" :modified="isDirty('in_watchlist')">
                    <OptionPicker v-model="filters.in_watchlist" :options="watchlistOptions" />
                </LabelDropDown>

                <div class="min-size-filter">
                    <label class="input-label">Min Size (GB)</label>
                    <input
                        v-model.number="filters.min_size_gb"
                        type="number"
                        min="0"
                        step="0.5"
                        placeholder="0"
                        class="size-input"
                    />
                </div>
            </div>

            <div class="right-filters">
                <LabelDropDown label="Sort by" :modified="isDirty('sort_by')">
                    <OptionPicker v-model="filters.sort_by" :options="sortByOptions" :defaultValue="'default'" />
                </LabelDropDown>

                <button
                    class="btn-text btn-even-padding filter-icon-button"
                    @click="cycleSortDirection"
                    :title="`Sort direction: ${filters.sort_direction}`"
                >
                    <ArrowDownUp v-if="filters.sort_direction === 'default'" size="sm" />
                    <ArrowDownNarrowWide v-else-if="filters.sort_direction === 'asc'" size="sm" />
                    <ArrowDownWideNarrow v-else size="sm" />
                </button>
            </div>
        </div>

        <!-- Data Table -->
        <section class="table-container card">
            <table class="audit-table">
                <thead>
                    <tr>
                        <th style="width: 32px;"></th>
                        <th>Folder / Title</th>
                        <th>Type</th>
                        <th>Completion</th>
                        <th>Files</th>
                        <th>Size</th>
                        <th>Quality</th>
                    </tr>
                </thead>
                <tbody>
                    <template v-if="loading">
                        <tr v-for="i in 5" :key="i" class="loading-row">
                            <td colspan="7"><div class="loading-wave skeleton"></div></td>
                        </tr>
                    </template>

                    <template v-else-if="items.length > 0">
                        <template v-for="item in items" :key="item.title_folder_id">
                            <!-- Main Row -->
                            <tr class="main-row" @click="toggleRow(item.title_folder_id)">
                                <td class="expand-cell">
                                    <component
                                        :is="expandedRows.has(item.title_folder_id) ? ChevronDown : ChevronRight"
                                        size="sm"
                                    />
                                </td>
                                <td>
                                    <div class="folder-name">{{ item.title_folder_name }}</div>
                                    <div v-if="item.linked_title" class="linked-title">
                                        Linked: {{ item.linked_title.name }}
                                    </div>
                                    <div v-else class="unlinked-tag">Unlinked</div>
                                </td>
                                <td>
                                    <span v-if="item.linked_title" class="title-type">
                                        {{ item.linked_title.type === 'movie' ? 'Movie' : 'TV Show' }}
                                    </span>
                                    <span v-else class="text-subtle">-</span>
                                </td>
                                <td>
                                    <div class="completion-box">
                                        <div class="progress-bar">
                                            <div
                                                class="fill"
                                                :style="{ width: `${item.completion_percentage}%` }"
                                                :class="{ complete: item.completion_percentage === 100 }"
                                            ></div>
                                        </div>
                                        <span class="pct">{{ item.completion_percentage }}%</span>
                                        <small v-if="item.missing_episodes_count > 0" class="missing-text">
                                            ({{ item.missing_episodes_count }} missing)
                                        </small>
                                    </div>
                                </td>
                                <td>
                                    <div class="file-counts">
                                        <span><strong>Total:</strong> {{ item.counts.file_count }}</span>
                                        <span v-if="item.counts.episodes_count"><strong>Eps:</strong> {{ item.counts.episodes_count }}</span>
                                        <span v-if="item.counts.unlinked_count" class="warning-text">
                                            <strong>Unlinked:</strong> {{ item.counts.unlinked_count }}
                                        </span>
                                    </div>
                                </td>
                                <td>
                                    <span class="size-text">{{ item.total_size_gb }} GB</span>
                                </td>
                                <td>
                                    <div class="tags">
                                        <span class="tag">{{ item.quality_summary.primary_display }}</span>
                                        <span v-if="!item.quality_summary.is_uniform" class="tag warning">Mixed</span>
                                    </div>
                                </td>
                            </tr>

                            <!-- Expandable Details Row -->
                            <tr v-if="expandedRows.has(item.title_folder_id)" class="detail-row">
                                <td colspan="7">
                                    <div v-if="loadingDetails[item.title_folder_id]" class="detail-loading">
                                        <RefreshCwAlt class="spin" size="sm" /> Fetching breakdown details...
                                    </div>

                                    <div v-else-if="detailsData[item.title_folder_id]" class="detail-container">
                                        <!-- MOVIE VARIANTS VIEW -->
                                        <div v-if="detailsData[item.title_folder_id].title_type === 'movie'" class="variants-container">
                                            <h4 class="detail-heading">Video Assets / Versions</h4>
                                            <div class="variant-list">
                                                <div
                                                    v-for="variant in detailsData[item.title_folder_id].movie_variants"
                                                    :key="variant.video_asset_id"
                                                    class="variant-card"
                                                >
                                                    <span class="badge-type">{{ variant.video_type }}</span>
                                                    <span class="file-name">{{ variant.file_name }}</span>
                                                    <div class="variant-specs">
                                                        <span class="spec-tag">{{ variant.resolution || 'Unknown' }}</span>
                                                        <span class="spec-tag hdr">{{ variant.hdr_type || 'SDR' }}</span>
                                                        <span class="spec-tag">{{ variant.codec }}</span>
                                                        <span class="spec-size">{{ variant.filesize_gb }} GB</span>
                                                    </div>
                                                </div>
                                            </div>
                                        </div>

                                        <!-- TV SHOW SEASONS & EPISODES GRID -->
                                        <div v-else-if="detailsData[item.title_folder_id].title_type === 'tv'" class="tv-container">
                                            <div
                                                v-for="(episodes, seasonNum) in detailsData[item.title_folder_id].seasons"
                                                :key="seasonNum"
                                                class="season-block"
                                            >
                                                <h4 class="detail-heading">Season {{ seasonNum }}</h4>
                                                <div class="episode-grid">
                                                    <div
                                                        v-for="ep in episodes"
                                                        :key="ep.episode_number"
                                                        class="ep-card"
                                                        :class="{ missing: ep.is_missing }"
                                                    >
                                                        <div class="ep-header">
                                                            <span class="ep-num">E{{ ep.episode_number }}</span>
                                                            <span v-if="ep.is_missing" class="badge-missing">Missing</span>
                                                        </div>

                                                        <div v-if="!ep.is_missing && ep.assets.length > 0" class="ep-content">
                                                            <div class="ep-res">
                                                                {{ ep.assets[0].resolution }}
                                                                <small v-if="ep.assets[0].hdr_type">{{ ep.assets[0].hdr_type }}</small>
                                                            </div>
                                                            <div class="ep-meta">
                                                                {{ ep.assets[0].codec }} • {{ ep.assets[0].filesize_gb }} GB
                                                            </div>
                                                        </div>
                                                    </div>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                </td>
                            </tr>
                        </template>
                    </template>

                    <template v-else>
                        <tr>
                            <td colspan="7" class="empty-state">
                                No video assets matched the current filters.
                            </td>
                        </tr>
                    </template>
                </tbody>
            </table>
        </section>
    </div>
</template>

<style scoped>
.audit-table {
    width: 100%;
    border-collapse: collapse;
}

.main-row {
    cursor: pointer;
    transition: background-color 0.15s ease;
}

.main-row:hover {
    background-color: rgba(255, 255, 255, 0.03);
}

.expand-cell {
    text-align: center;
    color: var(--text-subtle, #888);
}

.detail-row td {
    padding: 0;
    background-color: rgba(0, 0, 0, 0.15);
    border-bottom: 1px solid var(--border-color, #222);
}

.detail-container {
    padding: 1rem 1.5rem;
}

.detail-heading {
    margin: 0 0 0.75rem 0;
    font-size: 0.9rem;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    color: var(--text-subtle, #aaa);
}

.detail-loading {
    padding: 1.5rem;
    text-align: center;
    color: var(--text-subtle, #aaa);
}

.spin {
    animation: spin 1s linear infinite;
}

@keyframes spin {
    from { transform: rotate(0deg); }
    to { transform: rotate(360deg); }
}

/* Movie Variants */
.variant-list {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
}

.variant-card {
    display: flex;
    align-items: center;
    gap: 1rem;
    padding: 0.5rem 0.75rem;
    background: rgba(255, 255, 255, 0.04);
    border-radius: 6px;
    font-size: 0.85rem;
}

.badge-type {
    text-transform: uppercase;
    font-size: 0.7rem;
    font-weight: 700;
    padding: 2px 6px;
    border-radius: 4px;
    background: rgba(255, 255, 255, 0.1);
}

.file-name {
    flex: 1;
    font-family: monospace;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}

.variant-specs {
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

.spec-tag {
    font-size: 0.75rem;
    padding: 2px 6px;
    background: #333;
    border-radius: 4px;
}

.spec-tag.hdr {
    background: #4a3b00;
    color: #ffd700;
}

.spec-size {
    font-weight: bold;
}

/* TV Episode Grid */
.season-block {
    margin-bottom: 1.25rem;
}

.episode-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(130px, 1fr));
    gap: 0.5rem;
}

.ep-card {
    padding: 0.5rem;
    background: rgba(255, 255, 255, 0.04);
    border: 1px solid rgba(255, 255, 255, 0.06);
    border-radius: 6px;
    display: flex;
    flex-direction: column;
    gap: 0.25rem;
}

.ep-card.missing {
    border-color: rgba(220, 53, 69, 0.4);
    background: rgba(220, 53, 69, 0.08);
}

.ep-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.ep-num {
    font-weight: bold;
    font-size: 0.85rem;
}

.badge-missing {
    color: #ff6b6b;
    font-size: 0.7rem;
    font-weight: bold;
}

.ep-res {
    font-size: 0.8rem;
    font-weight: 600;
}

.ep-meta {
    font-size: 0.7rem;
    color: var(--text-subtle, #888);
}

.tag.warning {
    background: #5c4300;
    color: #ffcc00;
}
</style>