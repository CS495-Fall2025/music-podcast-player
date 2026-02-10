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

    expect(Array.from(searchedFeeds)).toEqual(mockFeeds);
  });

  // Test handling of HTTP error responses
  it("requestFeeds handles fetch error correctly", async () => {
    const consoleSpy = vi.spyOn(console, "log");

    mockConfig();
    globalThis.fetch.mockResolvedValueOnce({
      ok: false,
      status: 404,
    });

    await requestFeeds("test query");

    expect(consoleSpy).toHaveBeenCalledWith("Request returned status 404");
  });

  // Test handling of network errors
  it("requestFeeds handles network error correctly", async () => {
    const consoleSpy = vi.spyOn(console, "log");
    const mockError = new Error("Network error");

    mockConfig();
    globalThis.fetch.mockRejectedValueOnce(mockError);

    await requestFeeds("test query");

    expect(consoleSpy).toHaveBeenCalledWith(
      "Error encountered while reading response from backend.",
    );
    expect(consoleSpy).toHaveBeenCalledWith(mockError);
  });
});
