<style src="../style.css"></style>

<script src="../controllers/userTrack.js"></script>

<template>
  <div class="track" @click="selectTrack">
    <img class="track-image" :src="trackImage" />
    <div class="track-info">
      <div class="track-title">{{ trackTitle }}</div>
      <div class="track-artist">{{ trackArtist }}</div>
    </div>
    <div class="track-description" v-html="trackDescription"></div>

    <button
      class="add-playlist-btn"
      @click.stop="addToPlaylist"
      aria-label="Add to playlist"
      title="Add to playlist"
      type="button"
    >
      <img
        class="add-to-playlist-icon"
        src="../assets/images/plus-icon.svg"
        alt=""
        aria-hidden="true"
      />
    </button>
  </div>
</template>

<style scoped>
.track {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin: 0.5rem 1.5rem;
  padding: 0.5rem 0.75rem;
  background-color: var(--track-background);
  border-radius: var(--border-radius-sm);
  box-shadow: var(--shadow-md);
  cursor: pointer;
  transition:
    transform 0.2s ease,
    background-color 0.2s ease;
}

.track:hover {
  background-color: var(--hover-blue);
  color: var(--dark-blue);
  transform: scale(1.025);
}

.track-info {
  display: flex;
  flex-direction: column;
  min-width: 0;
  width: auto;
  max-width: 50%;
  /* flex: 0 0 auto; */
  /* overflow: hidden; */
}

.track-title {
  font-size: 1rem;
  font-weight: 600;
  text-overflow: ellipsis;
  overflow: hidden;
  white-space: nowrap;
}

.track:hover .track-title {
  text-overflow: clip;
  white-space: normal;
}

.track-artist {
  font-size: 0.8rem;
  opacity: 0.75;
  text-overflow: ellipsis;
  overflow: hidden;
  white-space: nowrap;
}

.track:hover .track-artist {
  text-overflow: clip;
  white-space: normal;
}

.track-image {
  width: 64px;
  height: 64px;
  flex-shrink: 0;
  border-radius: var(--border-radius-sm);
  object-fit: cover;
}

.track-description {
  flex: 1;
  min-width: 0;
  font-size: 0.85rem;
  color: #666;
  display: -webkit-box;
  -webkit-box-orient: vertical;
  line-clamp: 3;
  -webkit-line-clamp: 3;
  overflow: hidden;
}

.track:hover .track-description {
  line-clamp: 3;
  -webkit-line-clamp: unset;
}

.add-to-playlist-btn {
  flex-shrink: 0;
  width: 28px;
  height: 28px;
  border: none;
  border-radius: 50%;
  background: white;
  color: white;
  cursor: pointer;
  display: grid;
  place-items: center;
  padding: 0;
  transition:
    transform 0.15s ease,
    opacity 0.15s ease;
}

.add-to-playlist-btn:hover {
  transform: scale(1.08);
  opacity: 0.9;
}

.add-to-playlist-icon {
  width: 16px;
  height: 16px;
  display: block;
  object-fit: contain;
}
</style>
