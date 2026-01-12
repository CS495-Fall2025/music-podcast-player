<style src="../style.css"></style>

<script src="../controllers/userFeed.js"></script>

<template>
  <div class="user-feed">
  <div class="feed-info">
    <img class="feed-image" :src="feedImage"/>
    <div class="feed-title"> {{ feedTitle }}</div>
    <div class="feed-artist"> {{ feedArtist }}</div>
  </div>

      <Track v-for="(item, index) in feed" :key="index" :track="item" />
  </div>
</template>

<style scoped>
.user-feed {
  display: flex;
  flex-direction: column;
  gap: 2px;
  align-items: stretch;
  flex: 1;
  height: calc(86vh - var(--player-height));
  overflow-y: auto;
  overflow-x: hidden;
  padding-bottom: 5px;
  padding-top: 5px;
}

.feed-info{
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem;
  text-align: center;
}

.feed-image{
  width: 100%;
  max-width: 200px;
  aspect-ratio: 1 / 1;
  object-fit: cover;
  border: 2px solid black;
  border-radius: var(--border-radius-sm);
}

.feed-title{
  font-size: 2rem;
  font-weight: 700;
  max-width: 90%;
}

.feed-artist{
  font-size: 1.25rem;
  opacity: 0.85;
  max-width: 100%;
}
</style>
