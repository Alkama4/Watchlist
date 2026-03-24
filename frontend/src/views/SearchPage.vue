<script setup>
import { onMounted, onUnmounted, ref, watch } from 'vue';
import { useSearchStore } from '@/stores/search';
import TitleCard from '@/components/title_cards/TitleCard.vue';
import LabelDropDown from '@/components/LabelDropDown.vue';
import OptionPicker from '@/components/OptionPicker.vue';
import Imdb from '@/assets/icons/imdb.svg'
import Tmdb from '@/assets/icons/tmdb.svg'
import { ArrowDownNarrowWide, ArrowDownUp, ArrowDownWideNarrow, Calendar, Capitalize, ChartTrend, Check, Circle, CircleHalf, Clock, Film, Heart, History, ListPlus, RotateCcwDot, Shuffle, Timer, Tv, X } from '@boxicons/vue';
import SearchBar from '@/components/SearchBar.vue';
import { useRoute, useRouter } from 'vue-router';


const searchStore = useSearchStore();


//////////// URL AND STORE SYNCING ////////////
const route = useRoute();
const router = useRouter();

// Hydrate the store from the URL before doing anything else
searchStore.hydrateFromQuery(route.query);

// Watch the store's clean URL object and update the browser URL silently
watch(
    () => searchStore.queryForUrl,
    (newQuery) => {
        router.replace({ query: newQuery });
    },
    { deep: true }
);


//////////// SEARRCH PARAM OPTIONS ////////////
const typeOptions = [
    { icon: Film, label: 'Movie', value: 'movie', type: 'primary' },
    { icon: Tv, label: 'TV-show', value: 'tv', type: 'primary' },
]
const watchStatusOptions = [
    { icon: Circle, label: 'Finished', value: 'completed', type: 'positive' },
    { icon: CircleHalf, label: 'In progress', value: 'partial', type: 'primary' },
    { icon: Circle, iconNotFilled: true, label: 'Unwatched', value: 'not_watched',  type: 'negative' },
]
const favouriteOptions = [
    { icon: Heart, label: 'Favourite', value: true,  type: 'positive' },
    { icon: Heart, iconNotFilled: true, label: 'Not favourite', value: false, type: 'negative' },
]
const watchlistOptions = [
    { icon: Clock, label: 'In watchlist', value: true,  type: 'positive' },
    { icon: Clock, iconNotFilled: true, label: 'Not in watchlist', value: false, type: 'negative' },
]
const jellyfinOptions = [
    { icon: Check, label: 'Available', value: true,  type: 'positive' },
    { icon: X, label: 'Not available', value: false, type: 'negative' },
]
const videoAssetOptions = [
    { icon: Check, label: 'Available', value: true,  type: 'positive' },
    { icon: X, label: 'Not available', value: false, type: 'negative' },
]
const sortByOptions = [
    { icon: Tmdb, label: 'TMDB', value: 'tmdb_score', type: 'primary' },
    { icon: Imdb, label: 'IMDB', value: 'imdb_score', type: 'primary' },
    { icon: ChartTrend, label: 'Popularity', value: 'popularity', type: 'primary' },
    { icon: Capitalize, label: 'Alphabetical', value: 'title_name', type: 'primary' },
    { icon: Timer, label: 'Runtime', value: 'runtime', type: 'primary' },
    { icon: Calendar, label: 'Release date', value: 'release_date', type: 'primary' },
    { icon: History, label: 'Last viewed', value: 'last_viewed_at', type: 'primary' },
    { icon: ListPlus, label: 'Date Added', value: 'added_at', type: 'primary' },
    { icon: Shuffle, label: 'Random', value: 'random', type: 'primary' },
];

onMounted(async () => {
    searchStore.fetchGenres();
});


//////////// INFINITE SCROLL ////////////
const loadMoreTrigger = ref(null);
let observer = null;

onMounted(() => {
    observer = new IntersectionObserver((entries) => {
        const trigger = entries[0];
        if (
            trigger.isIntersecting
            && !searchStore.waitingFor.additionalPage
            && searchStore.searchResults.page_number < searchStore.searchResults.total_pages
            && !searchStore.tmdbFallback
        ) {
            searchStore.runSearch(true);
        }
    }, {
        rootMargin: '800px' 
    });
});

watch(loadMoreTrigger, (newTrigger, oldTrigger) => {
    if (oldTrigger) observer.unobserve(oldTrigger);
    if (newTrigger) observer.observe(newTrigger);
});

onUnmounted(() => {
    if (observer) observer.disconnect();
    // Optional: Decide if you want to keep TMDB mode sticky or reset it when leaving
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
        <SearchBar 
            class="mobile-only"
            placeholder="Search for titles" 
        />
        <div class="filters">
            <div>
                <LabelDropDown
                    label="Type"
                    :disabled="searchStore.tmdbFallback"
                    :modified="searchStore.isDirty('title_type')"
                >
                    <OptionPicker
                        v-model="searchStore.searchParams.title_type"
                        :options="typeOptions"
                    />
                </LabelDropDown>

                <hr>

                <LabelDropDown 
                    label="Watch status" 
                    :disabled="searchStore.tmdbFallback"
                    :modified="searchStore.isDirty('watch_status')"
                >
                    <OptionPicker
                        v-model="searchStore.searchParams.watch_status"
                        :options="watchStatusOptions"
                    />
                </LabelDropDown>
                
                <LabelDropDown 
                    label="Favourite" 
                    :disabled="searchStore.tmdbFallback"
                    :modified="searchStore.isDirty('is_favourite')"
                >
                    <OptionPicker
                        v-model="searchStore.searchParams.is_favourite"
                        :options="favouriteOptions"
                    />
                </LabelDropDown>
                
                <LabelDropDown 
                    label="Watchlist" 
                    :disabled="searchStore.tmdbFallback"
                    :modified="searchStore.isDirty('in_watchlist')"
                >
                    <OptionPicker
                        v-model="searchStore.searchParams.in_watchlist"
                        :options="watchlistOptions"
                    />
                </LabelDropDown>
                
                <hr>

                <LabelDropDown 
                    label="Genres Include" 
                    :disabled="searchStore.tmdbFallback"
                    :modified="searchStore.isDirty('genres_include')"
                >
                    <OptionPicker
                        v-model="searchStore.searchParams.genres_include"
                        mode="multiple"
                        :options="searchStore.genres" 
                    />
                </LabelDropDown>

                <LabelDropDown 
                    label="Genres Exclude" 
                    :disabled="searchStore.tmdbFallback"
                    :modified="searchStore.isDirty('genres_exclude')"
                >
                    <OptionPicker
                        v-model="searchStore.searchParams.genres_exclude"
                        mode="multiple"
                        :options="searchStore.genres" 
                    />
                </LabelDropDown>


                <hr>
                
                <LabelDropDown 
                    label="Jellyfin" 
                    :disabled="searchStore.tmdbFallback"
                    :modified="searchStore.isDirty('jellyfin_link')"
                >
                    <OptionPicker
                        v-model="searchStore.searchParams.jellyfin_link"
                        :options="jellyfinOptions"
                    />
                </LabelDropDown>

                <LabelDropDown 
                    label="Video Assets" 
                    :disabled="searchStore.tmdbFallback"
                    :modified="searchStore.isDirty('has_video_assets')"
                >
                    <OptionPicker
                        v-model="searchStore.searchParams.has_video_assets"
                        :options="videoAssetOptions"
                    />
                </LabelDropDown>

                <div v-if="searchStore.searchParamsIsDirty" class="flex-row">
                    <hr>

                    <button
                        class="btn-text btn-even-padding"
                        title="Reset filters"
                        @click="searchStore.resetFilters"
                        :disabled="searchStore.tmdbFallback"
                    >
                        <RotateCcwDot size="sm"/>
                    </button>
                </div>
            </div>

            <div>
                <LabelDropDown 
                    label="Sort by" 
                    :disabled="searchStore.tmdbFallback"
                    :modified="searchStore.isDirty('sort_by')"
                >
                    <OptionPicker
                        v-model="searchStore.searchParams.sort_by"
                        :options="sortByOptions"
                        :defaultValue="'default'"
                    />
                </LabelDropDown>

                <button
                    class="btn-text btn-even-padding filter-icon-button"
                    @click="searchStore.cycleSort"
                    :title="`Sort direction: ${searchStore.searchParams.sort_direction}`"
                    :disabled="searchStore.tmdbFallback"
                >
                    <ArrowDownUp v-if="searchStore.searchParams.sort_direction == 'default'" size="sm"/>
                    <ArrowDownNarrowWide v-else-if="searchStore.searchParams.sort_direction == 'asc'" size="sm"/>
                    <ArrowDownWideNarrow v-else size="sm"/>
                </button>
            </div>
        </div>

        <h3>
            Results 
            <template v-if="!searchStore.waitingFor.firstPage">
                ({{ searchStore.searchResults?.total_items }} found)
            </template>
        </h3>

        <div
            v-if="searchStore.searchResults?.titles?.length == 0 && !searchStore.waitingFor.firstPage"
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
                v-for="title in searchStore.searchResults?.titles"
                :key="title.id"
                :title-info="title"
                :store-image-flag="!searchStore.tmdbFallback"
                :grid-mode="true"
            />
            
            <template v-if="searchStore.waitingFor.firstPage || searchStore.waitingFor.additionalPage">
                <div v-for="_ in (searchStore.waitingFor.firstPage ? 25 : 5)" class="title-card-skeleton">
                    <div class="img"/>
                    <div class="header"/>
                    <div class="detail"/>
                    <div class="detail"/>
                </div>
            </template>
        </div>

        <div 
            v-if="searchStore.searchResults?.page_number < searchStore.searchResults?.total_pages && !searchStore.waitingFor.additionalPage" 
            ref="loadMoreTrigger"
            class="flex-col" 
            style="margin-top: 16px; min-height: 50px;"
        ></div>
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

.search-bar {
    width: 100%;
    max-width: unset;
    margin-bottom: var(--spacing-sm);
}

.filters {
    display: flex;
    justify-content: space-between;
    flex-wrap: wrap;

    > div {
        display: flex;
        flex-wrap: wrap;
        /* gap: var(--spacing-sm); */
    }
}


.title-card-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(var(--title-card-width), 1fr));
    gap: var(--spacing-lg) var(--spacing-md);

    .title-card {
        width: unset;
    }
}

.title-card-skeleton {
    width: 100%;
    display: flex;
    flex-direction: column;
    gap: var(--spacing-xs);

    * {
        border-radius: var(--border-radius-md);
        background: linear-gradient(
            90deg,
            var(--c-bg-level-1) 40%,
            var(--c-bg-level-2) 70%,
            var(--c-bg-level-1) 100%
        );
        background-size: 200% 100%;
        animation: highlight-wave 1.25s infinite linear;
    }
    .img {
        aspect-ratio: 2/3;
    }
    .header {
        width: 90%;
        height: 20px;
        margin-top: var(--spacing-xs);
    }
    .detail {
        width: 50%;
        height: 16px;
        &:last-child {
            width: 40%;
        }
    }
}

@keyframes highlight-wave {
    0% {
        background-position: 0% 0;
    }
    100% {
        background-position: -200% 0;
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