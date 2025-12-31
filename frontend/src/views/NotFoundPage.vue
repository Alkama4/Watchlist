<template>
    <div class="page-not-found">
        <h1>404</h1>
        <p>The page you were looking for doesn't exist.</p>
        <a href="#" class="btn no-deco" @click.prevent="$router.back()">Go back</a>
    </div>
</template>


<style scoped>
.page-not-found {
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    min-height: 50vh;
}
h1 {
    font-size: 64px;
    margin-bottom: var(--spacing-sm);
}

</style>