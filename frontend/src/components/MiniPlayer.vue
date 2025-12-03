<style src="../style.css"></style>

<script setup>
import { ref, computed, watch } from "vue";

import { currentTrack, feed } from "../controllers/localFeedStore.js";

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
    <p>{{ currentTrackObj?.title }}</p>

    <div class="player-info-row">
      <div class="track-info">
        <img
          class="track-thumbnail"
          :src="currentTrackObj?.image"
          alt="Track Thumbnail"
          v-if="currentTrackObj"
        />
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

<style scoped>
.player-box {
  background-color: var(--player-background);
  padding: 10px;
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  z-index: var(--player-z);
  max-height: var(--player-height);
  justify-content: center;
}

.player-box p {
  margin: 10px 0 0 0;
  white-space: nowrap;
  max-width: 100ch;
  color: var(--light-orange);
  font-size: large;
  font-weight: bold;
  text-align: center;
}

.player-info-row {
  display: flex;
  align-items: center;
  gap: 24px;
  width: 100%;
  max-width: 900px;
}

.track-info {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2px;
  min-width: 125px;
  max-width: 125px;
  min-height: 60px;
  max-height: 60px;
  color: var(--light-text);
  font-weight: bold;
}

.track-info p {
  margin: 0;
  white-space: normal;
  overflow-wrap: break-word;
  word-break: break-word;
  max-width: 125px;
  color: var(--light-orange);
  font-size: large;
  text-align: center;
}

.track-thumbnail {
  border-radius: var(--border-radius);
  vertical-align: middle;
  width: 100%;
  height: auto;
  max-width: 100px;
}

.progress-bar {
  flex: 1;
  color: var(--light-text);
  margin: 16px 20px 0 20px;
  display: flex;
  align-items: center;
  width: 100%;
  max-width: 600px;
}

.progress-bar input[type="range"] {
  flex: 1;
  min-width: 0;
  max-width: 100%;
  accent-color: var(--light-orange);
}

.button-row-1 {
  display: flex;
  flex-direction: row;
  justify-content: center;
  align-items: center;
  gap: 16px;
  margin: 1px 2px;
  transform: scale(0.8);
}

.play-button {
  background-color: var(--cream);
  border: var(--border-thick) var(--orange);
  border-radius: var(--border-radius-lg);
  color: black;
  font-size: 18px;
  height: 50px;
  width: 100px;
}

.play-button:disabled {
  background-color: grey;
  border-color: grey;
}

.play-button:hover:enabled,
.play-button:active:enabled {
  background-color: var(--lighter-orange);
}

.play-button:focus {
  outline: none;
}
</style>
