<style src="../style.css"></style>

<script setup>
import BoostModal from "./BoostModal.vue";
import { useMiniPlayer } from "../controllers/miniplayer.js";
import { ref } from "vue";

const volume = ref(1);

const {
  isPlaying,
  ready,
  audioRef,
  currentTime,
  duration,
  repeat,
  isShuffle,
  isReverse,
  currentTrack,
  feedTracks,
  playIcon,
  pauseIcon,
  stepIcon,
  shuffleIcon,
  reverseIcon,
  repeatIcon,
  volumeIcon,
  togglePlay,
  toggleReverse,
  skipToNextTrack,
  skipToPreviousTrack,
  toggleShuffle,
  repeatTrack,
  onTimeUpdate,
  onCanPlay,
  onEnded,
  formatTime,
} = useMiniPlayer();
</script>

<template>
  <div class="player-box" v-if="currentTrack">
    <audio
      ref="audioRef"
      :src="currentTrack.audio"
      preload="auto"
      :repeat="repeat"
      @canplay="onCanPlay"
      @timeupdate="onTimeUpdate"
      @ended="onEnded"
    ></audio>
    <div class="player-info-row">
      <div class="track-info">
        <img
          class="track-thumbnail"
          :src="currentTrack?.image"
          alt="Track Thumbnail"
          v-if="currentTrack"
        />
        <p>{{ currentTrack?.title }}</p>
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
        class="media-button repeat-button"
        @click="repeatTrack"
        :class="{ active: repeat, 'is-disabled': !repeat }"
        :disabled="!ready"
      >
        <img :src="repeatIcon" alt="Repeat" class="play-icon" />
      </button>
      <button
        class="media-button shuffle-button"
        :class="{ 'is-disabled': !isShuffle }"
        @click="toggleShuffle"
        vmodel="ready"
        :disabled="!ready || !feedTracks.length"
      >
        <img :src="shuffleIcon" alt="Shuffle" class="play-icon" />
      </button>
      <button
        class="media-button reverse-button"
        :class="{ 'is-disabled': !isReverse }"
        @click="toggleReverse"
        vmodel="ready"
        :disabled="!ready || !feedTracks.length"
      >
        <img
          :src="reverseIcon"
          alt="Reverse"
          class="play-icon"
          :style="'transform: rotate(90deg);'"
        />
      </button>
      <button
        class="media-button skip-back-button"
        @click="skipToPreviousTrack"
        :disabled="!ready"
      >
        <img
          :src="stepIcon"
          alt="Rewind"
          class="play-icon"
          :style="'transform: rotate(180deg);'"
        />
      </button>
      <button
        class="media-button play-button"
        @click="togglePlay"
        :disabled="!ready"
      >
        <img
          :src="isPlaying ? pauseIcon : playIcon"
          alt="Play / Pause"
          class="play-icon"
        />
      </button>
      <button
        class="media-button skip-button"
        @click="skipToNextTrack"
        vmodel="ready"
        :disabled="!ready"
      >
        <img :src="stepIcon" alt="Skip" class="play-icon" />
      </button>
      <BoostModal />

      <div class="volume-control">
        <div class="volume-icon" v-html="volumeIcon"></div>
        <input
          type="range"
          min="0"
          max="1"
          step="0.01"
          v-model="volume"
          @input="audioRef.volume = volume"
        />
      </div>
    </div>
  </div>
</template>

<style scoped>
.player-box {
  position: absolute;
  top: auto;
  right: 0;
  bottom: 0;
  left: 0;
  z-index: var(--player-z);

  display: flex;
  flex-direction: column;
  flex-shrink: 0;
  align-items: center;
  justify-content: space-between;

  height: auto;
  min-height: min-content;
  padding: clamp(8px, 1.5vh, 16px);
  padding-bottom: calc(clamp(8px, 1.5vh, 16px) + env(safe-area-inset-bottom));

  background-color: var(--player-background);
  border-top: 2px solid var(--orange);
}

.player-box p {
  max-width: 100ch;
  margin: 5px 0;

  color: var(--light-orange);
  font-size: large;
  font-weight: bold;
  text-align: center;
  white-space: nowrap;
}

.player-info-row {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 24px;

  width: 100%;
  max-width: 900px;
}

.track-info {
  display: flex;
  flex-direction: row;
  align-items: center;
  gap: clamp(8px, 2vw, 14px);

  max-width: 100%;
}

.track-info p {
  max-width: 100%;
  margin: 0;

  color: var(--light-orange);
  font-size: clamp(0.9rem, 2.5vw, 1.1rem);
  line-height: 1.2;
  text-align: left;
  white-space: nowrap;

  overflow: hidden;
  text-overflow: ellipsis;
}

.track-thumbnail {
  flex-shrink: 0;
  width: clamp(36px, 8vw, 50px);
  height: clamp(36px, 8vw, 50px);

  object-fit: cover;
  border-radius: var(--border-radius);
}

.progress-bar {
  display: flex;
  flex: 1;
  align-items: center;

  width: 100%;
  max-width: 600px;
  margin: 8px auto 0;

  color: var(--light-text);
}

.progress-bar input[type="range"] {
  flex: 1;
  min-width: 0;
  max-width: 100%;

  accent-color: var(--light-orange);
}

.progress-bar span {
  width: 6ch;
  text-align: center;
  font-variant-numeric: tabular-nums;
}

.button-row-1 {
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: center;
  gap: 16px;

  margin: 1px 2px;
  transform: scale(0.8);
}

.media-button {
  display: flex;
  align-items: center;
  justify-content: center;

  width: clamp(2.5em, 3.5vw, 3.25em);
  height: clamp(2.5em, 2vw, 3.25em);
  padding: 0;

  font-size: clamp(1em, 2.2vw, 1.1em);
  line-height: 1;
}

.media-button:disabled,
.play-button:disabled {
  background-color: grey;
  border-color: grey;
}

.media-button:disabled {
  cursor: not-allowed;
}

.media-button.is-disabled {
  opacity: 0.4;
  filter: grayscale(100%);
}

.play-button {
  width: 100px;
  height: 50px;

  color: black;
  font-size: 18px;

  background-color: var(--cream);
  border: var(--border-thick) var(--orange);
  border-radius: var(--border-radius-lg);
}

.media-button.play-button {
  width: clamp(3.5em, 5vw, 6em);
  height: clamp(2.5em, 2.5vw, 3em);
  font-size: clamp(1.15em, 3vw, 1.25em);
}

.play-button:hover:enabled,
.play-button:active:enabled {
  background-color: var(--lighter-orange);
}

.play-icon {
  width: 1.2em;
  height: 1.2em;
  fill: currentColor;
}

.volume-control {
  display: flex;
  align-items: center;
  gap: 8px;
  color: var(--light-text);
  margin-left: 8px;
}

.volume-control input[type="range"] {
  width: clamp(60px, 8vw, 100px); /* Keeps it responsive on desktop */
  accent-color: var(--light-orange);
  cursor: pointer;
}

.volume-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 2em;
  height: 2em;
  fill: currentColor;
}

@media (max-width: 768px) {
  .track-thumbnail,
  .track-info p,
  .volume-control {
    display: none;
  }

  .button-row-1,
  .progress-bar {
    scale: 0.9;
  }
}
</style>
