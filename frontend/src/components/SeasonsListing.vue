<script setup>
import { computed, ref } from 'vue'
import { getTitleImageUrl } from '@/utils/imagePath';
import { timeFormatters } from '@/utils/formatters';
import Tmdb from '@/assets/icons/tmdb.svg'

defineProps({
    titleDetails: {
        type: Object,
        required: true
    }
})

const wrapper = ref(null)
const expanded = ref(false)
const limitHeight = 450

const scrollHeight = computed(() => wrapper.value?.scrollHeight + 45 + 16)
const limitOverflow = computed(() => scrollHeight.value > limitHeight)

const computedHeight = computed(() => {
    if (!limitOverflow.value) return scrollHeight.value  // content fits, use natural height
    return expanded.value ? scrollHeight.value : limitHeight
})
</script>

<template>
    <div class="season-listing">
        <h4>Seasons</h4>
        <div class="seasons-container" :style="{ height: computedHeight + 'px' }">
            <div ref="wrapper" class="seasons-wrapper">
                <router-link
                    v-for="season in titleDetails?.seasons"
                    :key="season?.season_id"
                    class="season-card btn btn-even-padding no-deco"
                    :to="`/title/${titleDetails?.title_id}?season=${season?.season_number}`"
                >
                    <img 
                        :src="getTitleImageUrl(season, '800', 'poster')"
                        :alt="`Season poster: ${season?.season_name}`"
                        class="poster"
                    >

                    <div class="details">
                        <h4>{{ season?.season_name }}</h4>
                        <div class="detail-row">
                            <Tmdb/>
                            {{ season?.tmdb_vote_average }}
                            &bull;
                            {{ timeFormatters.timestampToYear(season?.episodes[0]?.air_date) }}
                        </div>

                        <div class="detail-row">
                            {{ season?.episodes?.length }} episodes
                        </div>
                    </div>
                </router-link>
            </div>

            <div class="fade-overlay" :class="{'expanded': expanded}" @click="expanded = !expanded">
                <div class="show-more-text">
                    <template v-if="expanded">
                        <i class="bx bx-chevron-up"></i>
                        Show less
                        <i class="bx bx-chevron-up"></i>
                    </template>
                    <template v-else>
                        <i class="bx bx-chevron-down"></i>
                        Show more
                        <i class="bx bx-chevron-down"></i>
                    </template>
                </div>
            </div>
        </div>
    </div>
</template>

<style scoped>
.season-listing {
    margin-top: var(--spacing-lg);
}
.seasons-container {
    position: relative;
    overflow: hidden;
    transition: height 0.25s var(--transition-ease-out);
}
.seasons-wrapper {
    display: flex;
    flex-direction: column;
    gap: var(--spacing-sm-md);
}

.fade-overlay {
    position: absolute;
    bottom: 0;
    left: 0;
    right: 0;
    height: 128px;
    background: linear-gradient(to bottom, transparent, var(--c-bg));
    display: flex;
    align-items: flex-end;
    padding-bottom: var(--spacing-sm);
    cursor: pointer;
    transition: height 0.25s var(--transition-ease-out);

    &.expanded {
        height: 45px;
    }

    .show-more-text {
        width: 100%;
        height: 45px;
        display: flex;
        justify-content: center;
        align-items: center;
        font-weight: 600;
        font-size: var(--fs-neg-1);
        gap: var(--spacing-md);
        background-color: transparent !important;
        transition: 0.3s transform var(--transition-bounce);
    
        i {
            font-size: var(--fs-3);
        }
    }

    &:hover .show-more-text {
        transform: translateY(4px);
    }
    &:hover.expanded .show-more-text {
        transform: translateY(-4px);
    }
}

.season-card {
    gap: var(--spacing-sm-md);
    border-radius: var(--border-radius-md);
    justify-content: flex-start;
    font-weight: 400;
}

img.poster {
    height: 100px;
    border-radius: var(--border-radius-sm);
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
}

h4 {
    margin: 0;
    margin-bottom: var(--spacing-sm);
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

.detail-row {
    display: flex;
    align-items: center;
    gap: var(--spacing-xs);
    font-size: var(--fs-neg-1);
}
</style>