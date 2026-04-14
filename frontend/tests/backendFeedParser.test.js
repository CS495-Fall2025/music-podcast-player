import { describe, it, expect, vi, beforeEach } from "vitest";
import { requestFeeds } from "../src/controllers/backendFeedParser.js";
import { searchedFeeds } from "../src/controllers/localFeedStore.js";
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

describe("backendFeedParser controller", () => {
  // mock config.json
  const mockConfig = () => {
    globalThis.fetch.mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve({ backendUrl: "http://localhost:5000" }),
    });
  };

  // Reset state and mock console/fetch before each test
  beforeEach(() => {
    searchedFeeds.splice(0, searchedFeeds.length);

    vi.spyOn(console, "log").mockImplementation(() => {});
    globalThis.fetch = vi.fn();

    vi.clearAllMocks();
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
    mockConfig();
    globalThis.fetch.mockResolvedValueOnce({
      ok: false,
      status: 404,
      json: () => Promise.resolve({}), // Added so response.json() doesn't throw
    });

    await requestFeeds("test query");

    expect(setError).toHaveBeenCalledWith(
      "error",
      "Invalid Request",
      "Your request was rejected by the server. Please try again.",
      "Retry",
      expect.any(Function),
    );
  });

  // Test handling of network errors
  it("requestFeeds handles network error correctly", async () => {
    const mockError = new Error("Network error");

    mockConfig();
    globalThis.fetch.mockRejectedValueOnce(mockError);

    await requestFeeds("test query");

    expect(setError).toHaveBeenCalledWith(
      "offline",
      "Connection Error",
      "Unable to reach the server.",
      "Retry",
      expect.any(Function),
    );
  });

  it("sets loading state correctly during a successful request", async () => {
    mockConfig();
    globalThis.fetch.mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve({ feeds: [{ id: 1 }] }),
    });

    await requestFeeds("test query");

    expect(setLoading).toHaveBeenCalledWith(true);
    expect(clearError).toHaveBeenCalled();
    expect(setLoading).toHaveBeenCalledWith(false); // Called in finally block
  });

  it("handles empty feed results by setting an empty-feed-error", async () => {
    mockConfig();
    globalThis.fetch.mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve({ feeds: [] }),
    });

    await requestFeeds("empty query");

    expect(setError).toHaveBeenCalledWith(
      "empty-feed-error",
      "No Results",
      'No music feeds found matching "empty query".',
      "Try Another Search",
      expect.any(Function),
    );
  });

  it("parses and handles ExternalApiBadResponse correctly", async () => {
    mockConfig();
    globalThis.fetch.mockResolvedValueOnce({
      ok: false,
      json: () => Promise.resolve({ error: "ExternalApiBadResponse" }),
    });

    await requestFeeds("test query");

    expect(setError).toHaveBeenCalledWith(
      "external-error",
      "PodcastIndex Error",
      "The PodcastIndex returned invalid data. Please try again later.",
      "Retry",
      expect.any(Function),
    );
  });

  it("parses and handles ExternalApiTimeout correctly", async () => {
    mockConfig();
    globalThis.fetch.mockResolvedValueOnce({
      ok: false,
      json: () => Promise.resolve({ error: "ExternalApiTimeout" }),
    });

    await requestFeeds("test query");

    expect(setError).toHaveBeenCalledWith(
      "external-error",
      "Search Timeout",
      "The PodcastIndex is taking too long to respond. Please try again.",
      "Retry",
      expect.any(Function),
    );
  });

  it("handles 500 status code correctly", async () => {
    mockConfig();
    globalThis.fetch.mockResolvedValueOnce({
      ok: false,
      status: 500,
      json: () => Promise.resolve({}),
    });

    await requestFeeds("test query");

    expect(setError).toHaveBeenCalledWith(
      "error",
      "Server Error",
      "Something went wrong on our end. Please try again.",
      "Retry",
      expect.any(Function),
    );
  });

  it("handles network connection exceptions gracefully", async () => {
    mockConfig();
    globalThis.fetch.mockRejectedValueOnce(new TypeError("Failed to fetch"));

    await requestFeeds("test query");

    expect(setError).toHaveBeenCalledWith(
      "offline",
      "Connection Error",
      "Unable to reach the server.",
      "Retry",
      expect.any(Function),
    );
    expect(setLoading).toHaveBeenCalledWith(false);
  });
});
