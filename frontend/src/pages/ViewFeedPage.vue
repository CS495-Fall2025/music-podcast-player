<script setup>
import MiniPlayer from "../components/MiniPlayer.vue";
import UserFeed from "../components/UserFeed.vue";
</script>

<template>
  <div class="page-layout">
    <UserFeed />
    <MiniPlayer />
  </div>
</template>

<style scoped>
.page-layout {
  position: relative;

  display: flex;
  flex-direction: column;
  flex: 1;
  min-height: 0;
  width: 100%;

  overflow: hidden;
}
</style>
