<script setup>
import { ref, useAttrs, onMounted, onUnmounted } from 'vue'
import { Clock, Search, X } from '@boxicons/vue';
import { useRouter } from 'vue-router';

const attrs = useAttrs()

const formRef = ref(null);
const inputSearch = ref(null);
const inputValue = ref('');
const overlayVisible = ref(false);

const suggestions = ref([
    { id: 1, title: 'Inception' },
    { id: 2, title: 'Breaking Bad' },
    { id: 3, title: 'Interstellar' },
    { id: 4, title: 'Stranger Things' },
    { id: 5, title: 'The Dark Knight' }
]);

const router = useRouter();

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

// Safely close the dropdown if a click occurs entirely outside the form component
function handleClickOutside(event) {
    if (formRef.value && !formRef.value.contains(event.target)) {
        overlayVisible.value = false;
    }
}

// Attach and detach global click listeners
onMounted(() => {
    document.addEventListener('click', handleClickOutside);
});
onUnmounted(() => {
    document.removeEventListener('click', handleClickOutside);
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
                    :key="item.id"
                    type="button" 
                    class="btn-text btn-even-padding"
                    @click="selectSuggestion(item.title)"
                >
                    <Clock size="xs"/>
                    <span>{{ item.title }}</span>
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