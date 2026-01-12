<script setup>
import { resolveImagePath } from '@/utils/imagePath';


    
defineProps({
    heroCards: {
        type: Object,
        required: true
    }
})
</script>

<template>
    <div class="title-hero-cards">
        <img 
            :src="resolveImagePath(
                'original', 
                heroCards?.titles[0]?.default_backdrop_image_path, 
                heroCards?.titles[0]?.user_details?.chosen_backdrop_image_path
            )"
            :alt="`Backdrop for the title ${heroCards?.titles[0]?.name}`"
        >
        {{ heroCards?.titles[0] }}
    </div>
</template>

<style scoped>
.title-hero-cards {
    margin: calc(-1 * var(--spacing-md));
    margin-bottom: var(--spacing-md);
}

img {
    width: 100vw;
}
</style>