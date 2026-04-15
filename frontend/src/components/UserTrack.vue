<style src="../style.css"></style>

<script src="../controllers/userTrack.js"></script>

<template>
  <div class="track" :class="{ active: isActive }" @click="selectTrack">
    <img class="track-image" :src="trackImage" />
    <div class="track-info">
      <div class="track-title">{{ trackTitle }}</div>
      <div class="track-artist">{{ trackArtist }}</div>
      <div class="track-number">{{ trackNumber }}</div>
    </div>
    <div class="track-description" v-html="trackDescription"></div>
  </div>
</template>

<style scoped>
/* --- Base Container --- */
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

/* --- Hover & Active States --- */
@media (hover: hover) and (pointer: fine) {
  .track:hover {
    background-color: var(--hover-blue);
    color: var(--dark-blue);
    transform: scale(1.015);
  }
}

.track.active {
  background-color: var(--active-blue);
  color: var(--dark-blue);
  transform: scale(1.015);
  border-left: 4px solid var(--dark-blue);
}

/* --- Track Image & Layout --- */
.track-image {
  width: 64px;
  height: 64px;
  flex-shrink: 0;
  border-radius: var(--border-radius-sm);
  object-fit: cover;
}

.track-info {
  display: flex;
  flex-direction: column;
  min-width: 0;
  width: auto;
  max-width: 50%;
}

/* --- Typography: Shared Truncation --- */
.track-title,
.track-artist,
.track-number {
  text-overflow: ellipsis;
  overflow: hidden;
  white-space: nowrap;
}

/* --- Typography: Specifics --- */
.track-title {
  font-size: 1rem;
  font-weight: 600;
}

.track-artist {
  font-size: 0.8rem;
  opacity: 0.75;
}

.track-number {
  font-size: 0.75rem;
  opacity: 0.65;
}

/* --- Typography: Active State Overrides --- */
.track.active .track-title,
.track.active .track-artist {
  text-overflow: clip;
  white-space: normal;
}

/* --- Description --- */
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

.track.active .track-description {
  line-clamp: 3;
  -webkit-line-clamp: unset;
}
</style>
