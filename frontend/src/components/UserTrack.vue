<style src="../style.css"></style>

<script src="../controllers/userTrack.js"></script>

<template>
  <div class="track" @click="selectTrack">
    <img class="track-image" :src="trackImage"/>
    <div class="track-info">
      <div class="track-title">{{ trackTitle }}</div>
      <div class="track-artist">{{ trackArtist }}</div>
    </div>
    <!-- <div class="track-description">{{ trackDescription }}</div> -->
    <div class="track-description">Track description that describes the track by describing information in a descriptive way. This text will often contain a description of the track, but can also contain the transcript. The description may also contain html tags that will be parsed by our app in the future to prevent xss and to allow things like links to be used.</div>
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
    background-color 0.2s ease
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

.track:hover .track-title{
  text-overflow: clip;
  white-space: normal;
}

.track-artist{
  font-size: 0.8rem;
  opacity: 0.75;
  text-overflow: ellipsis;
  overflow: hidden;
  white-space: nowrap;
}

.track:hover .track-artist{
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

.track:hover .track-description{
  line-clamp: 3;
  -webkit-line-clamp: unset;
}
</style>
