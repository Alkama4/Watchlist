<script setup>
import { ref, useAttrs, onMounted, onUnmounted, watch } from 'vue'
import { Clock, Search, X } from '@boxicons/vue';
import { useRouter } from 'vue-router';
import { fastApi } from '@/utils/fastApi';

const attrs = useAttrs()

const formRef = ref(null);
const inputSearch = ref(null);
const inputValue = ref('');
const overlayVisible = ref(false);
const waitingFor = ref({});

const suggestions = ref([]);
const recentSearches = ref([]);
const LOCAL_STORAGE_KEY = 'search_history';

const router = useRouter();

function loadRecentSearches() {
    try {
        const stored = localStorage.getItem(LOCAL_STORAGE_KEY);
        recentSearches.value = stored ? JSON.parse(stored) : [];
    } catch (e) {
        recentSearches.value = [];
    }
}

function saveSearchToHistory(queryStr) {
    if (!queryStr || !queryStr.trim()) return;
    
    const cleanedQuery = queryStr.trim();
    
    let updated = recentSearches.value.filter(item => item !== cleanedQuery);
    updated.unshift(cleanedQuery);
    
    if (updated.length > 5) {
        updated = updated.slice(0, 5);
    }
    
    recentSearches.value = updated;
    localStorage.setItem(LOCAL_STORAGE_KEY, JSON.stringify(updated));
}

function removeSearchFromHistory(queryStr) {
    recentSearches.value = recentSearches.value.filter(item => item !== queryStr);
    localStorage.setItem(LOCAL_STORAGE_KEY, JSON.stringify(recentSearches.value));

    fetchSuggestions();
}

async function fetchSuggestions() {
    // If empty string, fall back instantly to local storage history without calling backend
    if (!inputValue.value || !inputValue.value.trim()) {
        suggestions.value = recentSearches.value.map((name, index) => ({
            title_id: `history-${index}`, // uniquely identify list items
            name: name,
            isHistory: true
        }));
        return;
    }

    waitingFor.suggestions = true;
    try {
        const response = await fastApi.titles.searchSuggestions({ query: inputValue.value })
        suggestions.value = response.titles.map(t => ({ ...t, isHistory: false }));
    } catch (error) {
        console.error("Failed to load search suggestions", error);
    } finally {
        waitingFor.suggestions = false;
    }
}

function onSearchSubmit() {
    inputSearch.value?.blur();
    overlayVisible.value = false;

    saveSearchToHistory(inputValue.value);

    router.push({
        path: '/search',
        query: inputValue.value ? { q: inputValue.value } : undefined
    });
}

function handleClearButton() {
    inputValue.value = '';
    inputSearch.value?.focus();
}

function selectSuggestion(titleName) {
    inputValue.value = titleName;
    onSearchSubmit();
}

function handleMouseDownOutside(event) {
    if (formRef.value && !formRef.value.contains(event.target)) {
        overlayVisible.value = false;
    }
}

watch(
    () => inputValue.value,
    async () => {
        await fetchSuggestions();
    }
);

onMounted(() => {
    // Run both so that the correct one does its thing
    loadRecentSearches();
    fetchSuggestions(); 
    document.addEventListener('mousedown', handleMouseDownOutside);
});

onUnmounted(() => {
    document.removeEventListener('mousedown', handleMouseDownOutside);
});
</script>

<template>
    <form
        ref="formRef"
        role="search"
        @submit.prevent="onSearchSubmit"
        class="search-bar"
        :class="{ 'suggestions-active': overlayVisible }"
    >
        <div class="input-wrapper">
            <Search class="search" size="sm"/>
            <input
                v-model="inputValue"
                v-bind="attrs"
                :placeholder="attrs?.placeholder ?? 'Search for titles'"
                ref="inputSearch"
                type="search"
                @focus="overlayVisible = true"
            >
            <X
                v-if="inputValue"
                size="sm"
                class="btn btn-text soft wipe"
                @click="handleClearButton"
            />
        </div>

        <div v-if="overlayVisible" class="overlay">
            <div v-if="suggestions.length > 0" class="suggestions">
                <button
                    v-for="item in suggestions"
                    :key="item.title_id"
                    type="button" 
                    class="btn-text btn-even-padding suggestion-button"
                    @click="selectSuggestion(item.name)"
                >
                    <!-- Show a history clock if it is local history, otherwise a discovery lens -->
                    <Clock v-if="item.isHistory" size="xs"/>
                    <Search v-else size="xs" style="color: var(--c-text-soft);"/>
                    
                    <span>{{ item.name }}</span>

                    <X
                        v-if="inputValue.length == 0"
                        size="sm"
                        class="btn-text subtle remove-history-item-button"
                        @click.stop="removeSearchFromHistory(item.name)"
                    />
                </button>
            </div>
            <div v-else class="suggestions placeholder">
                <h4>
                    {{
                        inputValue.length == 0
                        ? 'Search for titles'
                        : 'No suggestions found'
                    }}
                </h4>
                <p>
                    {{
                        inputValue.length == 0
                        ? 'Start searching for any movie or TV show.'
                        : 'Press enter to search anyway, or to add the title.'
                    }}
                </p>
            </div>
        </div>

    </form>
</template>

<style scoped>
form {
    position: relative;
}

.input-wrapper {
    position: relative;
    z-index: 101;

    input {
        padding-left: calc(var(--spacing-md) * 2 + var(--spacing-sm-md));
        padding-right: calc(var(--spacing-lg) + var(--spacing-xs));
        margin: 0;
        width: 100%;
        border-radius: 100px;
    }
    
    .search,
    .wipe {
        top: 50%;
        transform: translateY(-50%);
    }
    .search {
        position: absolute;
        left: var(--spacing-md);
        pointer-events: none;
        color: var(--c-text-soft);
    }
    
    .wipe {
        position: absolute;
        right: var(--spacing-xs-sm);
        padding: var(--spacing-xs);
        border-radius: 100px;
    }
    
    input[type="search"]::-webkit-search-decoration,
    input[type="search"]::-webkit-search-cancel-button,
    input[type="search"]::-webkit-search-results-button,
    input[type="search"]::-webkit-search-results-decoration {
        -webkit-appearance: none;
        display: none;
    }
}

.overlay {
    --overlay-overdraw: var(--spacing-sm);
    
    display: flex;
    flex-direction: column;

    position: absolute;
    top: calc(-1 * var(--overlay-overdraw) - 1px);
    left: calc(-1 * var(--overlay-overdraw) - 1px);
    width: calc(100% + var(--overlay-overdraw) * 2);
    max-height: clamp(300px, 50vh, 700px);
    overflow-y: auto;
    box-sizing: border-box;

    background-color: var(--c-bg-opaque-base);
    backdrop-filter: blur(var(--blur-subtle));
    border: 1px solid var(--c-border);

    padding: var(--overlay-overdraw);
    border-radius: calc((38px + var(--spacing-md)) / 2);
    border-bottom-left-radius: var(--border-radius-md-lg);
    border-bottom-right-radius: var(--border-radius-md-lg);
    
    z-index: 100;
}

.suggestions {
    display: flex;
    flex-direction: column;
    margin-top: calc(38px + var(--spacing-sm));
    
    button {
        justify-content: start;
    }
}

.suggestions.placeholder {
    min-height: unset;
    justify-content: center;
    align-items: center;
    padding: var(--spacing-md-lg);
    gap: var(--spacing-xs-sm);

    h4, p {
        margin: 0;
    }
    p {
        color: var(--c-text-soft);
        /* font-size: var(--fs-neg-1) */
    }
}

.suggestion-button {
    position: relative;

    .remove-history-item-button {
        position: absolute;
        right: var(--spacing-xs);
        padding: var(--spacing-xs);
        border-radius: var(--border-radius-md);
    }
}

</style>