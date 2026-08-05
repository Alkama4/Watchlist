<script setup>
import { Search, Filter, ArrowDownUp } from '@boxicons/vue';

const props = defineProps({
  preset: { type: String, default: 'all' },
  search: { type: String, default: '' },
  titleType: { type: String, default: null },
  sortBy: { type: String, default: 'folder_name' },
  sortDirection: { type: String, default: 'asc' }
});

const emit = defineEmits([
  'update:preset',
  'update:search',
  'update:titleType',
  'update:sortBy',
  'update:sortDirection'
]);

const presets = [
  { id: 'all', label: 'All Assets' },
  { id: 'needs_action', label: 'Needs Action' },
  { id: 'incomplete_tv', label: 'Incomplete TV' },
  { id: 'multi_version', label: 'Multi-Version' },
  { id: 'watchlist_deficit', label: 'Watchlist Deficit' }
];
</script>

<template>
  <div class="filter-bar">
    <div class="preset-pills">
      <button
        v-for="p in presets"
        :key="p.id"
        class="pill-button"
        :class="{ active: preset === p.id }"
        @click="emit('update:preset', p.id)"
      >
        {{ p.label }}
      </button>
    </div>

    <div class="filter-controls">
      <div class="search-input">
        <Search size="sm" />
        <input
          :value="search"
          type="text"
          placeholder="Search folder or title..."
          @input="emit('update:search', $event.target.value)"
        />
      </div>

      <select :value="titleType" @change="emit('update:titleType', $event.target.value || null)">
        <option :value="null">All Types</option>
        <option value="movie">Movies</option>
        <option value="tv">TV Shows</option>
      </select>

      <button
        class="btn-icon"
        :title="`Sort Direction: ${sortDirection}`"
        @click="emit('update:sortDirection', sortDirection === 'asc' ? 'desc' : 'asc')"
      >
        <ArrowDownUp size="sm" />
      </button>
    </div>
  </div>
</template>