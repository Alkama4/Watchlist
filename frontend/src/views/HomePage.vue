<script setup>
import TitleHeroCards from '@/components/TitleHeroCards.vue';
import TitleCarousel from '@/components/carousel/TitleCarousel.vue';
import { fastApi } from '@/utils/fastApi';
import { onMounted, ref } from 'vue';
const homeData = ref({})

async function fetchHome() {
    homeData.value = await fastApi.home();
    console.log(homeData.value);
}

onMounted(async () => {
    await fetchHome();
})

</script>

<template>
    <div class="home-page">
        <TitleHeroCards
            :heroCards="homeData?.hero_cards"
        />

        <TitleCarousel v-for="list in homeData?.normal_cards" :carouselData="list"/>
    </div>
</template>
