import { describe, it, expect, vi, beforeEach } from "vitest";
import { requestLinkedFeeds } from "../src/controllers/backendLinkParser.js"; // Adjust import path as needed
import { feed, feedTracks } from "../src/controllers/localFeedStore.js";

describe("backendLinkParser controller", () => {
  const mockConfig = () => {
    globalThis.fetch.mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve({ backendUrl: "http://localhost:5000" }),
    });
  };

  vi.mock("../src/controllers/statusStore.js", () => ({
    setLoading: vi.fn(),
    navigateToError: vi.fn(),
    clearError: vi.fn(),
  }));

  vi.mock("../src/router", () => ({
    default: { push: vi.fn() },
  }));

  beforeEach(() => {
    feed.splice(0, feed.length);
    feedTracks.splice(0, feedTracks.length);
    globalThis.fetch = vi.fn();
    vi.clearAllMocks();
  });

  it("requestLinkedFeeds parses valid feed and populates stores", async () => {
    const mockResponse = {
      feeds: [
        {
          title: "Test Podcast",
          artist: "Test Artist",
          description: "A test podcast.",
          link: "https://example.com",
          art_url: "https://example.com/art.jpg",
          items: [
            {
              title: "Episode 1",
              description: "Ep 1 description",
              enclosure_url: "https://example.com/audio.mp3",
            },
          ],
          value_items: [
            {
              Name: "Alice",
              Type: "node",
              Address: "0x123",
              Split: "100",
            },
          ],
        },
      ],
    };

    mockConfig();
    globalThis.fetch.mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve(mockResponse),
    });

    const result = await requestLinkedFeeds("https://test.com/feed.xml");

    expect(result).toBe(true);
    expect(globalThis.fetch).toHaveBeenCalledWith(
      "http://localhost:5000/link/feed?url=https%3A%2F%2Ftest.com%2Ffeed.xml",
    );

    // Validate the parsed feed store
    expect(feed.length).toBe(1);
    expect(feed[0]).toEqual(
      expect.objectContaining({
        type: "feed",
        title: "Test Podcast",
        artist: "Test Artist",
      }),
    );

    // Validate the parsed feedTracks store
    expect(feedTracks.length).toBe(1);
    expect(feedTracks[0]).toEqual(
      expect.objectContaining({
        type: "track",
        title: "Episode 1",
        audio: "https://example.com/audio.mp3",
      }),
    );

    // Validate the parsed value blocks
    expect(feedTracks[0].value.length).toBe(1);
    expect(feedTracks[0].value[0]).toEqual(
      expect.objectContaining({
        type: "value",
        recipient: "Alice",
        split: "100",
      }),
    );
  });

  it("handles ExternalApiBadResponse and routes to home", async () => {
    const { navigateToError } = await import(
      "../src/controllers/statusStore.js"
    );
    mockConfig();
    globalThis.fetch.mockResolvedValueOnce({
      ok: false,
      json: () => Promise.resolve({ error: "ExternalApiBadResponse" }),
    });

    const result = await requestLinkedFeeds("https://test.com/feed.xml");

    expect(result).toBe(false);
    expect(navigateToError).toHaveBeenCalledWith(
      "feed-error",
      "Feed Parse Error",
      "Unable to read this RSS feed. The feed may have invalid syntax or be unreachable.",
      "Try Another",
      expect.any(Function),
    );
  });

  it("handles InternalApiTimeout correctly", async () => {
    const { navigateToError } = await import(
      "../src/controllers/statusStore.js"
    );
    mockConfig();
    globalThis.fetch.mockResolvedValueOnce({
      ok: false,
      json: () => Promise.resolve({ error: "InternalApiTimeout" }),
    });

    const result = await requestLinkedFeeds("https://test.com/feed.xml");

    expect(result).toBe(false);
    expect(navigateToError).toHaveBeenCalledWith(
      "external-error",
      "Feed Timeout",
      "The feed took too long to load. Please try again.",
      "Retry",
      expect.any(Function),
    );
  });

  it("handles network error correctly", async () => {
    const { navigateToError } = await import(
      "../src/controllers/statusStore.js"
    );
    mockConfig();
    globalThis.fetch.mockRejectedValueOnce(new Error("Network error"));

    const result = await requestLinkedFeeds("https://test.com/feed.xml");

    expect(result).toBe(false);
    expect(navigateToError).toHaveBeenCalledWith(
      "offline",
      "Connection Error",
      "Unable to reach the server.",
      "Retry",
      expect.any(Function),
    );
  });
});
