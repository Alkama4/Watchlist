<script setup>
import { ref, watch, useAttrs } from 'vue'
import { X } from '@boxicons/vue';

const attrs = useAttrs()
const query = defineModel({ type: String, default: '' });
const emit = defineEmits(['focus']);

const inputSearch = ref(null);
const localQuery = ref(query.value);

let debounceTimeout = null;

watch(localQuery, (newVal) => {
    clearTimeout(debounceTimeout);
    debounceTimeout = setTimeout(() => {
        query.value = newVal; // This updates the store -> updates URL -> triggers search
    }, 500);
});

function onSearchSubmit() {
    // If they press enter, skip the debounce delay and search immediately
    clearTimeout(debounceTimeout);
    query.value = localQuery.value;
}

function handleClearButton() {
    localQuery.value = '';
    onSearchSubmit();
    inputSearch.value.focus();
}
</script>

<template>
    <form
        role="search"
        class="search-bar"
        @submit.prevent="onSearchSubmit"
    >
        <input
            v-model="localQuery" 
            v-bind="attrs"
            :placeholder="attrs?.placeholder ?? 'Filter by title'"
            ref="inputSearch"
            type="search"
            @focus="emit('focus')"
        >
        <X
            v-if="localQuery"
            size="sm"
            class="btn btn-text soft wipe"
            @click="handleClearButton"
        />
    </form>
</template>

<style scoped>
form {
    position: relative;
}

input {
    padding-left: var(--spacing-sm-md);
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
</style>