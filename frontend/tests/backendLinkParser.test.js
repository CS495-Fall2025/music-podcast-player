import { describe, it, expect, vi, beforeEach } from "vitest";
import { requestLinkedFeeds } from "../src/controllers/backendLinkParser.js";
import { feed, feedTracks } from "../src/controllers/localFeedStore.js";
import {
  setLoading,
  setError,
  clearError,
} from "../src/controllers/statusStore.js";

vi.mock("../src/controllers/statusStore.js", () => ({
  setLoading: vi.fn(),
  setError: vi.fn(),
  clearError: vi.fn(),
}));

describe("linkedFeedParser controller", () => {
  const mockConfig = () => {
    globalThis.fetch.mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve({ backendUrl: "http://localhost:5000" }),
    });
  };

  beforeEach(() => {
    feed.splice(0, feed.length);
    feedTracks.splice(0, feedTracks.length);

    globalThis.fetch = vi.fn();
    vi.clearAllMocks();
  });

  it("successfully parses feeds and tracks on valid response and returns true", async () => {
    const mockUrl = "https://example.com/feed.xml";
    const mockResponse = {
      feed: {
        artist: "Test Artist",
        title: "Test Podcast",
        description: "A podcast about testing",
        link: mockUrl,
        art_url: "https://example.com/art.jpg",
        items: [
          {
            title: "Episode 1",
            enclosure_url: "https://example.com/audio1.mp3",
          },
        ],
        value_items: [
          {
            Name: "Test Node",
            Type: "node",
            Address: "03abc...",
            Split: 100,
          },
        ],
      },
    };

    mockConfig();
    globalThis.fetch.mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve(mockResponse),
    });

    const result = await requestLinkedFeeds(mockUrl);

    // Assert fetch call
    expect(globalThis.fetch).toHaveBeenCalledWith(
      `http://localhost:5000/link/feed?url=${encodeURIComponent(mockUrl)}`,
    );

    // Assert stores were updated
    expect(feed.length).toBe(1);
    expect(feed[0]).toMatchObject({
      type: "feed",
      artist: "Test Artist",
      title: "Test Podcast",
    });

    expect(feedTracks.length).toBe(1);
    expect(feedTracks[0]).toMatchObject({
      type: "track",
      title: "Episode 1",
      artist: "Test Artist",
      audio: "https://example.com/audio1.mp3",
    });

    // Check value node was mapped correctly inside the track
    expect(feedTracks[0].value.length).toBe(1);
    expect(feedTracks[0].value[0].recipient).toBe("Test Node");

    expect(clearError).toHaveBeenCalled();
    expect(setLoading).toHaveBeenCalledWith(false);
    expect(result).toBe(true);
  });

  it("handles InternalApiBadResponse correctly and returns false", async () => {
    mockConfig();
    globalThis.fetch.mockResolvedValueOnce({
      ok: false,
      json: () => Promise.resolve({ error: "InternalApiBadResponse" }),
    });

    const result = await requestLinkedFeeds("bad-url");

    expect(setError).toHaveBeenCalledWith(
      "feed-error",
      "Feed Parse Error",
      "Unable to read this RSS feed. The feed may have invalid syntax or be unreachable.",
      "Try Another",
      expect.any(Function),
    );
    expect(result).toBe(false);
  });

  it("handles ExternalApiTimeout correctly and returns false", async () => {
    mockConfig();
    globalThis.fetch.mockResolvedValueOnce({
      ok: false,
      json: () => Promise.resolve({ error: "ExternalApiTimeout" }),
    });

    const result = await requestLinkedFeeds("timeout-url");

    expect(setError).toHaveBeenCalledWith(
      "external-error",
      "Feed Timeout",
      "The feed took too long to load. Please try again.",
      "Retry",
      expect.any(Function),
    );
    expect(result).toBe(false);
  });

  it("handles 400 status correctly and returns false", async () => {
    mockConfig();
    globalThis.fetch.mockResolvedValueOnce({
      ok: false,
      status: 400,
      json: () => Promise.resolve({}),
    });

    const result = await requestLinkedFeeds("invalid-url");

    expect(setError).toHaveBeenCalledWith(
      "error",
      "Invalid Request",
      "Your request was rejected by the server. Please try again.",
      "Retry",
      expect.any(Function),
    );
    expect(result).toBe(false);
  });

  it("handles offline/fetch exceptions and returns false", async () => {
    mockConfig();
    globalThis.fetch.mockRejectedValueOnce(new Error("Network disconnect"));

    const result = await requestLinkedFeeds("test-url");

    expect(setError).toHaveBeenCalledWith(
      "offline",
      "Connection Error",
      "Unable to reach the server.",
      "Retry",
      expect.any(Function),
    );
    expect(setLoading).toHaveBeenCalledWith(false);
    expect(result).toBe(false);
  });
});
