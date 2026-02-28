<script setup>
import { useSettingsStore } from '@/stores/settings';
import { ref } from 'vue';

const settings = useSettingsStore();

const textField = ref('');
const themes = ref([
    { id: 'void', name: 'Void (Default)', description: 'True black for OLED displays' },
    { id: 'midnight', name: 'Midnight', description: 'Cool blue dark mode' },
    { id: 'amethyst', name: 'Amethyst', description: 'Rich purple darkness' },
    { id: 'flashbang', name: 'Flashbang', description: 'Cover your eyes' },
    { id: '16-bit', name: '16-Bit', description: 'Greyscale retro vibes' },
]);
</script>

<template>
    <div class="theme-picker">
        <div 
            v-for="theme in themes" 
            :key="theme.id" 
            :data-theme="theme.id"
            class="theme-card"
        >
            <h4>{{ theme.name }}</h4>

            <p class="description">{{ theme.description }}</p>
            
            <div class="swatch-bar">
                <div class="swatch primary" title="Primary"></div>
                <div class="swatch positive" title="Positive"></div>
                <div class="swatch favourite" title="Accent"></div>
                <div class="swatch accent" title="Negative"></div>
            </div>
            
            <form @submit.prevent>
                <label for="mock">Input field</label>
                <input type="text" id="mock" v-model="textField" placeholder="Type here">
                <button>Click me</button>
            </form>

            <i
                @click="settings.updateSetting('theme', theme.id)"
                class="choose-button bx btn btn-text btn-even-padding"
                :class="[
                    theme.id === settings.preferences.theme ? 'bx-check-circle' : 'bx-circle',
                    { 'theme-picker-fix': theme.id !== '16-bit' }
                ]"
            ></i>
        </div>
    </div>
</template>

<style scoped>
.theme-picker {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(270px, 1fr));
    gap: var(--spacing-md);
}

.theme-card {
    background-color: var(--c-bg-base);
    border: 1px solid var(--c-border);
    color: var(--c-text-base);
    border-radius: var(--border-radius-lg);
    padding: var(--spacing-md-lg);
    position: relative;
}

h4 {
    margin-top: 0;
}

.choose-button {
    position: absolute;
    top: var(--spacing-md);
    right: var(--spacing-md);
}

.swatch-bar {
    display: flex;
    gap: var(--spacing-sm);
    margin-bottom: var(--spacing-md);
}

.swatch {
    flex: 1;
    height: var(--spacing-md-lg);
    border-radius: var(--border-radius-sm);
    cursor: pointer;
    transition: background-color 0.1s ease-out;
}

.swatch.primary {
    background-color: var(--c-primary);
    &:hover {
        background-color: var(--c-primary-subtle);
    }
    &:active {
        background-color: var(--c-primary-soft);
    }
}
.swatch.positive {
    background-color: var(--c-positive);
    &:hover {
        background-color: var(--c-positive-subtle);
    }
    &:active {
        background-color: var(--c-positive-soft);
    }
}
.swatch.favourite {
    background-color: var(--c-negative);
    &:hover {
        background-color: var(--c-negative-subtle);
    }
    &:active {
        background-color: var(--c-negative-soft);
    }
}
.swatch.accent {
    background-color: var(--c-accent);
    &:hover {
        background-color: var(--c-accent-subtle);
    }
    &:active {
        background-color: var(--c-accent-soft);
    }
}
</style>