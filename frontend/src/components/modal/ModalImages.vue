<script setup>
import { ref, computed, inject } from 'vue'
import ModalBase from '@/components/modal/ModalBase.vue'
import { fastApi } from '@/utils/fastApi'
import { buildImageUrl } from '@/utils/imagePath'
import LabelDropDown from '../LabelDropDown.vue'
import OptionPicker from '../OptionPicker.vue'
import { ArrowOutUpRightSquare, InfoCircle, RefreshCcwAltDot, Star } from '@boxicons/vue';
import Tooltip from '../Tooltip.vue'


const props = defineProps({
    titleId: { type: Number, required: true },
    seasonId: { type: Number, required: true },
    userDetails: { type: Object, required: true },
    displayLocale: { type: String, required: true },
    tmdbBaseUrl: { type: String, required: false }
})

defineExpose({ open })


const updateChosenImage = inject('updateChosenImage')
const imageCategories = [
    { key: 'posters', label: 'Posters' },
    { key: 'backdrops', label: 'Backdrops' },
    { key: 'logos', label: 'Logos' }
]
const modalRef = ref(null)
const imageData = ref({ posters: {}, backdrops: {}, logos: {} })
const activeType = ref('posters')
const localeFilters = ref({})


const availableCategories = computed(() => {
    return imageCategories.filter(cat => imageData.value[cat.key]?.total_count > 0)
})

const currentCategory = computed(() => {
    return imageData.value[activeType.value] || { images: [], available_locale: [] }
})

const localeFilterDefaults = computed(() => {
    return {
        posters: imageData.value?.posters?.images?.find(x => x.is_default)?.locale,
        backdrops: imageData.value?.backdrops?.images?.find(x => x.is_default)?.locale,
        logos: imageData.value?.logos?.images?.find(x => x.is_default)?.locale
    }
})

const localeFilterOptions = computed(() => {
    const available = currentCategory.value.available_locale || []
    return available.map(locale => ({
        label: locale === null ? 'No locale' : locale,
        value: locale,
        type: 'primary'
    }))
})

const filteredImages = computed(() => {
    const images = currentCategory.value?.images || []
    const currentFilter = localeFilters.value[activeType.value]
    return images.filter(img => currentFilter === 'all' || img.locale === currentFilter)
})

function getFileType(image) {
    const parts = image?.file_path.split(".");
    return parts[parts.length - 1];
}

async function open() {
    try {
        if (props.titleId) {
            imageData.value = await fastApi.titles.imagesById(props.titleId)
        } else if (props.seasonId) {
            imageData.value = await fastApi.seasons.imagesById(props.seasonId)
        } else {
            throw new Error('[ModalImages] Missing titleId or seasonId.')
        }

        // Sync filters with defaults and set initial tab
        localeFilters.value = { ...localeFilterDefaults.value }
        
        if (availableCategories.value.length > 0) {
            activeType.value = availableCategories.value[0].key
        }

        modalRef.value.open()
    } catch (error) {
        console.error(error)
    }
}

async function setAsPreferred(imageType, imagePath) {
    const isTitle = !!props.titleId
    const id = props.titleId || props.seasonId
    const apiTarget = isTitle ? fastApi.titles : fastApi.seasons

    await apiTarget.imagesSetPreference(id, imageType, { image_path: imagePath })
    updateDomData(imageType, imagePath)
}

function updateDomData(imageType, imagePath) {
    // Notify parent
    updateChosenImage({
        imageType,
        imagePath,
        seasonId: props.seasonId ?? null
    })

    // Update internal state to reflect the new selection
    const categoryKey = `${imageType}s`
    const category = imageData.value[categoryKey]

    if (category?.images) {
        category.images.forEach(img => {
            img.is_user_choice = (img.file_path === imagePath)
        })
    }
}

function catHasUserChoise(category) {
    const images = imageData.value?.[category.key]?.images;
    
    if (!images) return false;

    return images.some(image => image?.is_user_choice);
}
</script>

<template>
    <ModalBase :header="titleId ? 'Title Images' : 'Season Images'" ref="modalRef">
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
                <div class="cat-buttons">
                    <button 
                        v-for="cat in imageCategories" 
                        :key="cat.key"
                        :class="{ 'btn-primary': activeType === cat.key }"
                        :disabled="!imageData[cat.key]?.total_count"
                        @click="activeType = cat.key"
                    >
                        <Star :pack="catHasUserChoise(cat) ? 'filled' : ''" size="xs"/>
                        {{ cat.label }} ({{ imageData[cat.key]?.total_count || 0 }})
                    </button>
                </div>

                <hr>

                <div class="filters-wrapper">
                    <LabelDropDown
                        label="Image Locale"
                        :modified="localeFilters[activeType] != localeFilterDefaults[activeType]"
                    >
                        <OptionPicker
                            v-model="localeFilters[activeType]"
                            defaultValue="all"
                            :options="localeFilterOptions"
                        />
                    </LabelDropDown>
    
                    <RefreshCcwAltDot
                        v-if="localeFilters[activeType] != localeFilterDefaults[activeType]"
                        class="btn btn-text btn-even-padding"
                        size="sm"
                        @click="localeFilters[activeType] = localeFilterDefaults[activeType]"
                    />
                </div>
            </div>

            <div class="images-wrapper">
                <div 
                    v-for="image in filteredImages"
                    :key="image.file_path"
                    class="image-card"
                    :class="{'user-choice': image?.is_user_choice, 'default': image?.is_default}"
                >
                    <a :href="buildImageUrl(image?.file_path, 'original', false)" target="_blank">
                        <img 
                            :src="buildImageUrl(image?.file_path, 400, false)"
                            :style="{'aspect-ratio': `${image?.width} / ${image?.height}`}"
                            loading="lazy"
                        >
                        <ArrowOutUpRightSquare width="32" height="32"/>
                    </a>

                    <div class="details-section">
                        <div class="star-wrapper">
                            <button
                                class="btn-even-padding btn-text"
                                :class="{'subtle': !image?.is_user_choice}"
                                @click="setAsPreferred(image.type, image.is_user_choice ? null: image.file_path)"
                            >
                                <Star :pack="image?.is_user_choice ? 'filled' : ''"/>
                            </button>
                        </div>
    
                        <div class="details">
                            <div class="resolution">{{ image?.width }}px x {{ image?.height }}px</div>
                            <div class="rest">{{ image?.vote_average.toFixed(1) }} &bull; {{ image?.locale ?? 'No locale' }} &bull; {{ getFileType(image) }}</div>
                        </div>
                    </div>
                </div>
            </div>

            <span v-if="tmdbBaseUrl" class="subtle bottom-text">
                Want to vote or add images?
                <a :href="`${tmdbBaseUrl}/images/${activeType}`" target="_blank" class="subtle">
                    Browse {{ activeType }} on TMDB
                </a>.
                <Tooltip>
                    <InfoCircle pack="filled" size="xs" class="inline"/>
                    <template #content>
                        TMDB takes a moment to process changes. They will appear here once the changes go live, and the titles details are updated.
                    </template>
                </Tooltip>
            </span>
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
    overflow-x: auto;
    flex-shrink: 0;

    .cat-buttons {
        display: grid;
        grid-template-columns: 1fr 1fr 1fr;
        gap: var(--spacing-sm);
        white-space: nowrap;
    }

    .filters-wrapper {
        display: flex;
        flex-direction: row;
        gap: var(--spacing-xs-sm);
    }
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

.image-card {
    position: relative;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    background: var(--c-bg-level-2);
    padding: 0;
    border-radius: var(--border-radius-md);
    border: 2px solid var(--c-bg-level-1);

    a {
        position: relative;
        display: flex;

        img {
            width: 100%;
            height: auto;
            object-fit: cover;
            border-radius: var(--border-radius-md);
            background: var(--c-bg);
            transition: filter 0.1s ease-out;
        }
        svg {
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            opacity: 0;
            transition: opacity 0.1s ease-out;
        }

        &:hover {
            img { filter: opacity(0.5); }
            svg { opacity: 1; }
        }
    }


    .details-section {
        display: flex;
        align-items: center;
        padding: var(--spacing-sm);

        .star-wrapper {
            display: flex;
            align-items: center;
            margin-right: var(--spacing-xs-sm);
        }

        .details {
            font-size: var(--fs-neg-2);
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

            font-size: var(--fs-neg-3);
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
            var(--c-neutral) 90deg 180deg,
            transparent 180deg 270deg,
            var(--c-neutral) 270deg 360deg
        ) top left / 32px 32px;
}

.bottom-text {
    text-align: center;
    font-size: var(--fs-neg-2);
}


@media(max-width: 768px) {
    .images-wrapper {
        grid-template-columns: 1fr;
    }
    .posters .images-wrapper {
        grid-template-columns: 1fr 1fr;
    }
}
</style>