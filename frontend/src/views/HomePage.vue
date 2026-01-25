<script setup>
import TitleHeroCards from '@/components/TitleHeroCards.vue';
import Carousel from '@/components/Carousel.vue';
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

        <Carousel v-for="list in homeData?.normal_cards" :carouselData="list"/>
    </div>
</template>
