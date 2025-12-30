<script setup></script>

<template>
    <div class="side-by-side">
        <aside>
            <header>
                <h2 class="name">Watchlist</h2>
            </header>
            <nav>
                <ul>
                    <li><router-link to="/">Home</router-link></li>
                    <li><router-link to="/account">Account</router-link></li>
                    <li><router-link to="/login">Login</router-link></li>
                </ul>
                <img src="" alt="Profile icon">
            </nav>
        </aside>

        <main>
            <header>
                <form role="search">
                    <input type="search" placeholder="Search for titles">
                </form>
            </header>

            <div class="content">
                <router-view/>
            </div>

            <footer>
                © Aleksi Malkki 2026
            </footer>
        </main>
    </div>
</template>

<style scoped>
.side-by-side {
    display: flex;
    flex-direction: row;
    width: 100vw;
}

aside {
    box-sizing: border-box;
    height: 100vh;
    width: 250px;
    padding: var(--spacing-sm) var(--spacing-md);

    background-color: var(--c-bg-section);
}

main {
    overflow-y: scroll;
    min-height: 100vh;
    width: 100%;
    display: flex;
    flex-direction: column;
}

header {
    padding: var(--spacing-md);
}

input[type="search"] {
    margin: 0;
}

.content {
    padding-inline: var(--spacing-md);
}

footer {
    margin-top: auto;
    margin-bottom: 0;
    justify-content: center;
    display: flex;
    padding: var(--spacing-sm) 0;
    color: var(--c-text-3);
}
</style>
