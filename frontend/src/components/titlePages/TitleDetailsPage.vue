<script setup>
import TitleCarousel from '@/components/TitleCarousel.vue';
import LoadingButton from '@/components/LoadingButton.vue';
import { fastApi } from '@/utils/fastApi';
import { isoFormatters, numberFormatters, timeFormatters } from '@/utils/formatters';
import { resolveImagePath } from '@/utils/imagePath';
import { ref, computed } from 'vue';
import Tmdb from '@/assets/icons/tmdb.svg'
import Imdb from '@/assets/icons/imdb.svg'
import NoticeBlock from '@/components/NoticeBlock.vue';
import { preferredLocale, fallbackLocale } from '@/utils/conf';
import ModalBase from '@/components/modal/ModalBase.vue';
import SeasonsListing from '@/components/SeasonsListing.vue';
import EpisodeMap from '@/components/EpisodeMap.vue';

const { titleDetails } = defineProps({
    titleDetails: {
        type: Object,
        required: true
    },
    similarTitles: {
        type: Object,
        required: true
    }
})

const waitingFor = ref({});
const AgeRatingsModal = ref(null);

async function updateTitleDetails() {
    waitingFor.value.titleUpdate = true;
    try {
        await fastApi.titles.updateById(titleDetails.title_id);
        await fetchTitleDetails();
    } finally {
        waitingFor.value.titleUpdate = false;
    }
}

async function toggleFavourite() {
    let response;
    if (titleDetails.user_details.is_favourite) {
        response = await fastApi.titles.setFavourite(titleDetails.title_id, false);
    } else {
        response = await fastApi.titles.setFavourite(titleDetails.title_id, true);
    }
    if (!response) return;

    titleDetails.user_details.is_favourite = response.is_favourite;
    titleDetails.user_details.in_library = response.in_library;
}

async function toggleWatchlist() {
    let response;
    if (titleDetails.user_details.in_watchlist) {
        response = await fastApi.titles.setWatchlist(titleDetails.title_id, false);
    } else {
        response = await fastApi.titles.setWatchlist(titleDetails.title_id, true);
    }
    if (!response) return;
    
    titleDetails.user_details.in_watchlist = response.in_watchlist;
    titleDetails.user_details.in_library = response.in_library;
}

function adjustCollections() {
    alert("Collections are under construction.")
}

async function removeFromLibrary() {
    const response = await fastApi.titles.library.remove(titleDetails.title_id);
    titleDetails.user_details.in_library = response.in_library;
}
async function addToLibrary() {
    const response = await fastApi.titles.library.add(titleDetails.title_id);
    titleDetails.user_details.in_library = response.in_library;
}

async function setTitleWatchCount(count) {
    const response = await fastApi.titles.setWatchCount(titleDetails.title_id, count);
    console.log(response);
    titleDetails.user_details.watch_count = response.watch_count;
    titleDetails.user_details.in_library = response.in_library;
}
async function addToTitleWatchCount() {
    await setTitleWatchCount(titleDetails.user_details.watch_count + 1);
}
async function removeFromTitleWatchCount() {
    await setTitleWatchCount(titleDetails.user_details.watch_count - 1);
}


function showAllAgeRatings() {
    AgeRatingsModal.value.open();
}

const chosenAgeRating = computed(() => {
    const ratings = titleDetails?.age_ratings ?? []

    // Try to find preferred locale
    const pref = ratings.find(
        r => r.iso_3166_1 === preferredLocale.iso_3166_1
    )
    if (pref && pref.rating) return pref

    // Else fall back to US
    return ratings.find(r => r.iso_3166_1 === fallbackLocale.iso_3166_1) ?? null
})

const tmdbEditAgeRatingUrl = computed(() => {
    const { title_type, tmdb_id } = titleDetails;
    const path =
        title_type === 'movie'
            ? 'edit?active_nav_item=release_information'
            : 'edit?active_nav_item=content_ratings';
    return `https://www.themoviedb.org/${title_type}/${tmdb_id}/${path}`;
})
</script>

<template>
    <div class="title-details-page">
        <div class="layout-contained layout-spacing-top">
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
            </div>
    
            <NoticeBlock
                v-if="titleDetails?.user_details?.in_library === false"
                type="warning"
                header="Title not in Library"
                message="Please note that the title is currently not in your library. It will not appear in search, listings or recommendations. You can add the title to your library by using either the button below, or by searching for it from TMDB."
            />
    
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
                        </h1>
                        <h4 v-if="titleDetails?.name_original != titleDetails?.name" class="name-original">
                            {{ titleDetails?.name_original }}
                        </h4>
                        <q v-if="titleDetails?.tagline" class="tagline">{{ titleDetails?.tagline }}</q>
                    </div>
    
                    <div class="general-stats">
                        <div class="stat">
                            <Tmdb/>
                            <span :title="`${titleDetails?.tmdb_vote_count} votes`">
                                {{ titleDetails?.tmdb_vote_average || '-' }}
                                ({{ numberFormatters.formatCompactNumber(titleDetails?.tmdb_vote_count) }} votes)
                            </span>
                        </div>
    
                        <div v-if="titleDetails?.title_type == 'movie'" class="stat">
                            <i class="bx bxs-stopwatch"></i>
                            {{ timeFormatters.minutesToHrAndMin(titleDetails?.movie_runtime) }}
                        </div>
                        <div v-else class="stat">
                            <i class="bx bxs-stopwatch"></i>
                            {{ titleDetails?.seasons?.length }}
                            Season{{ titleDetails?.seasons?.length == 1 ? '': 's' }},
                            {{ titleDetails?.seasons?.reduce((sum, s) => sum + s.episodes.length, 0) }}
                            Episode{{ titleDetails?.seasons?.reduce((sum, s) => sum + s.episodes.length, 0) == 1 ? '': 's' }}
                        </div>
    
                        <div class="stat" @click="showAllAgeRatings">
                            <i class="bx bxs-star"></i>
                            <span class="btn-underline">
                                {{ chosenAgeRating?.rating || '-'  }}
                                <template v-if="chosenAgeRating?.descriptors">
                                    ({{ chosenAgeRating?.descriptors }})
                                </template>
                            </span>
                        </div>
    
                        <div class="stat">
                            <i class="bx bxs-label"></i>
                            <div class="genres">
                                <router-link
                                    v-for="(genre, index) in titleDetails?.genres"
                                    :to="`/search?genres_include=${genre.tmdb_genre_id}`"
                                    class="hover-line"
                                >
                                    {{ genre?.genre_name }}{{ index == titleDetails?.genres?.length - 1 ? '' : ',' }}
                                </router-link>
                                <span v-if="!titleDetails?.genres?.length >= 1">-</span>
                            </div>
                        </div>
    
                        <div class="stat">
                            <i class="bx bxs-calendar"></i>
                            {{ timeFormatters.timestampToFullDate(titleDetails?.release_date) }}
                        </div>
                    </div>
            
                    <p>{{ titleDetails?.overview }}</p>
                    
                    <div class="flex-row align-center gap-sm" style="margin-top: var(--spacing-md);">
                        <button @click="addToTitleWatchCount">Add</button>
                        <div>Watched {{ titleDetails?.user_details?.watch_count }} times</div>
                        <button @click="removeFromTitleWatchCount">Remove</button>
                    </div>
    
                    <div class="actions">
                        <i
                            class="bx bxs-heart btn btn-text btn-square"
                            :class="{'btn-favourite': titleDetails?.user_details?.is_favourite }"
                            @click="toggleFavourite"
                        ></i>
                        <i
                            class="bx bxs-time btn btn-text btn-square"
                            :class="{'btn-watchlist': titleDetails?.user_details?.in_watchlist }"
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
                            :loading="waitingFor?.titleUpdate ?? false"
                        >
                            Update title details
                        </LoadingButton>
                        
                        <!-- <a href="">Choose different images</a> -->
                         
                        <button 
                            v-if="titleDetails?.title_type === 'tv'"
                            @click="$refs.EpisodeMapModal.open()"
                        >
                            Episode Map
                        </button>

                        <!-- <button @click="$refs.EpisodeGraphModal.open()">Episode Rating Graphs</button> -->
                    </div>
                </div>
            </div>
    
            <h4>Links</h4>
            <div class="links">
                <a
                    :href="`https://www.themoviedb.org/${titleDetails?.title_type}/${titleDetails?.tmdb_id}`"
                    target="_blank"
                    class="btn-text"
                >
                    <Tmdb/>
                </a>
                <a
                    v-if="titleDetails?.imdb_id"
                    :href="`https://www.imdb.com/title/${titleDetails?.imdb_id}`"
                    target="_blank"
                    class="btn-text"
                >
                    <Imdb/>
                </a>
                <a
                    v-if="titleDetails?.homepage"
                    :href="titleDetails?.homepage"
                    target="_blank"
                    class="btn-text"
                >
                    <i class="bx bx-link"></i>
                </a>
            </div>
        </div>

        <SeasonsListing v-if="titleDetails?.title_type === 'tv'" :titleDetails="titleDetails"/>

        <TitleCarousel :carouselData="similarTitles" class="layout-spacing-bottom"/>


        <!-- Modals -->

        <ModalBase header="Age ratings" ref="AgeRatingsModal" :minimumCard="true">
            <p>The following list shows age ratings by country for the current title. The star icon indicates your <i class="bx bxs-star"></i> preferred language (or <i class="bx bx-star"></i> fallback). You can adjust your preffered languages in the <router-link to="/account">application settings</router-link>.</p>
            <div class="age-ratings-table">
                <table>
                    <thead>
                        <tr>
                            <th>Default</th>
                            <th>iso_3166_1</th>
                            <th>Country</th>
                            <th>Rating</th>
                            <th>Descriptors</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr v-for="ageRating in titleDetails?.age_ratings">
                            <td>
                                <span>
                                    <i
                                        v-if="ageRating.iso_3166_1 === preferredLocale.iso_3166_1"
                                        class="bx bxs-star"
                                        title="Your preferred language"
                                    ></i>
                                    <i
                                        v-else-if="ageRating.iso_3166_1 === fallbackLocale.iso_3166_1"
                                        class="bx bx-star"
                                        title="Default backup"
                                    ></i>

                                </span>
                            </td>
                            <td>{{ ageRating.iso_3166_1 }}</td>
                            <td>{{ isoFormatters.iso_3166_1ToCountry(ageRating.iso_3166_1) }}</td>
                            <td>{{ ageRating.rating }}</td>
                            <td>{{ ageRating.descriptors }}</td>
                        </tr>
                        <tr v-if="!titleDetails?.age_ratings?.length >= 1">
                            <td>-</td>
                            <td>-</td>
                            <td>-</td>
                            <td>-</td>
                            <td>-</td>
                        </tr>
                    </tbody>
                </table>
            </div>
            <span class="subtle details-missing-note">
                Can't find age ratings for your country? You can contribute the info on TMDB
                <a class="subtle" target="_blank" :href="tmdbEditAgeRatingUrl">here</a>.
                Changes usually take a few hours to appear in the "update title details" requests.
            </span>
        </ModalBase>

        <ModalBase header="Episode Map" ref="EpisodeMapModal">
            <EpisodeMap :seasons="titleDetails?.seasons"/>
        </ModalBase>
    </div>
</template>

<style scoped>
.title-details-page {
    display: flex;
    flex-direction: column;
    gap: var(--spacing-md);
}


img.backdrop {
    width: 100%;
    height: 100vh;
    max-height: 1200px;
    top: 0;
    left: 0;
    position: absolute;
    object-fit: cover;
    z-index: -10;

    filter: brightness(calc(var(--details-backdrop-min-brightness) + var(--details-backdrop-fade-intensity) * (1 - var(--details-backdrop-min-brightness))));
    mask-image: linear-gradient(
        to top,
        rgba(0, 0, 0, 0) 0%,
        rgba(0, 0, 0, calc(1 - var(--details-backdrop-fade-intensity))) 50%
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

.notice {
    margin-bottom: var(--spacing-md);
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
    color: var(--c-text-soft);
    font-style: italic;
}


.general-stats {
    display: flex;
    flex-direction: column;
    gap: var(--spacing-xs);
    margin-bottom: var(--spacing-sm);
}
.general-stats .stat {
    display: flex;
    align-items: center;
    gap: var(--spacing-sm);
}
.general-stats i {
    font-size: var(--fs-1);
    padding-inline: 2px;
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
    gap: var(--spacing-sm-md);
    font-size: var(--fs-3);
}
.links * {
    display: flex;
    align-items: center;
    text-decoration: none;
}
.links svg {
    width: 42px;
    height: auto;
}


.page-loading-indicator {
    min-height: 50vh;
}


.age-ratings-table {
    overflow-y: auto;
    width: fit-content;
}
.age-ratings-table span {
    width: 100%;
    display: flex;
    justify-content: center;
}
.age-ratings-table td {
    white-space: nowrap;
}

.details-missing-note {
    text-align: center;
    margin-top: var(--spacing-md-lg);
    font-size: var(--fs-neg-1);
}
</style>
