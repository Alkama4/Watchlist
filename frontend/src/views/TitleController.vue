<script setup>
import LoadingIndicator from '@/components/LoadingIndicator.vue';
import NotFoundPage from './NotFoundPage.vue';
import { nextTick, onMounted, ref, watch } from 'vue';
import { useRoute } from 'vue-router';
import TitleDetailsPage from '@/components/titlePages/TitleDetailsPage.vue';
import { fastApi } from '@/utils/fastApi';
import SeasonDetailsPage from '@/components/titlePages/SeasonDetailsPage.vue';

const titleDetails = ref(null);
const similarTitles = ref({});

const pageLoading = ref(true);
const route = useRoute();

async function fetchTitleDetails() {
    const title_id = route.params.title_id;
    titleDetails.value = await fastApi.titles.getById(title_id)
}

async function fetchSimilarTitles() {
    const title_id = route.params.title_id;
    similarTitles.value = await fastApi.titles.similarById(title_id);
}

async function loadTitleData() {
    pageLoading.value = true;
    try {
        await fetchTitleDetails();
        await fetchSimilarTitles();
    } catch (e) {
        console.error('Failed to fetch title', e);
        titleDetails.value = false; // signal invalid title
    } finally {
        pageLoading.value = false;
    }
}

// Fetch data initially
onMounted(async () => {
    await loadTitleData();
});

// Watch for route changes
watch(
    () => route.params.title_id,
    async () => {
        // Wipe old data
        titleDetails.value = null;
        similarTitles.value = null;

        await loadTitleData();
    }
);

// Watch for when loading, and scroll to the saved location once 
// no longer loading. If not for this the scroll is set immiadetly,
// which is lost since the content isn't on page and the page is 100vh.
watch(pageLoading, (newLoading) => {
  if (!newLoading) {
    // Wait for the DOM to render after loading finishes
    nextTick(() => {
       const savedPos = window.history.state.scroll;
       if (savedPos) window.scrollTo(savedPos);
    });
  }
});
</script>

<template>
    <div class="title-controller">
        <LoadingIndicator class="page-loading-indicator" v-if="pageLoading"/>
    
        <NotFoundPage v-else-if="titleDetails === false"/>

        <SeasonDetailsPage 
            v-else-if="route.query.season" 
            :titleDetails="titleDetails"
            :seasonNumber="route.query.season"
        />

        <TitleDetailsPage 
            v-else 
            :titleDetails="titleDetails"
            :similarTitles="similarTitles"
        />
    </div>
</template>
