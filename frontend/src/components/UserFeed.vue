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
  flex-wrap: wrap;
  gap: 15px;
  justify-content: center;
  max-height: 400px;
  overflow-y: auto;
  overflow-x: hidden;
  padding-bottom: 10px;
}
</style>
