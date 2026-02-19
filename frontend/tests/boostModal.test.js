import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";

// Mock the lightning payments
vi.mock("../src/controllers/lightningPayments.js", async () => {
  const { ref } = await import("vue");
  return {
    connectWallet: vi.fn(),
    walletConnected: ref(false),
    makeBoostMeta: vi.fn(),
    makeValueMeta: vi.fn(),
    sendBoost: vi.fn(),
  };
});

// Mock currentTrack store ref
vi.mock("../src/controllers/localFeedStore.js", async () => {
  const { ref } = await import("vue");
  return {
    currentTrack: ref(null),
  };
});

import { useBoostModal } from "../src/controllers/boostModal.js";

import {
  makeBoostMeta,
  makeValueMeta,
  sendBoost,
} from "../src/controllers/lightningPayments.js";
import { currentTrack } from "../src/controllers/localFeedStore.js";

const makeTrack = () => ({
  feedTitle: "Feed Title",
  feedGuid: "feed-guid",
  title: "Episode Title",
  guid: "episode-guid",
  value: { some: "value" },
});

beforeEach(() => {
  vi.clearAllMocks();
  currentTrack.value = makeTrack();
});

afterEach(() => {
  vi.unstubAllGlobals();
});

describe("useBoostModal (minimal)", () => {
  it("openModal opens and sets recipients (and fetches price)", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        json: vi.fn().mockResolvedValue({ bitcoin: { usd: 50000 } }),
      }),
    );

    const modal = useBoostModal();
    await modal.openModal();

    expect(modal.isOpen.value).toBe(true);
    expect(modal.recipients.value).toEqual(currentTrack.value);
    expect(fetch).toHaveBeenCalled();
  });

  it("onSendBoost blocks invalid sats and sets satsError", () => {
    const modal = useBoostModal();

    modal.isOpen.value = true;
    modal.sats.value = 0; // invalid

    modal.onSendBoost();

    expect(modal.satsError.value).toBe(
      "Enter a positive integer amount of sats.",
    );
    expect(sendBoost).not.toHaveBeenCalled();
    expect(modal.isOpen.value).toBe(true);
  });

  it("onSendBoost sends boost when valid and then closes/resets", () => {
    const modal = useBoostModal();

    const track = makeTrack();
    currentTrack.value = track;

    modal.isOpen.value = true;
    modal.sats.value = 100;
    modal.message.value = "Great track";

    makeBoostMeta.mockReturnValue({ boost: true });
    makeValueMeta.mockReturnValue({ value: true });

    modal.onSendBoost();

    expect(makeBoostMeta).toHaveBeenCalledWith(
      track.feedTitle,
      track.feedGuid,
      track.title,
      track.guid,
      "Great track",
    );
    expect(makeValueMeta).toHaveBeenCalledWith(100, track.value);
    expect(sendBoost).toHaveBeenCalled();

    // verify it closed and reset
    expect(modal.isOpen.value).toBe(false);
    expect(modal.sats.value).toBe(0);
    expect(modal.message.value).toBe("");
    expect(modal.satsError.value).toBe("");
  });
});
