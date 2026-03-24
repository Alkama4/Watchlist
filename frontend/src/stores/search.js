import { defineStore } from 'pinia';
import { ref, computed, watch } from 'vue';
import { fastApi } from '@/utils/fastApi';

const PARAM_MAP = {
    // internal_key: [url_key, type]
    title_type:       ['type',      'string'],
    watch_status:     ['status',    'string'],
    is_favourite:     ['fav',       'boolean'],
    in_watchlist:     ['watchlist', 'boolean'],
    jellyfin_link:    ['jellyfin',  'boolean'],
    has_video_assets: ['video',     'boolean'],
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

    
    // --- URL Sync Utilities ---
    function hydrateFromQuery(routeQuery) {
        query.value = routeQuery.q || '';
        tmdbFallback.value = routeQuery.tmdb === 'true';

        const newParams = { ...initialSearchParams };

        Object.entries(PARAM_MAP).forEach(([internalKey, [urlKey, type]]) => {
            const rawValue = routeQuery[urlKey];
            if (rawValue === undefined) return;

            if (type === 'boolean') {
                newParams[internalKey] = rawValue === 'true' ? true : rawValue === 'false' ? false : null;
            } else {
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
            const defaultValue = initialSearchParams[internalKey];

            // Only add to URL if value is not default and not null/undefined
            if (value !== defaultValue && value !== null) {
                params[urlKey] = String(value);
            }
        });

        return params;
    });


    // --- Computed ---
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