<script setup>
import { Search, ArrowDownUp } from '@boxicons/vue';

const props = defineProps({
  preset: { type: String, default: 'all' },
  search: { type: String, default: '' },
  titleType: { type: String, default: null },
  sortBy: { type: String, default: 'size' },
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
        class="btn btn-pill"
        :class="{ 'btn-primary': preset === p.id }"
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

      <label>
        Title type
        <select :value="titleType" @change="emit('update:titleType', $event.target.value || null)">
          <option value="">Any</option>
          <option value="movie">Movies</option>
          <option value="tv">TV Shows</option>
          <option value="unknown">Unknown</option>
        </select>
      </label>

      <label>
        Sort by
        <select :value="sortBy" @change="emit('update:sortBy', $event.target.value)">
          <option value="folder_name">Folder name</option>
          <option value="size">Storage size</option>
          <option value="completion">Completion</option>
        </select>
      </label>

      <button
        class="btn btn-even-padding"
        :title="`Sort Direction: ${sortDirection}`"
        @click="emit('update:sortDirection', sortDirection === 'asc' ? 'desc' : 'asc')"
      >
        <ArrowDownUp size="sm" />
      </button>
    </div>
  </div>
</template>

<style scoped>
.filter-bar {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-md);
  margin: var(--spacing-lg) 0 var(--spacing-md);
}

.preset-pills {
  display: flex;
  overflow-x: auto;
  gap: var(--spacing-sm);
  padding-bottom: 2px;
}

.filter-controls {
  display: grid;
  grid-template-columns: minmax(220px, 1fr) auto auto auto;
  align-items: end;
  gap: var(--spacing-sm-md);
}
.filter-controls label {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-xs);
}
.search-input {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
}
.search-input input {
  flex: 1;
  min-width: 0;
}
@media (max-width: 760px) {
  .filter-controls { grid-template-columns: 1fr 1fr; }
  .search-input { grid-column: 1 / -1; }
}
@media (max-width: 440px) {
  .filter-controls { grid-template-columns: 1fr; }
  .search-input { grid-column: auto; }
}
</style>