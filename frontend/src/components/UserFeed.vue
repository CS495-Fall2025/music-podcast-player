<style src="../style.css"></style>

<script src="./userFeed.js"></script>

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
  flex: 1;
  min-height: 0;
  overflow-y: auto;
  overflow-x: hidden;
  margin-bottom: var(--player-height);
  padding-bottom: 10px;
}
</style>
