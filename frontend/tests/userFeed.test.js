import { describe, it, expect } from "vitest";
import UserFeed from "../src/controllers/userFeed.js";
import { feed } from "../src/controllers/localFeedStore.js";

describe("UserFeed", () => {
  // Test component name is set correctly
  it("has correct component name", () => {
    expect(UserFeed.name).toBe("UserFeed");
  });

  // Test Track component is registered
  it("includes Track component", () => {
    expect(UserFeed.components.Track).toBeDefined();
  });

  // Test computed property returns feed with correct data
  it("computes feed correctly", () => {
    const testTrack = { type: "track", title: "Test Track", audio: "test.mp3" };
    feed.push(testTrack);

    const computed = UserFeed.computed.feed();
    expect(computed).toBe(feed);
    expect(computed[0]).toEqual(testTrack);

    feed.splice(0, feed.length);
  });
});
