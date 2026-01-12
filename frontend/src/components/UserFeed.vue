<style src="../style.css"></style>

<script src="../controllers/userFeed.js"></script>

<template>
  <div class="user-feed">
  <div class="feed-info">
    <img class="feed-image" :src="feedImage"/>
    <div class="feed-title"> {{ feedTitle }}</div>
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
  padding-bottom: 10px;
  padding-top: 10px;
}

.feed-info{
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 5px;
}

.feed-image{
  margin: 20px 0px 10px 0px;
  height: 200px;
  width: 200px;
  border: 2px solid black;
}

.feed-title{
  font-size: 36px;
  font-weight: bold;
  inline-size: auto;
  max-width: 90%;
  text-align: center;
}
</style>
