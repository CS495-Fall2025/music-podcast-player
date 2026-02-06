import { describe, it, expect } from "vitest";
import UserFeed from "../src/controllers/userFeed.js";
import { feedTracks } from "../src/controllers/localFeedStore.js";

describe("UserFeed", () => {
  // Test component name is set correctly
  it("has correct component name", () => {
    expect(UserFeed.name).toBe("UserFeed");
  });

  // Test Track component is registered
  it("includes Track component", () => {
    expect(UserFeed.components.Track).toBeDefined();
  });

  // Test computed property returns feedTracks with correct data
  it("computes feedTracks correctly", () => {
    const testTrack = { type: "track", title: "Test Track", audio: "test.mp3" };
    feedTracks.push(testTrack);

    const computed = UserFeed.computed.feedTracks();
    expect(computed).toBe(feedTracks);
    expect(computed[0]).toEqual(testTrack);

    feedTracks.splice(0, feedTracks.length);
  });
});
