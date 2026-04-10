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
    <AddToPlaylistModal
  v-if="playlistPopupOpen"
  :playlists="playlists"
  :loading="popupLoading"
  :error="popupError"
  :track="selectedTrack"
  @close="closePlaylistPopup"
  @select-playlist="handleAddTrackToPlaylist($event.id)"
  @create-playlist="handleCreatePlaylistFromModal"
/>
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
</style>
