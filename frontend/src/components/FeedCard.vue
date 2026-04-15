<style src="../style.css"></style>

<script src="../controllers/feedCard.js"></script>

<template>
  <div class="feed" @click="selectTrack">
    <img class="feed-image" :src="feed.art_url" :alt="feed.title" />
    <div class="feed-title">{{ feed.title }}</div>
  </div>
</template>

<style scoped>
.feed {
  cursor: pointer;
  text-align: center;
  background-color: var(--track-background);
  margin: 5px;
  box-shadow: var(--shadow-md);
  border-radius: var(--border-radius-sm);
  transition:
    transform 0.2s ease,
    background-color 0.2s ease,
    color 0.2s ease;
}

.feed:hover {
  background-color: var(--hover-blue);
  color: var(--dark-blue);
  transform: scale(1.05);
  z-index: var(--track-hover-z);
}

.feed-image {
  width: 100px;
  height: 100px;
  object-fit: cover;
  border-radius: var(--border-radius);
  margin-top: 10px;
}

.feed-title {
  font-size: 16px;
  font-weight: bold;
  margin: 1px;
  inline-size: 125px;
  overflow-wrap: break-word;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
</style>
