<script src="./UserFeed.js"></script>

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
}
</style>
