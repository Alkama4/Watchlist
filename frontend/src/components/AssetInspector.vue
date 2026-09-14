<script setup>
import { File, AlertTriangle, CheckCircle, XCircle } from '@boxicons/vue';

defineProps({
  details: { type: Object, required: true }
});
</script>

<template>
  <div class="asset-inspector">
    <!-- Movie Variants Layout -->
    <div v-if="['movie', 'unlinked'].includes(details.title_type)" class="movie-inspector">
      <div class="inspector-heading">
        <div>
          <span class="eyebrow">{{ details.title_type === 'unlinked' ? 'Unlinked directory' : 'Movie' }}</span>
          <h4>{{ details.title_type === 'unlinked' ? 'Files found in this directory' : 'Movie versions' }}</h4>
        </div>
        <span class="badge">{{ details.movie_variants?.length || 0 }} files</span>
      </div>
      <div class="variants-grid">
        <div
          v-for="variant in details.movie_variants"
          :key="variant.video_asset_id"
          class="variant-card card"
          :class="{ default: variant.is_default }"
        >
          <div class="variant-header">
            <span class="badge">{{ variant.variant_type }}</span>
            <span class="file-size">{{ variant.file_size_gb.toFixed(2) }} GB</span>
          </div>
          <div class="file-name" :title="variant.file_path">{{ variant.file_name }}</div>
          <div class="spec-pills">
            <span><File size="sm" /> {{ variant.specs.resolution }}</span>
            <span v-if="variant.specs.hdr_type" class="badge-hdr">{{ variant.specs.hdr_type }}</span>
            <span>{{ variant.specs.video_codec }}</span>
            <span v-if="variant.specs.audio_tracks?.length">{{ variant.specs.audio_tracks.join(', ') }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- TV Show Seasons & Episode Matrix -->
    <div v-else-if="details.title_type === 'tv'" class="tv-inspector">
      <div class="inspector-heading">
        <div>
          <span class="eyebrow">Episode coverage</span>
          <h4>Show seasons</h4>
        </div>
        <span class="count-chip">{{ details.seasons?.length || 0 }} seasons</span>
      </div>
      <div v-for="season in details.seasons" :key="season.season_number" class="season-block">
        <h4>Season {{ season.season_number }}</h4>
        <div class="episode-matrix">
          <div
            v-for="ep in season.episodes"
            :key="ep.episode_number"
            class="ep-node card"
            :class="{ missing: ep.is_missing, duplicate: ep.assets.length > 1 }"
          >
            <div class="ep-head">
              <strong>E{{ String(ep.episode_number).padStart(2, '0') }}</strong>
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
  padding: var(--spacing-md-lg);
}
.inspector-heading {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: var(--spacing-md);
  margin-bottom: var(--spacing-md);
}
.eyebrow {
  display: block;
  white-space: nowrap;
}
.variants-grid, .episode-matrix {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(130px, 1fr));
  gap: 0.75rem;
}
.ep-node {
}
.ep-node.missing {
  opacity: 0.7;
}
.season-block + .season-block {
  margin-top: var(--spacing-md-lg);
}
.season-block h4 {
  margin-bottom: var(--spacing-sm-md);
  font-size: var(--fs-0);
}
.ep-head, .variant-header, .spec-pills, .ep-details {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
}
.ep-head, .variant-header {
  justify-content: space-between;
}
.ep-details {
  margin-top: var(--spacing-sm);
}
.variant-card {
  min-width: 0;
}
.file-name {
  overflow: hidden;
  margin: var(--spacing-sm-md) 0;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.spec-pills {
  flex-wrap: wrap;
}
.spec-pills span {
  display: inline-flex;
  align-items: center;
  gap: 3px;
}
.ep-views {
  margin-top: var(--spacing-sm);
}
.unmatched-banner {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  margin-top: var(--spacing-md);
}
@media (max-width: 640px) {
  .asset-inspector { padding: var(--spacing-sm-md); }
  .inspector-heading { align-items: flex-start; }
  .variants-grid, .episode-matrix { grid-template-columns: repeat(2, minmax(0, 1fr)); }
}
</style>