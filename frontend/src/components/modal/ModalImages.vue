<script setup>
import { ref, computed, inject } from 'vue'
import ModalBase from '@/components/modal/ModalBase.vue'
import { fastApi } from '@/utils/fastApi';
import { buildImageUrl } from '@/utils/imagePath';

const props = defineProps({
    titleId: { type: Number, required: true },
    seasonId: { type: Number, required: true },
    userDetails: { type: Object, required: true }
})

defineExpose({ open })

const updateChosenImage = inject('updateChosenImage')

const imageData = ref({ posters: {}, backdrops: {}, logos: {} });
const activeType = ref('posters');
const modalRef = ref(null);

const localeFilters = ref({
    posters: 'all',
    backdrops: 'all',
    logos: 'all'
});

const imageCategories = [
    { key: 'posters', label: 'Posters' },
    { key: 'backdrops', label: 'Backdrops' },
    { key: 'logos', label: 'Logos' }
];

const availableCategories = computed(() => {
    return imageCategories.filter(cat => imageData.value[cat.key]?.total_count > 0);
});

const currentCategory = computed(() => {
    return imageData.value[activeType.value] || [];
});

const filteredImages = computed(() => {
    const images = currentCategory.value?.images || []; 
    const currentFilter = localeFilters.value[activeType.value];
    return images.filter((img) => currentFilter === 'all' || img.locale == currentFilter);
})

async function open() {
    if (props.titleId) {
        imageData.value = await fastApi.titles.imagesById(props.titleId);
    } else if (props.seasonId) {
        imageData.value = await fastApi.seasons.imagesById(props.seasonId);
    } else {
        throw '[ModalImages] Missing titleId or seasonId.'
    }

    if (availableCategories.value.length > 0) {
        activeType.value = availableCategories.value[0].key;
    }

    modalRef.value.open();
}

async function setAsPreferred(imageType, imagePath) {
    const isTitle = !!props.titleId;
    const id = props.titleId || props.seasonId;
    const apiTarget = isTitle ? fastApi.titles : fastApi.seasons;

    await apiTarget.imagesSetPreference(id, imageType, { image_path: imagePath });
    updateDomData(imageType, imagePath);
}

function updateDomData(imageType, imagePath) {
    // Notify the parent component
    updateChosenImage({ 
        imageType,
        imagePath,
        seasonId: props.seasonId ?? null
    });

    // Update the internal data as well
    const categoryKey = `${imageType}s`; 
    const category = imageData.value[categoryKey];

    if (category?.images) {
        category.images.forEach(img => {
            img.is_user_choice = (img.file_path === imagePath);
        });
    }
}
</script>

<template>
    <ModalBase header="Choose displayed images" ref="modalRef">
        <div class="modal-images" :class="activeType">
            <details>
                <summary>How are images selected?</summary>
                <div class="content">
                    <p>The system automatically displays the highest-rated images available (tagged "Default") with some caveats. For <strong>posters and logos</strong> it prioritizes your language preferences (set in setttings), and for <strong>backdrops</strong> it prefers the textless versions. If an image with a higher rating is found, the system will swap it out automatically.</p>
    
                    <p><strong>Favoriting an image</strong> locks your selection. This overrides the automated system and ensures the image will never change unless you update it again yourself.</p>
    
                    <p class="soft"><em>Note: Backdrops work best without text (No locale).</em></p>
                </div>
            </details>

            <div class="tab-buttons">
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

                <select v-model="localeFilters[activeType]">
                    <option value="all">All</option>
                    <option 
                        v-for="locale in currentCategory?.available_locale"
                        :key="locale"
                        :value="locale"
                    >
                        {{ locale === null ? 'No locale' : locale }}
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

                    <div class="details-section">
                        <div class="star-wrapper">
                            <button
                                class="btn-square btn-text"
                                :class="{'subtle': !image?.is_user_choice}"
                                @click="setAsPreferred(image.type, image.is_user_choice ? null: image.file_path)"
                            >
                                <i class="bx" :class="image?.is_user_choice ? 'bxs-star' : 'bx-star'"></i>
                            </button>
                        </div>
    
                        <div class="details">
                            <div class="resolution">{{ image?.width }}px x {{ image?.height }}px</div>
                            <div class="rest">{{ image?.vote_average.toFixed(1) }} &bull; {{ image?.locale ?? 'No locale' }}</div>
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
        display: flex;

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


    .details-section {
        display: flex;
        align-items: center;
        padding-top: var(--spacing-sm);

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
            display: flex;
            flex-direction: column;
            gap: var(--spacing-xs);
            color: var(--c-text);
    
            .rest {
                color: var(--c-text-soft)
            }
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