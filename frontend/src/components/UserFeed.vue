<style src="../style.css"></style>

<script src="../controllers/userFeed.js"></script>

<template>
  <div class="user-feed">
    <div class="feed-info">
      <img class="feed-image" :src="feedImage" />
      <div class="feed-title">{{ feedTitle }}</div>
      <div class="feed-artist">{{ feedArtist }}</div>
    </div>

    <Track
      v-for="(item, index) in feedTracks"
      :key="index"
      :track="item"
      @add-to-playlist="handleAddToPlaylist"
    />
    <div v-if="playlistPopupOpen" class="playlist-popup" :style="popupStyle">
      <div class="playlist-popup-header">
        <strong>Add to playlist</strong>
        <button class="playlist-popup-close" @click="closePlaylistPopup">
          ✕
        </button>
      </div>

      <div v-if="popupLoading" class="playlist-popup-state">
        Loading playlists...
      </div>

      <div v-else>
        <div v-if="popupError" class="playlist-popup-error">
          {{ popupError }}
        </div>

        <div v-if="playlists.length" class="playlist-popup-list">
          <button
            v-for="playlist in playlists"
            :key="playlist.id"
            class="playlist-popup-item"
            @click="handleAddTrackToPlaylist(playlist.id)"
          >
            {{ playlist.title }}
          </button>
        </div>

        <div class="playlist-popup-create">
          <input
            v-model="newPlaylistTitle"
            type="text"
            placeholder="New playlist name"
            class="playlist-popup-input"
          />

          <textarea
            v-model="newPlaylistDescription"
            placeholder="Description (optional)"
            class="playlist-popup-textarea"
            rows="4"
          ></textarea>

          <button
            class="playlist-popup-create-btn"
            @click="handleCreatePlaylist"
          >
            Create + Add
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.user-feed {
  display: flex;
  flex-direction: column;
  flex: 1;
  min-height: 0;
  position: relative;

  overflow-x: hidden;
  overflow-y: auto;
  align-items: stretch;

  padding-top: 5px;
  gap: 0.5rem;

  /* padding-bottom: var(--player-height, 150px); */
  padding-bottom: calc(
    var(--player-height) + env(safe-area-inset-bottom) + 130px
  );
}

.feed-info {
  display: flex;
  flex-direction: column;
  align-items: center;
  min-width: 0;
  gap: 0.5rem;
  padding: 0.5rem;
  text-align: center;
}

.feed-image {
  width: 100%;
  max-width: 200px;
  aspect-ratio: 1 / 1;
  object-fit: cover;
  border: 2px solid black;
  border-radius: var(--border-radius-sm);
  transition: transform 0.2s ease;
}

.feed-image:hover {
  transform: scale(1.0125);
}

.feed-title {
  max-width: 100%;
  overflow: hidden;
  text-overflow: ellipsis;
  font-size: 2rem;
  font-weight: 700;
  white-space: nowrap;
}

.feed-artist {
  max-width: 100%;
  overflow: hidden;
  text-overflow: ellipsis;
  font-size: 1.25rem;
  opacity: 0.85;
  white-space: nowrap;
}
.playlist-popup {
  position: fixed;
  z-index: 1000;
  min-width: 220px;
  max-width: 260px;
  background: white;
  border: 1px solid #d9d9d9;
  border-radius: 12px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.16);
  padding: 0.75rem;
}

.playlist-popup-header {
  color: #000;
  font-weight: 700;
  font-size: 1.1rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin: 0;
}

.playlist-popup-close {
  border: none;
  background: white;
  cursor: pointer;
  font-size: 1.8rem;
  line-height: 1;
  padding: 0.35rem 0.7rem;
  border-radius: 12px;
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.12);
  color: #222;
  margin: 0;
}

.playlist-popup-state {
  font-size: 0.9rem;
  color: #555;
}

.playlist-popup-error {
  color: #b00020;
  font-size: 0.85rem;
  margin-bottom: 0.5rem;
}

.playlist-popup-list {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
  margin-bottom: 0.75rem;
}

.playlist-popup-item {
  border: none;
  background: #f3f4f6;
  padding: 0.5rem 0.65rem;
  border-radius: 8px;
  cursor: pointer;
  text-align: left;
}

.playlist-popup-item:hover {
  background: #e5e7eb;
}

.playlist-popup-create {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.playlist-popup-input {
  border: 1px solid #d1d5db;
  border-radius: 8px;
  padding: 0.5rem 0.65rem;
}

.playlist-popup-create-btn {
  border: none;
  background: #1f6feb;
  color: white;
  border-radius: 8px;
  padding: 0.55rem 0.7rem;
  cursor: pointer;
}

.playlist-popup-create-btn:hover {
  opacity: 0.92;
}

.playlist-popup-textarea {
  border: 1px solid #d1d5db;
  border-radius: 8px;
  padding: 0.5rem 0.65rem;
  resize: vertical;
  min-height: 90px;
  font: inherit;
}
</style>
