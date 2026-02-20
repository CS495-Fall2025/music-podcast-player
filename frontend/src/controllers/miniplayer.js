import { ref, watch } from "vue";
import { currentTrack, feedTracks } from "../controllers/localFeedStore.js";

import playIcon from "../assets/images/play-icon.svg";
import pauseIcon from "../assets/images/pause-icon.svg";
import skipIcon from "../assets/images/forward-icon.svg";
import rewindIcon from "../assets/images/backward-icon.svg";
import shuffleIcon from "../assets/images/random-icon.svg";
import repeatIcon from "../assets/images/undo-arrow-icon.svg";
import reverseIcon from "../assets/images/reverse-icon.svg";

export function useMiniPlayer() {
  const isPlaying = ref(false);
  const ready = ref(false);
  const audioRef = ref(null);
  const currentTime = ref(0);
  const duration = ref(0);
  const repeat = ref(false);
  const isShuffle = ref(false);
  const isReverse = ref(false);
  const shuffleOrder = ref([]);
  const shuffleIndex = ref(-1);
  const prevClickTimeout = ref(null);
  const DOUBLE_CLICK_DELAY = 800;

  const getCurrentIndex = () => {
    if (!currentTrack.value || !currentTrack.value.audio) return -1;
    return feedTracks.findIndex(
      (track) => track.audio === currentTrack.value.audio,
    );
  };

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

    indices.push(currentIndex);
    return indices;
  };

  const toggleShuffle = () => {
    // Not shuffling
    if (!isShuffle.value) {
      const order = buildShuffleOrder();
      if (!order.length) return;

      shuffleOrder.value = order;
      shuffleIndex.value = -1;
      isShuffle.value = true;
    }
    // Shuffling
    else {
      isShuffle.value = false;
      shuffleOrder.value = [];
      shuffleIndex.value = -1;
    }
  };

  const toggleReverse = () => {
    isReverse.value = !isReverse.value;
    feedTracks.reverse();
  };

  watch(currentTrack, () => {
    isPlaying.value = false;
    ready.value = false;
  });

  watch(ready, (val) => {
    if (val && audioRef.value) {
      audioRef.value
        .play()
        .then(() => (isPlaying.value = true))
        .catch(() => (isPlaying.value = false));
    }
  });

  const togglePlay = () => {
    const audio = audioRef.value;
    if (!audio) return;

    if (isPlaying.value) audio.pause();
    else audio.play();

    isPlaying.value = !isPlaying.value;
  };

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

    // Not shuffling
    if (!isShuffle.value || !shuffleOrder.value.length) {
      const i = getCurrentIndex();
      if (i === -1) return;
      currentTrack.value = feedTracks[(i + 1) % feedTracks.length];
    }
    // Shuffling
    else {
      shuffleIndex.value = (shuffleIndex.value + 1) % shuffleOrder.value.length;
      currentTrack.value = feedTracks[shuffleOrder.value[shuffleIndex.value]];
    }

    isPlaying.value = false;
    ready.value = false;
    repeat.value = false;
  };

  const skipToPreviousTrack = () => {
    if (prevClickTimeout.value) {
      clearTimeout(prevClickTimeout.value);
      prevClickTimeout.value = null;

      // Not shuffling
      if (!isShuffle.value) {
        const i = getCurrentIndex();
        if (i > 0) currentTrack.value = feedTracks[i - 1];
        else restartSong();
      }
      // Shuffling
      else {
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

    prevClickTimeout.value = setTimeout(() => {
      restartSong();
      prevClickTimeout.value = null;
    }, DOUBLE_CLICK_DELAY);
  };

  const onTimeUpdate = () => {
    if (!audioRef.value) return;
    currentTime.value = audioRef.value.currentTime;
    duration.value = audioRef.value.duration;
    if (currentTime.value >= duration.value && !repeat.value) {
      isPlaying.value = false;
    }
  };

  const formatTime = (time) => {
    const m = Math.floor(time / 60);
    const s = Math.floor(time % 60);
    return `${m}:${s < 10 ? "0" : ""}${s}`;
  };

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
    skipIcon,
    rewindIcon,
    shuffleIcon,
    repeatIcon,
    reverseIcon,

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
