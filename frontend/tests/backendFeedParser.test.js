import { describe, it, expect, vi, beforeEach } from "vitest";
import { requestFeeds } from "../src/controllers/backendFeedParser.js";
import { searchedFeeds } from "../src/controllers/localFeedStore.js";

describe("backendFeedParser controller", () => {
  // mock config.json
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

  // Reset state and mock console/fetch before each test
  beforeEach(() => {
    searchedFeeds.splice(0, searchedFeeds.length);

    vi.spyOn(console, "log").mockImplementation(() => {});
    globalThis.fetch = vi.fn();
  });

  // Test successful API call and data storage
  it("requestFeeds calls fetch with correct URL and updates searchedFeeds on success", async () => {
    const mockFeeds = [{ id: 1, title: "Test Feed" }];
    const mockResponse = { feeds: mockFeeds };

    mockConfig();
    globalThis.fetch.mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve(mockResponse),
    });

    await requestFeeds("test query");

    // Check that the backend API was called with correct URL
    expect(globalThis.fetch).toHaveBeenCalledWith(
      "http://localhost:5000/search/feeds?query=test%20query&count=50",
    );

    await vi.dynamicImportSettled();
    expect(Array.from(searchedFeeds)).toEqual(mockFeeds);
  });

  // Test handling of HTTP error responses
  it("requestFeeds handles fetch error correctly", async () => {
    const { navigateToError } = await import(
      "../src/controllers/statusStore.js"
    );

    mockConfig();
    globalThis.fetch.mockResolvedValueOnce({
      ok: false,
      status: 404,
      json: () => Promise.resolve({}),
    });

    await requestFeeds("test query");

    expect(navigateToError).toHaveBeenCalledWith(
      "error",
      "Invalid Request",
      expect.any(String),
      "Retry",
      expect.any(Function),
    );
  });

  // Test handling of network errors
  it("requestFeeds handles network error correctly", async () => {
    const { navigateToError } = await import(
      "../src/controllers/statusStore.js"
    );

    mockConfig();
    globalThis.fetch.mockRejectedValueOnce(new Error("Network error"));

    await requestFeeds("test query");

    expect(navigateToError).toHaveBeenCalledWith(
      "offline",
      "Connection Error",
      "Unable to reach the server.",
      "Retry",
      expect.any(Function),
    );
  });

  it("handles ExternalApiBadResponse correctly", async () => {
    const { navigateToError } = await import(
      "../src/controllers/statusStore.js"
    );
    mockConfig();
    globalThis.fetch.mockResolvedValueOnce({
      ok: false,
      json: () => Promise.resolve({ error: "ExternalApiBadResponse" }),
    });

    await requestFeeds("test query");

    expect(navigateToError).toHaveBeenCalledWith(
      "external-error",
      "PodcastIndex Error",
      "The PodcastIndex returned invalid data. Please try again later.",
      "Retry",
      expect.any(Function),
    );
  });

  it("handles ExternalApiTimeout correctly", async () => {
    const { navigateToError } = await import(
      "../src/controllers/statusStore.js"
    );
    mockConfig();
    globalThis.fetch.mockResolvedValueOnce({
      ok: false,
      json: () => Promise.resolve({ error: "ExternalApiTimeout" }),
    });

    await requestFeeds("test query");

    expect(navigateToError).toHaveBeenCalledWith(
      "external-error",
      "Search Timeout",
      "The PodcastIndex is taking too long to respond. Please try again.",
      "Retry",
      expect.any(Function),
    );
  });

  it("handles ExternalApiUnavaliable correctly", async () => {
    const { navigateToError } = await import(
      "../src/controllers/statusStore.js"
    );
    mockConfig();
    globalThis.fetch.mockResolvedValueOnce({
      ok: false,
      json: () => Promise.resolve({ error: "ExternalApiUnavaliable" }),
    });

    await requestFeeds("test query");

    expect(navigateToError).toHaveBeenCalledWith(
      "external-error",
      "Service Unavailable",
      "The PodcastIndex service is temporarily unavailable. Please try again later.",
      "Retry",
      expect.any(Function),
    );
  });

  it("handles 500 server error correctly", async () => {
    const { navigateToError } = await import(
      "../src/controllers/statusStore.js"
    );
    mockConfig();
    globalThis.fetch.mockResolvedValueOnce({
      ok: false,
      status: 500,
      json: () => Promise.resolve({}),
    });

    await requestFeeds("test query");

    expect(navigateToError).toHaveBeenCalledWith(
      "error",
      "Server Error",
      "Something went wrong on our end. Please try again.",
      "Retry",
      expect.any(Function),
    );
  });

  it("navigates to empty-feed-error when results are empty", async () => {
    const { navigateToError } = await import(
      "../src/controllers/statusStore.js"
    );

    mockConfig();
    globalThis.fetch.mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve({ feeds: [] }),
    });

    await requestFeeds("empty query");

    expect(navigateToError).toHaveBeenCalledWith(
      "empty-feed-error",
      "No Results",
      'No music feeds found matching "empty query".',
      "Try Different Search",
      expect.any(Function),
    );
  });
});
