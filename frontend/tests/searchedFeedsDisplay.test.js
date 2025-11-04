import { describe, it, expect } from "vitest";
import SearchedFeedsDisplay from "../src/controllers/searchedFeedsDisplay.js";
import { searchedFeeds } from "../src/controllers/localFeedStore.js";

describe("SearchedFeedsDisplay", () => {
  it("has correct component name", () => {
    expect(SearchedFeedsDisplay.name).toBe("SearchedFeedsDisplay");
  });

  it("includes FeedCard component", () => {
    expect(SearchedFeedsDisplay.components.FeedCard).toBeDefined();
  });

  it("computes feed correctly", () => {
    const testFeed = { id: 1, title: "Test Feed" };
    searchedFeeds.push(testFeed);

    const computed = SearchedFeedsDisplay.computed.searchedFeeds();
    expect(computed).toEqual(searchedFeeds); // Use deep equality
    expect(computed).toContainEqual(testFeed); // Use deep equality for object comparison

    searchedFeeds.splice(0, searchedFeeds.length); // Clean up
  });
});
