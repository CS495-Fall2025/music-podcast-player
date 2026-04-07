<style src="../style.css"></style>

<script setup>
import { ref, watch, onBeforeUnmount } from "vue";
import BoostModal from "./BoostModal.vue";
import { useMiniPlayer } from "../controllers/miniplayer.js";
import {
  satDripEnabled,
  satDripRate,
} from "../controllers/localFeedStore.js";

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
  skipIcon,
  rewindIcon,
  shuffleIcon,
  reverseIcon,
  repeatIcon,
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

const DRIP_SUMMARY_INTERVAL_MINUTES = 30;
const DRIP_SUMMARY_INTERVAL_MS = DRIP_SUMMARY_INTERVAL_MINUTES * 60 * 1000;
const DRIP_TICK_MS = 1000;
const POPUP_DURATION_MS = 4000;

const contributionPopupVisible = ref(false);
const contributionPopupMessage = ref("");

let dripTimerId = null;
let popupTimeoutId = null;
let activeDripMs = 0;
let satsAccumulated = 0;

function clearDripTimer() {
  if (dripTimerId !== null) {
    clearInterval(dripTimerId);
    dripTimerId = null;
  }
}

function hideContributionPopup() {
  contributionPopupVisible.value = false;

  if (popupTimeoutId !== null) {
    clearTimeout(popupTimeoutId);
    popupTimeoutId = null;
  }
}

function resetContributionInterval() {
  activeDripMs = 0;
  satsAccumulated = 0;
  hideContributionPopup();
}

function showContributionPopup(totalSats) {
  contributionPopupMessage.value = `You dripped ${totalSats} sats in the last ${DRIP_SUMMARY_INTERVAL_MINUTES} minutes.`;
  contributionPopupVisible.value = true;

  if (popupTimeoutId !== null) {
    clearTimeout(popupTimeoutId);
  }

  popupTimeoutId = setTimeout(() => {
    contributionPopupVisible.value = false;
    popupTimeoutId = null;
  }, POPUP_DURATION_MS);
}

function handleDripTick() {
  if (
    !satDripEnabled.value ||
    Number(satDripRate.value) <= 0 ||
    !isPlaying.value ||
    !currentTrack.value
  ) {
    return;
  }

  activeDripMs += DRIP_TICK_MS;
  satsAccumulated += Number(satDripRate.value) / 60;

  if (activeDripMs >= DRIP_SUMMARY_INTERVAL_MS) {
    showContributionPopup(Math.round(satsAccumulated));
    activeDripMs = 0;
    satsAccumulated = 0;
  }
}

function updateDripTimer() {
  const shouldTrackDripping =
    satDripEnabled.value &&
    Number(satDripRate.value) > 0 &&
    isPlaying.value &&
    !!currentTrack.value;

  if (shouldTrackDripping) {
    if (dripTimerId === null) {
      dripTimerId = setInterval(handleDripTick, DRIP_TICK_MS);
    }
  } else {
    clearDripTimer();
  }
}

watch([isPlaying, currentTrack], updateDripTimer, { immediate: true });

watch(satDripEnabled, (enabled) => {
  if (!enabled) {
    clearDripTimer();
    resetContributionInterval();
    return;
  }

  updateDripTimer();
});

watch(satDripRate, (newRate) => {
  if (Number(newRate) <= 0) {
    clearDripTimer();
    resetContributionInterval();
    return;
  }

  updateDripTimer();
});

onBeforeUnmount(() => {
  clearDripTimer();
  hideContributionPopup();
});
</script>

<template>
  <div class="player-box" v-if="currentTrack">
    <div v-if="contributionPopupVisible" class="contribution-popup">
      {{ contributionPopupMessage }}
    </div>

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
        <img :src="reverseIcon" alt="Reverse" class="play-icon" />
      </button>
      <button
        class="media-button skip-back-button"
        @click="skipToPreviousTrack"
        :disabled="!ready"
      >
        <img :src="rewindIcon" alt="Rewind" class="play-icon" />
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
        <img :src="skipIcon" alt="Skip" class="play-icon" />
        <!-- Skip Icon -->
      </button>
      <BoostModal />
    </div>
  </div>
</template>

<style scoped>
.player-box {
  background-color: var(--player-background);
  position: relative;

  padding: clamp(8px, 1.5vh, 16px);
  padding-bottom: calc(clamp(8px, 1.5vh, 16px) + env(safe-area-inset-bottom));
  right: 0;
  bottom: 0;
  left: 0;

  display: flex;
  flex-direction: column;
  flex-shrink: 0;

  align-items: center;
  justify-content: space-between;

  z-index: var(--player-z);
  height: auto;
  width: 100%;
  min-height: min-content;
  border-top: 2px solid var(--orange);
}

.contribution-popup {
  position: absolute;
  top: -58px;
  right: 20px;
  background-color: var(--nav-bg);
  color: var(--light-orange);
  border: 1px solid var(--orange);
  border-radius: var(--border-radius);
  box-shadow: var(--shadow-md);
  padding: 0.75rem 1rem;
  font-size: 0.95rem;
  font-weight: 600;
  z-index: 2100;
  max-width: 320px;
}

.player-box p {
  margin: 5px 0;
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
  flex-direction: column;
  gap: 24px;
  width: 100%;
  max-width: 900px;
}

.track-info {
  display: flex;
  align-items: center;
  gap: clamp(8px, 2vw, 14px);
  max-width: 100%;
  flex-direction: row;
  /* color: var(--light-text);
  font-weight: bold; */
}

.track-info p {
  margin: 0;
  color: var(--light-orange);

  font-size: clamp(0.9rem, 2.5vw, 1.1rem);
  line-height: 1.2;

  max-width: 100%;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;

  text-align: left;
}

@media (max-width: 480px) {
  .track-info {
    gap: 8px;
  }

  .track-info p {
    font-size: 0.9rem;
  }
}

.track-thumbnail {
  border-radius: var(--border-radius);
  width: clamp(36px, 8vw, 50px);
  height: clamp(36px, 8vw, 50px);
  object-fit: cover;
  flex-shrink: 0;
}

.progress-bar {
  flex: 1;
  color: var(--light-text);
  margin: 8px 20px 0 20px;
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

.progress-bar span {
  width: 6ch;
  text-align: center;
  font-variant-numeric: tabular-nums;
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

.media-button {
  padding: 0;

  width: clamp(2.5em, 3.5vw, 3.25em);
  height: clamp(2.5em, 2vw, 3.25em);

  font-size: clamp(1em, 2.2vw, 1.1em);
  line-height: 1;

  display: flex;
  align-items: center;
  justify-content: center;
}

.media-button:disabled {
  background-color: grey;
  border-color: grey;
  cursor: not-allowed;
}

.media-button.is-disabled {
  opacity: 0.4;
  filter: grayscale(100%);
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

.play-icon {
  width: 1.2em;
  height: 1.2em;
  fill: currentColor;
}

.media-button.play-button {
  width: clamp(3.5em, 5vw, 6em);
  height: clamp(2.5em, 2.5vw, 3em);
  font-size: clamp(1.15em, 3vw, 1.25em);
}

.play-button:disabled {
  background-color: grey;
  border-color: grey;
}

.play-button:hover:enabled,
.play-button:active:enabled {
  background-color: var(--lighter-orange);
}
</style>