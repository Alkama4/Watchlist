<script setup>
import { resolveImagePath } from '@/utils/imagePath';
import { timeFormatters } from '@/utils/formatters';

defineProps({
    heroCards: {
        type: Object,
        required: true
    }
})
</script>

<template>
    <section class="title-hero-cards">
        <img 
            :src="resolveImagePath(
                'original', 
                heroCards?.titles[0]?.default_backdrop_image_path, 
                heroCards?.titles[0]?.user_details?.chosen_backdrop_image_path
            )"
            :alt="`Backdrop for the title ${heroCards?.titles[0]?.name}`"
            class="backdrop"
        >
        
        <div class="details">
            <img 
                :src="resolveImagePath(
                    'original', 
                    heroCards?.titles[0]?.default_logo_image_path, 
                    heroCards?.titles[0]?.user_details?.chosen_logo_image_path
                )"
                :alt="`Backdrop for the title ${heroCards?.titles[0]?.name}`"
                class="logo"
            >
            <h1>{{ heroCards?.titles[0]?.name }}</h1>
            <div>
                {{ heroCards?.titles[0]?.type }}
                &bull;
                {{ timeFormatters.timestampToYear(heroCards?.titles[0]?.release_date) }}
                &bull;
                {{ heroCards?.titles[0]?.tmdb_vote_average }}
                ({{ heroCards?.titles[0]?.tmdb_vote_count }})
            </div>
        </div>
    </section>
</template>

<!-- { "title_id": 2, "tmdb_id": 83533, "type": "movie", "name": "Avatar: Fire and Ash", "release_date": "2025-12-17", "movie_runtime": 198, "show_season_count": 0, "show_episode_count": 0, "tmdb_vote_average": 7.4, "tmdb_vote_count": 1359, "imdb_vote_average": null, "imdb_vote_count": null, "default_poster_image_path": "/cf7hE1ifY4UNbS25tGnaTyyDrI2.jpg", "default_backdrop_image_path": "/vm4H1DivjQoNIm0Vs6i3CTzFxQ0.jpg", "default_logo_image_path": "/qzuSPiHF08bUZXPaXST24ANfoqK.png", "user_details": { "in_library": true, "is_favourite": false, "in_watchlist": false, "watch_count": 0, "chosen_poster_image_path": null, "chosen_backdrop_image_path": null, "chosen_logo_image_path": null } } -->

<style scoped>
.title-hero-cards {
    height: 50vh;
    width: 100vw;
    overflow: hidden;
    position: relative;

    display: flex;
    flex-direction: column;
}

img.backdrop {
    position: absolute;
    inset: 0;
    width: 100%;
    height: 100%;
    object-fit: cover;
    z-index: -10;
    mask-image: linear-gradient(
        to top,
        rgba(0, 0, 0, 0) 0%,
        rgba(0, 0, 0, 1) 60%
    );
}
img.logo {
    height: 150px;
    width: 400px;
    object-fit: contain;
}

.details {
    display: flex;
    flex-direction: column;
}
</style>