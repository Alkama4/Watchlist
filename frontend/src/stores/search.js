import { defineStore } from 'pinia';
import { ref, computed, watch } from 'vue';
import { fastApi } from '@/utils/fastApi';

export const useSearchStore = defineStore('search', () => {
    // --- State ---
    const query = ref('');
    const tmdbFallback = ref(false);
    const pageNumber = ref(1);
    const waitingFor = ref({ firstPage: false, additionalPage: false });

    const initialSearchParams = {
        title_type: null,
        watch_status: null,
        is_favourite: null,
        in_watchlist: null,
        jellyfin_link: null,
        has_video_assets: null,
        sort_by: 'default',
        sort_direction: 'default',
    };
    const searchParams = ref({ ...initialSearchParams });

    const initialSearchResults = {
        titles: [],
        page_number: 1,
        page_size: 0,
        total_items: 0,
        total_pages: 1
    };
    const searchResults = ref({ ...initialSearchResults });

    // --- URL Sync Utilities ---
    
    // Reads from URL and sets store state
    function hydrateFromQuery(routeQuery) {
        // Helper to convert URL strings back to correct types
        const parseBool = (val) => {
            if (val === 'true') return true;
            if (val === 'false') return false;
            return null;
        };

        query.value = routeQuery.q || '';
        tmdbFallback.value = routeQuery.tmdb === 'true';

        searchParams.value = {
            title_type: routeQuery.type || initialSearchParams.title_type,
            watch_status: routeQuery.status || initialSearchParams.watch_status,
            is_favourite: parseBool(routeQuery.fav),
            in_watchlist: parseBool(routeQuery.watchlist),
            jellyfin_link: parseBool(routeQuery.jellyfin),
            has_video_assets: parseBool(routeQuery.video),
            sort_by: routeQuery.sort || initialSearchParams.sort_by,
            sort_direction: routeQuery.dir || initialSearchParams.sort_direction,
        };
    }

    // Creates a clean object to push to the URL
    const queryForUrl = computed(() => {
        const params = {};
        
        // Only add to URL if they differ from the defaults
        if (query.value) params.q = query.value;
        if (tmdbFallback.value) params.tmdb = 'true';
        
        if (searchParams.value.title_type !== initialSearchParams.title_type) params.type = searchParams.value.title_type;
        if (searchParams.value.watch_status !== initialSearchParams.watch_status) params.status = searchParams.value.watch_status;
        if (searchParams.value.is_favourite !== initialSearchParams.is_favourite) params.fav = searchParams.value.is_favourite;
        if (searchParams.value.in_watchlist !== initialSearchParams.in_watchlist) params.watchlist = searchParams.value.in_watchlist;
        if (searchParams.value.jellyfin_link !== initialSearchParams.jellyfin_link) params.jellyfin = searchParams.value.jellyfin_link;
        if (searchParams.value.has_video_assets !== initialSearchParams.has_video_assets) params.video = searchParams.value.has_video_assets;
        if (searchParams.value.sort_by !== initialSearchParams.sort_by) params.sort = searchParams.value.sort_by;
        if (searchParams.value.sort_direction !== initialSearchParams.sort_direction) params.dir = searchParams.value.sort_direction;

        return params;
    });

    // --- Getters / Computed ---
    const searchParamsIsDirty = computed(() => {
        return Object.keys(initialSearchParams).some(
            key => searchParams.value[key] !== initialSearchParams[key]
        );
    });

    // --- Actions ---
    function resetResults() {
        pageNumber.value = 1;
        searchResults.value = { ...initialSearchResults };
    }

    function resetFilters() {
        searchParams.value = { ...initialSearchParams };
    }

    function cycleSort() {
        const mapping = {
            'default': 'asc',
            'asc': 'desc',
            'desc': 'default'
        };
        searchParams.value.sort_direction = mapping[searchParams.value.sort_direction] || 'default';
    }

    async function runSearch(append = false) {
        if (append && (waitingFor.value.additionalPage || searchResults.value.page_number >= searchResults.value.total_pages)) {
            return;
        }

        try {
            if (!append) {
                waitingFor.value.firstPage = true;
                pageNumber.value = 1;
                resetResults();
            } else {
                waitingFor.value.additionalPage = true;
                pageNumber.value += 1;
            }

            const params = {
                query: query.value,
                page_number: pageNumber.value,
                ...(tmdbFallback.value ? {} : searchParams.value)
            };

            const response = await (tmdbFallback.value 
                ? fastApi.titles.searchTmdb(params) 
                : fastApi.titles.search(params));

            response.titles.forEach((item, i) => item.batchIndex = i);

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

    function submit() {
        if (query.value || !tmdbFallback.value) {
            runSearch();
        }
    }

    // --- Watchers ---
    watch(
        [query, searchParams],
        () => {
            if (!tmdbFallback.value) {
                runSearch(false);
            }
        },
        { deep: true }
    );

    watch(
        tmdbFallback,
        (isTmdbMode) => {
            if (query.value || !isTmdbMode) {
                runSearch();
            } else {
                resetResults();
            }
        },
        { immediate: true }
    );

    return {
        // State
        query,
        tmdbFallback,
        searchParams,
        initialSearchParams,
        pageNumber,
        waitingFor,
        searchResults,
        // Sync
        hydrateFromQuery,
        queryForUrl,
        // Computed
        searchParamsIsDirty,
        // Actions
        resetResults,
        resetFilters,
        cycleSort,
        runSearch,
        submit
    };
});