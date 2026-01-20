<script setup>
import LoadingButton from '@/components/LoadingButton.vue';
import { fastApi } from '@/utils/fastApi';
import { timeFormatters } from '@/utils/formatters';
import { resolveImagePath } from '@/utils/imagePath';
import { onMounted, ref } from 'vue';
import { useRoute } from 'vue-router';

const route = useRoute();
const titleDetails = ref({});
const waitingFor = ref({})

async function fetchTitleDetails() {
    const title_id = route.params.title_id;
    titleDetails.value = await fastApi.titles.getById(title_id)
}

async function updateTitleDetails() {
    waitingFor.value.titleUpdate = true;
    try {
        await fastApi.titles.putById(titleDetails.value.title_id);
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


onMounted(async () => {
    await fetchTitleDetails();
})
</script>

<template>
    <div class="title-details-page layout-contained layout-spacing-top layout-spacing-bottom">
        <img 
            :src="resolveImagePath(titleDetails, 'original', 'backdrop')"
            :alt="`${titleDetails?.type} backdrop: ${titleDetails?.name}`"
            class="backdrop"
        >
        
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
                <h1 class="name">
                    {{ titleDetails?.name }}
                    ({{ timeFormatters.timestampToYear(titleDetails?.release_date) }})
                </h1>
                <h4 class="name-original" v-if="titleDetails?.name_original != titleDetails?.name">
                    {{ titleDetails?.name_original }}
                </h4>
                <q class="tagline">{{ titleDetails?.tagline }}</q>
        
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
                <div class="links">
                    <a
                        :href="`https://www.themoviedb.org/${titleDetails?.type}/${titleDetails?.tmdb_id}`"
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
            </div>
        </div>

        <p style="color: var(--c-text-3)">{{ titleDetails }}</p>
    </div>
</template>

<style scoped>
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

img.logo {
    object-fit: contain;
    object-position: left center;

    width: 100%;
    height: 10vh;
    margin: 17.5vh 0;
    box-sizing: border-box;
}

.main-info {
    display: grid;
    grid-template-columns: 1fr auto;
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

.name {
    margin: 0;
}
.name-original {
    margin: 0;
}
.tagline {
    display: block;
    margin: var(--spacing-md) 0;
    color: var(--c-text-1);
    font-style: italic;
}

.actions {
    display: flex;
    gap: var(--spacing-sm);
}
.links {
    display: flex;
    gap: var(--spacing-sm);
}

</style>
