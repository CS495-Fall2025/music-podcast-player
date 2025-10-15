<style src="../style.css"></style>

<script src="./feedCard.js"></script>

<template>
  <div class="track" @click="selectTrack">
    <img class="track-image" :src="feed.art_url" :alt="feed.title" />
    <div class="track-title">{{ feed.title }}</div>
  </div>
</template>
