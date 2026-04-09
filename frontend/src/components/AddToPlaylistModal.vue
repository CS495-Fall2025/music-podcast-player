<style src="../style.css"></style>

<script src="../controllers/addToPlaylistModal.js"></script>

<template>
  <div class="modal-overlay" @click.self="close">
    <div class="modal-card" role="dialog" aria-modal="true">
      <div class="modal-header">
        <h2 class="modal-title">Add to playlist</h2>
        <button class="modal-close" type="button" @click="close">✕</button>
      </div>

      <div class="modal-subtitle" v-if="track">
        <div class="subtitle-line">
          <span class="subtitle-label">Track:</span>
          <span class="subtitle-value">{{ track.title }}</span>
        </div>
        <div class="subtitle-line">
          <span class="subtitle-label">Artist:</span>
          <span class="subtitle-value">{{ track.artist }}</span>
        </div>
      </div>

      <div v-if="loading" class="modal-state">Loading playlists...</div>

      <div v-else-if="error" class="modal-state error">
        {{ error }}
      </div>

      <div v-else>
        <div v-if="!playlists || playlists.length === 0" class="modal-state">
          No playlists found.
        </div>

        <div v-else class="playlist-list">
          <button
            v-for="p in playlists"
            :key="p.id"
            class="playlist-item"
            type="button"
            :disabled="submitting"
            @click="selectPlaylist(p)"
          >
            <div class="playlist-title">{{ p.title }}</div>
            <div class="playlist-meta">{{ p.track_count }} tracks</div>
          </button>
        </div>
      </div>

      <div class="modal-footer">
        <button class="secondary-btn" type="button" @click="close">
          Cancel
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.55);
  display: grid;
  place-items: center;
  z-index: 9999;
  padding: 16px;
}

.modal-card {
  width: min(520px, 95vw);
  background: white;
  border-radius: 14px;
  box-shadow: 0 12px 30px rgba(0, 0, 0, 0.25);
  padding: 14px;
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
}

.modal-title {
  margin: 0;
  font-size: 1.2rem;
  font-weight: 700;
}

.modal-close {
  border: none;
  background: transparent;
  font-size: 1.25rem;
  cursor: pointer;
  padding: 6px 10px;
  border-radius: 10px;
}

.modal-close:hover {
  background: rgba(0, 0, 0, 0.06);
}

.modal-subtitle {
  margin-top: 10px;
  padding: 10px;
  border-radius: 12px;
  background: rgba(0, 0, 0, 0.04);
}

.subtitle-line {
  display: flex;
  gap: 8px;
  margin: 2px 0;
}

.subtitle-label {
  font-weight: 600;
  opacity: 0.8;
}

.subtitle-value {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.modal-state {
  margin-top: 12px;
  padding: 10px;
  border-radius: 12px;
  background: rgba(0, 0, 0, 0.04);
}

.modal-state.error {
  background: rgba(255, 0, 0, 0.08);
}

.playlist-list {
  margin-top: 12px;
  display: flex;
  flex-direction: column;
  gap: 8px;
  max-height: 320px;
  overflow: auto;
  padding-right: 2px;
}

.playlist-item {
  width: 100%;
  text-align: left;
  border: 1px solid rgba(0, 0, 0, 0.12);
  border-radius: 12px;
  padding: 10px 12px;
  background: white;
  cursor: pointer;
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: 10px;
}

.playlist-item:hover {
  background: rgba(0, 0, 0, 0.03);
}

.playlist-item:disabled {
  opacity: 0.65;
  cursor: not-allowed;
}

.playlist-title {
  font-weight: 700;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.playlist-meta {
  font-size: 0.85rem;
  opacity: 0.75;
  flex-shrink: 0;
}

.modal-footer {
  margin-top: 12px;
  display: flex;
  justify-content: flex-end;
}

.secondary-btn {
  border: 1px solid rgba(0, 0, 0, 0.18);
  background: white;
  padding: 8px 12px;
  border-radius: 12px;
  cursor: pointer;
}

.secondary-btn:hover {
  background: rgba(0, 0, 0, 0.03);
}
</style>
