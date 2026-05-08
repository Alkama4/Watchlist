<script setup>
import { ref, useAttrs } from 'vue'
import { Search, X } from '@boxicons/vue';

const attrs = useAttrs()

// Two-way binding with the parent
const query = defineModel({ type: String, default: '' });
const emit = defineEmits(['submit', 'focus']);

const inputSearch = ref(null);

function onSearchSubmit() {
    emit('submit', query.value);
}

function handleClearButton() {
    query.value = '';
    inputSearch.value.focus();
}
</script>

<template>
    <form role="search" @submit.prevent="onSearchSubmit" class="search-bar">
        <Search class="search" size="sm"/>
        <input
            v-model="query"
            v-bind="attrs"
            ref="inputSearch"
            type="search"
            @focus="emit('focus')"
        >
        <X
            v-if="query"
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
    padding-left: calc(var(--spacing-md) * 2 + var(--spacing-sm-md));
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