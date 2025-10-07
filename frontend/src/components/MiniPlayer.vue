<style src="../style.css"> </style>

<script setup>
import { ref, computed, watch } from "vue";

import { currentTrack, feed } from "./localFeedStore.js";

const isPlaying = ref(false); // Track if audio is playing
const ready = ref(false); // Track if audio is ready to play
const audioRef = ref(null); // Reference to the audio element
const currentTime = ref(0); // Current time of the audio
const duration = ref(0); // Duration of the audio

const currentTrackObj = computed(() => {
  return feed.find((track) => track.audio === currentTrack.value);
});

watch(currentTrack, () => {
  isPlaying.value = false; // Reset playing state when track changes
  ready.value = false; // Reset ready state until new track is loaded
});

watch(ready, (val) => {
  if (val && audioRef.value) {
    audioRef.value
      .play()
      .then(() => {
        isPlaying.value = true;
      })
      .catch((e) => {
        console.error("Error playing audio:", e);
        isPlaying.value = false;
      });
  }
});

// Function to toggle play/pause
const togglePlay = () => {
  const audio = audioRef.value;
  if (!audio) return;
  // Checks if audio is playing or paused and toggles accordingly
  if (isPlaying.value) {
    audio.pause();
  } else {
    audio.play().catch((error) => {
      console.error("Error playing audio:", error);
    });
  }
  // Updates playing state to the opposite of current state, so that the button text updates correctly
  isPlaying.value = !isPlaying.value;
};

const skipToNextTrack = () => {
  // Logic to skip to the next track in the feed
  const currentIndex = feed.findIndex(
    (track) => track.audio === currentTrack.value,
  );
  currentTrack.value = feed[(currentIndex + 1) % feed.length].audio;
  isPlaying.value = false; // Reset playing state
  ready.value = false; // Reset ready state until new track is loade
};

const skipToLastTrack = () => {
  // Logic to skip to the previous track in the feed
  const currentIndex = feed.findIndex(
    (track) => track.audio === currentTrack.value,
  );
  currentTrack.value = feed[(currentIndex - 1) % feed.length].audio;
  isPlaying.value = false; // Reset playing state
  ready.value = false; // Reset ready state until new track is loaded
};

const onTimeUpdate = () => {
  if (audioRef.value) {
    currentTime.value = audioRef.value.currentTime;
    duration.value = audioRef.value.duration;
  }
};

const formatTime = (time) => {
  const minutes = Math.floor(time / 60);
  const seconds = Math.floor(time % 60);
  return `${minutes}:${seconds < 10 ? "0" : ""}${seconds}`;
};

// Event handler for when audio can play
const onCanPlay = () => {
  ready.value = true;
};
</script>

<template>
<div class="player-box" v-if="currentTrack">
  <audio
    ref="audioRef"
    :src="currentTrack"
    preload="auto"
    @canplay="onCanPlay"
    @timeupdate="onTimeUpdate"
  ></audio>
  
  <div class="player-info-row">
    <div class="track-info">
      <img
        class="track-thumbnail"
        :src="currentTrackObj?.image"
        alt="Track Thumbnail"
        v-if="currentTrackObj"
      />
      <p>{{ currentTrackObj?.title }}</p>
    </div>
    
    <div class="progress-bar">
      <span>{{ formatTime(currentTime) }}</span>
      <input
        type="range"
        min="0"
        :max="duration"
        step="1"
        v-model="currentTime"
        @input="audioRef.currentTime = currentTime"
      />
      <span class="timeSpan">{{ formatTime(duration) }}</span>
    </div>
  </div>
  
  <div class="button-row-1">
    <button
      class="skip-back-button"
      @click="skipToLastTrack"
      vmodel="ready"
      :disabled="!ready"
    >
      Back
    </button>
    <button class="play-button" @click="togglePlay" :disabled="!ready">
      {{ isPlaying ? "Pause" : "Play" }}
    </button>
    <button
      class="skip-button"
      @click="skipToNextTrack"
      vmodel="ready"
      :disabled="!ready"
    >
      Skip
    </button>
  </div>
</div>
</template>