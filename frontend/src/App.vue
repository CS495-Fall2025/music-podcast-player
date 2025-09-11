<script setup>
// Import components here.
import LocalFeed from "./components/LocalFeed.vue";
import NavigationBar from "./components/NavigationBar.vue";
import MiniPlayer from "./components/MiniPlayer.vue";
import RSSFeedForm from "./components/RSSFeedForm.vue";
import UserFeed from "./components/UserFeed.vue";
</script>

<template>
  <NavigationBar />
  <RSSFeedForm />
  <LocalFeed />
  <MiniPlayer />
  <UserFeed />
</template>

<style scoped></style>
