<script setup>
import { RefreshCwAlt, HardDrive, CheckCircle, AlertTriangle, Bookmark } from '@boxicons/vue';

defineProps({
  summary: { type: Object, default: null },
  syncLoading: { type: Boolean, default: false }
});

defineEmits(['sync']);
</script>

<template>
  <header class="summary-header">
    <div class="header-top">
      <div>
        <h1>Asset Control Center</h1>
        <p class="subtitle">Manage local storage files and TMDB metadata associations</p>
      </div>
      <button class="btn btn-primary" :disabled="syncLoading" @click="$emit('sync')">
        <RefreshCwAlt :class="{ spin: syncLoading }" size="sm" />
        <span>{{ syncLoading ? 'Scanning Directory...' : 'Scan & Sync' }}</span>
      </button>
    </div>

    <div class="stats-grid">
      <div class="stat-card">
        <HardDrive class="stat-icon" />
        <div class="stat-meta">
          <label>Total Storage</label>
          <strong>{{ summary ? `${summary.total_storage_gb.toFixed(1)} GB` : '-' }}</strong>
        </div>
      </div>

      <div class="stat-card">
        <CheckCircle class="stat-icon success" />
        <div class="stat-meta">
          <label>Linking Status</label>
          <strong>{{ summary ? `${summary.linked_percentage.toFixed(1)}%` : '-' }}</strong>
          <small v-if="summary">{{ summary.total_linked_assets }} / {{ summary.total_video_assets }} files</small>
        </div>
      </div>

      <div class="stat-card">
        <AlertTriangle class="stat-icon warning" />
        <div class="stat-meta">
          <label>Unlinked Folders</label>
          <strong>{{ summary?.unlinked_folders_count ?? '-' }}</strong>
        </div>
      </div>

      <div class="stat-card">
        <Bookmark class="stat-icon info" />
        <div class="stat-meta">
          <label>Watchlist Deficit</label>
          <strong>{{ summary?.watchlist_deficit_count ?? '-' }}</strong>
          <small>Missing wanted titles</small>
        </div>
      </div>
    </div>
  </header>
</template>

<style scoped>
.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
  margin-top: 1.5rem;
}
.stat-card {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem;
  border-radius: 8px;
  background: var(--surface-card);
}
</style>