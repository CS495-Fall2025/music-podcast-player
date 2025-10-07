<style src="../style.css"></style>

<script src="./userTrack.js"></script>

<template>
  <div class="track" @click="selectTrack">
    <img class="track-image" :src="track.image" :alt="track.title"/>
    <div class="track-title">{{ track.title }}</div>
  </div>
</template>