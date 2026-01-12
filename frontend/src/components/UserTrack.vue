<style src="../style.css"></style>

<script src="../controllers/userTrack.js"></script>

<template>
  <div class="track" @click="selectTrack">
    <img class="track-image" :src="trackImage"/>
    <div class="track-info">
      <div class="track-title">{{ trackTitle }}</div>
      <div class="track-artist">{{ trackArtist }}</div>
    </div>
    <div class="track-description">{{ trackDescription }}</div>
  </div>
</template>

<style scoped>
.track {
  display: flex;
  flex-direction: row;
  margin: 5px 30px;
  padding: 0;
  background-color: var(--track-background);
  border-radius: var(--border-radius-sm);
  box-shadow: var(--shadow-md);
  cursor: pointer;
  transition:
    transform 0.2s ease,
    background-color 0.2s ease,
    color 0.2s ease;
}

.track:hover {
  background-color: var(--hover-blue);
  color: var(--dark-blue);
  transform: scale(1.025);
}

.track-info {
  display: flex;
  flex-direction: column;
  align-items: left;
  align-self: center;
  max-width: 200px;
  margin: 5px;
}

.track-title {
  writing-mode: horizontal-tb;
  min-inline-size: 125px;
  max-inline-size: 300px;
  font-size: 16px;
  font-weight: bold;
  text-align: left; 
  text-overflow: ellipsis;
  overflow: hidden;
  white-space: nowrap;
}

.track:hover .track-title{
  text-overflow: clip;
  overflow: visible;
  white-space: normal;
}

.track-artist{
  writing-mode: horizontal-tb;
  max-inline-size:400px;
  min-inline-size: 200px;
  font-size: 12px;
  text-align: left;
  text-overflow: ellipsis;
  overflow: hidden;
  white-space: nowrap;
}

.track:hover .track-artist{
  text-overflow: clip;
  overflow: visible;
  white-space: normal;
}

.track-image {
  width: 50px;
  height: 50px;
  margin: 5px;
  border-radius: var(--border-radius);
  object-fit: cover;
  align-self: center;
}

.track-description {
  width: 100%;
  margin: 5px;
  font-size: 14px;
  overflow: hidden;

  display: -webkit-box;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 3;
}

.track:hover .track-description{
  text-overflow: clip;
  overflow: visible;
  white-space: normal;
  -webkit-line-clamp: unset;
}
</style>
