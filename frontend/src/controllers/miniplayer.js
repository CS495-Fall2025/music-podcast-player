import { ref, watch } from "vue";
import {
  currentTrack,
  feedTracks,
  currentVolume,
} from "../controllers/localFeedStore.js";
import { drippingState } from "../controllers/drippingState.js";

import playIcon from "../assets/images/play-icon.svg";
import pauseIcon from "../assets/images/pause-icon.svg";
import stepIcon from "../assets/images/step-icon.svg";
import shuffleIcon from "../assets/images/random-icon.svg";
import repeatIcon from "../assets/images/undo-arrow-icon.svg";
import reverseIcon from "../assets/images/reverse-icon.svg";
import volumeIcon from "../assets/images/volume-icon.svg?raw";

export function useMiniPlayer() {
  // --- State Variables ---
  const isPlaying = ref(false);
  const ready = ref(false);
  const audioRef = ref(null);
  const currentTime = ref(0);
  const duration = ref(0);

  // --- Playback Modes ---
  const repeat = ref(false);
  const isShuffle = ref(false);
  const isReverse = ref(false);

  // --- Shuffle & Navigation State ---
  const shuffleOrder = ref([]);
  const shuffleIndex = ref(-1);
  const prevClickTimeout = ref(null);
  const DOUBLE_CLICK_DELAY = 800; // Time window (ms) to detect a double-click for the previous button

  // --- Helpers ---

  // Extracts a unique identifier for a given track to handle comparisons
  const getTrackKey = (track) => {
    if (!track) return null;
    return track.id ?? track.track_url ?? track.audio ?? null;
  };

  // Finds the index of the currently playing track within the feed list
  const getCurrentIndex = () => {
    const key = getTrackKey(currentTrack.value);
    if (key !== null) {
      const keyedIndex = feedTracks.findIndex(
        (track) => getTrackKey(track) === key,
      );
      if (keyedIndex !== -1) return keyedIndex;
    }

    if (!currentTrack.value || !currentTrack.value.audio) return -1;
    return feedTracks.findIndex(
      (track) => track.audio === currentTrack.value.audio,
    );
  };

  // Generates a randomized array of track indices, excluding the currently playing track
  const buildShuffleOrder = () => {
    if (!feedTracks.length) return [];
    const currentIndex = getCurrentIndex();
    if (currentIndex === -1) return [];

    const indices = [];
    for (let i = 0; i < feedTracks.length; i++) {
      if (i !== currentIndex) indices.push(i);
    }

    for (let i = indices.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      [indices[i], indices[j]] = [indices[j], indices[i]];
    }

    // Add the current track back to the end of the shuffled list
    indices.push(currentIndex);
    return indices;
  };

  // --- Core Player Methods ---

  // Toggles shuffle mode on and off, generating a new order if turned on
  const toggleShuffle = () => {
    if (!isShuffle.value) {
      const order = buildShuffleOrder();
      if (!order.length) return;

      shuffleOrder.value = order;
      shuffleIndex.value = -1;
      isShuffle.value = true;
    } else {
      isShuffle.value = false;
      shuffleOrder.value = [];
      shuffleIndex.value = -1;
    }
  };

  // Toggles reverse mode and directly reverses the main track array
  const toggleReverse = () => {
    isReverse.value = !isReverse.value;
    feedTracks.reverse();
  };

  // --- Watchers ---

  // Reset player playback states whenever a new track is loaded
  watch(currentTrack, () => {
    isPlaying.value = false;
    ready.value = false;
  });

  // Autoplay the track once the audio element signals it is ready
  watch(ready, (val) => {
    if (val && audioRef.value) {
      audioRef.value
        .play()
        .then(() => (isPlaying.value = true))
        .catch(() => (isPlaying.value = false));
      audioRef.value.volume = currentVolume.value;
    }
  });

  // Sync the 'dripping' (streaming value/payments) state with the current playback status
  watch(isPlaying, (newIsPlaying) => {
    if (drippingState.enabled) {
      if (currentTrack.value.value.length === 0) {
        return;
      }
      drippingState.active = newIsPlaying;
    }
  });

  // Handle edge cases where dripping is enabled mid-playback
  watch(
    () => drippingState.enabled,
    (newEnabled) => {
      if (!isPlaying.value) {
        return;
      }
      const canDrip = currentTrack.value.value.length > 0;
      if (newEnabled && canDrip && isPlaying.value) {
        drippingState.active = true;
      }
    },
  );

  // --- Playback Controls ---

  const togglePlay = () => {
    const audio = audioRef.value;
    if (!audio) return;

    if (isPlaying.value) audio.pause();
    else audio.play();

    isPlaying.value = !isPlaying.value;
  };

  // Resets the current song to the beginning and ensures it is playing
  const restartSong = () => {
    const audio = audioRef.value;
    if (!audio) return;
    audio.currentTime = 0;
    audio.play();
    isPlaying.value = true;
    ready.value = true;
  };

  const skipToNextTrack = () => {
    if (!feedTracks.length) return;

    // Standard linear skip
    if (!isShuffle.value || !shuffleOrder.value.length) {
      const i = getCurrentIndex();
      if (i === -1) return;
      currentTrack.value = feedTracks[(i + 1) % feedTracks.length];
    }
    // Shuffled skip
    else {
      shuffleIndex.value = (shuffleIndex.value + 1) % shuffleOrder.value.length;
      currentTrack.value = feedTracks[shuffleOrder.value[shuffleIndex.value]];
    }

    isPlaying.value = false;
    ready.value = false;
    repeat.value = false;
  };

  // Implements double-click logic: Single click restarts the song, double-click goes to previous track
  const skipToPreviousTrack = () => {
    if (prevClickTimeout.value) {
      clearTimeout(prevClickTimeout.value);
      prevClickTimeout.value = null;

      // Double click detected: Skip backwards
      if (!isShuffle.value) {
        const i = getCurrentIndex();
        if (i > 0) currentTrack.value = feedTracks[i - 1];
        else restartSong();
      } else {
        if (shuffleIndex.value > 0) {
          shuffleIndex.value--;
          currentTrack.value =
            feedTracks[shuffleOrder.value[shuffleIndex.value]];
        } else restartSong();
      }

      ready.value = false;
      isPlaying.value = false;
      repeat.value = false;
      return;
    }

    // Single click detected: Restart current song
    prevClickTimeout.value = setTimeout(() => {
      restartSong();
      prevClickTimeout.value = null;
    }, DOUBLE_CLICK_DELAY);
  };

  // Keeps the UI progress bar synced with the HTML audio element's internal clock
  const onTimeUpdate = () => {
    if (!audioRef.value) return;
    currentTime.value = audioRef.value.currentTime;
    duration.value = audioRef.value.duration;
    if (currentTime.value >= duration.value && !repeat.value) {
      isPlaying.value = false;
    }
  };

  // Formats raw seconds into a standard "MM:SS" layout
  const formatTime = (time) => {
    const m = Math.floor(time / 60);
    const s = Math.floor(time % 60);
    return `${m}:${s < 10 ? "0" : ""}${s}`;
  };

  // --- Audio Event Listeners ---

  const repeatTrack = () => (repeat.value = !repeat.value);
  const onCanPlay = () => (ready.value = true);
  const onEnded = () => (repeat.value ? restartSong() : skipToNextTrack());

  return {
    // state
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

    // icons
    playIcon,
    pauseIcon,
    stepIcon,
    shuffleIcon,
    repeatIcon,
    reverseIcon,
    volumeIcon,

    // methods
    togglePlay,
    skipToNextTrack,
    skipToPreviousTrack,
    toggleShuffle,
    toggleReverse,
    repeatTrack,
    onTimeUpdate,
    onCanPlay,
    onEnded,
    formatTime,
  };
}
