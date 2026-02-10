<script setup>
import { ref, computed } from 'vue'
import ModalBase from '@/components/modal/ModalBase.vue'
import { fastApi } from '@/utils/fastApi';
import { buildImageUrl } from '@/utils/imagePath';
import { isoFormatters } from '@/utils/formatters';

const props = defineProps({
    titleId: {
        type: Number,
        required: true
    },
    userDetails: {
        type: Object,
        required: true
    }
})

defineExpose({ open })

const imageData = ref({ posters: [], backdrops: [], logos: [] });
const activeType = ref('posters');
const modalRef = ref(null)

// Configuration for our types
const imageCategories = [
    { key: 'posters', label: 'Posters' },
    { key: 'backdrops', label: 'Backdrops' },
    { key: 'logos', label: 'Logos' }
];

// Determine how many categories actually have images
const availableCategories = computed(() => {
    return imageCategories.filter(cat => imageData.value[cat.key]?.length > 0);
});

// Get the images for the currently selected tab
const currentImages = computed(() => {
    return imageData.value[activeType.value] || [];
});

async function open() {
    const data = await fastApi.titles.imagesById(props.titleId);
    imageData.value = data;

    // Default to the first category that has images
    if (availableCategories.value.length > 0) {
        activeType.value = availableCategories.value[0].key;
    }

    modalRef.value.open();
}
</script>

<template>
    <ModalBase header="Choose Title Images" ref="modalRef">
        <div class="modal-images">
            <div v-if="availableCategories.length > 1" class="tab-buttons">
                <button 
                    v-for="cat in imageCategories" 
                    :key="cat.key"
                    :class="{ 'btn-primary': activeType === cat.key }"
                    :disabled="!imageData[cat.key]?.length"
                    @click="activeType = cat.key"
                >
                    {{ cat.label }} ({{ imageData[cat.key]?.length || 0 }})
                </button>
            </div>

            <div class="images-wrapper">
                <div 
                    v-for="image in currentImages"
                    :key="image.file_path"
                    class="image"
                    :class="{'user-choise': image?.is_user_choise, 'default': image?.is_default}"
                >
                    <a :href="buildImageUrl(image?.file_path, 'original', false)" target="_blank">
                        <img :src="buildImageUrl(image?.file_path, 400, false)" alt="">
                    </a>

                    <div class="flex-row">
                        <div class="markers">
                            <button
                                class="btn-square btn-text"
                                :class="{'subtle': !image?.is_user_choise}"
                                @click="image.is_user_choise = !image.is_user_choise"
                            >
                                <i class="bx" :class="image?.is_user_choise ? 'bxs-star' : 'bx-star'"></i>
                            </button>
                        </div>
    
                        <div class="details">
                            <div>
                                {{ image?.vote_average }}
                                ({{ image?.vote_count }} votes)
                            </div>
                            <div class="resolution">{{ image?.width }}px x {{ image?.height }}px</div>
                            <div class="locale">{{ isoFormatters.iso_3166_1ToCountry(image?.iso_3166_1) ?? 'No language' }}</div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </ModalBase>
</template>

<style scoped>
.modal-images {
    display: flex;
    flex-direction: column;
    overflow: hidden;
    gap: var(--spacing-md);
}

.tab-buttons {
    display: flex;
    gap: var(--spacing-sm);
}

.images-wrapper {
    display: flex;
    flex-wrap: wrap;
    overflow-y: auto;
    gap: var(--spacing-md);
    padding-top: var(--spacing-md);
}

.image {
    position: relative;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    background: var(--c-bg-level-2);
    padding: var(--spacing-sm);
    border-radius: var(--border-radius-md);
    border: 2px solid transparent;

    .details {
        font-size: var(--fs-neg-1);
        margin-top: var(--spacing-sm);
        display: flex;
        flex-direction: column;
        gap: var(--spacing-xs);

        .resolution,
        .locale {
            color: var(--c-text-soft);
        }
    }

    &.user-choise {
        background-color: var(--c-favourite);
    }
    &.default {
        border-color: var(--c-border);

        &::after {
            content: 'Default';
            position: absolute;
            bottom: calc(100% + 2px);
            left: var(--spacing-md);
            padding: 0px var(--spacing-sm);
            border-top-left-radius: var(--border-radius-sm);
            border-top-right-radius: var(--border-radius-sm);

            font-size: var(--fs-neg-2);
            font-weight: 600;
            color: var(--c-text-soft);
            background-color: var(--c-border);
        }
    }
    &.user-choise.default {
        border-color: var(--c-favourite-subtle);

        &::after {
            color: var(--c-text);
            background-color: var(--c-favourite-subtle);
        }
    }
}

.markers {
    display: flex;
    align-items: center;
    margin-right: var(--spacing-xs-sm);

    button .inactive {
        color: var(--c-text-subtle);

    }
    button:hover .inactive {
        color: var(--c-text-soft);
    }
}

i {
    font-size: var(--fs-2);
}

img {
    max-width: 300px;
    max-height: 300px;
    height: auto;
    object-fit: cover;
    /* border-radius: var(--border-radius-sm); */
}


</style>