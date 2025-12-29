<script setup></script>

<template>
  <div>
    <header>
      <h2>Watchlist</h2>
      <nav>
        <router-link to="/">Home</router-link>
        <router-link to="/user">Account</router-link>
      </nav>
    </header>
    <main>
      <router-view/>
    </main>
    <footer>

    </footer>
  </div>
</template>

<style scoped></style>
