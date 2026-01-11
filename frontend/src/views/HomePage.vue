<script setup>
import TitleCard from '@/components/TitleCard.vue';
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

        <div class="carousel-wrapper">
            <div v-for="list in homeData?.normal_cards" class="card">
                <h3>{{ list?.header }}</h3>
                <div class="carousel">
                    <TitleCard 
                        v-for="title in list?.titles"
                        :titleInfo="title"
                    />
                    <router-link 
                        v-if="list?.total_page > 1"
                        class="fake-card"
                        :to="'/search'"
                    >
                        Show more
                    </router-link>
                </div>
            </div>
        </div>
    </div>
</template>

<style scoped>
.carousel-wrapper {
    display: flex;
    flex-direction: column;
    gap: var(--spacing-md);
}

.carousel-wrapper h3 {
    margin-top: 0;
}

.carousel {
    display: flex;
    gap: var(--spacing-md);
    overflow-x: scroll;
}
</style>