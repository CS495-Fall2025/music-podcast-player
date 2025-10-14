<script setup>
import { ref, watch } from "vue";

import { currentTrack, feed } from "./localFeedStore.js";

const isPlaying = ref(false); // Track if audio is playing
const ready = ref(false); // Track if audio is ready to play
const audioRef = ref(null); // Reference to the audio element
const currentTime = ref(0); // Current time of the audio
const duration = ref(0); // Duration of the audio
const repeat = ref(false); // Track if audio is set to repeat

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
  const currentIndex = feed.findIndex(
    (track) => track.audio === currentTrack.value,
  );
  const nextIndex = (currentIndex + 1) % feed.length;
  currentTrack.value = feed[nextIndex].audio;
  isPlaying.value = false; // Reset playing state
  ready.value = false; // Reset ready state until new track is loade
  repeat.value = false; // Turn off repeat when skipping to next track
};

const skipToLastTrack = () => {
  const currentIndex = feed.findIndex(
    (track) => track.audio === currentTrack.value,
  );
  currentTrack.value = feed[currentIndex - 1].audio;
  isPlaying.value = false; // Reset playing state
  ready.value = false; // Reset ready state until new track is loaded
  repeat.value = false; // Turn off repeat when skipping to last track
};

const onTimeUpdate = () => {
  if (audioRef.value) {
    currentTime.value = audioRef.value.currentTime;
    duration.value = audioRef.value.duration;
  }
  if (currentTime.value >= duration.value && !repeat.value) {
    isPlaying.value = false; // Stop playing when track ends and repeat is off
  }
};

const formatTime = (time) => {
  const minutes = Math.floor(time / 60);
  const seconds = Math.floor(time % 60);
  return `${minutes}:${seconds < 10 ? "0" : ""}${seconds}`;
};

const repeatTrack = () => {
  repeat.value = !repeat.value;
};

// Event handler for when audio can play
const onCanPlay = () => {
  ready.value = true;
};

const onEnded = () => {
  if (repeat.value && audioRef.value) {
    audioRef.value.currentTime = 0;
    audioRef.value.play().catch((error) => {
      console.error("Error playing audio:", error);
    });
  } else {
    skipToNextTrack();
  }
};
</script>
<template>
  <div id="player-box" v-if="currentTrack">
    <audio
      ref="audioRef"
      :src="currentTrack"
      preload="auto"
      @canplay="onCanPlay"
      @timeupdate="onTimeUpdate"
      @ended="onEnded"
    ></audio>
    <img
      id="track-thumbnail"
      :src="currentTrackObj?.image"
      alt="Track Thumbnail"
      width="300"
      height="300"
      v-if="currentTrackObj"
    />
    <p>{{ currentTrackObj?.title }}</p>
    <div id="progress-bar">
      <span>{{ formatTime(currentTime) }}</span>
      <input
        type="range"
        min="0"
        :max="duration"
        step="1"
        v-model="currentTime"
        @input="audioRef.currentTime = currentTime"
      />
      <span id="timeSpan">{{ formatTime(duration) }}</span>
    </div>
    <div id="button-row-1">
      <button id="repeat-button" @click="repeatTrack">
        {{ repeat ? "Stop Repeat" : "Repeat" }}
      </button>
      <button
        id="skip-back-button"
        @click="skipToLastTrack"
        vmodel="ready"
        :disabled="!ready"
      >
        Back
      </button>
      <button id="play-button" @click="togglePlay" :disabled="!ready">
        {{ isPlaying ? "Pause" : "Play" }}
      </button>
      <button
        id="skip-button"
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
#player-box {
  background-color: #090909;
  padding: 24px;
  position: fixed;
  bottom: 0;
  width: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
}

#button-row-1 {
  display: flex;
  flex-direction: row;
  justify-content: center;
  align-items: center;
  gap: 16px;
  margin-top: 16px;
}

#progress-bar {
  margin: 16px auto 0 auto;
  display: flex;
  align-items: center;
  width: 100%;
  max-width: 600px;
  margin-top: 16px;
}

#progress-bar input[type="range"] {
  flex: 1;
  min-width: 0;
  max-width: 100%;
  accent-color: #fc766a;
}

#track-thumbnail {
  border-radius: 8px;
  vertical-align: middle;
}

#play-button {
  background-color: black;
  border: red solid 2px;
  border-radius: 10px;
  color: white;
  cursor: pointer;
  font-size: 16px;
  height: 50px;
  width: 100px;
  margin-top: 16px;
}

#play-button:disabled {
  background-color: grey;
  border: grey solid 2px;
  cursor: not-allowed;
}
#play-button:hover:enabled {
  background-color: #fc766a;
  border: #fc766a solid 2px;
}

#play-button:active:enabled {
  background-color: #d94f4a;
  border: #d94f4a solid 2px;
}
#play-button:focus {
  outline: none;
}
</style>
