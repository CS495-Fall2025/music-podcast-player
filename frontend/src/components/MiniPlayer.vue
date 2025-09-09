<script setup lang="ts">
import { ref } from 'vue';
import LocalFeedStore from '../stores/LocalFeedStore';

const isPlaying = ref(false); // Track if audio is playing
const ready = ref(false); // Track if audio is ready to play
const audioRef = ref<HTMLAudioElement | null>(null); // Reference to the audio element
const chosenTrack = ref(true); // This should be set based on actual track selection logic

function selectTrack(track) {
  chosenTrack.value = track !== null;
}

// Function to toggle play/pause
const togglePlay = () => {
  const audio = audioRef.value;
  if (!audio) return;
  // Checks if audio is playing or paused and toggles accordingly
  if (isPlaying.value) {
    audio.pause();
  } else {
    audio.play().catch(e => {
      console.error("Error playing audio:", e);
      isPlaying.value = false;
    });
  }
  // Updates playing state to the opposite of current state, so that the button text updates correctly
  isPlaying.value = !isPlaying.value;
};

// Event handler for when audio can play
const onCanPlay = () => {
  ready.value = true;
};
</script>
<template>
  <div id="player-box" v-if="chosenTrack">
    <audio
      ref="audioRef"
      src="https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3"
      preload="auto"
      @canplay="onCanPlay"></audio>
    <button @click="togglePlay" :disabled="!ready">
      {{ isPlaying ? 'Pause' : 'Play' }}
    </button>
  </div>
</template>

<style scoped>
#player-box {
  background-color: #090909;
  padding: 24px;
  position: fixed;
  bottom: 0;
  width: 100%;
}
</style>
