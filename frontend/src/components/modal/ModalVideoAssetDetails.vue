<script setup>
import ModalBase from '@/components/modal/ModalBase.vue';
import { timeFormatters, videoAssetFormatters } from '@/utils/formatters';
import { buildVideoAssetUrl, getDeviceHandler } from '@/utils/videoAssetUtils';
import { ArrowRightStroke, Play } from '@boxicons/vue';
import { computed, ref } from 'vue';

defineExpose({ open })

const modalRef = ref(null);

const props = defineProps({
    videoAsset: {
        type: Object,
        required: true
    },
    titleFolder: {
        type: Object,
        required: true
    }
})

function open() {
    modalRef.value.open();
}

const modalHeader = computed(() => {
    const parts = props.videoAsset?.file_name?.split('.');
    if (!parts) return '';
    
    return parts.length > 1 ? parts.slice(0, -1).join('.') : parts[0];
});
</script>

<template>
    <ModalBase :header="modalHeader" ref="modalRef">
        <div class="details-container">
            <section class="first-things">
                <div class="first-row">
                    <div class="small-details">
                        <span class="badge" :class="videoAsset?.video_type">{{ videoAsset?.video_type }}</span>
                        <span class="id-tag">#{{ videoAsset?.video_asset_id }}</span>
                    </div>
                    <a
                        :href="buildVideoAssetUrl(videoAsset, null, getDeviceHandler())"
                        class="btn btn-primary no-deco"
                    >
                        <Play pack="filled" size="sm"/>
                        <span>Play</span>
                    </a>
                </div>

                <div class="code-area code break-all">
                    {{ videoAsset?.file_path }}
                </div>
            </section>

            <section v-if="videoAsset?.is_linked" class="linked-section">
                <h4>Linked To</h4>
                <RouterLink
                    :to="videoAsset?.linked_episode
                        ? `/title/${titleFolder?.linked_title?.title_id}?season=${videoAsset?.linked_episode?.season_number}`
                        : `/title/${titleFolder?.linked_title?.title_id}`"
                    class="linked-card btn no-deco"
                    target="_blank"
                >
                    <div class="title">{{ titleFolder?.linked_title?.name }}</div>
                    <div v-if="videoAsset?.linked_episode" class="sub-details">
                        <div class="sub-detail">
                            <span>S{{ String(videoAsset?.linked_episode?.season_number).padStart(2, '0') }}</span>
                            <span class="seperator">&bull;</span>
                            <span class="name">{{ videoAsset?.linked_episode?.season_name }}</span>
                        </div>
                        <div class="sub-detail">
                            <span>E{{ String(videoAsset?.linked_episode?.episode_number).padStart(2, '0') }}</span>
                            <span class="seperator">&bull;</span>
                            <span class="name">{{ videoAsset?.linked_episode?.episode_name }}</span>
                        </div>
                    </div>
                    <div class="linked-card-arrow">
                        <ArrowRightStroke width="32" height="32"/>
                    </div>
                </RouterLink>
            </section>
            <section v-else class="linked-section">
                <h4>Linked To</h4>
                <span class="not-linked">Not linked to any title</span>
            </section>

            <section>
                <h4>Technical details</h4>
                <div class="specs-lists-wrapper">
                    <dl class="specs-list">
                        <dt>Resolution</dt>
                        <dd class="value">{{ videoAsset?.resolution ?? '-' }}</dd>
                        <dt>Duration</dt>
                        <dd class="value">{{ timeFormatters.msToHrAndMin(videoAsset?.duration_ms) ?? '-' }}</dd>
                        <dt>File size</dt>
                        <dd class="value">{{ videoAssetFormatters.formatSize(videoAsset?.filesize_bytes) ?? '-' }}</dd>
                        <dt>Bitrate</dt>
                        <dd class="value">{{ videoAssetFormatters.formatBitrate(videoAsset?.filesize_bytes, videoAsset?.duration_ms) ?? '-' }}</dd>
                    </dl>
                    <dl class="specs-list">
                        <dt>Codec</dt>
                        <dd>{{ videoAsset?.codec ?? '-' }}</dd>
                        <dt>HDR Metadata</dt>
                        <dd>{{ videoAsset?.hdr_type ?? 'None' }}</dd>
                        <dt>Bit depth</dt>
                        <dd>{{ videoAsset?.bit_depth ? `${videoAsset.bit_depth}-bit` : '-' }}</dd>
                        <dt>Framerate</dt>
                        <dd>{{ videoAsset?.frame_rate ? `${videoAsset.frame_rate} fps` : '-' }}</dd>
                    </dl>
                </div>
            </section>
        </div>
    </ModalBase>
</template>

<style scoped>
.details-container {
    display: flex;
    flex-direction: column;
    overflow-y: auto;
}

.first-things {
    display: flex;
    flex-direction: column;
    row-gap: var(--spacing-md);

    .first-row {
        display: flex;
        justify-content: space-between;
    }
    
    .small-details {
        display: flex;
        align-items: center;
        gap: var(--spacing-md);
        
        .id-tag {
            color: var(--c-text-soft);
        }

        .badge {
            background-color: var(--c-neutral);
            color: var(--c-text);
        }
    }
}

/* Info Columns */
.specs-lists-wrapper {
    display: grid;
    grid-template-columns: 1fr 1fr;
    column-gap: var(--spacing-xl);
    row-gap: var(--spacing-sm);

    .specs-list {
        margin: 0;
        column-gap: 0;
        grid-template-columns: 150px auto;
    }
}


.linked-card {
    display: flex;
    gap: var(--spacing-sm);
    padding: var(--spacing-md) var(--spacing-md-lg);

    .title {
        font-weight: 700;
        font-size: var(--fs-1);
        margin-right: auto;

        display: -webkit-box;
        -webkit-line-clamp: 2;
        line-clamp: 2;
        -webkit-box-orient: vertical;
        overflow: hidden;
    }


    .sub-details {
        display: flex;
        flex-direction: row;
        column-gap: var(--spacing-md);

        .sub-detail {
            display: flex;
            gap: var(--spacing-xs-sm);
            font-size: var(--fs-neg-1);
            color: var(--c-text-subtle);

            .name {
                display: -webkit-box;
                -webkit-line-clamp: 1;
                line-clamp: 1;
                -webkit-box-orient: vertical;
                overflow: hidden;
            }
        }
    }

    .linked-card-arrow {
        color: var(--c-text-subtle);
        display: flex;
        justify-content: center;
        align-items: center;
        transition: color 0.15s, transform 0.15s;
    }

    &:hover .linked-card-arrow {
        color: var(--c-text);
        transform: translateX(3px);
    }
}


.not-linked {
    font-size: var(--fs-neg-1);
    color: var(--c-text-subtle);
}


@media (max-width: 768px) {
    .specs-lists-wrapper {
        grid-template-columns: 1fr;
    }
    .stats-grid {
        grid-template-columns: 1fr 1fr;
    }
    
    .linked-card .sub-details {
        flex-direction: column;
    }
}

@media (max-width: 400px) {
    .stats-grid {
        grid-template-columns: 1fr;
    }
}
</style>