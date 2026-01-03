<script setup>
import { fastApi } from '@/utils/fastApi';

async function test() {
    const response = await fastApi.titles.search({
        is_released: false
    });
    console.log(response)
}

</script>

<template>
    <div>
        <h1>Home</h1>

        <p>Welcome!</p>
        <p>This will be the discovery page.</p>

        <button @click="test">Test</button>
    </div>
</template>