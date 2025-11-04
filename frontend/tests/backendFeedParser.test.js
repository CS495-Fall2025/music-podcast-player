import { describe, it, expect, vi, beforeEach } from "vitest";
import { requestFeeds } from "../src/controllers/backendFeedParser.js";
import { searchedFeeds } from "../src/controllers/localFeedStore.js";

describe("backendFeedParser controller", () => {
  beforeEach(() => {
    // Clear searchedFeeds before each test
    searchedFeeds.splice(0, searchedFeeds.length);
    // Mock console
    vi.spyOn(console, "log").mockImplementation(() => {});
    // Mock fetch
    global.fetch = vi.fn();
  });

  it("requestFeeds calls fetch with correct URL and updates searchedFeeds on success", async () => {
    const mockFeeds = [{ id: 1, title: "Test Feed" }];
    const mockResponse = { feeds: mockFeeds };

    fetch.mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve(mockResponse),
    });

    requestFeeds("test query");

    // Wait for micro tasks to complete
    await Promise.resolve();

    // Verify the fetch call
    expect(fetch).toHaveBeenCalledWith(
      "http://localhost:5000/search/feeds?query=test%20query&count=50",
    );

    // Wait for state updates
    await vi.dynamicImportSettled();
    expect(Array.from(searchedFeeds)).toEqual(mockFeeds);
  });

  it("requestFeeds handles fetch error correctly", async () => {
    const consoleSpy = vi.spyOn(console, "log");

    fetch.mockResolvedValueOnce({
      ok: false,
      status: 404,
    });

    requestFeeds("test query");

    // Wait for micro tasks and promises
    await Promise.resolve();
    await vi.dynamicImportSettled();

    expect(consoleSpy).toHaveBeenCalledWith("Request returned status 404");
  });

  it("requestFeeds handles network error correctly", async () => {
    const consoleSpy = vi.spyOn(console, "log");
    const mockError = new Error("Network error");

    fetch.mockRejectedValueOnce(mockError);

    requestFeeds("test query");

    // Wait for micro tasks and promises
    await Promise.resolve();
    await vi.dynamicImportSettled();

    expect(consoleSpy).toHaveBeenCalledWith(
      "Error encountered while reading response from backend.",
    );
    expect(consoleSpy).toHaveBeenCalledWith(mockError);
  });
});
