import { defineStore } from 'pinia';
import { ref, computed, watch } from 'vue';
import { fastApi } from '@/utils/fastApi';

const PARAM_MAP = {
    title_type:       ['type',      'string'],
    watch_status:     ['status',    'string'],
    is_favourite:     ['fav',       'boolean'],
    in_watchlist:     ['watchlist', 'boolean'],
    jellyfin_link:    ['jellyfin',  'boolean'],
    has_video_assets: ['video',     'boolean'],
    genres_include:   ['genres_inc','array'],
    genres_exclude:   ['genres_exc','array'],
    sort_by:          ['sort',      'string'],
    sort_direction:   ['dir',       'string'],
};

const absoluteInitialSearchParams = {
    title_type: null,
    watch_status: null,
    is_favourite: null,
    in_watchlist: null,
    jellyfin_link: null,
    has_video_assets: null,
    genres_include: [],
    genres_exclude: [],
    sort_by: 'default',
    sort_direction: 'default',
};

const initialSearchResults = {
    titles: [],
    page_number: 1,
    page_size: 0,
    total_items: 0,
    total_pages: 1
};

export const SMART_COLLECTIONS = {
    favourites: {
        header: 'Favourites',
        params: {
            is_favourite: true
        }
    },
    watchlist: {
        header: 'Watchlist',
        params: {
            in_watchlist: true
        }
    },
    jellyfin: {
        header: 'Jellyfin',
        params: {
            jellyfin_link: true
        }
    },
    video_assets: {
        header: 'Video Assets',
        params: {
            has_video_assets: true
        }
    }
};

export const useSearchStore = defineStore('search', () => {
    // --- State ---
    const query = ref('');
    const tmdbFallback = ref(false);
    const headerLabel = ref('');
    const pageNumber = ref(1);
    const waitingFor = ref({ firstPage: false, additionalPage: false });
    
    // Tracks the current route name so watchers know where we are saving to
    const currentRouteName = ref('');

    // Dynamic initial params based on current route
    const activeInitialParams = ref({ ...absoluteInitialSearchParams });
    
    const searchParams = ref({ ...absoluteInitialSearchParams });
    const searchResults = ref({ ...initialSearchResults });
    const genres = ref([]);

    // CACHE: to remember normal searches
    const cachedMainSearch = ref({
        query: '',
        params: { ...absoluteInitialSearchParams }
    });

    // --- URL Sync Utilities ---
    function hydrateFromRoute(route) {
        const isSmart = route.name === 'Smart Collection';
        const collectionId = route.params.smart_collection_id;
        currentRouteName.value = route.name;
        
        let baseParams = { ...absoluteInitialSearchParams };

        // Determine context baseline
        if (isSmart && SMART_COLLECTIONS[collectionId]) {
            const config = SMART_COLLECTIONS[collectionId];
            headerLabel.value = config.header;
            baseParams = { ...baseParams, ...config.params };
        } else {
            headerLabel.value = '';
        }

        activeInitialParams.value = baseParams;

        const routeQuery = route.query;
        const hasQueryParams = Object.keys(routeQuery).length > 0;

        // If going back to normal search WITHOUT specific URL overrides, load from cache
        if (!isSmart && !hasQueryParams) {
            query.value = cachedMainSearch.value.query;
            // JSON stringify trick to deep-clone arrays inside the state safely
            searchParams.value = JSON.parse(JSON.stringify(cachedMainSearch.value.params));
        } else {
            // Start with current context baseline, override with URL params if they exist
            const newParams = { ...baseParams };
            query.value = routeQuery.q || '';
            tmdbFallback.value = routeQuery.tmdb === 'true';

            Object.entries(PARAM_MAP).forEach(([internalKey, [urlKey, type]]) => {
                const rawValue = routeQuery[urlKey];
                if (rawValue === undefined || rawValue === null) return;

                if (type === 'boolean') {
                    newParams[internalKey] = rawValue === 'true' ? true : rawValue === 'false' ? false : null;
                } 
                else if (type === 'array') {
                    const val = Array.isArray(rawValue) ? rawValue[0] : rawValue;
                    newParams[internalKey] = val.split(',').map(Number).filter(n => !isNaN(n));
                } 
                else {
                    newParams[internalKey] = rawValue;
                }
            });

            searchParams.value = newParams;
        }
    }

    const queryForUrl = computed(() => {
        const params = {};

        if (query.value) params.q = query.value;
        if (tmdbFallback.value) params.tmdb = 'true';

        Object.entries(PARAM_MAP).forEach(([internalKey, [urlKey, type]]) => {
            const value = searchParams.value[internalKey];
            const baseValue = activeInitialParams.value[internalKey]; // Diff against the current context
            
            if (type === 'array') {
                const baseArray = Array.isArray(baseValue) ? baseValue : [];
                if (Array.isArray(value) && value.length > 0) {
                    if (value.length !== baseArray.length || !value.every((v, i) => v === baseArray[i])) {
                        params[urlKey] = value.join(',');
                    }
                }
            } 
            else if (value !== null && value !== undefined && value !== baseValue) {
                params[urlKey] = String(value);
            }
        });

        return params;
    });

    // --- Helpers ---
    const isDirty = (key) => {
        const current = searchParams.value[key];
        const initial = activeInitialParams.value[key]; // Changed from absolute to active

        if (Array.isArray(current) && Array.isArray(initial)) {
            return current.length !== initial.length || 
                !current.every((val, index) => val === initial[index]);
        }
        return current !== initial;
    };

    // --- Computed ---
    const searchParamsIsDirty = computed(() => {
        return Object.keys(absoluteInitialSearchParams).some(key => isDirty(key));
    });

    // --- Actions ---
    function resetResults() {
        pageNumber.value = 1;
        searchResults.value = { ...initialSearchResults };
    }

    function resetFilters() {
        // Now resets back to the SMART collection's default, not absolute default
        searchParams.value = JSON.parse(JSON.stringify(activeInitialParams.value)); 
    }

    function cycleSort() {
        const mapping = {
            'default': 'asc',
            'asc': 'desc',
            'desc': 'default'
        };
        searchParams.value.sort_direction = mapping[searchParams.value.sort_direction] || 'default';
    }

    async function fetchGenres() {
        if (genres.value.length > 0) return;

        try {
            const response = await fastApi.titles.genres();
            genres.value = response.genres.map(({ tmdb_genre_id, genre_name }) => ({
                label: genre_name,
                value: tmdb_genre_id,
            }));
        } catch (error) {
            console.error("Failed to fetch genres:", error);
        }
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
            // Update cache silently whenever params change on the normal Search page
            if (currentRouteName.value === 'Search') {
                cachedMainSearch.value = {
                    query: query.value,
                    params: JSON.parse(JSON.stringify(searchParams.value))
                };
            }

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
        }
    );

    
    return {
        // State
        query,
        tmdbFallback,
        headerLabel,
        searchParams,
        activeInitialParams,
        absoluteInitialSearchParams,
        pageNumber,
        waitingFor,
        searchResults,
        genres,
        // Sync
        hydrateFromRoute,
        queryForUrl,
        // Helpers
        isDirty,
        // Computed
        searchParamsIsDirty,
        // Actions
        resetResults,
        resetFilters,
        cycleSort,
        fetchGenres,
        runSearch,
        submit
    };
});