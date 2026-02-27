<script setup>
import { computed, onUnmounted, ref, watch } from 'vue';
import { useSearchStore } from '@/stores/search';
import { fastApi } from '@/utils/fastApi';
import TitleCard from '@/components/TitleCard.vue';
import LoadingIndicator from '@/components/LoadingIndicator.vue';
import FilterDropDown from '@/components/FilterDropDown.vue';
import OptionPicker from '@/components/OptionPicker.vue';

const searchStore = useSearchStore();

const initialSearchParams = {
    title_type: null,
    watch_status: null,
    is_favourite: null,
    in_watchlist: null,
    jellyfin_link: null,
    sort_by: 'default',
    sort_direction: 'default',
}
const searchParams = ref({...initialSearchParams});
const pageNumber = ref(1);

const waitingFor = ref({})
const initialSearchResults = {
    titles: [],
    page_number: 1,
    page_size: 0,
    total_items: 0,
    total_pages: 1
}
const searchResults = ref({...initialSearchResults});


const typeOptions = [
    { label: 'Movie', value: 'movie', type: 'primary' },
    { label: 'TV-show', value: 'tv', type: 'primary' },
]
const watchStatusOptions = [
    { label: 'Not watched', value: 'not_watched',  type: 'negative' },
    { label: 'Partial', value: 'partial', type: 'primary' },
    { label: 'Completed', value: 'completed', type: 'positive' },
]
const favouriteOptions = [
    { label: 'Favourite', value: true,  type: 'positive' },
    { label: 'Not favourite', value: false, type: 'negative' },
]
const watchlistOptions = [
    { label: 'In your watchlist', value: true,  type: 'positive' },
    { label: 'Not in your watchlist', value: false, type: 'negative' },
]
const jellyfinOptions = [
    { label: 'Available', value: true,  type: 'positive' },
    { label: 'Not available', value: false, type: 'negative' },
]
const sortByOptions = [
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
            pageNumber.value = 1;
        } else {
            waitingFor.value.additionalPage = true;
            pageNumber.value += 1;
        }

        const params = {
            query: searchStore.query,
            page_number: pageNumber.value,
            ...(searchStore.tmdbFallback ? {} : searchParams.value)
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
    pageNumber.value = 1;
    searchResults.value = {
        titles: [],
        page_number: 1,
        page_size: 0,
        total_items: 0,
        total_pages: 1
    };
}

function resetFilters() {
    searchParams.value = {...initialSearchParams};
}

const searchParamsIsDirty = computed(() => {
    return Object.keys(initialSearchParams).some(
        key => searchParams.value[key] !== initialSearchParams[key]
    );
});


const cycleSort = () => {
    const mapping = {
        'default': 'asc',
        'asc': 'desc',
        'desc': 'default'
    };
    
    searchParams.value.sort_direction = mapping[searchParams.value.sort_direction] || 'default';
};


// On search parameter change auto search if not in tmdb mode
watch(
    [() => searchStore.query, searchParams],
    () => {
        if (!searchStore.tmdbFallback) {
            runSearch(false);
        }
    },
    { deep: true }
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
                <FilterDropDown
                    label="Type"
                    :disabled="searchStore.tmdbFallback"
                    :modified="searchParams.title_type != initialSearchParams.title_type"
                >
                    <OptionPicker
                        v-model="searchParams.title_type"
                        :options="typeOptions"
                    />
                </FilterDropDown>

                <hr>

                <FilterDropDown 
                    label="Watch status" 
                    :disabled="searchStore.tmdbFallback"
                    :modified="searchParams.watch_status != initialSearchParams.watch_status"
                >
                    <OptionPicker
                        v-model="searchParams.watch_status"
                        :options="watchStatusOptions"
                    />
                </FilterDropDown>
                
                <FilterDropDown 
                    label="Favourite" 
                    :disabled="searchStore.tmdbFallback"
                    :modified="searchParams.is_favourite != initialSearchParams.is_favourite"
                >
                    <OptionPicker
                        v-model="searchParams.is_favourite"
                        :options="favouriteOptions"
                    />
                </FilterDropDown>
                
                <FilterDropDown 
                    label="Watchlist" 
                    :disabled="searchStore.tmdbFallback"
                    :modified="searchParams.in_watchlist != initialSearchParams.in_watchlist"
                >
                    <OptionPicker
                        v-model="searchParams.in_watchlist"
                        :options="watchlistOptions"
                    />
                </FilterDropDown>
                
                <hr>
                
                <FilterDropDown 
                    label="Jellyfin" 
                    :disabled="searchStore.tmdbFallback"
                    :modified="searchParams.jellyfin_link != initialSearchParams.jellyfin_link"
                >
                    <OptionPicker
                        v-model="searchParams.jellyfin_link"
                        :options="jellyfinOptions"
                    />
                </FilterDropDown>

                <div v-if="searchParamsIsDirty" class="flex-row">
                    <hr>

                    <button
                        class="btn-text btn-even-padding"
                        title="Reset filters"
                        @click="resetFilters"
                        :disabled="searchStore.tmdbFallback"
                    >
                        <i class="bx bx-reset"></i>
                    </button>
                </div>
            </div>

            <div>
                <FilterDropDown 
                    label="Sort by" 
                    :disabled="searchStore.tmdbFallback"
                    :modified="searchParams.sort_by != initialSearchParams.sort_by"
                >
                    <OptionPicker
                        v-model="searchParams.sort_by"
                        :options="sortByOptions"
                        :defaultValue="'default'"
                    />
                </FilterDropDown>

                <button
                    class="btn-text btn-even-padding filter-icon-button"
                    @click="cycleSort"
                    :title="`Sort direction: ${searchParams.sort_direction}`"
                    :disabled="searchStore.tmdbFallback"
                >
                    <i v-if="searchParams.sort_direction == 'default'" class="bx bx-sort"></i>
                    <i v-else-if="searchParams.sort_direction == 'asc'" class="bx bx-sort-up"></i>
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

    i {
        font-size: var(--fs-1);
    }
}


.title-card-grid {
    display: grid;
    /* This creates as many 175px columns as will fit, then distributes leftover space */
    grid-template-columns: repeat(auto-fill, minmax(175px, 1fr));
    gap: var(--spacing-lg) var(--spacing-md);

    .title-card {
        width: unset;
    }
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