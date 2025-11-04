import { describe, it, expect } from "vitest";
import {
  feed,
  currentTrack,
  searchedFeeds,
} from "../src/controllers/localFeedStore.js";

describe("localFeedStore", () => {
  it("feed is initialized as an empty reactive array", () => {
    expect(Array.isArray(feed)).toBe(true);
    expect(feed.length).toBe(0);
  });

  it("currentTrack is initialized as an empty ref string", () => {
    expect(currentTrack.value).toBe("");
  });

  it("searchedFeeds is initialized as an empty reactive array", () => {
    expect(Array.isArray(searchedFeeds)).toBe(true);
    expect(searchedFeeds.length).toBe(0);
  });

  it("feed can be modified", () => {
    const testItem = {
      type: "audio",
      title: "Test",
      imageUrl: "test.jpg",
      audioUrl: "test.mp3",
    };
    feed.push(testItem);
    expect(feed[0]).toEqual(testItem);
    feed.splice(0, feed.length); // Clean up
  });

  it("currentTrack can be modified", () => {
    const testUrl = "http://test.com/audio.mp3";
    currentTrack.value = testUrl;
    expect(currentTrack.value).toBe(testUrl);
    currentTrack.value = ""; // Clean up
  });

  it("searchedFeeds can be modified", () => {
    const testFeed = { id: 1, title: "Test Feed" };
    searchedFeeds.push(testFeed);
    expect(searchedFeeds[0]).toEqual(testFeed);
    searchedFeeds.splice(0, searchedFeeds.length); // Clean up
  });
});
