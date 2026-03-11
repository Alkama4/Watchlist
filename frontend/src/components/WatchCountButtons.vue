<script setup>
import { Check, Minus } from '@boxicons/vue';
import LoadingButton from './LoadingButton.vue';
import { ref } from 'vue';
import { adjustWatchCount } from '@/utils/titleActions';

const waitingFor = ref({});

defineProps({
    watchCount: { type: Boolean, default: false },
    title: { required: false },
    season: { required: false }
})
</script>

<template>
    <div class="watch-count-buttons">
        <LoadingButton
            :class="watchCount ? 'btn-positive' : 'btn-primary'"
            :loading="waitingFor[`${season ? 'season' : 'title'}WcAdd_${season?.season_id || title?.title_id}`]"
            @click="adjustWatchCount[season ? 'season' : 'title'].add(season || title, waitingFor, title)"
        >
            <template v-if="!watchCount">
                Mark watched
            </template>
            <template v-else-if="watchCount == 1">
                <Check size="sm"/> Watched
            </template>
            <template v-else-if="watchCount > 1">
                Watched {{ watchCount }} times
            </template>
        </LoadingButton>
        <LoadingButton
            v-if="watchCount"
            :loading="waitingFor[`${season ? 'season' : 'title'}WcSub_${season?.season_id || title?.title_id}`]"
            @click="adjustWatchCount[season ? 'season' : 'title'].subtract(season || title, waitingFor, title)"
        >
            <Minus size="sm"/>
        </LoadingButton>
    </div>
</template>

<style scoped>
.watch-count-buttons {
    display: flex;
    width: 220px;

    button:first-child {
        flex: 1;
    }
    button:last-child {
        width: 52px;
    }
    button:first-child:not(:last-child) {
        border-top-right-radius: 0;
        border-bottom-right-radius: 0;
    }
    button:last-child:not(:first-child) {
        /* padding-inline: var(--spacing-md); */
        padding-inline: 0;
        border-top-left-radius: 0;
        border-bottom-left-radius: 0;
    }
}
</style>