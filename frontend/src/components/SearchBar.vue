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

const suggestions = ref([
    { title_id: 1, name: 'Inception' },
    { title_id: 2, name: 'Breaking Bad' },
    { title_id: 3, name: 'Interstellar' },
    { title_id: 4, name: 'Stranger Things' },
    { title_id: 5, name: 'The Dark Knight' }
]);

const router = useRouter();

async function fetchSuggestions() {
    waitingFor.suggestions = true;
    try {
        const response = await fastApi.titles.searchSuggestions({ query: inputValue.value })
        suggestions.value = response.titles;
    } finally {
        waitingFor.suggestions = false;
    }
}

function onSearchSubmit() {
    inputSearch.value?.blur();
    overlayVisible.value = false;

    router.push({
        path: '/search',
        query: inputValue.value ? { q: inputValue.value } : undefined
    });
}

function handleClearButton() {
    inputValue.value = '';
    inputSearch.value?.focus();
}

function selectSuggestion(title) {
    inputValue.value = title;
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
            <div class="suggestions">
                <button
                    v-for="item in suggestions"
                    :key="item.title_id"
                    type="button" 
                    class="btn-text btn-even-padding"
                    @click="selectSuggestion(item.name)"
                >
                    <Clock size="xs"/>
                    <span>{{ item.name }}</span>
                </button>
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
</style>