<script setup>
import { useRoute } from 'vue-router';
import SearchBar from './components/SearchBar.vue';
import { AlbumCovers, Compass, Home, Search, User } from '@boxicons/vue';

const route = useRoute();
</script>

<template>
    <header v-if="route.meta.requiresAuth">
        <nav>
            <router-link to="/" class="no-deco">
                <h2 class="name">Watchlist</h2>
            </router-link>
            <SearchBar 
                placeholder="Search for titles" 
            />
            <div class="flex-row align-center">
                <ul>
                    <li>
                        <router-link 
                            class="btn btn-text no-deco" 
                            to="/collections"
                        >
                            <AlbumCovers pack="filled" size="sm"/>
                            Collections
                        </router-link>
                    </li>
                    <li>
                        <router-link 
                            class="btn btn-text no-deco" 
                            to="/discover"
                        >
                            <Compass pack="filled" size="sm"/>
                            Discover
                        </router-link>
                    </li>
                </ul>
                <router-link 
                    class="btn btn-user btn-even-padding no-deco"
                    to="/account"
                >
                    <User pack="filled" size="sm"/>
                </router-link>
            </div>
        </nav>
    </header>

    <nav class="mobile-nav" :class="{'nav-visible': route.meta.requiresAuth && !route.meta.disableHeaderPadding}">
        <router-link class="btn btn-text no-deco" to="/">
            <Home pack="filled"/>
            <span>Home</span>
        </router-link>
        <router-link class="btn btn-text no-deco" to="/collections">
            <AlbumCovers pack="filled"/>
            <span>Collections</span>
        </router-link>
        <router-link class="btn btn-text no-deco" to="/search">
            <Search pack="basic"/>
            <span>Search</span>
        </router-link>
        <router-link class="btn btn-text no-deco" to="/discover">
            <Compass pack="filled"/>
            <span>Discover</span>
        </router-link>
        <router-link class="btn btn-text no-deco" to="/account">
            <User pack="filled"/>
            <span>Account</span>
        </router-link>
    </nav>

    <main :class="{'nav-visible': route.meta.requiresAuth && !route.meta.disableHeaderPadding}">
        <router-view/>
    </main>

    <footer :class="{'nav-visible': route.meta.requiresAuth && !route.meta.disableHeaderPadding}">
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
    background: var(--c-bg-opaque-base);
    z-index: var(--z-nav);

    nav {
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
}

nav.mobile-nav {
    display: none;
}

.name {
    margin: 0;
    color: var(--c-text);
}

.search-bar {
    margin-left: var(--spacing-lg);
    margin-right: var(--spacing-md);
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

.btn.btn-user {
    margin-left: var(--spacing-sm);
    border-radius: 100px;
    aspect-ratio: 1;
    padding: var(--spacing-sm);
}

main.nav-visible {
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
    color: var(--c-text-subtle);
}


@media(max-width: 768px) {
    header {
        display: none;
    }

    main.nav-visible {
        margin-top: 0;
        margin-bottom: 64px;
    }

    footer {
        display: none;
    }

    nav.mobile-nav.nav-visible {
        position: fixed;
        bottom: 0;
        left: 0;
        right: 0;

        display: flex;
        justify-content: space-between;
        align-items: center;

        padding: var(--spacing-sm) var(--spacing-md);
        border-top: 1px solid var(--c-border);
        backdrop-filter: blur(var(--blur-heavy));
        background: var(--c-bg-opaque-base);

        z-index: var(--z-nav);

        .btn {
            flex: 1;
            padding-inline: 0;
            /* border-radius: 100px; */
            flex-direction: column;

            span {
                font-size: var(--fs-neg-2);
                font-weight: 500;
                opacity: 0.5;
            }
        }
    }
}

</style>
