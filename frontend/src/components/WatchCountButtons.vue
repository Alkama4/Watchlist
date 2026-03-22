<script setup>
import { Check, Minus } from '@boxicons/vue';
import LoadingButton from './LoadingButton.vue';
import { ref, computed } from 'vue';
import { adjustWatchCount } from '@/utils/titleActions';

const props = defineProps({
    watchCount: { type: [Number, Boolean], default: 0 },
    title: { type: Object, required: false },
    season: { type: Object, required: false },
    episode: { type: Object, required: false }
});

const waitingFor = ref({});

const entity = computed(() => {
    if (props.episode) return {
        type: 'episode',
        data: props.episode,
        id: props.episode.episode_id
    };
    if (props.season) return {
        type: 'season',
        data: props.season,
        id: props.season.season_id
    };
    return {
        type: 'title',
        data: props.title,
        id: props.title?.title_id
    };
});

const handleAction = (action) => {
    const { type, data } = entity.value;
    adjustWatchCount[type][action](data, waitingFor.value, props.title);
};
</script>

<template>
    <div class="watch-count-buttons">
        <LoadingButton
            :class="watchCount ? 'btn-positive' : 'btn-primary'"
            :loading="waitingFor[`${entity.type}WcAdd_${entity.id}`]"
            @click="handleAction('add')"
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
            :loading="waitingFor[`${entity.type}WcSub_${entity.id}`]"
            @click="handleAction('subtract')"
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
        flex: 2;
    }
    button:last-child {
        flex: 1;
        min-width: 52px;
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