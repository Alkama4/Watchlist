<script setup>
import { getTitleImageUrl } from '@/utils/imagePath';
import { timeFormatters } from '@/utils/formatters';
import Tmdb from '@/assets/icons/tmdb.svg'
import { useSearchStore } from '@/stores/search';
import { fastApi } from '@/utils/fastApi';
import { ref } from 'vue';
import LoadingButton from '@/components/LoadingButton.vue';

const searchStore = useSearchStore();

const waiting = ref({})

async function addTitle() {
    waiting.value.library = true;
    try {
        if (titleInfo.title_id) {
            await fastApi.titles.library.add(titleInfo.title_id)
        } else {
            // Brand new title so need to use tmdb_id
            const response = await fastApi.titles.addToLibrary({
                tmdb_id: titleInfo.tmdb_id,
                title_type: titleInfo.title_type
            })
    
            // Need to init some data
            titleInfo.title_id = response.title_id;
        }
        
        // The user_details might not exist regardless if title_id exists.
        // Based on if its falsy fill in the data that this component uses
        // and set to be in library
        if (!titleInfo.user_details) {
            titleInfo.user_details = {
                in_library: true,
                is_favourite: false,
                in_watchlist: false,
                watch_count: 0,
            }
        } else {
            titleInfo.user_details.in_library = true
        }
    } finally {
        waiting.value.library = false;
    }
}

async function removeTitle() {
    waiting.value.library = true;
    try {
        await fastApi.titles.library.remove(titleInfo.title_id)
        titleInfo.user_details.in_library = false;
    } finally {
        waiting.value.library = false;
    }
}


async function toggleFavourite() {
    waiting.value.favourite = true;
    try {
        let response;
        if (titleInfo.user_details.is_favourite) {
            response = await fastApi.titles.setFavourite(titleInfo.title_id, false);
        } else {
            response = await fastApi.titles.setFavourite(titleInfo.title_id, true);
        }
        if (!response) return;
    
        titleInfo.user_details.is_favourite = response.is_favourite;
    } finally {
        waiting.value.favourite = false;
    }
}

async function toggleWatchlist() {
    waiting.value.watchlist = true;
    try {
        let response;
        if (titleInfo.user_details.in_watchlist) {
            response = await fastApi.titles.setWatchlist(titleInfo.title_id, false);
        } else {
            response = await fastApi.titles.setWatchlist(titleInfo.title_id, true);
        }
        if (!response) return;
        
        titleInfo.user_details.in_watchlist = response.in_watchlist;
    } finally {
        waiting.value.watchlist = false;
    }
}

async function addToWatchCount() {
    waiting.value.watchCountAdd = true;
    try {
        const response = await fastApi.titles.setWatchCount(titleInfo.title_id, titleInfo.user_details.watch_count + 1);
        titleInfo.user_details.watch_count = response.watch_count;
    } finally {
        waiting.value.watchCountAdd = false;
    }
}

async function subtractFromWatchCount() {
    waiting.value.watchCountSubtract = true;
    try {
        // Prevent going below 0
        const newCount = Math.max(0, titleInfo.user_details.watch_count - 1);
        const response = await fastApi.titles.setWatchCount(titleInfo.title_id, newCount);
        titleInfo.user_details.watch_count = response.watch_count;
    } finally {
        waiting.value.watchCountSubtract = false;
    }
}

const { titleInfo, storeImageFlag } = defineProps({
    titleInfo: {
        type: Object,
        required: true,
    },
    storeImageFlag: {
        type: Boolean,
        default: true
    },
    gridMode: {
        type: Boolean,
        default: false
    },
    index: {
        type: Number,
    }
})

</script>

<template>
    <component 
        :is="titleInfo.title_id ? 'router-link' : 'div'"
        :to="titleInfo.title_id ? `/title/${titleInfo.title_id}` : null"
        :style="`animation-delay: ${(index ?? titleInfo?.batchIndex ?? 0) * 0.01}s`"
        class="title-card"
        :class="{'grid-mode': gridMode}"
        draggable="false"
    >
        <img 
            :src="getTitleImageUrl(titleInfo, '800', 'poster', storeImageFlag)"
            :alt="`${titleInfo?.title_type === 'tv' ? 'TV show' : 'Movie'} poster: ${titleInfo?.name}`"
            draggable="false"
        >
    
        <div class="button-row" v-if="searchStore.tmdbFallback" @click.prevent>
            <LoadingButton 
                v-if="!titleInfo?.user_details?.in_library" 
                class="btn-primary"
                :loading="waiting?.library"
                @click="addTitle(titleInfo.title_id, titleInfo.tmdb_id, titleInfo.title_type)"
            >
                <i class="bx bx-plus"></i>
                Add
            </LoadingButton>
    
            <LoadingButton v-else :loading="waiting?.library" @click="removeTitle(titleInfo.title_id)">
                <i class="bx bx-trash"></i>
                Remove
            </LoadingButton>

            <a 
                class="btn no-deco"
                :href="`https://www.themoviedb.org/${titleInfo?.title_type}/${titleInfo?.tmdb_id}`"
                target="_blank"
                @click.stop
            >
                <i class="bx bx-link-external"></i>
            </a>
        </div>

        <div class="details">
            <h5>{{ titleInfo?.name }}</h5>
            <div class="detail-row">
                <Tmdb/>
                {{ titleInfo?.tmdb_vote_average ? titleInfo?.tmdb_vote_average?.toFixed(1) : "-" }}
                &bull;
                {{ timeFormatters.timestampToYear(titleInfo?.release_date) }}
            </div>

            <div v-if="!searchStore.tmdbFallback" class="detail-row">
                <template v-if="titleInfo?.title_type === 'tv'">
                    {{ titleInfo?.show_season_count }} seasons,
                    {{ titleInfo?.show_episode_count }} episodes
                </template>
                <template v-else>{{ timeFormatters.minutesToHrAndMin(titleInfo?.movie_runtime) }}</template>
            </div>
            <div v-else class="detail-row">
                {{ titleInfo?.title_type == 'tv' ? 'TV' : 'Movie' }}
            </div>
        </div>

        <div class="indicator-wrapper">
            <div
                :class="{
                    'active': titleInfo?.user_details?.watch_count
                }"
                class="indicator-circle watch-count"
            >
                <LoadingButton
                    class="inner-action"
                    :class="{'btn-positive': titleInfo?.user_details?.watch_count}"
                    :loading="waiting?.watchCountAdd"
                    @click.prevent="addToWatchCount()"
                >
                    <template v-if="titleInfo?.user_details?.watch_count >= 2">
                        {{ titleInfo?.user_details?.watch_count }}
                    </template>
                    <i v-else class="bx bx-check"></i>
                </LoadingButton>

                <LoadingButton
                    class="inner-action"
                    :loading="waiting?.watchCountSubtract"
                    @click.prevent="subtractFromWatchCount()"
                >
                    <i class="bx bx-minus"></i>
                </LoadingButton>
            </div>
    
            <LoadingButton
                :class="{
                    'active': titleInfo?.user_details?.is_favourite,
                    'btn-favourite': titleInfo?.user_details?.is_favourite
                }"
                class="indicator-circle favourite"
                :loading="waiting?.favourite"
                @click.prevent="toggleFavourite()" 
            >
                <i class="bx bxs-heart"></i>
            </LoadingButton>
    
            <LoadingButton
                :class="{
                    'active': titleInfo?.user_details?.in_watchlist,
                    'btn-accent': titleInfo?.user_details?.in_watchlist
                }"
                class="indicator-circle watchlist"
                :loading="waiting?.watchlist"
                @click.prevent="toggleWatchlist()" 
            >
                <i class="bx bxs-time"></i>
            </LoadingButton>
        </div>
    </component>
</template>


<style scoped>
.title-card {
    width: 200px;
    display: inline-flex;
    flex-direction: column;
    text-decoration: none;
    position: relative;
    padding-right: var(--spacing-md);

    animation: fadeIn 0.5s var(--transition-ease-out) forwards;
    opacity: 0;
}
.title-card:last-of-type,
.title-card.grid-mode {
    padding-right: 0;
}

@keyframes fadeIn {
    to {
        opacity: 1;
    }
}

img {
    border-radius: var(--border-radius-md);
    aspect-ratio: 2/3;
    object-fit: cover;
}

.button-row {
    margin-top: var(--spacing-sm);
    display: grid;
    grid-template-columns: 1fr auto;
    gap: var(--spacing-sm);
}
.button-row a {
    padding: var(--spacing-sm);
    width: 32px;
    box-sizing: border-box;
}

.details {
    display: flex;
    flex-direction: column;
    gap: var(--spacing-xs);
    margin-top: var(--spacing-xs-sm);
}

h5 {
    margin: 0;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

.detail-row {
    display: flex;
    align-items: center;
    gap: var(--spacing-xs);
    color: var(--c-text-soft);
    font-size: var(--fs-neg-1);
}


/* ----- Indicator circles ----- */

.indicator-wrapper {
    position: absolute;
    padding: var(--spacing-sm);
    top: 0;
    left: 0;
    --spacing-amount: 8px;
}

.indicator-circle {
    position: absolute;
    width: var(--spacing-lg);
    height: var(--spacing-lg);
    padding: 0;
    border-radius: 100px;
    left: 0;
    opacity: 0;
    overflow: hidden;
    backdrop-filter: blur(var(--blur-subtle));
    transition: 
        height 0.2s var(--transition-ease-out),
        left 0.2s var(--transition-ease-out), 
        opacity 0.1s var(--transition-ease-out),
        background-color 0.1s var(--transition-ease-out);

    &.watch-count {
        z-index: 50;
        left: calc(var(--spacing-amount) * 0 + var(--spacing-sm));

        &.active {
            background-color: var(--c-positive);

            &:hover {
                background-color: var(--c-neutral);
                height: calc(var(--spacing-lg) * 2);
            }
        }

        .inner-action {
            width: var(--spacing-lg);
            height: var(--spacing-lg);
            flex-shrink: 0;
            padding: 0;
            border-radius: 100px;
        }
    }
    &.favourite {
        z-index: 40;
        left: calc(var(--spacing-amount) * 1 + var(--spacing-sm));
    }
    &.watchlist {
        z-index: 30;
        left: calc(var(--spacing-amount) * 2 + var(--spacing-sm));
    }

    &.active {
        opacity: 1;
    }
    &.active:nth-child(1 of .active) {
        left: calc(var(--spacing-amount) * 0 + var(--spacing-sm)) !important;
    }
    &.active:nth-child(2 of .active) {
        left: calc(var(--spacing-amount) * 1 + var(--spacing-sm)) !important;
    }
    &.active:nth-child(3 of .active) {
        left: calc(var(--spacing-amount) * 2 + var(--spacing-sm)) !important;
    }
}


.indicator-circle.watch-count i {
    font-size: var(--fs-2);
}
.indicator-circle.watchlist i,
.indicator-circle.favourite i {
    font-size: var(--fs-1);
}

.title-card:hover .indicator-wrapper {
    --spacing-amount: calc(var(--spacing-lg) + var(--spacing-xs));

    .indicator-circle {
        opacity: 1;
    
        &.active:nth-child(1) {
            left: calc(var(--spacing-amount) * 0 + var(--spacing-sm)) !important;
        }
    
        &.active:nth-child(2) {
            left: calc(var(--spacing-amount) * 1 + var(--spacing-sm)) !important;
        }
    
        &.active:nth-child(3) {
            left: calc(var(--spacing-amount) * 2 + var(--spacing-sm)) !important;
        }
    }
}
</style>