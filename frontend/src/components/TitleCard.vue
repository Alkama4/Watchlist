<script setup>
import { resolveImagePath } from '@/utils/imagePath';
import { timeFormatters } from '@/utils/formatters';
import Tmdb from '@/assets/icons/tmdb.svg'
import { useSearchStore } from '@/stores/search';
import { fastApi } from '@/utils/fastApi';
import { ref } from 'vue';
import LoadingButton from './LoadingButton.vue';

const searchStore = useSearchStore();

const waiting = ref(null)

async function addTitle() {
    waiting.value = true;
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
        waiting.value = false;
    }
}

async function removeTitle() {
    waiting.value = true;
    try {
        await fastApi.titles.library.remove(titleInfo.title_id)
        titleInfo.user_details.in_library = false;
    } finally {
        waiting.value = false;
    }
}

const { titleInfo } = defineProps({
    titleInfo: {
        type: Object,
        required: true,
    }
})

</script>

<template>
    <component 
        :is="titleInfo.title_id ? 'router-link' : 'div'"
        :to="titleInfo.title_id ? `/title/${titleInfo.title_id}` : null"
        class="title-card"
        draggable="false"
    >
        <img 
            :src="resolveImagePath(titleInfo, '800', 'poster')"
            :alt="`${titleInfo?.title_type === 'tv' ? 'TV show' : 'Movie'} poster: ${titleInfo?.name}`"
            draggable="false"
        >
    
        <div class="button-row" v-if="searchStore.tmdbFallback" @click.prevent>
            <LoadingButton 
                v-if="!titleInfo?.user_details?.in_library" 
                class="btn-primary"
                :loading="waiting"
                @click="addTitle(titleInfo.title_id, titleInfo.tmdb_id, titleInfo.title_type)"
            >
                <i class="bx bx-plus"></i>
                Add
            </LoadingButton>
    
            <LoadingButton v-else :loading="waiting" @click="removeTitle(titleInfo.title_id)">
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
                {{ titleInfo?.tmdb_vote_average?.toFixed(1) }}
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

        <div v-if="titleInfo?.user_details?.watch_count" class="watch-count-marker">
            <template v-if="titleInfo?.user_details?.watch_count >= 2">
                {{ titleInfo?.user_details?.watch_count }}
            </template>
            <i v-else class="bx bx-check"></i>
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
}
.title-card:last-of-type {
    padding-right: 0;
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
    color: var(--c-text-3);
    font-size: var(--fs-neg-1);
}

.watch-count-marker {
    position: absolute;
    top: var(--spacing-sm);
    left: var(--spacing-sm);
    background-color: var(--c-positive);
    width: var(--spacing-lg);
    height: var(--spacing-lg);
    border-radius: 100px;
    display: flex;
    justify-content: center;
    align-items: center;
    font-weight: 500;
    color: var(--c-text);
}
.watch-count-marker i {
    font-size: var(--fs-3);
}
</style>