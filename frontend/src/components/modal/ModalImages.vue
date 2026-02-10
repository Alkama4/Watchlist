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

const imageData = ref({ posters: {}, backdrops: {}, logos: {} });
const activeType = ref('posters');
const modalRef = ref(null);
const localeFilter = ref('all');

// Configuration for our types
const imageCategories = [
    { key: 'posters', label: 'Posters' },
    { key: 'backdrops', label: 'Backdrops' },
    { key: 'logos', label: 'Logos' }
];

// Determine how many categories actually have images
const availableCategories = computed(() => {
    return imageCategories.filter(cat => imageData.value[cat.key]?.total_count > 0);
});

const currentCategory = computed(() => {
    return imageData.value[activeType.value] || [];
});

const filteredImages = computed(() => {
    const images = currentCategory.value?.images || []; 
    return images.filter((img) => localeFilter.value === 'all' || img.locale == localeFilter.value);
})

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
    <ModalBase header="Title Images" ref="modalRef">
        <div class="modal-images" :class="activeType">
            <div v-if="availableCategories.length > 1" class="tab-buttons">
                <button 
                    v-for="cat in imageCategories" 
                    :key="cat.key"
                    :class="{ 'btn-primary': activeType === cat.key }"
                    :disabled="!imageData[cat.key]?.total_count"
                    @click="activeType = cat.key"
                >
                    {{ cat.label }} ({{ imageData[cat.key]?.total_count || 0 }})
                </button>

                <hr>

                <select v-model="localeFilter" v-if="currentCategory?.available_locale?.length >= 2">
                    <option value="all" selected>All</option>
                    <option 
                        v-for="locale in currentCategory?.available_locale"
                        :value="locale"
                    >
                        {{ locale === null ? 'No language' : locale }}
                    </option>
                </select>
            </div>

            <div class="images-wrapper">
                <div 
                    v-for="image in filteredImages"
                    :key="image.file_path"
                    class="image"
                    :class="{'user-choice': image?.is_user_choice, 'default': image?.is_default}"
                >
                    <a :href="buildImageUrl(image?.file_path, 'original', false)" target="_blank">
                        <img 
                            :src="buildImageUrl(image?.file_path, 400, false)"
                            :style="{'aspect-ratio': `${image?.width} / ${image?.height}`}"
                            loading="lazy"
                        >
                        <i class="bx bx-link-external"></i>
                    </a>

                    <div class="flex-row">
                        <div class="star-wrapper">
                            <button
                                class="btn-square btn-text"
                                :class="{'subtle': !image?.is_user_choice}"
                                @click="image.is_user_choice = !image.is_user_choice"
                            >
                                <i class="bx" :class="image?.is_user_choice ? 'bxs-star' : 'bx-star'"></i>
                            </button>
                        </div>
    
                        <div class="details">
                            <div>
                                {{ image?.vote_average }} / 10
                                ({{ image?.vote_count }} votes)
                            </div>
                            <div class="resolution">{{ image?.width }}px x {{ image?.height }}px</div>
                            <div class="locale">{{ image?.locale ?? 'No language' }}</div>
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
    width: 100vw;
    max-width: 100%;
}

.tab-buttons {
    display: flex;
    gap: var(--spacing-sm);
}

.images-wrapper {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
    overflow-y: auto;

    padding-top: var(--spacing-md);
    gap: var(--spacing-md);
}
.posters .images-wrapper {
    grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
}

hr {
    margin: var(--spacing-xs) var(--spacing-sm);
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

    a {
        position: relative;

        img {
            width: 100%;
            height: auto;
            object-fit: cover;
            border-radius: var(--border-radius-sm);
            background: var(--c-bg-level-1);
            transition: filter 0.1s ease-out;
        }
        i {
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            font-size: var(--fs-3);
            opacity: 0;
            transition: opacity 0.1s ease-out;
        }

        &:hover {
            img { filter: brightness(0.5); }
            i { opacity: 1; }
        }
    }

    .star-wrapper {
        display: flex;
        align-items: center;
        margin-right: var(--spacing-xs-sm);

        i {
            font-size: var(--fs-2);
        }
    }

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

    &.user-choice {
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
    &.user-choice.default {
        border-color: var(--c-favourite-border);

        &::after {
            color: var(--c-text);
            background-color: var(--c-favourite-border);
        }
    }
}

.logos .image img {
    background: 
        conic-gradient(
            transparent 0deg 90deg,
            var(--c-neutral-subtle) 90deg 180deg,
            transparent 180deg 270deg,
            var(--c-neutral-subtle) 270deg 360deg
        ) top left / 32px 32px;
}

</style>