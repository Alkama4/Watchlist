import { defineStore } from 'pinia';
import { ref, computed, watch } from 'vue';
import { fastApi } from '@/utils/fastApi';
import { Circle } from '@boxicons/vue';

const PARAM_MAP = {
    // internal_key: [url_key, type]
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

const initialSearchParams = {
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

export const useSearchStore = defineStore('search', () => {
    // --- State ---
    const query = ref('');
    const tmdbFallback = ref(false);
    const pageNumber = ref(1);
    const waitingFor = ref({ firstPage: false, additionalPage: false });
    
    const searchParams = ref({ ...initialSearchParams });
    const searchResults = ref({ ...initialSearchResults });

    const genres = ref([]);

    
    // --- URL Sync Utilities ---
    function hydrateFromQuery(routeQuery) {
        query.value = routeQuery.q || '';
        tmdbFallback.value = routeQuery.tmdb === 'true';

        const newParams = { ...initialSearchParams };

        Object.entries(PARAM_MAP).forEach(([internalKey, [urlKey, type]]) => {
            const rawValue = routeQuery[urlKey];
            if (rawValue === undefined || rawValue === null) return;

            if (type === 'boolean') {
                newParams[internalKey] = rawValue === 'true' ? true : rawValue === 'false' ? false : null;
            } 
            else if (type === 'array') {
                // Handle both single values and comma-separated strings
                const val = Array.isArray(rawValue) ? rawValue[0] : rawValue;
                newParams[internalKey] = val.split(',').map(Number).filter(n => !isNaN(n));
            } 
            else {
                newParams[internalKey] = rawValue;
            }
        });

        searchParams.value = newParams;
    }

    const queryForUrl = computed(() => {
        const params = {};

        if (query.value) params.q = query.value;
        if (tmdbFallback.value) params.tmdb = 'true';

        Object.entries(PARAM_MAP).forEach(([internalKey, [urlKey, type]]) => {
            const value = searchParams.value[internalKey];
            
            // Handle Arrays
            if (type === 'array' && Array.isArray(value) && value.length > 0) {
                params[urlKey] = value.join(',');
            } 
            // Handle Booleans and Strings (as you were)
            else if (value !== null && value !== undefined && value !== initialSearchParams[internalKey]) {
                if (type !== 'array') {
                    params[urlKey] = String(value);
                }
            }
        });

        return params;
    });


    // --- Helpers ---
    const isDirty = (key) => {
        const current = searchParams.value[key];
        const initial = initialSearchParams[key];

        if (Array.isArray(current) && Array.isArray(initial)) {
            return current.length !== initial.length || 
                !current.every((val, index) => val === initial[index]);
        }

        return current !== initial;
    };


    // --- Computed ---
    const searchParamsIsDirty = computed(() => {
        return Object.keys(initialSearchParams).some(key => isDirty(key));
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

    async function fetchGenres() {
        if (genres.value.length > 0) return;

        try {
            const response = await fastApi.titles.genres();
            genres.value = response.genres.map(({ tmdb_genre_id, genre_name }) => ({
                icon: Circle,
                iconNotFilled: true,
                label: genre_name,
                value: tmdb_genre_id,
                type: 'primary'
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
        searchParams,
        initialSearchParams,
        pageNumber,
        waitingFor,
        searchResults,
        genres,
        // Sync
        hydrateFromQuery,
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