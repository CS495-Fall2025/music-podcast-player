<style src="../style.css"></style>

<script src="../controllers/userFeed.js"></script>

<template>
  <div class="user-feed">
    <Track v-for="(item, index) in feed" :key="index" :track="item" />
  </div>
</template>

<style scoped>
.user-feed {
  display: flex;
  flex-direction: column;
  gap: 2px;
  align-items: stretch;
  height: calc(85vh - var(--player-height));
  overflow-y: auto;
  overflow-x: hidden;
  padding-bottom: 10px;
}
</style>
