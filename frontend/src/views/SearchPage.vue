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
});

const searchResults = ref({});
const loadingTitles = ref(false)


const typeOptions = [
    { label: 'Any', value: null, type: 'primary' },
    { label: 'Movie', value: 'movie', type: 'primary' },
    { label: 'TV-show', value: 'tv', type: 'primary' },
]
const sortByOptions = [
    { label: 'Default', value: 'default', type: 'primary' },
    { label: 'TMDB', value: 'tmdb_score', type: 'primary' },
    { label: 'IMDB', value: 'imdb_score', type: 'primary' },
    { label: 'Popularity', value: 'popularity', type: 'primary' },
    { label: 'Name', value: 'title_name', type: 'primary' },
    { label: 'Runtime', value: 'runtime', type: 'primary' },
    { label: 'Date', value: 'release_date', type: 'primary' },
    { label: 'Viewed', value: 'last_viewed_at', type: 'primary' },
    { label: 'Random', value: 'random', type: 'primary' },
];
const jellyfinOptions = [
    { label: 'Yes', value: true,  type: 'positive' },
    { label: 'No', value: false, type: 'negative' },
]

async function search() {
    loadingTitles.value = true;
    resetResults(); // Wipe values to prevent old images from sticking
    try {
        if (searchStore.tmdbFallback) {
            searchResults.value = await fastApi.titles.searchTmdb({
                query: searchStore.query,
            });
        } else {
            searchResults.value = await fastApi.titles.search({
                query: searchStore.query,
                title_type: sp.value.title_type,
                sort_by: sp.value.sort_by,
                sort_direction: sp.value.sort_direction,
                jellyfin_link: sp.value.jellyfin_link,
            });
        }
    } finally {
        loadingTitles.value = false;
    }
}

function resetResults() {
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
        () => sp.value,
    ],
    () => {
        if (!searchStore.tmdbFallback) {
            search();
        }
    },
    { immediate: true, deep: true }
);

// On manual submit prevent empty TMDB searches, but keep results
watch(
    () => searchStore.submitTick,
    () => {
        if (searchStore.query || !searchStore.tmdbFallback) {
            search();
        }
    }
);

// On mode change prevent empty TMDB searches, but wipe results
watch(
    () => searchStore.tmdbFallback,
    () => {
        if (searchStore.query || !searchStore.tmdbFallback) {
            search();
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
        <h1>Search</h1>
        <div class="filters">
            <div>
                <FilterDropDown label="Type" :disabled="searchStore.tmdbFallback">
                    <OptionPicker
                        class="listing"
                        mode="single-required"
                        :options="typeOptions"
                        v-model="sp.title_type"
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

                <div class="checkbox-row">
                    <input
                        type="checkbox"
                        id="tmdbFallback"
                        v-model="searchStore.tmdbFallback"
                    />
                    <label for="tmdbFallback">TMDB</label>
                </div>
            </div>

            <div>
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
                    class="btn-text btn-square sort-direction-button"
                    @click="cycleSort"
                    :title="`Sort direction: ${sp.sort_direction}`"
                >
                    <i v-if="sp.sort_direction == 'default'" class="bx bx-sort"></i>
                    <i v-else-if="sp.sort_direction == 'asc'" class="bx bx-sort-up"></i>
                    <i v-else class="bx bx-sort-down"></i>
                </button>
            </div>
        </div>

        <h3>Results</h3>

        <LoadingIndicator v-if="loadingTitles"/>

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
    </div>
</template>

<style scoped>
.filters {
    display: flex;
    justify-content: space-between;

    > div {
        display: flex;
        /* gap: var(--spacing-sm); */
    }

    .sort-direction-button i {
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