<script setup>
import { ref, useAttrs } from 'vue'
import { Clock, Search, X } from '@boxicons/vue';
import { useRouter } from 'vue-router';

const attrs = useAttrs()

const inputSearch = ref(null);
const inputValue = ref('');

const suggestionsVisible = ref(false);
const suggestions = ref([
    { id: 1, title: 'Inception' },
    { id: 2, title: 'Breaking Bad' },
    { id: 3, title: 'Interstellar' },
    { id: 4, title: 'Stranger Things' },
    { id: 5, title: 'The Dark Knight' }
]);

const router = useRouter();

function onSearchSubmit() {
    suggestionsVisible.value = false;
    router.push({
        path: '/search',
        query: inputValue.value ? { q: inputValue.value } : undefined
    });
}

function handleClearButton() {
    inputValue.value = '';
    inputSearch.value.focus();
    onSearchSubmit(); 
}

// Set search input value when a recommendation is clicked
function selectSuggestion(title) {
    inputValue.value = title;
    suggestionsVisible.value = false;
    onSearchSubmit();
}

// Safely close the dropdown if focus leaves the search form completely
function handleFocusOut(event) {
    if (!event.currentTarget.contains(event.relatedTarget)) {
        suggestionsVisible.value = false;
    }
}
</script>

<template>
    <form
        role="search"
        @submit.prevent="onSearchSubmit"
        @focusout="handleFocusOut"
        class="search-bar"
        :class="{ 'suggestions-active': suggestionsVisible }"
    >
        <div class="input-wrapper">
            <Search class="search" size="sm"/>
            <input
                v-model="inputValue"
                v-bind="attrs"
                :placeholder="attrs?.placeholder ?? 'Search for titles'"
                ref="inputSearch"
                type="search"
                @focus="suggestionsVisible = true"
            >
            <X
                v-if="inputValue"
                size="sm"
                class="btn btn-text soft wipe"
                @click="handleClearButton"
            />
        </div>

        <div 
            v-if="suggestionsVisible" 
            class="suggestions"
        >
            <button
                v-for="item in suggestions"
                :key="item.id"
                class="btn-text btn-even-padding"
                @click="selectSuggestion(item.title)"
            >
                <Clock size="xs"/>
                <span>{{ item.title }}</span>
            </button>
        </div>
    </form>
</template>

<style scoped>
form {
    position: relative;
}

.input-wrapper {
    position: relative;

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

.suggestions {
    display: flex;
    flex-direction: column;

    position: absolute;
    top: 100%;
    width: 100%;
    max-height: clamp(300px, 50vh, 700px);
    overflow-y: auto;
    box-sizing: border-box;

    background-color: var(--c-bg-opaque-base);
    backdrop-filter: blur(var(--blur-subtle));
    border: 1px solid var(--c-border);

    padding: var(--spacing-xs);
    border-radius: var(--border-radius-md-lg);
    
    z-index: 100;
    
    button {
        justify-content: start;
    }
}

</style>