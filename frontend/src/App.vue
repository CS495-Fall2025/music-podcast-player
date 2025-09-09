<script setup>
// Import components here.
import LocalFeed from "./components/LocalFeed.vue";
import NavigationBar from "./components/NavigationBar.vue";
import MiniPlayer from "./components/MiniPlayer.vue";
import RSSFeedForm from "./components/RSSFeedForm.vue";
</script>

<template>
  <NavigationBar />
  <RSSFeedForm />
  <LocalFeed />
  <MiniPlayer />
</template>

<style scoped></style>
