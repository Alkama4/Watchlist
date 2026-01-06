<script setup>
import { ref, watch } from 'vue';
import { useSearchStore } from '@/stores/search';
import { fastApi } from '@/utils/fastApi';
import TitleCard from '@/components/TitleCard.vue';
import LoadingIndicator from '@/components/LoadingIndicator.vue';
import LoadingButton from '@/components/LoadingButton.vue';

const searchStore = useSearchStore();

const sp = ref({
    titleType: null,
});

const searchResults = ref({});
const loadingTitles = ref(false)

async function search() {
    loadingTitles.value = true;
    try {
        if (searchStore.tmdbFallback) {
            searchResults.value = await fastApi.titles.searchTMDB({
                search: searchStore.query,
            });
        } else {
            searchResults.value = await fastApi.titles.search({
                search: searchStore.query,
                title_type: sp.value.titleType
            });
        }
    } finally {
        loadingTitles.value = false;
    }
}

watch(
    [
        () => searchStore.query,
        () => sp.value.titleType
    ],
    () => {
        if (searchStore.tmdbFallback) return;
        search();
    },
    { immediate: true }
);

watch(
    () => searchStore.tmdbFallback,
    () => {
        searchResults.value = {
            titles: []
        };
        search();
    }
)
</script>

<template>
    <div>
        <h1>Search</h1>
        <button @click="search">Search</button>

        <form @submit.prevent>
            <div class="checkbox-row"><label>
                <input
                    type="radio"
                    value="tv"
                    v-model="sp.titleType"
                    :disabled="searchStore.tmdbFallback"
                />
                TV
            </label></div>
            <div class="checkbox-row"><label>
                <input
                    type="radio"
                    value="movie"
                    v-model="sp.titleType"
                    :disabled="searchStore.tmdbFallback"
                />
                Movie
            </label></div>
            <div class="checkbox-row"><label>
                <input
                    type="radio"
                    :value="null"
                    v-model="sp.titleType"
                    :disabled="searchStore.tmdbFallback"
                />
                All
            </label></div>

            <div class="checkbox-row">
                <label>
                    <input
                        type="checkbox"
                        v-model="searchStore.tmdbFallback"
                    />
                    "Add titles" mode
                </label>
            </div>
        </form>

        <h3>Results</h3>

        <div class="title-card-grid">
            <TitleCard
                v-for="title in searchResults?.titles"
                :key="title.id"
                :title-info="title"
            />
        </div>

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