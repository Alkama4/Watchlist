<script setup>
import { HardDrive, AlertTriangle, CheckCircle, XCircle } from '@boxicons/vue';

defineProps({
  details: { type: Object, required: true }
});
</script>

<template>
  <div class="asset-inspector">
    <!-- Movie Variants Layout -->
    <div v-if="details.title_type === 'movie'" class="movie-inspector">
      <h4>Movie Asset Versions ({{ details.movie_variants?.length || 0 }})</h4>
      <div class="variants-grid">
        <div
          v-for="variant in details.movie_variants"
          :key="variant.video_asset_id"
          class="variant-card"
          :class="{ default: variant.is_default }"
        >
          <div class="variant-header">
            <span class="badge">{{ variant.variant_type }}</span>
            <span class="file-size">{{ variant.file_size_gb.toFixed(2) }} GB</span>
          </div>
          <div class="file-name">{{ variant.file_name }}</div>
          <div class="spec-pills">
            <span>{{ variant.specs.resolution }}</span>
            <span v-if="variant.specs.hdr_type" class="badge-hdr">{{ variant.specs.hdr_type }}</span>
            <span>{{ variant.specs.video_codec }}</span>
            <span>{{ variant.specs.audio_tracks.join(', ') }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- TV Show Seasons & Episode Matrix -->
    <div v-else-if="details.title_type === 'tv'" class="tv-inspector">
      <div v-for="season in details.seasons" :key="season.season_number" class="season-block">
        <h4>Season {{ season.season_number }}</h4>
        <div class="episode-matrix">
          <div
            v-for="ep in season.episodes"
            :key="ep.episode_number"
            class="ep-node"
            :class="{ missing: ep.is_missing, duplicate: ep.assets.length > 1 }"
          >
            <div class="ep-head">
              <strong>E{{ ep.episode_number }}</strong>
              <component :is="ep.is_missing ? XCircle : CheckCircle" size="sm" />
            </div>

            <div v-if="!ep.is_missing && ep.assets.length > 0" class="ep-details">
              <span>{{ ep.assets[0].specs.resolution }}</span>
              <small>{{ ep.assets[0].specs.video_codec }}</small>
            </div>

            <div v-if="ep.user_views?.length" class="ep-views" :title="`Watched by: ${ep.user_views.map(v => v.username).join(', ')}`">
              👁 {{ ep.user_views.length }}
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Unmatched files alert footer -->
    <div v-if="details.unmatched_files?.length" class="unmatched-banner">
      <AlertTriangle size="sm" />
      <span>Found {{ details.unmatched_files.length }} unmapped video assets in this directory.</span>
    </div>
  </div>
</template>

<style scoped>
.asset-inspector {
  padding: 1.25rem;
  background: var(--surface-ground);
  border-radius: 6px;
}
.variants-grid, .episode-matrix {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(130px, 1fr));
  gap: 0.75rem;
}
.ep-node {
  padding: 0.5rem;
  border-radius: 4px;
  background: var(--surface-card);
  border: 1px solid var(--border-color);
}
.ep-node.missing {
  border-color: var(--danger-color);
  opacity: 0.7;
}
</style>