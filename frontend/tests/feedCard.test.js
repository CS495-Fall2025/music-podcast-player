import { describe, it, expect, vi } from "vitest";
import feedCard from "../src/controllers/feedCard.js";
import { requestFeedFromURL } from "../src/controllers/rssParsing.js";
import router from "../src/router";

vi.mock("../router", () => ({
  default: {
    push: vi.fn(),
  },
}));

vi.mock("../src/controllers/rssParsing.js", () => ({
  requestFeedFromURL: vi.fn(),
}));

describe("feedCard controller", () => {
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

    expect(requestFeedFromURL).toHaveBeenCalledWith(mockFeed.url);
    expect(vi.mocked(router).push).toHaveBeenCalledWith("/view");
  });
});
