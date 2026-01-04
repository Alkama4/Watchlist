<script setup>
import { ref, watch } from 'vue';
import { useSearchStore } from '@/stores/search';
import { fastApi } from '@/utils/fastApi';

const searchStore = useSearchStore();

const sp = ref({
    titleType: null
});

const searchResults = ref({});

async function search(q) {
    searchResults.value = await fastApi.titles.search({
        search: q,
        title_type: sp.value.titleType
    });
}

watch(
    [
        () => searchStore.query,
        () => sp.value.titleType
    ],
    ([q]) => {
        search(q);
    },
    { immediate: true }
);
</script>

<template>
    <div>
        <h1>Search</h1>

        <form @submit.prevent>
            <div class="checkbox-row">
                <label>
                    <input
                        type="radio"
                        value="tv"
                        v-model="sp.titleType"
                    />
                    TV
                </label>
            </div>

            <div class="checkbox-row">
                <label>
                    <input
                        type="radio"
                        value="movie"
                        v-model="sp.titleType"
                    />
                    Movie
                </label>
            </div>

            <div class="checkbox-row">
                <label>
                    <input
                        type="radio"
                        :value="null"
                        v-model="sp.titleType"
                    />
                    All
                </label>
            </div>
        </form>

        <h3>Search results for {{ searchStore.query }}:</h3>

        <div v-for="title in searchResults?.titles" :key="title.id">
            {{ title }}
        </div>
    </div>
</template>
