<script setup>
import { ref, useAttrs } from 'vue'
import { useSearchStore } from '@/stores/search';
import router from '@/router';

const attrs = useAttrs()
const searchStore = useSearchStore();
const inputSearch = ref(null);

function onSearchFocus() {
    if (router.currentRoute.value.name !== 'search') {
        router.push({ name: 'Search' });
    }
}
function onSearchSubmit() {
    searchStore.submit();
}

function handleClearButton() {
    searchStore.query = "";
    inputSearch.value.focus();
}
</script>

<template>
    <form role="search" @submit.prevent="onSearchSubmit" class="search-bar">
        <i class="bx bx-search"></i>
        <input
            v-model="searchStore.query"
            v-bind="attrs"
            ref="inputSearch"
            type="search"
            @focus="onSearchFocus"
        >
        <i
            v-if="searchStore.query"
            class="bx bx-x btn btn-text soft"
            @click="handleClearButton"
        ></i>
    </form>
</template>

<style scoped>

form {
    position: relative;
}

input {
    padding-left: calc(var(--spacing-md) * 2 + var(--spacing-sm-md));
    margin: 0;
    width: 100%;
    border-radius: 100px;
}

i {
    top: 50%;
    transform: translateY(-50%);
}
i.bx-search {
    position: absolute;
    left: var(--spacing-md);
    pointer-events: none;
    color: var(--c-text-soft);
    font-size: var(--fs-1);
}

i.bx-x {
    position: absolute;
    right: var(--spacing-xs);
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