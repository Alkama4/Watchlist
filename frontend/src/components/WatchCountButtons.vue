<script setup>
import { Check, Minus } from '@boxicons/vue';
import LoadingButton from './LoadingButton.vue';
import { ref } from 'vue';
import { adjustWatchCount } from '@/utils/titleActions';

const waitingFor = ref({});

defineProps({
    watchCount: {
        type: Boolean,
        default: false
    },
    item: {
        required: true
    },
})
</script>

<template>
    <div class="watch-count-buttons">
        <LoadingButton
            :class="watchCount ? 'btn-positive' : 'btn-primary'"
            :loading="waitingFor[`titleWcAdd_${item?.title_id || item?.season_id}`]"
            @click="adjustWatchCount.title.add(item, waitingFor)"
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
            :loading="waitingFor[`titleWcSub_${item?.title_id || item?.season_id}`]"
            @click="adjustWatchCount.title.subtract(item, waitingFor)"
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