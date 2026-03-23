import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { effectScope } from "vue";

vi.mock("../src/controllers/localFeedStore.js", async () => {
  const { ref, reactive } = await import("vue");
  return {
    currentTrack: ref(""),
    feedTracks: reactive([]),
  };
});

import { useMiniPlayer } from "../src/controllers/miniplayer.js";
import { currentTrack, feedTracks } from "../src/controllers/localFeedStore.js";

const makeTrack = (id) => ({
  audio: `track-${id}.mp3`,
  title: `T${id}`,
});

function createMiniPlayer() {
  const scope = effectScope();
  const mp = scope.run(() => useMiniPlayer());
  return { mp, scope };
}

beforeEach(() => {
  feedTracks.splice(0, feedTracks.length);
  currentTrack.value = "";
  vi.clearAllMocks();
});

afterEach(() => {
  vi.useRealTimers();
});

describe("useMiniPlayer (minimal)", () => {
  it("togglePlay plays/pauses and flips isPlaying", () => {
    const { mp, scope } = createMiniPlayer();

    const audio = {
      play: vi.fn(),
      pause: vi.fn(),
      currentTime: 0,
      duration: 120,
    };
    mp.audioRef.value = audio;

    mp.togglePlay();
    expect(audio.play).toHaveBeenCalledTimes(1);
    expect(mp.isPlaying.value).toBe(true);

    mp.togglePlay();
    expect(audio.pause).toHaveBeenCalledTimes(1);
    expect(mp.isPlaying.value).toBe(false);

    scope.stop();
  });

  it("skipToNextTrack goes to next track (wraps) and resets flags", () => {
    const { mp, scope } = createMiniPlayer();

    const t0 = makeTrack(0);
    const t1 = makeTrack(1);
    feedTracks.push(t0, t1);

    currentTrack.value = t1;

    mp.isPlaying.value = true;
    mp.ready.value = true;
    mp.repeat.value = true;

    mp.skipToNextTrack();

    expect(currentTrack.value).toEqual(t0);
    expect(mp.isPlaying.value).toBe(false);
    expect(mp.ready.value).toBe(false);
    expect(mp.repeat.value).toBe(false);

    scope.stop();
  });

  it("skipToPreviousTrack single-click restarts after 800ms", () => {
    const { mp, scope } = createMiniPlayer();
    vi.useFakeTimers();

    const t0 = makeTrack(0);
    const t1 = makeTrack(1);
    feedTracks.push(t0, t1);
    currentTrack.value = t1;

    const audio = {
      play: vi.fn(),
      pause: vi.fn(),
      currentTime: 42,
      duration: 120,
    };
    mp.audioRef.value = audio;

    mp.skipToPreviousTrack();
    vi.advanceTimersByTime(800);

    expect(audio.currentTime).toBe(0);
    expect(audio.play).toHaveBeenCalledTimes(1);
    expect(mp.isPlaying.value).toBe(true);
    expect(mp.ready.value).toBe(true);

    scope.stop();
  });

  it("toggleShuffle toggles on/off (won’t enable without valid currentTrack)", () => {
    const { mp, scope } = createMiniPlayer();

    feedTracks.push(makeTrack(0), makeTrack(1));

    currentTrack.value = "";
    mp.toggleShuffle();
    expect(mp.isShuffle.value).toBe(false);

    // has to be a track that exists in feedTracks by audio match
    currentTrack.value = makeTrack(0);
    mp.toggleShuffle();
    expect(mp.isShuffle.value).toBe(true);

    mp.toggleShuffle();
    expect(mp.isShuffle.value).toBe(false);

    scope.stop();
  });

  it("toggleReverse toggles isReverse and reverses feedTracks", () => {
    const { mp, scope } = createMiniPlayer();

    const t0 = makeTrack(0);
    const t1 = makeTrack(1);
    const t2 = makeTrack(2);
    feedTracks.push(t0, t1, t2);

    expect(mp.isReverse.value).toBe(false);
    expect(feedTracks.map((t) => t.audio)).toEqual([
      "track-0.mp3",
      "track-1.mp3",
      "track-2.mp3",
    ]);

    mp.toggleReverse();

    expect(mp.isReverse.value).toBe(true);
    expect(feedTracks.map((t) => t.audio)).toEqual([
      "track-2.mp3",
      "track-1.mp3",
      "track-0.mp3",
    ]);

    scope.stop();
  });

  it("repeatTrack toggles repeat", () => {
    const { mp, scope } = createMiniPlayer();

    expect(mp.repeat.value).toBe(false);
    mp.repeatTrack();
    expect(mp.repeat.value).toBe(true);

    scope.stop();
  });

  it("formatTime formats correctly", () => {
    const { mp, scope } = createMiniPlayer();

    expect(mp.formatTime(5)).toBe("0:05");
    expect(mp.formatTime(65)).toBe("1:05");

    scope.stop();
  });
});
