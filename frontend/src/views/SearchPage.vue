<script setup>
import { onUnmounted, ref, watch } from 'vue';
import { useSearchStore } from '@/stores/search';
import { fastApi } from '@/utils/fastApi';
import TitleCard from '@/components/TitleCard.vue';
import LoadingIndicator from '@/components/LoadingIndicator.vue';

const searchStore = useSearchStore();

const sp = ref({
    title_type: null,
    sort_by: 'default',
    sort_direction: 'default',
});

const searchResults = ref({});
const loadingTitles = ref(false)

async function search() {
    loadingTitles.value = true;
    resetResults(); // Wipe values to prevent old images from sticking
    try {
        if (searchStore.tmdbFallback) {
            searchResults.value = await fastApi.titles.searchTMDB({
                query: searchStore.query,
            });
        } else {
            searchResults.value = await fastApi.titles.search({
                query: searchStore.query,
                title_type: sp.value.title_type,
                sort_by: sp.value.sort_by,
                sort_direction: sp.value.sort_direction,
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
    <div class="search-page layout-contained">
        <h1>Search</h1>
        <form @submit.prevent>
            <label for="typeFilter">Type filter</label>
            <select id="typeFilter" v-model="sp.title_type" :disabled="searchStore.tmdbFallback">
                <option :value="null" selected>All</option>
                <option value="movie">Movie</option>
                <option value="tv">TV</option>
            </select>

            <label for="sortBy">Sort By</label>
            <select
                id="sortBy"
                v-model="sp.sort_by"
                :disabled="searchStore.tmdbFallback"
            >
                <option value="default" selected>Default</option>
                <option value="tmdb_score">TMDB</option>
                <option value="imdb_score">IMDB</option>
                <option value="popularity">Popularity</option>
                <option value="title_name">Title name</option>
                <option value="runtime">Runtime</option>
                <option value="release_date">Release date</option>
                <option value="last_viewed_at">Last viewed</option>
                <option value="random">Random</option>
            </select>

            <label for="sortDirection">Sort Direction</label>
            <select
                id="sortDirection"
                v-model="sp.sort_direction"
                :disabled="searchStore.tmdbFallback"
            >
                <option value="default" selected>Default</option>
                <option value="desc">Descending</option>
                <option value="asc">Ascending</option>
            </select>
            
            <div class="checkbox-row card">
                <input
                    type="checkbox"
                    id="tmdbFallback"
                    v-model="searchStore.tmdbFallback"
                />
                <label for="tmdbFallback">Add titles from TMDB</label>
            </div>
        </form>

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
            />
        </div>

    </div>
</template>

<style scoped>
.title-card-grid {
    display: flex;
    gap: var(--spacing-md);
    flex-wrap: wrap;
}

.results-not-found {
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;

    padding: var(--spacing-xl);
}

.results-not-found h2 {
    margin: 0;
}
</style>