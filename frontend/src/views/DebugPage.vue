<script setup>
import { ref } from 'vue'
import ModalBase from '@/components/modal/ModalBase.vue';

const modal = ref(null)


function openModal() {
    modal.value.open();
}

function playVideo() {
    window.chrome.webview.postMessage({ action: "playVideo", url: "http://localhost:8000/media/video" });
}

</script>

<template>
    <div>
        <h2>Video test</h2>

        <div class="buttons">
            <button @click="playVideo">Test video</button>
        </div>

        <h2>Buttons</h2>

        <h3>Basic buttons</h3>
        <div class="buttons">
            <button>Default button</button>
            <button class="btn-primary">Primary button</button>
            <button class="btn-text">Text button</button>
        </div>

        <h3>Color buttons</h3>
        <div class="buttons">
            <button class="btn-negative">Negative button</button>
            <button class="btn-warning">Warning button</button>
            <button class="btn-positive">Positive button</button>
        </div>

        <h2>Modals</h2>
            <button @click="openModal">Open modal</button>
            <ModalBase header="Modal header" ref="modal">
                <p>Some text</p>
                <button>A button</button>
            </ModalBase>

        <h2>Form</h2>
        <form @submit.prevent="" class="card">
            <h2>Form header</h2>

            <label for="1">Text field</label>
            <input id="1" type="text">

            <label for="2">Password input</label>
            <input id="2" type="password">

            <label for="3">Number selector</label>
            <input id="3" type="number">

            <button type="submit">Submit</button>
        </form>

        <h2>Listing</h2>
        <dl>
            <dt>Progress</dt>
            <dd>18 / 19 episodes (94.7%)</dd>

            <dt>Season count</dt>
            <dd>4 seasons</dd>

            <dt>Episode count</dt>
            <dd>19 episodes</dd>

            <dt>First air date</dt>
            <dd>21. elokuuta 2022</dd>

            <dt>Last air date</dt>
            <dd>1. tammikuuta 1970</dd>

            <dt>Original language</dt>
            <dd>en</dd>
        </dl>

        <h2>Normal text elements</h2>
        <p>
            Lorem ipsum dolor sit amet, consectetur adipiscing elit. Cras ultricies efficitur nisl, id egestas risus. Etiam quis leo finibus, sollicitudin ante non, vulputate magna. Curabitur non ante nisi. Aenean pellentesque at quam eget aliquet. Sed ultrices dictum odio, in tincidunt ipsum commodo in. Duis ultrices massa ac sapien varius ultricies. <a href="">https://google.com</a> Cras tempus, leo pharetra iaculis tempus, ipsum risus accumsan quam, quis placerat est augue eu velit. Etiam varius turpis non eros porttitor tempor vel a quam. In consequat lectus in diam dapibus, vel viverra mi sodales. Ut nec tincidunt velit. Vestibulum ac posuere nisl.
        </p>
        
    </div>
</template>

<style scoped>
.buttons {
    display: flex;
    flex-direction: row;
    gap: 8px;
}

.labeled-list {
    list-style: none;
    padding: 0;
    margin: 0;
}

.labeled-list li {
    display: grid;
    grid-template-columns: auto 1fr;
    gap: 0.5rem 1rem;
}

.label {
    font-weight: 600;
    white-space: nowrap;
}

</style>