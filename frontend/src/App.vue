<script setup>
import { useRoute } from 'vue-router';
import router from './router';
import { useSearchStore } from './stores/search';

const route = useRoute();
const searchStore = useSearchStore();

function onSearchFocus() {
    if (router.currentRoute.value.name !== 'search') {
        router.push({ name: 'Search' });
    }
}

function onSearchSubmit() {
    searchStore.submit();
}

</script>

<template>
    <header v-if="route.meta.requiresAuth">
        <nav>
            <router-link to="/" class="no-deco">
                <h2 class="name">Watchlist</h2>
            </router-link>
            <form role="search" @submit.prevent="onSearchSubmit">
                <input 
                    type="search" 
                    placeholder="Search for titles"
                    @focus="onSearchFocus"
                    v-model="searchStore.query"
                >
            </form>
            <div class="flex-row align-center">
                <ul>
                    <li>
                        <router-link 
                            class="btn btn-text no-deco" 
                            to="/"
                        >
                            <i class="bx bxs-compass"></i>
                            Discover
                        </router-link>
                    </li>
                    <li>
                        <router-link 
                            class="btn btn-text no-deco" 
                            to="/collections"
                        >
                            <i class="bx bxs-collection"></i>
                            Collections
                        </router-link>
                    </li>
                </ul>
                <router-link 
                    class="btn no-deco btn-user"
                    to="/account"
                >
                    <i class="bx bxs-user"></i>
                </router-link>
            </div>
        </nav>
    </header>

    <main :class="{'header-visible': route.meta.requiresAuth && !route.meta.disableHeaderPadding}">
        <router-view/>
    </main>

    <footer>
        <router-link to="/debug" class="no-deco">© Aleksi Malkki 2026. All Rights Reserved.</router-link>
    </footer>
</template>

<style scoped>
header {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    padding: var(--spacing-sm-md) var(--spacing-md);
    border-bottom: 1px solid var(--c-border);
    backdrop-filter: blur(var(--blur-heavy));
    background-color: var(--c-bg-opaque);
    z-index: var(--z-nav);
}

nav {
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.name {
    margin: 0;
    color: var(--c-text);
}

input[type="search"] {
    margin: 0;
}


ul {
    list-style-type: none;
    display: flex;
    padding: 0;
    margin: 0;
    /* gap: var(--spacing-sm); */
}

header .btn {
    padding: var(--spacing-sm) var(--spacing-sm-md);
    font-size: var(--fs-0);
    display: flex;
    align-items: center;
}

.btn-user {
    border-radius: 100px;
    padding: 10px !important;
    font-size: var(--fs-1) !important;
}

main.header-visible {
    margin-top: 64px;
}

footer {
    margin-top: auto;
    margin-bottom: 0;
    justify-content: center;
    display: flex;
    padding: var(--spacing-sm) 0;
}

footer a {
    color: var(--c-text-fine-print);
}
</style>
