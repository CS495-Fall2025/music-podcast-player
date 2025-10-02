<script setup>
// Import components here.
import NavigationBar from "./components/NavigationBar.vue";
import MiniPlayer from "./components/MiniPlayer.vue";
import RSSFeedForm from "./components/RSSFeedForm.vue";
import UserFeed from "./components/UserFeed.vue";
import NavBar from "./components/NavBar.vue";
</script>

<template>
  <NavBar />
  <!-- <NavigationBar /> -->
  <RSSFeedForm />
  <MiniPlayer />
  <UserFeed />
</template>

<style scoped></style>
