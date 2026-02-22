<script setup>
import TitleHeroCards from '@/components/TitleHeroCards.vue';
import TitleCarousel from '@/components/TitleCarousel.vue';
import { fastApi } from '@/utils/fastApi';
import { onMounted, ref } from 'vue';
const homeData = ref({})

async function fetchHome() {
    homeData.value = await fastApi.home();
}

onMounted(async () => {
    await fetchHome();
})

</script>

<template>
    <div class="home-page layout-spacing-bottom">
        <TitleHeroCards
            :heroCards="homeData?.hero_cards"
        />

        <TitleCarousel v-for="list in homeData?.normal_cards" :carouselData="list"/>
    </div>
</template>
