<script setup>
import TitleCarousel from '@/components/TitleCarousel.vue';
import { fastApi } from '@/utils/fastApi';
import { isoFormatters, numberFormatters, timeFormatters } from '@/utils/formatters';
import { getTitleImageUrl } from '@/utils/imagePath';
import { ref, computed } from 'vue';
import Tmdb from '@/assets/icons/tmdb.svg'
import Imdb from '@/assets/icons/imdb.svg'
import JustWatch from '@/assets/icons/justWatch.svg'
import Jellyfin from '@/assets/icons/jellyfin.svg'
import NoticeBlock from '@/components/NoticeBlock.vue';
import ModalBase from '@/components/modal/ModalBase.vue';
import SeasonsListing from '@/components/SeasonsListing.vue';
import EpisodeMap from '@/components/EpisodeMap.vue';
import ModalImages from '@/components/modal/ModalImages.vue';
import KebabMenu from '@/components/KebabMenu.vue';
import { AlbumCovers, AlertCircle, AlertTriangle, Check, CheckCircle, Clock, Heart, Images, InfoCircle, Link, ListMinus, ListPlus, MapIcon, Minus, RefreshCw, Star, Translate } from '@boxicons/vue';
import ModalLocale from '@/components/modal/ModalLocale.vue';
import { resolveAgeRating } from '@/utils/titleUtils';
import { useSettingsStore } from '@/stores/settings';
import Tooltip from '@/components/Tooltip.vue';

const props = defineProps({
    titleDetails: {
        type: Object,
        required: true
    },
    similarTitles: {
        type: Object,
        required: true
    },
    fetchTitleDetails: {
        type: Function,
        required: true
    },
    jellyfinConfig: {
        type: Object,
        required: true
    },
    tmdbBaseUrl: {
        type: String,
        required: true
    }
})

const settings = useSettingsStore();

const waitingFor = ref({});
const updateResponse = ref({});
const AgeRatingsModal = ref(null);
const ImagesModal = ref(null);
const LocaleModal = ref(null);

async function updateTitleDetails() {
    waitingFor.value.titleUpdate = true;
    try {
        await fastApi.titles.updateById(props.titleDetails.title_id);
        await props.fetchTitleDetails();
        updateResponse.value = {
            icon: CheckCircle,
            type: 'positive',
            header: 'Update successful!',
            message: 'The title is now up to date.'
        }
    } catch (e) {
        updateResponse.value = {
            icon: AlertCircle,
            type: 'negative',
            header: e?.message,
            message: e?.response?.data?.detail || e
        }
    } finally {
        waitingFor.value.titleUpdate = false;
    }
}

async function toggleFavourite() {
    let response;
    if (props.titleDetails.user_details.is_favourite) {
        response = await fastApi.titles.setFavourite(props.titleDetails.title_id, false);
    } else {
        response = await fastApi.titles.setFavourite(props.titleDetails.title_id, true);
    }
    if (!response) return;

    props.titleDetails.user_details.is_favourite = response.is_favourite;
    props.titleDetails.user_details.in_library = response.in_library;
}

async function toggleWatchlist() {
    let response;
    if (props.titleDetails.user_details.in_watchlist) {
        response = await fastApi.titles.setWatchlist(props.titleDetails.title_id, false);
    } else {
        response = await fastApi.titles.setWatchlist(props.titleDetails.title_id, true);
    }
    if (!response) return;
    
    props.titleDetails.user_details.in_watchlist = response.in_watchlist;
    props.titleDetails.user_details.in_library = response.in_library;
}

function adjustCollections() {
    alert("Collections are under construction.")
}

async function removeFromLibrary() {
    const response = await fastApi.titles.library.remove(props.titleDetails.title_id);
    props.titleDetails.user_details.in_library = response.in_library;
}
async function addToLibrary() {
    const response = await fastApi.titles.library.add(props.titleDetails.title_id);
    props.titleDetails.user_details.in_library = response.in_library;
}

async function setTitleWatchCount(count) {
    const response = await fastApi.titles.setWatchCount(props.titleDetails.title_id, count);
    props.titleDetails.user_details.watch_count = response.watch_count;
    props.titleDetails.user_details.in_library = response.in_library;
}
async function adjustWatchCount() {
    await setTitleWatchCount(props.titleDetails.user_details.watch_count + 1);
}
async function removeFromTitleWatchCount() {
    await setTitleWatchCount(props.titleDetails.user_details.watch_count - 1);
}


const chosenAgeRating = computed(() => {
    return resolveAgeRating(props?.titleDetails?.age_ratings);
})


const tmdbEditAgeRatingUrl = computed(() => {
    const path = props?.titleDetails?.title_type === 'movie'
        ? 'edit?active_nav_item=release_information'
        : 'edit?active_nav_item=content_ratings';
    return `${props.tmdbBaseUrl}/${path}`;
})

const jellyfinLink = computed(() => {
    const baseUrl = props?.jellyfinConfig?.base_url
    const serverId = props?.jellyfinConfig?.server_id
    const jellyfinId = props?.titleDetails?.jellyfin_id

    const serverIdParam = serverId ? `&serverId=${serverId}` : ''

    return `${baseUrl}/web/#/details?id=${jellyfinId}${serverIdParam}`
})

const lastAirDate = computed(() => {
    const seasons = props?.titleDetails?.seasons;
    if (!seasons || seasons.length === 0) return undefined;

    for (let i = seasons.length - 1; i >= 0; i--) {
        const season = seasons[i];
        if (!season || !season.episodes) continue;

        const validEpisodes = season.episodes.filter(ep => Boolean(ep.air_date));
        if (validEpisodes.length > 0) {
            return validEpisodes
                .sort((a, b) => new Date(a.air_date) - new Date(b.air_date))
                .at(-1)
                .air_date;
        }
    }

    return undefined;
});
</script>

<template>
    <div class="title-details-page">
        <div class="layout-contained layout-spacing-top" :class="{'layout-spacing-bottom': titleDetails?.title_type === 'movie'}">
            <img 
                :src="getTitleImageUrl(titleDetails, 'original', 'backdrop')"
                :alt="`${titleDetails?.title_type} backdrop: ${titleDetails?.name}`"
                class="backdrop"
            >
    
            <div class="logo-wrapper" v-if="getTitleImageUrl(titleDetails, 'original', 'logo')">
                <img 
                    :src="getTitleImageUrl(titleDetails, 'original', 'logo')"
                    :alt="`${titleDetails?.title_type} logo: ${titleDetails?.name}`"
                    class="logo"
                >
            </div>
    
            <div class="main-info">
                <div class="left-side">
                    <img 
                        :src="getTitleImageUrl(titleDetails, 'original', 'poster')"
                        :alt="`${titleDetails?.title_type} poster: ${titleDetails?.name}`"
                        class="poster"
                    >

                    <h4>External Resources</h4>
                    <div class="links-wrapper">
                        <a
                            :href="tmdbBaseUrl"
                            target="_blank"
                            class="btn btn-even-padding btn-text"
                            title="View on TMDB"
                        >
                            <Tmdb class="four-letter"/>
                        </a>
                        <a
                            v-if="titleDetails?.imdb_id"
                            :href="`https://www.imdb.com/title/${titleDetails?.imdb_id}`"
                            target="_blank"
                            class="btn btn-even-padding btn-text"
                            title="View on IMDB"
                        >
                            <Imdb class="four-letter"/>
                        </a>
                        <a
                            v-if="titleDetails?.homepage"
                            :href="titleDetails?.homepage"
                            target="_blank"
                            class="btn btn-even-padding btn-text"
                            title="Visit Official Website"
                        >
                            <Link/>
                        </a>
                        
                        <hr>
                        
                        <div class="flex-row">
                            <a
                                :href="`https://www.justwatch.com/${settings.primaryCountry}/search?q=${titleDetails?.name_original}`"
                                target="_blank"
                                class="btn btn-even-padding btn-text"
                                title="Check Availability on JustWatch"
                            >
                                <JustWatch/>
                            </a>
                            <a  
                                v-if="titleDetails?.jellyfin_id && jellyfinConfig?.base_url"
                                :href="jellyfinLink"
                                target="_blank"
                                class="btn btn-even-padding btn-text"
                                title="Open in Jellyfin"
                            >
                                <Jellyfin/>
                            </a>
                        </div>
                    </div>
                </div>
                
                <div class="right-side">
                    <NoticeBlock
                        v-if="titleDetails?.user_details?.in_library === false"
                        type="warning"
                        :iconComponent="AlertTriangle"
                        header="Title not in Library"
                        message="Please note that the title is currently not in your library. It <strong>will not appear</strong> in search, listings or recommendations."
                    >
                        <button @click="addToLibrary">Add to library</button>
                    </NoticeBlock>

                    <NoticeBlock
                        v-if="waitingFor?.titleUpdate == false"
                        :iconComponent="updateResponse.icon"
                        :type="updateResponse.type"
                        :header="updateResponse.header"
                        :message="updateResponse.message"
                        :dismissible="true"
                        @dismiss="waitingFor.titleUpdate = null"
                    />
                    <NoticeBlock
                        v-if="waitingFor?.titleUpdate == true"
                        type="info"
                        header="Updating title..."
                        message="This shouldn't take long."
                        :loadingEffect="true"
                    />

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
                        <div class="stat tmdb">
                            <div>
                                <Tmdb/>
                                {{ numberFormatters.formatNumberToLocale(titleDetails?.tmdb_vote_average) || '-' }}
                            </div>
                            <div class="votes" :title="`${numberFormatters.formatNumberToLocale(titleDetails?.tmdb_vote_count)} votes`">
                                ({{ numberFormatters.formatCompactNumber(titleDetails?.tmdb_vote_count) }} votes)
                            </div>
                        </div>
    
                        <template v-if="titleDetails?.title_type == 'movie'">
                            |
                            <div class="stat">
                                {{ timeFormatters.minutesToHrAndMin(titleDetails?.movie_runtime) }}
                            </div>
                        </template>
                        <template v-else>
                            |
                            <div class="stat">
                                {{ titleDetails?.seasons?.length }}
                                Season{{ titleDetails?.seasons?.length == 1 ? '': 's' }},
                                {{ titleDetails?.seasons?.reduce((sum, s) => sum + s.episodes.length, 0) }}
                                Episode{{ titleDetails?.seasons?.reduce((sum, s) => sum + s.episodes.length, 0) == 1 ? '': 's' }}
                            </div>
                        </template>
    
                        |
                        <div class="stat btn-underline" @click="AgeRatingsModal.open()">
                            {{ chosenAgeRating?.rating || '-'  }}
                            <template v-if="chosenAgeRating?.descriptors">
                                ({{ chosenAgeRating?.descriptors }})
                            </template>
                        </div>
    
                        |
                        <div
                            class="stat"
                            :title="
                                titleDetails?.title_type == 'tv'
                                ? `${timeFormatters.timestampToFullDate(titleDetails?.release_date)} - ${timeFormatters.timestampToFullDate(lastAirDate)}`
                                : `${timeFormatters.timestampToFullDate(titleDetails?.release_date)}`
                            "
                        >
                            {{ timeFormatters.timestampToYear(titleDetails?.release_date) }}
                            <template v-if="
                                titleDetails?.title_type == 'tv' &&
                                timeFormatters.timestampToYear(lastAirDate) !=
                                timeFormatters.timestampToYear(titleDetails?.release_date)
                            ">
                                - {{ timeFormatters.timestampToYear(lastAirDate) }}
                            </template>
                        </div>
                        
                        |
                        <div class="stat genres">
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
            
                    <p>{{ titleDetails?.overview }}</p>

                    <div class="actions">
                        <div class="primary-actions">
                            <div class="watch-count-buttons">
                                <button
                                    @click="adjustWatchCount"
                                    :class="titleDetails?.user_details?.watch_count ? 'btn-positive' : 'btn-primary'"
                                >
                                    <template v-if="!titleDetails?.user_details?.watch_count">
                                        Mark watched
                                    </template>
                                    <template v-else-if="titleDetails?.user_details?.watch_count == 1">
                                        <Check size="sm"/> Watched
                                    </template>
                                    <template v-else-if="titleDetails?.user_details?.watch_count > 1">
                                        Watched {{ titleDetails?.user_details?.watch_count }} times
                                    </template>
                                </button>
                                <button 
                                    v-if="titleDetails?.user_details?.watch_count"
                                    @click="removeFromTitleWatchCount"
                                >
                                    <Minus size="sm"/>
                                </button>
                            </div>
                            
                            <Heart
                                pack="filled"
                                class="btn btn-text btn-even-padding"
                                :class="{'btn-favourite': titleDetails?.user_details?.is_favourite }"
                                @click="toggleFavourite"
                            />
                            <Clock
                                pack="filled"
                                class="btn btn-text btn-even-padding"
                                :class="{'btn-accent': titleDetails?.user_details?.in_watchlist }"
                                @click="toggleWatchlist"
                            />
                            <AlbumCovers
                                pack="filled"
                                class="btn btn-text btn-even-padding"
                                @click="adjustCollections"
                            />

                            <MapIcon
                                v-if="titleDetails?.title_type == 'tv'"
                                pack="filled"
                                class="btn btn-text btn-even-padding"
                                @click="$refs.EpisodeMapModal.open()"
                            />
    
                            <ListMinus
                                v-if="titleDetails?.user_details?.in_library"
                                pack="filled"
                                class="btn btn-text btn-even-padding"
                                @click="removeFromLibrary"
                            />
                            <ListPlus
                                v-else
                                pack="filled"
                                class="btn btn-text btn-even-padding"
                                @click="addToLibrary"
                            />
                        </div>

                        <KebabMenu
                            :menuItems="[
                                { iconComponent: RefreshCw, label: 'Update Details', action: updateTitleDetails },
                                { iconComponent: Images, label: 'Manage Images', action: ImagesModal?.open },
                                { iconComponent: Translate, label: 'Change Language', action: LocaleModal?.open },
                            ]"
                        />
                    </div>
                    
                    <SeasonsListing 
                        v-if="titleDetails?.title_type === 'tv'" 
                        :titleDetails="titleDetails"
                        :class="{'layout-spacing-bottom': !similarTitles?.titles?.length > 0}"
                    />
                </div>
            </div>
        </div>

        <TitleCarousel 
            v-if="similarTitles?.titles?.length > 0"
            :carouselData="similarTitles"
            class="layout-spacing-bottom"
        />


        <!-- Modals -->

        <ModalBase header="Age ratings" ref="AgeRatingsModal" :minimumCard="true">
            <p>The following list shows age ratings by country for the current title. The star icon indicates your <Star pack="filled" size="xs" class="inline"/> preferred language (or <Star size="xs" class="inline"/> fallback). You can adjust your preffered languages in the <router-link to="/account">application settings</router-link>.</p>
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
                                    <Star
                                        v-if="ageRating.iso_3166_1 === settings.primaryCountry"
                                        pack="filled"
                                        title="Your preferred language"
                                        size="sm"
                                    />
                                    <Star
                                        v-else-if="settings.preferredCountries.includes(ageRating.iso_3166_1)"
                                        title="Default backup"
                                        size="sm"
                                    />
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
                Missing age ratings for your country?
                <a class="subtle" target="_blank" :href="tmdbEditAgeRatingUrl">Add them on TMDB</a>.
                <Tooltip>
                    <InfoCircle pack="filled" size="xs" class="inline"/>
                    <template #content>
                        TMDB takes a moment to process changes. They will appear here once the changes go live, and the titles details are updated.
                    </template>
                </Tooltip>
            </span>
        </ModalBase>

        <ModalBase header="Episode Map" ref="EpisodeMapModal">
            <EpisodeMap :seasons="titleDetails?.seasons"/>
        </ModalBase>

        <ModalImages
            ref="ImagesModal"
            :titleId="titleDetails?.title_id"
            :userDetails="titleDetails?.user_details"
            :displayLocale="titleDetails?.display_locale"
            :tmdbBaseUrl="tmdbBaseUrl"
        />

        <ModalLocale
            ref="LocaleModal"
            :titleDetails="titleDetails"
            :fetchTitleDetails="fetchTitleDetails"
            :waitingFor="waitingFor"
        />
    </div>
</template>

<style scoped>
.title-details-page {
    display: flex;
    flex-direction: column;
    gap: var(--spacing-md);
}

.left-side {
    display: flex;
    flex-direction: column;
    min-width: 225px;
    width: 30vw;
    max-width: 325px;
}


img.backdrop {
    width: 100%;
    height: 100vh;
    max-height: 1200px;
    top: 0;
    left: 0;
    position: absolute;
    object-fit: cover;

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

    z-index: 5;
}

.notice {
    margin-bottom: var(--spacing-md);
}

.main-info {
    display: grid;
    grid-template-columns: auto 1fr;
    gap: var(--spacing-md-lg);

    > * {
        z-index: 5;
    }
}

/* .right-side {
    background-color: rgba(0, 0, 0, 0.226);
    backdrop-filter: blur(8px);
    padding: var(--spacing-md-lg);
    border-radius: var(--border-radius-lg);
    border: 1px solid var(--c-border);
} */


img.poster {
    width: 100%;
    aspect-ratio: 2/3;
    object-fit: cover;
    background-color: var(--c-bg-level-1);
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
    flex-direction: row;
    align-items: center;
    column-gap: var(--spacing-sm-md);
    row-gap: var(--spacing-xs);
    font-weight: 600;
    flex-wrap: wrap;

    .stat {
        display: flex;
        white-space: nowrap;
    }

    .tmdb {
        flex-direction: column;
        align-items: center;
        gap: var(--spacing-xs);
        
        .votes {
            font-size: var(--fs-neg-2);
            font-weight: 500;
            color: var(--c-text-subtle);
            margin-bottom: 0px;
            margin-top: -4px;
        }
    }

    .genres {
        gap: var(--spacing-xs);
    }
}


.watch-count-buttons {
    display: flex;
    width: 220px;

    button:first-child {
        flex: 1;
    }
    button:first-child:not(:last-child) {
        border-top-right-radius: 0;
        border-bottom-right-radius: 0;
    }
    button:last-child:not(:first-child) {
        padding-inline: var(--spacing-md);
        border-top-left-radius: 0;
        border-bottom-left-radius: 0;
    }
}


.actions {
    display: flex;
    gap: var(--spacing-sm);
    justify-content: space-between;

    .primary-actions {
        display: flex;
        gap: var(--spacing-sm);
    }
}

/* .links h4 {
    margin-top: 0;
} */
.links-wrapper {
    display: flex;
    flex-wrap: wrap;
    
    .btn {
        font-size: var(--fs-3);
        display: flex;
        align-items: center;
        text-decoration: none;

        svg {
            width: 27.65px;
            height: auto;
        }
        svg.four-letter {
            width: 42px;
            height: auto;
        }
    }
}

.data-actions {
    display: flex;
    flex-direction: column;
    gap: var(--spacing-sm);

    form {
        display: grid;
        grid-template-columns: 100px auto;
        gap: var(--spacing-sm);

        input {
            margin: 0;
        }
    }
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
