<style src="../style.css"></style>

<script src="../controllers/userTrack.js"></script>

<template>
  <div class="track" @click="selectTrack">
    <div class="track-info">
      <img class="track-image" :src="track.image" :alt="track.title" />
      <div class="track-title">{{ track.title }}</div>
    </div>
    <div class="track-description">Track description</div>
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
  align-items: center;
  max-width: 200px;
  margin: 10px;
}

.track-image {
  width: 100px;
  height: 100px;
  margin-top: 10px;
  border-radius: var(--border-radius);
  object-fit: cover;
}

.track-title {
  inline-size: 125px;
  margin: 1px;
  font-size: 16px;
  font-weight: bold;
  text-align: center;
  overflow-wrap: break-word;
}

.track-description {
  width: 100%;
  margin: 10px;
  font-size: 16px;
}
</style>
