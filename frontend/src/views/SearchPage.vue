<script setup>
import { onUnmounted, ref, watch } from 'vue';
import { useSearchStore } from '@/stores/search';
import { fastApi } from '@/utils/fastApi';
import TitleCard from '@/components/TitleCard.vue';
import LoadingIndicator from '@/components/LoadingIndicator.vue';
import FilterDropDown from '@/components/FilterDropDown.vue';
import OptionPicker from '@/components/OptionPicker.vue';

const searchStore = useSearchStore();

const sp = ref({
    title_type: null,
    sort_by: 'default',
    sort_direction: 'default',
    page_number: 1,
});

const waitingFor = ref({})
const searchResults = ref({
    titles: [],
    page_number: 1,
    page_size: 0,
    total_items: 0,
    total_pages: 1
});


const typeOptions = [
    { label: 'Movie', value: 'movie', type: 'primary' },
    { label: 'TV-show', value: 'tv', type: 'primary' },
]
const watchStatusOptions = [
    { label: 'Not watched', value: 'not_watched',  type: 'primary' },
    { label: 'Partial', value: 'partial', type: 'primary' },
    { label: 'Completed', value: 'completed', type: 'primary' },
]
const jellyfinOptions = [
    { label: 'Available', value: true,  type: 'positive' },
    { label: 'Not available', value: false, type: 'negative' },
]
const sortByOptions = [
    { label: 'Default', value: 'default', type: 'primary' },
    { label: 'TMDB', value: 'tmdb_score', type: 'primary' },
    { label: 'IMDB', value: 'imdb_score', type: 'primary' },
    { label: 'Popularity', value: 'popularity', type: 'primary' },
    { label: 'Alphabetical', value: 'title_name', type: 'primary' },
    { label: 'Runtime', value: 'runtime', type: 'primary' },
    { label: 'Release date', value: 'release_date', type: 'primary' },
    { label: 'Last viewed', value: 'last_viewed_at', type: 'primary' },
    { label: 'Random', value: 'random', type: 'primary' },
];

async function runSearch(append = false) {
    if (append && searchResults.value.page_number >= searchResults.value.total_pages) return;

    try {
        if (!append) {
            waitingFor.value.firstPage = true;
            sp.value.page_number = 1;
        } else {
            waitingFor.value.additionalPage = true;
            sp.value.page_number += 1;
        }

        const params = {
            query: searchStore.query,
            page_number: sp.value.page_number,
            ...(searchStore.tmdbFallback ? {} : {
                title_type: sp.value.title_type,
                sort_by: sp.value.sort_by,
                sort_direction: sp.value.sort_direction,
                jellyfin_link: sp.value.jellyfin_link,
                watch_status: sp.value.watch_status,
            })
        };

        const response = await (searchStore.tmdbFallback 
            ? fastApi.titles.searchTmdb(params) 
            : fastApi.titles.search(params));

        if (append) {
            searchResults.value = {
                ...response,
                titles: [...searchResults.value.titles, ...response.titles]
            };
        } else {
            searchResults.value = response;
        }
    } catch (error) {
        console.error("Search failed", error);
    } finally {
        waitingFor.value.additionalPage = false;
        waitingFor.value.firstPage = false;
    }
}

function resetResults() {
    sp.value.page_number = 1;
    searchResults.value = {
            titles: [],
            page_number: 1,
            page_size: 0,
            total_items: 0,
            total_pages: 1
        };
}


const cycleSort = () => {
    const mapping = {
        'default': 'asc',
        'asc': 'desc',
        'desc': 'default'
    };
    
    sp.value.sort_direction = mapping[sp.value.sort_direction] || 'default';
};


// On search parameter change auto search if not in tmdb mode
watch(
    [
        () => searchStore.query,
        () => sp.value.title_type,
        () => sp.value.sort_by,
        () => sp.value.sort_direction,
        () => sp.value.jellyfin_link,
        () => sp.value.watch_status,
    ],
    () => {
        if (!searchStore.tmdbFallback) {
            runSearch(false);
        }
    }
);

// On manual submit prevent empty TMDB searches, but keep results
watch(
    () => searchStore.submitTick,
    () => {
        if (searchStore.query || !searchStore.tmdbFallback) {
            runSearch();
        }
    }
);

// On mode change prevent empty TMDB searches, but wipe results
watch(
    () => searchStore.tmdbFallback,
    () => {
        if (searchStore.query || !searchStore.tmdbFallback) {
            runSearch();
        } else {
            resetResults();
        }
    },
    { immediate: true }
)

// Disable TMDB mode when leaving, so that we are always using the
// internal system by default.
onUnmounted(() => {
    searchStore.tmdbFallback = false;
});
</script>

<template>
    <div class="search-page layout-contained layout-spacing-bottom">
        <h1 class="mode-header">
            <div
                :class="{'active': !searchStore.tmdbFallback}"
                @click="searchStore.tmdbFallback = false"
            >
                Search Library
            </div>
            <div
                :class="{'active': searchStore.tmdbFallback}"
                @click="searchStore.tmdbFallback = true"
            >
                Add titles
            </div>
        </h1>
        <div class="filters">
            <div>
                <FilterDropDown label="Type" :disabled="searchStore.tmdbFallback">
                    <OptionPicker
                        :options="typeOptions"
                        v-model="sp.title_type"
                    />
                </FilterDropDown>

                <FilterDropDown 
                    label="Watch status" 
                    :disabled="searchStore.tmdbFallback"
                >
                    <OptionPicker
                        :options="watchStatusOptions"
                        v-model="sp.watch_status"
                    />
                </FilterDropDown>
                
                <FilterDropDown 
                    label="Jellyfin" 
                    :disabled="searchStore.tmdbFallback"
                >
                    <OptionPicker
                        :options="jellyfinOptions"
                        v-model="sp.jellyfin_link"
                    />
                </FilterDropDown>
            </div>

            <div>
                <button
                    v-if="sp.sort_by == 'random'"
                    class="btn-text btn-square filter-icon-button"
                    @click="runSearch"
                    title="Reroll random results"
                    :disabled="searchStore.tmdbFallback"
                >
                    <i class="bx bx-refresh"></i>
                </button>

                <FilterDropDown 
                    label="Sort by" 
                    :disabled="searchStore.tmdbFallback"
                >
                    <OptionPicker
                        class="listing"
                        mode="single-required"
                        :options="sortByOptions"
                        v-model="sp.sort_by"
                    />
                </FilterDropDown>

                <button
                    class="btn-text btn-square filter-icon-button"
                    @click="cycleSort"
                    :title="`Sort direction: ${sp.sort_direction}`"
                    :disabled="searchStore.tmdbFallback"
                >
                    <i v-if="sp.sort_direction == 'default'" class="bx bx-sort"></i>
                    <i v-else-if="sp.sort_direction == 'asc'" class="bx bx-sort-up"></i>
                    <i v-else class="bx bx-sort-down"></i>
                </button>
            </div>
        </div>

        <h3>Results ({{ searchResults?.total_items }} found)</h3>
        <LoadingIndicator v-if="waitingFor.firstPage"/>

        <div
            v-else-if="
                searchResults?.titles?.length == 0 
            "
            class="card results-not-found" 
        >
            <h2>No results found</h2>
            <p>{{ searchStore.tmdbFallback 
                ? "No titles found from TMDB." 
                : "No titles were found in your library." 
            }}</p>
            <button 
                v-if="!searchStore.tmdbFallback"
                @click="searchStore.tmdbFallback = true"
            >
                Search TMDB for new titles
            </button>
        </div>
        
        <div v-else class="title-card-grid">
            <TitleCard
                v-for="title in searchResults?.titles"
                :key="title.id"
                :title-info="title"
                :store-image-flag="!searchStore.tmdbFallback"
                :grid-mode="true"
            />
        </div>

        <div v-if="searchResults?.page_number < searchResults?.total_pages" class="flex-col" style="margin-top: 16px;">
            <button @click="runSearch(true)">MORE</button>
        </div>
        
    </div>
</template>

<style scoped>
.mode-header {
    display: flex;
    gap: var(--spacing-md);

    div {
        color: var(--c-text-subtle);
        cursor: pointer;
        display: flex;
        align-items: end;
        transition: color 0.1s var(--transition-ease-out);
        

        &:hover,
        &:active {
            color: var(--c-text-soft)
        }

        &.active {
            color: var(--c-text);

            &:hover,
            &:active {
                color: var(--c-text-strong);
            }
        }
        
    }
}

.filters {
    display: flex;
    justify-content: space-between;

    > div {
        display: flex;
        /* gap: var(--spacing-sm); */
    }

    .filter-icon-button i {
        font-size: var(--fs-1);
    }
}


.title-card-grid {
    display: flex;
    gap: var(--spacing-lg) var(--spacing-md);
    flex-wrap: wrap;
}

.results-not-found {
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;

    padding: var(--spacing-xl);

    h2 {
        margin: 0;
    }
}
</style>