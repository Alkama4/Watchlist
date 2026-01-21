<script setup>
import LoadingButton from '@/components/LoadingButton.vue';
import LoadingIndicator from '@/components/LoadingIndicator.vue';
import TitleCard from '@/components/TitleCard.vue';
import { fastApi } from '@/utils/fastApi';
import { numberFormatters, timeFormatters } from '@/utils/formatters';
import { resolveImagePath } from '@/utils/imagePath';
import { onMounted, ref, watch } from 'vue';
import { useRoute } from 'vue-router';
import NotFoundPage from './NotFoundPage.vue';
import Tmdb from '@/assets/icons/tmdb.svg'

const route = useRoute();
const titleDetails = ref(null);
const waitingFor = ref({});
const similarTitles = ref({});

async function fetchTitleDetails() {
    const title_id = route.params.title_id;
    titleDetails.value = await fastApi.titles.getById(title_id)
}

async function fetchSimilarTitles() {
    const title_id = route.params.title_id;
    similarTitles.value = await fastApi.titles.similarById(title_id);
}

async function updateTitleDetails() {
    waitingFor.value.titleUpdate = true;
    try {
        await fastApi.titles.updateById(titleDetails.value.title_id);
        await fetchTitleDetails();
    } finally {
        waitingFor.value.titleUpdate = false;
    }
}

async function toggleFavourite() {
    let response;
    if (titleDetails.value.user_details.is_favourite) {
        response = await fastApi.titles.setFavourite(titleDetails.value.title_id, false);
    } else {
        response = await fastApi.titles.setFavourite(titleDetails.value.title_id, true);
    }
    if (!response) return;

    titleDetails.value.user_details.is_favourite = response.is_favourite;
}

async function toggleWatchlist() {
    let response;
    if (titleDetails.value.user_details.in_watchlist) {
        response = await fastApi.titles.setWatchlist(titleDetails.value.title_id, false);
    } else {
        response = await fastApi.titles.setWatchlist(titleDetails.value.title_id, true);
    }
    if (!response) return;
    
    titleDetails.value.user_details.in_watchlist = response.in_watchlist;
}

function adjustCollections() {
    alert("Collections are under construction.")
}

async function removeFromLibrary() {
    const response = await fastApi.titles.library.remove(titleDetails.value.title_id);
    titleDetails.value.user_details.in_library = response.in_library;
}
async function addToLibrary() {
    const response = await fastApi.titles.library.add(titleDetails.value.title_id);
    titleDetails.value.user_details.in_library = response.in_library;
}

async function setTitleWatchCount(count) {
    const response = await fastApi.titles.setWatchCount(titleDetails.value.title_id, count);
    console.log(response);
    titleDetails.value.user_details.watch_count = response.watch_count;
}
async function addToTitleWatchCount() {
    await setTitleWatchCount(titleDetails.value.user_details.watch_count + 1);
}
async function removeFromTitleWatchCount() {
    await setTitleWatchCount(titleDetails.value.user_details.watch_count - 1);
}

async function loadTitleData() {
    try {
        await fetchTitleDetails();
        await fetchSimilarTitles();
    } catch (e) {
        console.error('Failed to fetch title', e);
        titleDetails.value = false; // signal invalid title
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
</script>

<template>
    <LoadingIndicator class="page-loading-indicator" v-if="titleDetails === null"/>

    <NotFoundPage v-else-if="titleDetails === false"/>

    <div v-else class="title-details-page layout-contained layout-spacing-top layout-spacing-bottom">
        <img 
            :src="resolveImagePath(titleDetails, 'original', 'backdrop')"
            :alt="`${titleDetails?.type} backdrop: ${titleDetails?.name}`"
            class="backdrop"
        >
        
        <div class="logo-wrapper">
        <img 
            :src="resolveImagePath(titleDetails, 'original', 'logo')"
            :alt="`${titleDetails?.type} logo: ${titleDetails?.name}`"
            class="logo"
        >

        <div class="main-info">
            <img 
                :src="resolveImagePath(titleDetails, 'original', 'poster')"
                :alt="`${titleDetails?.type} poster: ${titleDetails?.name}`"
                class="poster"
            >
            
            <div class="right-side">
                <div class="name-part">
                <h1 class="name">
                    {{ titleDetails?.name }}
                    ({{ timeFormatters.timestampToYear(titleDetails?.release_date) }})
                </h1>
                    <h4 v-if="titleDetails?.name_original != titleDetails?.name" class="name-original">
                    {{ titleDetails?.name_original }}
                </h4>
                    <q v-if="titleDetails?.tagline" class="tagline">{{ titleDetails?.tagline }}</q>
                </div>

                <div class="general-stats">
                    <div class="tmdb">
                        <span>
                            <Tmdb/>
                            {{ titleDetails?.tmdb_vote_average }}
                        </span>
                        <span class="tiny">
                            ({{ numberFormatters.formatCompactNumber(titleDetails?.tmdb_vote_count) }} votes)
                        </span>
                    </div>

                    <div v-if="titleDetails?.title_type == 'movie'">
                        {{ timeFormatters.minutesToHrAndMin(titleDetails?.movie_runtime) }}
                    </div>
                    <div v-else>
                        {{ titleDetails?.show_season_count }}
                        Season{{ titleDetails?.show_season_count == 1 ? '': 's' }},
                        {{ titleDetails?.show_episode_count }}
                        Episode{{ titleDetails?.show_episode_count == 1 ? '': 's' }}
                    </div>

                    <template v-if="titleDetails?.age_rating">
                        <div>{{ titleDetails?.age_rating }}</div>
                    </template>

                    <template v-if="titleDetails?.genres?.length > 0">
                        <div class="genres">
                            <routerLink v-for="genre in titleDetails?.genres" to="/search" class="no-deco">
                                {{ genre?.genre_name }}
                            </routerLink>
                        </div>
                    </template>
                </div>
        
                <div class="actions">
                    <i
                        class="bx bxs-heart btn btn-text btn-square"
                        :class="{'btn-favourite': titleDetails?.user_details?.is_favourite }"
                        @click="toggleFavourite"
                    ></i>
                    <i
                        class="bx bxs-time btn btn-text btn-square"
                        :class="{'btn-accent': titleDetails?.user_details?.in_watchlist }"
                        @click="toggleWatchlist"
                    ></i>
                    <i
                        class="bx bxs-collection btn btn-text btn-square"
                        @click="adjustCollections"
                    ></i>
        
                    <!-- Move actions below to a drop down -->
        
                    <i
                        v-if="titleDetails?.user_details?.in_library"
                        class="bx bx-list-minus btn btn-text btn-square"
                        @click="removeFromLibrary"
                    ></i>
                    <i
                        v-else
                        class="bx bx-list-plus btn btn-text btn-square"
                        @click="addToLibrary"
                    ></i>
        
                    <LoadingButton
                        @click="updateTitleDetails"
                        :loading="waitingFor?.titleUpdate"
                    >
                        Update title details
                    </LoadingButton>
                    <!-- <a href="">Choose different images</a> -->
                </div>
                <div class="flex-row align-center gap-sm" style="margin-top: var(--spacing-md);">
                    <button @click="addToTitleWatchCount">Add</button>
                    <div>Watched {{ titleDetails?.user_details?.watch_count }} times</div>
                    <button @click="removeFromTitleWatchCount">Remove</button>
                </div>
                <p>{{ titleDetails?.overview }}</p>
            </div>
        </div>

                <div class="links">
                    <a
                :href="`https://www.themoviedb.org/${titleDetails?.title_type}/${titleDetails?.tmdb_id}`"
                        target="_blank"
                        class="btn no-deco"
                    >
                        TMDB
                        <i class="bx bx-link-external"></i>
                    </a>
                    <a
                        v-if="titleDetails?.imdb_id"
                        :href="`https://www.imdb.com/title/${titleDetails?.imdb_id}`"
                        target="_blank"
                        class="btn no-deco"
                    >
                        IMDB
                        <i class="bx bx-link-external"></i>
                    </a>
                    <a
                        v-if="titleDetails?.homepage"
                        :href="titleDetails?.homepage"
                        target="_blank"
                        class="btn no-deco"
                    >
                        Homepage
                        <i class="bx bx-link-external"></i>
                    </a>
        </div>

        <div class="carousel-wrapper">
            <h3>{{ similarTitles?.header }}</h3>
            <div class="carousel">
                <TitleCard
                    v-for="title in similarTitles?.titles"
                    :titleInfo="title"
                />
                <router-link 
                    v-if="similarTitles?.total_pages > 1"
                    class="fake-card"
                    :to="'/search'"
                >
                    Show more
                </router-link>
            </div>
        </div>

        <p style="color: var(--c-text-3)">{{ titleDetails }}</p>
    </div>
</template>

<style scoped>
.title-details-page {
    display: flex;
    flex-direction: column;
    gap: var(--spacing-md);
}


/* TEMP SETUP - DO A COMPONENT */
.carousel-wrapper {
    display: flex;
    flex-direction: column;
    gap: var(--spacing-md);
}

.carousel-wrapper h3 {
    margin-bottom: 0;
}

.carousel {
    display: flex;
    gap: var(--spacing-md);
    overflow-x: scroll;
}
/* TEMP SETUP - DO A COMPONENT */



img.backdrop {
    width: 100vw;
    height: 100vh;
    top: 0;
    left: 0;
    position: absolute;
    object-fit: cover;
    z-index: -10;

    mask-image: linear-gradient(
        to top,
        rgba(0, 0, 0, 0) 0%,
        rgba(0, 0, 0, 0.25) 50%
    );
}

.logo-wrapper {
    display: flex;
    align-items: center;
    justify-content: left;
    height: 50vh;
    max-height: 800px;
    min-height: 500px;
}
img.logo {
    object-fit: contain;
    object-position: left center;

    width: 100%;
    max-width: 600px;
    max-height: 300px;
    box-sizing: border-box;
}

.main-info {
    display: grid;
    grid-template-columns: auto 1fr;
    gap: var(--spacing-md-lg);
}

/* .right-side {
    background-color: rgba(0, 0, 0, 0.226);
    backdrop-filter: blur(8px);
    padding: var(--spacing-md-lg);
    border-radius: var(--border-radius-lg);
    border: 1px solid var(--c-border);
} */


img.poster {
    width: 300px;
    border-radius: var(--border-radius-lg);
}

.name-part {
    margin-bottom: var(--spacing-md);
}
.name {
    margin: 0;
}
.name-original {
    margin: 0;
    margin-top: var(--spacing-xs);
}
.tagline {
    display: block;
    margin-top: var(--spacing-md);
    color: var(--c-text-1);
    font-style: italic;
}

.genres {
    display: flex;
    gap: var(--spacing-xs);
}

.actions {
    display: flex;
    gap: var(--spacing-sm);
}
.links {
    display: flex;
    gap: var(--spacing-sm);
}


.page-loading-indicator {
    min-height: 50vh;
}
</style>
