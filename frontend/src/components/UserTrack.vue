<script src="./userTrack.js"></script>

<template>
  <div class="track" @click="selectTrack">
    <img :src="track.image" :alt="track.title" class="track-image" />
    <h3 class="track-title">{{ track.title }}</h3>
  </div>
</template>

<style scoped>
.track {
  cursor: pointer;
  text-align: center;
  margin: 10px;
}
.track-image {
  width: 100px;
  height: 100px;
  object-fit: cover;
}
.track-title {
  font-size: 14px;
  margin-top: 5px;
}
</style>
