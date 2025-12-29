<script setup>
function handleSubmit(event) {
    event.preventDefault(); // optional, because of .prevent
    const form = event.target;
    const username = form[0].value;
    const password = form[1].value;
    alert(`Username: ${username}, Password: ${password}`);
}
</script>

<template>
    <div>
        <h1>Login</h1>

        <form @submit.prevent="handleSubmit">
            <label>Username</label>
            <input type="text" required>

            <label>Password</label>
            <input type="password" required>

            <button type="submit">Login</button>
        </form>
    </div>
</template>
