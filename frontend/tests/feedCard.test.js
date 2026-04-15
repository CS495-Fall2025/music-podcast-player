import { describe, it, expect, vi, beforeEach } from "vitest";
import { requestLinkedFeeds } from "../src/controllers/backendLinkParser.js";

vi.mock("../src/router", () => ({
  default: {
    push: vi.fn(),
  },
}));

vi.mock("../src/controllers/backendLinkParser.js", () => ({
  requestLinkedFeeds: vi.fn(),
}));

// import after mocks are defined
import router from "../src/router";
import feedCard from "../src/controllers/feedCard.js";

describe("feedCard controller", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("has correct component name", () => {
    expect(feedCard.name).toBe("feedCard");
  });

  it("requires feed prop", () => {
    expect(feedCard.props.feed.required).toBe(true);
    expect(feedCard.props.feed.type).toBe(Object);
  });

  it("selectTrack method requests feed and navigates to view page", () => {
    const mockFeed = { url: "http://test.com/feed" };
    const component = {
      feed: mockFeed,
    };

    feedCard.methods.selectTrack.call(component);

    expect(requestLinkedFeeds).toHaveBeenCalledWith(mockFeed.url);
    expect(router.push).toHaveBeenCalledWith("/view");
  });
});
