import { describe, it, expect } from "vitest";
import SearchedFeedsDisplay from "../src/controllers/searchedFeedsDisplay.js";
import { searchedFeeds } from "../src/controllers/localFeedStore.js";

describe("SearchedFeedsDisplay", () => {
  // Test component name is set correctly
  it("has correct component name", () => {
    expect(SearchedFeedsDisplay.name).toBe("SearchedFeedsDisplay");
  });

  // Test FeedCard component is registered
  it("includes FeedCard component", () => {
    expect(SearchedFeedsDisplay.components.FeedCard).toBeDefined();
  });

  // Test computed property returns searchedFeeds
  it("computes feed correctly", () => {
    const testFeed = { id: 1, title: "Test Feed" };
    searchedFeeds.push(testFeed);

    const computed = SearchedFeedsDisplay.computed.searchedFeeds();
    expect(computed).toEqual(searchedFeeds);
    expect(computed).toContainEqual(testFeed);

    searchedFeeds.splice(0, searchedFeeds.length);
  });
});
