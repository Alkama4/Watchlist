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
      <div class="stat-card card">
        <HardDrive class="stat-icon" />
        <div class="stat-meta">
          <label>Total Storage</label>
          <strong v-if="summary">{{ `${summary.total_storage_gb.toFixed(1)} GB` }}</strong>
          <span v-else class="summary-skeleton loading-wave"></span>
        </div>
      </div>

      <div class="stat-card card">
        <CheckCircle class="stat-icon success" />
        <div class="stat-meta">
          <label>Linking Status</label>
          <strong v-if="summary">{{ `${summary.linked_percentage.toFixed(1)}%` }}</strong>
          <span v-else class="summary-skeleton loading-wave"></span>
          <small v-if="summary">{{ summary.total_linked_assets }} / {{ summary.total_video_assets }} files</small>
        </div>
      </div>

      <div class="stat-card card">
        <AlertTriangle class="stat-icon warning" />
        <div class="stat-meta">
          <label>Unlinked Folders</label>
          <strong v-if="summary">{{ summary.unlinked_folders_count }}</strong>
          <span v-else class="summary-skeleton loading-wave"></span>
        </div>
      </div>

      <div class="stat-card card">
        <Bookmark class="stat-icon info" />
        <div class="stat-meta">
          <label>Watchlist Deficit</label>
          <strong v-if="summary">{{ summary.watchlist_deficit_count }}</strong>
          <span v-else class="summary-skeleton loading-wave"></span>
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
}
.summary-header {
  padding-top: var(--spacing-lg);
}
.header-top {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: var(--spacing-md-lg);
}
.header-top h1 {
  margin: 0;
}
.subtitle {
  max-width: 600px;
  margin: var(--spacing-sm) 0 0;
}
.stat-meta { min-width: 0; }
.stat-meta label {
  display: block;
}
.stat-meta strong {
  display: block;
  margin-top: 3px;
}
.summary-skeleton {
  display: block;
  width: 86px;
  height: 25px;
  margin-top: 5px;
  border-radius: var(--border-radius-sm);
}
@media (max-width: 620px) {
  .header-top { flex-direction: column; }
  .header-top .btn { width: 100%; }
}
</style>