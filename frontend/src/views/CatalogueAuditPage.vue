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
    Clock,
    Film,
    HardDrive,
    MinusCircle,
    PieChart,
    RefreshCwAlt,
    Tv,
    XCircle
} from '@boxicons/vue';
import { ref, reactive, watch, onMounted } from 'vue';

const items = ref([]);
const loading = ref(false);

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

// Options for OptionPickers
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

function cycleSortDirection() {
    if (filters.sort_direction === 'default' || filters.sort_direction === 'asc') {
        filters.sort_direction = 'desc';
    } else {
        filters.sort_direction = 'asc';
    }
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
        filters.has_missing_episodes,
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

onMounted(() => {
    fetchAuditData();
});
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

        <!-- Filters Toolbar using LabelDropDown & OptionPicker -->
        <div class="filters margin-fix">
            <div class="left-filters">
                <LabelDropDown
                    label="Type"
                    :modified="isDirty('title_type')"
                >
                    <OptionPicker
                        v-model="filters.title_type"
                        :options="typeOptions"
                    />
                </LabelDropDown>

                <LabelDropDown
                    label="Asset status"
                    :modified="isDirty('asset_status')"
                >
                    <OptionPicker
                        v-model="filters.asset_status"
                        :options="assetStatusOptions"
                    />
                </LabelDropDown>

                <LabelDropDown
                    label="Watchlist"
                    :modified="isDirty('in_watchlist')"
                >
                    <OptionPicker
                        v-model="filters.in_watchlist"
                        :options="watchlistOptions"
                    />
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
                <LabelDropDown
                    label="Sort by"
                    :modified="isDirty('sort_by')"
                >
                    <OptionPicker
                        v-model="filters.sort_by"
                        :options="sortByOptions"
                        :defaultValue="'default'"
                    />
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
                        <th>Folder / Title</th>
                        <th>Type</th>
                        <th>Status</th>
                        <th>Files</th>
                        <th>Completion</th>
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
                        <tr v-for="item in items" :key="item.title_folder_id">
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
                                <span class="badge" :class="{ 'in-watchlist': item.is_in_watchlist }">
                                    {{ item.is_in_watchlist ? 'In Watchlist' : 'Not Saved' }}
                                </span>
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
                                <span class="size-text">{{ item.total_size_gb }} GB</span>
                            </td>
                            <td>
                                <div class="tags">
                                    <span v-if="item.max_resolution" class="tag">{{ item.max_resolution }}</span>
                                    <span v-if="item.has_hdr" class="tag hdr">HDR</span>
                                </div>
                            </td>
                        </tr>
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
.page-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: var(--spacing-md);
}

.filters {
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;

    &.margin-fix {
        margin-bottom: var(--spacing-md);
    }

    .left-filters, .right-filters {
        display: flex;
        align-items: center;
        flex-wrap: wrap;
        gap: var(--spacing-xs);
    }
}

.min-size-filter {
    display: flex;
    align-items: center;
    gap: var(--spacing-xs);
    
    .input-label {
        font-size: var(--fs-neg-1);
        color: var(--c-text-subtle);
    }

    .size-input {
        width: 70px;
        background-color: var(--c-bg-level-1);
        border: 1px solid var(--c-bg-level-2);
        color: var(--c-text);
        padding: 4px 8px;
        border-radius: var(--border-radius-sm);
        outline: none;

        &:focus {
            border-color: var(--c-primary);
        }
    }
}

.card {
    background-color: var(--c-bg-level-1);
    border-radius: var(--border-radius-md-lg);
    padding: var(--spacing-md);
}

.table-container {
    overflow-x: auto;
}

.audit-table {
    width: 100%;
    border-collapse: collapse;
    text-align: left;

    th, td {
        padding: var(--spacing-md) var(--spacing-sm);
        border-bottom: 1px solid var(--c-bg-level-2);
    }

    th {
        font-size: var(--fs-neg-1);
        color: var(--c-text-subtle);
        font-weight: 600;
    }
}

.folder-name {
    font-weight: 600;
    color: var(--c-text);
}

.linked-title {
    font-size: var(--fs-neg-1);
    color: var(--c-primary);
}

.unlinked-tag {
    font-size: var(--fs-neg-2);
    color: var(--c-text-subtle);
    font-style: italic;
}

.title-type {
    font-size: var(--fs-neg-1);
    text-transform: capitalize;
}

.badge {
    display: inline-block;
    padding: 2px 8px;
    border-radius: var(--border-radius-sm);
    font-size: var(--fs-neg-2);
    background-color: var(--c-bg-level-2);
    color: var(--c-text-subtle);

    &.in-watchlist {
        background-color: rgba(var(--c-primary-rgb, 0, 120, 255), 0.15);
        color: var(--c-primary);
    }
}

.file-counts {
    display: flex;
    flex-direction: column;
    font-size: var(--fs-neg-1);

    .warning-text {
        color: var(--c-danger, #ff4d4f);
    }
}

.completion-box {
    display: flex;
    flex-direction: column;
    gap: 2px;
    width: 120px;

    .progress-bar {
        height: 6px;
        background-color: var(--c-bg-level-2);
        border-radius: 3px;
        overflow: hidden;

        .fill {
            height: 100%;
            background-color: var(--c-warning, #faad14);

            &.complete {
                background-color: var(--c-success, #52c41a);
            }
        }
    }

    .pct {
        font-size: var(--fs-neg-1);
        font-weight: 600;
    }

    .missing-text {
        font-size: var(--fs-neg-2);
        color: var(--c-danger, #ff4d4f);
    }
}

.tags {
    display: flex;
    gap: 4px;

    .tag {
        font-size: var(--fs-neg-2);
        padding: 2px 6px;
        border-radius: 4px;
        background-color: var(--c-bg-level-2);

        &.hdr {
            background-color: var(--c-accent, #722ed1);
            color: white;
        }
    }
}

.skeleton {
    height: 30px;
    border-radius: var(--border-radius-sm);
}

.empty-state {
    text-align: center;
    padding: var(--spacing-xl) 0;
    color: var(--c-text-subtle);
}
</style>